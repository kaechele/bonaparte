from __future__ import annotations

from dataclasses import dataclass
from dataclasses import fields as dc_fields
import logging
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeVar

from .const import (
    MAX_BLOWER_SPEED,
    MAX_FLAME_HEIGHT,
    MAX_NIGHT_LIGHT_BRIGHTNESS,
    AuxControlState,
    EfireCommand,
    LedMode,
    LedState,
    PasswordAction,
    PasswordCommandResult,
    PowerState,
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

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def needs_auth(
    func: Callable[Concatenate[Fireplace, P], Awaitable[T]]
) -> Callable[Concatenate[Fireplace, P], Awaitable[T]]:
    """Define a wrapper to authenticate if we aren't yet authenticated."""

    async def _authenticated_operation(
        self: Fireplace, *args: P.args, **kwargs: P.kwargs
    ) -> T:
        if not self._is_authenticated:  # pylint: disable=protected-access
            _LOGGER.debug(
                "[%s]: Command %s requires authentication. Attempting authentication.",
                self.name,
                func.__name__,
            )
            auth_result = await self.authenticate(
                self._password  # pylint: disable=protected-access
            )
            if not auth_result:
                msg = (
                    "Command requires authentication but authentication was"
                    " not successful"
                )
                raise AuthError(msg)
        return await func(self, *args, **kwargs)

    return _authenticated_operation


@dataclass
class FireplaceFeatures:
    aux: bool = False
    blower: bool = False
    led_lights: bool = False
    night_light: bool = False
    split_flow: bool = False
    timer: bool = False


@dataclass
class FireplaceState:
    aux: bool = False
    blower_speed: int = 0
    flame_height: int = 0
    led_color: tuple[int, int, int] = (0, 0, 0)
    led_mode: LedMode = LedMode.HOLD  # type: ignore[assignment]
    led: bool = False
    main_mode: int = 0
    night_light_brightness: int = 0
    pilot: bool = False
    power: bool = False
    remote_in_use: bool = False
    split_flow: bool = False
    time_left: tuple[int, int, int] = (0, 0, 0)
    timer: bool = False
    mcu_version: str = ""
    ble_version: str = ""


class Fireplace(EfireDevice):
    _features: FireplaceFeatures
    _is_authenticated: bool
    _state: FireplaceState
    _password: str

    def __init__(
        self,
        ble_device: BLEDevice,
        features: FireplaceFeatures | None = None,
    ) -> None:
        super().__init__(ble_device)

        self._features = features if features else FireplaceFeatures()
        self._is_authenticated = False
        self._state = FireplaceState()
        self._disconnect_callbacks: list[Callable[[Fireplace], None]] = []

        def disconnected_callback(self: Fireplace) -> None:
            self._is_authenticated = False

        self._register_disconnect_callback(disconnected_callback)

    @property
    def has_aux(self) -> bool:
        return self._features.aux

    @property
    def has_blower(self) -> bool:
        return self._features.blower

    @property
    def has_led_lights(self) -> bool:
        return self._features.led_lights

    @property
    def has_night_light(self) -> bool:
        return self._features.night_light

    @property
    def has_split_flow(self) -> bool:
        return self._features.split_flow

    @property
    def state(self) -> FireplaceState:
        return self._state

    def set_features(self, features: set[str]) -> FireplaceFeatures:
        feature_set = {field.name for field in dc_fields(self._features)}
        if not feature_set >= features:
            invalid_feature = features - feature_set
            msg = (
                f"Invalid feature value{'s' if len(invalid_feature) > 1 else ''} found"
                f" in input set: {invalid_feature}"
            )
            raise ValueError(msg)
        new_featureset = FireplaceFeatures(**{f: True for f in features})
        self._features = new_featureset
        return self._features

    async def _simple_command(
        self, command: int, parameter: int | bytes | bytearray | None = None
    ) -> bool:
        result = await self.execute_command(command, parameter)

        return result[0] == ReturnCode.SUCCESS

    async def _ifc_cmd1(self) -> bool:
        payload = bytearray(
            [
                0x0,
                self._state.main_mode << 1
                | (self._state.night_light_brightness << 4)
                | self._state.pilot << 7,
            ]
        )
        result = await self._simple_command(EfireCommand.SET_IFC_CMD1, payload)

        _LOGGER.debug("[%s]: Off State command result: %s", self.name, result)
        return result

    async def _ifc_cmd2(self) -> bool:
        data = (
            (self._state.split_flow << 7)
            | (self._state.blower_speed << 4)
            | (self._state.aux << 3)
            | self._state.flame_height
        )
        payload = bytearray([0x0, data])
        result = await self._simple_command(EfireCommand.SET_IFC_CMD2, payload)

        _LOGGER.debug("[%s]: On State command result: %s", self.name, result)
        return result

    async def authenticate(self, password: str) -> bool:
        response = await self.execute_command(
            EfireCommand.SEND_PASSWORD, password.encode("ascii")
        )
        self._is_authenticated = False
        if response[0] == PasswordCommandResult.LOGIN_SUCCESS:
            _LOGGER.debug("[%s]: Login successful", self.name)
            self._password = password
            self._is_authenticated = True
        elif response[0] == PasswordCommandResult.INVALID_PASSWORD:
            _LOGGER.debug("[%s]: Invalid password", self.name)

        return self._is_authenticated

    @needs_auth
    async def power(self, *, on: bool) -> bool:
        result = await self._simple_command(
            EfireCommand.SET_POWER, PowerState.ON if on else PowerState.OFF
        )

        self._state.power = result
        if not on:
            self._state.blower_speed = 0
            self._state.flame_height = 0
        return result

    @needs_auth
    async def power_on(self) -> bool:
        return await self.power(on=True)

    @needs_auth
    async def power_off(self) -> bool:
        return await self.power(on=False)

    @needs_auth
    async def set_night_light_brightness(self, brightness: int) -> bool:
        if not 0 <= brightness <= MAX_NIGHT_LIGHT_BRIGHTNESS:
            msg = "Night Light brightness must be between 0 and 6."
            raise ValueError(msg)
        self._state.night_light_brightness = brightness
        return await self._ifc_cmd1()

    @needs_auth
    async def set_continuous_pilot(self, *, enabled: bool = True) -> bool:
        self._state.pilot = enabled
        return await self._ifc_cmd1()

    @needs_auth
    async def set_aux(self, *, enabled: bool) -> bool:
        if not self._features.aux:
            msg = f"Fireplace {self.name} does not support AUX relais control"
            raise FeatureNotSupported(msg)
        self._state.aux = enabled
        return await self._ifc_cmd2()

    @needs_auth
    async def set_flame_height(self, flame_height: int) -> bool:
        if not 0 <= flame_height <= MAX_FLAME_HEIGHT:
            msg = "Flame height must be between 0 and 6."
            raise ValueError(msg)
        self._state.flame_height = flame_height
        return await self._ifc_cmd2()

    @needs_auth
    async def set_blower_speed(self, blower_speed: int) -> bool:
        if not self._features.aux:
            msg = f"Fireplace {self.name} does not have a blower"
            raise FeatureNotSupported(msg)

        if not 0 <= blower_speed <= MAX_BLOWER_SPEED:
            msg = "Blower speed must be between 0 and 6."
            raise ValueError(msg)
        self._state.blower_speed = blower_speed
        return await self._ifc_cmd2()

    @needs_auth
    async def set_split_flow(self, *, enabled: bool) -> bool:
        if not self._features.split_flow:
            msg = f"Fireplace {self.name} does not have split flow valve"
            raise FeatureNotSupported(msg)

        self._state.split_flow = enabled
        return await self._ifc_cmd2()

    @needs_auth
    async def set_led_mode(self, light_mode: LedMode, *, on: bool = False) -> bool:
        if not self._features.led_lights:
            msg = f"Fireplace {self.name}does not have LED controller"
            raise FeatureNotSupported(msg)
        parameter = light_mode.setvalue  # pyright: ignore

        # the value to disable modes is the value for enabling it + 5
        if not on:
            parameter = parameter + 0x5

        result = await self._simple_command(EfireCommand.SET_LED_MODE, parameter)
        return result == ReturnCode.SUCCESS

    @needs_auth
    async def set_timer(self, hours: int, minutes: int, *, enabled: bool) -> bool:
        ret_timer = await self._simple_command(
            EfireCommand.SET_TIMER, bytes([hours, minutes, enabled])
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
            msg = f"Fireplace {self.name} does not have LED controller"
            raise FeatureNotSupported(msg)

        return await self._simple_command(
            EfireCommand.SET_LED_COLOR, bytes([color[0], color[1], color[2]])
        )

    @needs_auth
    async def set_led_state(self, *, on: bool) -> bool:
        if not self._features.led_lights:
            msg = f"Fireplace {self.name} does not have LED controller"
            raise FeatureNotSupported(msg)

        return await self._simple_command(
            EfireCommand.SET_LED_POWER,
            LedState.ON.long  # type: ignore[attr-defined] # pylint: disable=no-member
            if on
            else LedState.OFF.long,  # type: ignore[attr-defined] # pylint: disable=no-member   # noqa: E501
        )

    @needs_auth
    async def led_on(self) -> bool:
        return await self.set_led_state(on=True)

    @needs_auth
    async def led_off(self) -> bool:
        return await self.set_led_state(on=False)

    @needs_auth
    async def query_aux_control(self) -> AuxControlState:
        result = await self.execute_command(EfireCommand.GET_AUX_CTRL)
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
        return await self._simple_command(
            EfireCommand.PASSWORD_MGMT, PasswordAction.RESET
        )

    # E0
    @needs_auth
    async def update_led_state(self) -> None:
        result = await self.execute_command(EfireCommand.GET_LED_STATE)

        self._state.led = (
            result
            == LedState.ON.long  # type: ignore[attr-defined] # pylint: disable=no-member  # noqa: E501
        )

    # E1
    @needs_auth
    async def update_led_color(self) -> None:
        result = await self.execute_command(EfireCommand.GET_LED_COLOR)

        self._state.led_color = parse_led_color(result)

    # E2
    @needs_auth
    async def update_led_controller_mode(self) -> None:
        result = await self.execute_command(EfireCommand.GET_LED_MODE)

        self._state.led_mode = LedMode(int.from_bytes(result, "big"))  # pyright: ignore

    # E3
    @needs_auth
    async def update_off_state_settings(self) -> None:
        result = await self.execute_command(EfireCommand.GET_IFC_CMD1_STATE)

        if result[0] == ReturnCode.FAILURE:
            msg = f"Command failed with return code {result.hex()}"
            raise CommandFailedException(msg)
        (
            self._state.pilot,
            self._state.night_light_brightness,
            self._state.main_mode,
        ) = parse_off_state(result)

    # E4
    @needs_auth
    async def update_on_state_settings(self) -> None:
        result = await self.execute_command(EfireCommand.GET_IFC_CMD2_STATE)
        (
            self._state.split_flow,
            self._state.aux,
            self._state.blower_speed,
            self._state.flame_height,
        ) = parse_on_state(result)

    # E6
    @needs_auth
    async def update_timer_state(self) -> None:
        result = await self.execute_command(EfireCommand.GET_TIMER)
        self._state.time_left, self._state.timer = parse_timer(result)

    # E7
    @needs_auth
    async def update_power_state(self) -> None:
        result = await self.execute_command(EfireCommand.GET_POWER_STATE)

        self._state.power = result[0] == PowerState.ON

    # EB
    @needs_auth
    async def update_led_controller_state(self) -> None:
        result = await self.execute_command(EfireCommand.GET_LED_CONTROLLER_STATE)

        (
            self._state.led,
            self._state.led_color,
            self._state.led_mode,
        ) = parse_led_controller_state(result)

    # EE
    @needs_auth
    async def update_remote_usage(self) -> None:
        result = await self.execute_command(EfireCommand.GET_REMOTE_USAGE)

        self._state.remote_in_use = result == AuxControlState.USED

    # F2
    @needs_auth
    async def query_ble_version(self) -> str:
        result = await self.execute_command(EfireCommand.GET_BLE_VERSION)

        return parse_ble_version(result)

    # F3
    @needs_auth
    async def query_mcu_version(self) -> str:
        result = await self.execute_command(EfireCommand.GET_MCU_VERSION)

        return parse_mcu_version(result)

    async def update_state(self) -> None:
        await self.update_off_state_settings()
        await self.update_on_state_settings()
        await self.update_power_state()
        if self._features.timer:
            await self.update_timer_state()
        if self._features.led_lights:
            await self.update_led_state()
            await self.update_led_color()
            await self.update_led_controller_mode()

    async def update_firmware_version(self) -> None:
        self._state.mcu_version = await self.query_mcu_version()
        self._state.ble_version = await self.query_ble_version()
