from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Concatenate, ParamSpec, TypeVar

from bleak.backends.device import BLEDevice

from .const import (
    AuxControlState,
    EfireCommand,
    LedMode,
    LedState,
    PasswordAction,
    PasswordCommandResult,
    PowerState,
    ResponseCode,
    ReturnCode,
)
from .device import EfireDevice
from .exceptions import AuthError, CommandFailedException, FeatureNotSupported
from .parser import (
    parse_ble_version,
    parse_led_color,
    parse_led_controller_state,
    parse_mcu_version,
    parse_off_state,
    parse_on_state,
    parse_timer,
)

_LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def needs_auth(
    func: Callable[Concatenate[Fireplace, P], Awaitable[T]]
) -> Callable[Concatenate[Fireplace, P], Awaitable[T]]:
    """Define a wrapper to authenticate if we aren't yet."""

    async def _authenticated_operation(
        self: Fireplace, *args: P.args, **kwargs: P.kwargs
    ) -> T:
        if not self._is_authenticated:
            _LOGGER.debug(
                "[%s]: Command %s requires authentication. Attempting authentication.",
                self.name,
                func.__name__,
            )
            auth_result = await self.authenticate(self._password)
            if not auth_result:
                raise AuthError(
                    "Command requires authentication but authentication was"
                    " not successful"
                )
        return await func(self, *args, **kwargs)

    return _authenticated_operation


@dataclass
class FireplaceFeatures:
    aux: bool = False
    blower: bool = False
    led_lights: bool = False
    night_light: bool = False
    split_flow: bool = False


@dataclass
class FireplaceState:
    aux: bool = False
    blower_speed: int = 0
    flame_height: int = 0
    led_color: tuple[int, int, int] = (0, 0, 0)
    led_mode: LedMode = LedMode.HOLD  # type: ignore
    led: bool = False
    main_mode: int = 0
    night_light_brightness: int = 0
    pilot: bool = False
    power: bool = False
    remote_in_use: bool = False
    split_flow: bool = False
    time_left: tuple[int, int, int] = (0, 0, 0)
    timer: bool = False


class Fireplace(EfireDevice):
    _features: FireplaceFeatures
    _state: FireplaceState

    def __init__(
        self,
        ble_device: BLEDevice,
        password: str,
        features: FireplaceFeatures | None = None,
    ) -> None:
        super().__init__(ble_device)

        self._password = password
        self._features = features if features else FireplaceFeatures()
        self._state = FireplaceState()

    async def _simple_command(
        self, command: int, parameter: int | bytes | bytearray | None = None
    ) -> bool:
        result = await self.execute_command(command, parameter)

        return result == ReturnCode.SUCCESS

    async def _off_state_command(self) -> bool:
        payload = bytearray(
            [
                0x0,
                1 | (self._state.night_light_brightness << 4) | self._state.pilot << 7,
            ]
        )
        result = await self._simple_command(EfireCommand.OFF_STATE_CMDS, payload)

        _LOGGER.debug("[%s]: Off State command result: %s", self.name, result)
        return result

    async def _on_state_command(self) -> bool:
        data = (
            (self._state.split_flow << 7)
            | (self._state.blower_speed << 4)
            | (self._state.aux << 3)
            | self._state.flame_height
        )
        payload = bytearray([0x0, data])
        result = await self._simple_command(EfireCommand.ON_STATE_CMDS, payload)

        _LOGGER.debug("[%s]: On State command result: %s", self.name, result)
        return result

    async def authenticate(self, password: str) -> bool:
        response = await self.execute_command(
            EfireCommand.SEND_PASSWORD, password.encode("ascii")
        )
        self._is_authenticated = False
        if response[0] == PasswordCommandResult.LOGIN_SUCCESS:
            _LOGGER.debug("[%s]: Login successful", self.name)
            self._is_authenticated = True
        elif response[0] == PasswordCommandResult.INVALID_PASSWORD:
            _LOGGER.debug("[%s]: Invalid password", self.name)

        return self._is_authenticated

    @needs_auth
    async def power(self, state: bool) -> bool:
        result = await self._simple_command(
            EfireCommand.POWER, PowerState.ON if state else PowerState.OFF
        )

        self._state.power = result
        return result

    @needs_auth
    async def power_on(self) -> bool:
        return await self.power(True)

    @needs_auth
    async def power_off(self) -> bool:
        return await self.power(False)

    @needs_auth
    async def set_night_light_brightness(self, brightness: int) -> bool:
        if not 0 <= brightness <= 6:
            raise ValueError("Night Light brightness must be between 0 and 6.")
        self._state.night_light_brightness = brightness
        return await self._off_state_command()

    @needs_auth
    async def set_continuous_pilot(self, enable: bool = True) -> bool:
        self._state.pilot = enable
        return await self._off_state_command()

    @needs_auth
    async def set_aux(self, enabled: bool) -> bool:
        if not self._features.aux:
            raise FeatureNotSupported(
                f"Fireplace {self.name} does not support AUX relais control"
            )
        self._state.aux = enabled
        return await self._on_state_command()

    @needs_auth
    async def set_flame_height(self, flame_height: int) -> bool:
        if not 0 <= flame_height <= 6:
            raise ValueError("Flame height must be between 0 and 6.")
        self._state.flame_height = flame_height
        return await self._on_state_command()

    @needs_auth
    async def set_blower_speed(self, blower_speed: int) -> bool:
        if not self._features.aux:
            raise FeatureNotSupported(f"Fireplace {self.name} does not have a blower")

        if not 0 <= blower_speed <= 6:
            raise ValueError("Blower speed must be between 0 and 6.")
        self._state.blower_speed = blower_speed
        return await self._on_state_command()

    @needs_auth
    async def set_split_flow(self, enabled: bool) -> bool:
        if not self._features.split_flow:
            raise FeatureNotSupported(
                f"Fireplace {self.name} does not have split flow valve"
            )

        self._state.split_flow = enabled
        return await self._on_state_command()

    @needs_auth
    async def set_led_mode(self, light_mode: LedMode, state: bool = False) -> bool:
        if not self._features.led_lights:
            raise FeatureNotSupported(
                f"Fireplace {self.name}does not have LED controller"
            )
        parameter = light_mode.setvalue  # pyright: ignore

        # the value to disable modes is the value for enabling it + 5
        if not state:
            parameter = parameter + 0x5

        result = await self._simple_command(EfireCommand.LED_MODE, parameter)
        return result == ReturnCode.SUCCESS

    @needs_auth
    async def set_timer(self, hours: int, minutes: int, enabled: bool) -> bool:
        ret_timer = await self._simple_command(
            EfireCommand.TIMER, bytes([hours, minutes, enabled])
        )
        # Not entirely sure what the following does. But this mimics what the app
        # would send
        ret_sync = await self._simple_command(
            EfireCommand.SYNC_TIME, bytes([hours, minutes, False])
        )

        return ret_timer and ret_sync

    @needs_auth
    async def set_led_color(self, color: tuple[int, int, int]) -> bool:
        if not self._features.led_lights:
            raise FeatureNotSupported(
                f"Fireplace {self.name} does not have LED controller"
            )

        return await self._simple_command(
            EfireCommand.LED_COLOR, bytes([color[0], color[1], color[2]])
        )

    @needs_auth
    async def set_led_state(self, state: bool) -> bool:
        if not self._features.led_lights:
            raise FeatureNotSupported(
                f"Fireplace {self.name} does not have LED controller"
            )

        result = await self._simple_command(
            EfireCommand.LED_POWER,
            LedState.ON.long if state else LedState.OFF.long,  # type: ignore
        )
        return result

    @needs_auth
    async def led_on(self) -> bool:
        return await self.set_led_state(True)

    @needs_auth
    async def led_off(self) -> bool:
        return await self.set_led_state(False)

    @needs_auth
    async def query_aux_control(self) -> AuxControlState:
        result = await self.execute_command(EfireCommand.QUERY_AUX_CTRL)
        _LOGGER.debug("[%s]: Aux Control State: %x", self.name, result)
        return AuxControlState(int.from_bytes(result, "big"))

    @needs_auth
    async def set_password(self, password: str) -> bool:
        # Enter Password management
        enable_password_mgmt = await self._simple_command(
            EfireCommand.PASSWORD_MGMT, PasswordAction.SET
        )
        if enable_password_mgmt:
            # Send the desired password
            result = await self.execute_command(
                EfireCommand.SEND_PASSWORD, password.encode("ascii")
            )

            return result[0] == PasswordCommandResult.SET_SUCCESS
        return False

    async def reset_password(self) -> bool:
        result = await self._simple_command(
            EfireCommand.PASSWORD_MGMT, PasswordAction.RESET
        )

        return result

    # E0
    @needs_auth
    async def update_led_state(self) -> None:
        result = await self.execute_command(ResponseCode.LED_STATE)

        self._state.led = result == LedState.ON.long  # type:ignore

    # E1
    @needs_auth
    async def update_led_color(self) -> None:
        result = await self.execute_command(ResponseCode.LED_COLOR)

        self._state.led_color = parse_led_color(result)

    # E2
    @needs_auth
    async def update_led_controller_mode(self) -> None:
        result = await self.execute_command(ResponseCode.LED_MODE)

        self._state.led_mode = LedMode(int.from_bytes(result, "big"))  # pyright: ignore

    # E3
    @needs_auth
    async def update_off_state_settings(self) -> None:
        result = await self.execute_command(ResponseCode.OFF_STATE_CMDS)

        if result[0] == ReturnCode.FAILURE:
            raise CommandFailedException(
                f"Command failed with return code {result.hex()}"
            )
        (
            self._state.pilot,
            self._state.night_light_brightness,
            self._state.main_mode,
        ) = parse_off_state(result)

    # E4
    @needs_auth
    async def update_on_state_settings(self) -> None:
        result = await self.execute_command(ResponseCode.ON_STATE_CMDS)
        (
            self._state.split_flow,
            self._state.aux,
            self._state.blower_speed,
            self._state.flame_height,
        ) = parse_on_state(result)

    # E6
    @needs_auth
    async def update_timer_state(self) -> None:
        result = await self.execute_command(ResponseCode.TIMER)
        self._state.time_left, self._state.timer = parse_timer(result)

    # E7
    @needs_auth
    async def update_power_state(self) -> None:
        result = await self.execute_command(ResponseCode.POWER_STATE)

        self._state.power = result == PowerState.ON

    # EB
    @needs_auth
    async def update_led_controller_state(self) -> None:
        result = await self.execute_command(ResponseCode.LED_CONTROLLER_STATE)

        (
            self._state.led,
            self._state.led_color,
            self._state.led_mode,
        ) = parse_led_controller_state(result)

    # EE
    @needs_auth
    async def update_remote_usage(self) -> None:
        result = await self.execute_command(ResponseCode.REMOTE_USAGE)

        self._state.remote_in_use = result == AuxControlState.USED

    # F2
    @needs_auth
    async def query_ble_version(self) -> str:
        result = await self.execute_command(EfireCommand.BLE_VERSION)

        return parse_ble_version(result)

    # F3
    @needs_auth
    async def query_mcu_version(self) -> str:
        result = await self.execute_command(EfireCommand.MCU_VERSION)

        return parse_mcu_version(result)

    async def update_state(self) -> None:
        await self.update_off_state_settings()
        await self.update_on_state_settings()
        await self.update_power_state()
        await self.update_timer_state()
        if self._features.aux:
            await self.query_aux_control()
        if self._features.led_lights:
            await self.update_led_state()
            await self.update_led_color()
            await self.update_led_controller_mode()
