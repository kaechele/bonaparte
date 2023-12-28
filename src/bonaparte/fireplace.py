"""Representation of a Fireplace."""
from __future__ import annotations

from dataclasses import dataclass, fields as dc_fields
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
    parse_ifc_cmd1_state,
    parse_ifc_cmd2_state,
    parse_led_color,
    parse_led_controller_state,
    parse_mcu_version,
    parse_timer,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def needs_auth(
    func: Callable[Concatenate[Fireplace, P], Awaitable[T]],
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
    """The set of features selected for the fireplace."""

    aux: bool = False
    blower: bool = False
    led_lights: bool = False
    night_light: bool = False
    split_flow: bool = False
    timer: bool = False


@dataclass
class FireplaceState:
    """State of each component in the fireplace."""

    aux: bool = False
    ble_version: str = ""
    blower_speed: int = 0
    bt_power: bool = False
    flame_height: int = 0
    ifc_power: bool = False
    led_color: tuple[int, int, int] = (0, 0, 0)
    led_mode: LedMode = LedMode.HOLD  # type: ignore[assignment]
    led: bool = False
    mcu_version: str = ""
    night_light_brightness: int = 0
    pilot: bool = False
    remote_in_use: bool = False
    split_flow: bool = False
    thermostat: bool = False
    time_left: tuple[int, int, int] = (0, 0, 0)
    timer: bool = False

    def __init__(self, *, compatibility_mode: bool = True) -> None:
        """Initialize the fireplace state."""
        self._compatibility_mode = compatibility_mode

    @property
    def power(self) -> bool:
        """Return whether the fireplace is considered turned on."""
        if self._compatibility_mode:
            return self.bt_power

        return self.ifc_power and self.flame_height > 0


class Fireplace(EfireDevice):
    """A class representing the fireplace with state and actions."""

    _features: FireplaceFeatures
    _is_authenticated: bool
    _state: FireplaceState
    _password: str

    def __init__(
        self,
        ble_device: BLEDevice,
        features: FireplaceFeatures | None = None,
        *,
        compatibility_mode: bool = True,
    ) -> None:
        """Initialize a fireplace."""
        super().__init__(ble_device)

        self._compatibility_mode = compatibility_mode
        self._features = features if features else FireplaceFeatures()

        self._is_authenticated = False
        self._state = FireplaceState(compatibility_mode=self._compatibility_mode)
        self._disconnect_callbacks: list[Callable[[Fireplace], None]] = []

        def disconnected_callback(self: Fireplace) -> None:
            self._is_authenticated = False

        self._register_disconnect_callback(disconnected_callback)

    @property
    def has_aux(self) -> bool:
        """Whether the AUX relay control is enabled."""
        return self._features.aux

    @property
    def has_blower(self) -> bool:
        """Whether the blower speed control is enabled."""
        return self._features.blower

    @property
    def has_led_lights(self) -> bool:
        """Whether the LED controller is enabled."""
        return self._features.led_lights

    @property
    def has_night_light(self) -> bool:
        """Whether the Night Light control is enabled."""
        return self._features.night_light

    @property
    def has_split_flow(self) -> bool:
        """Whether the split flow valve control is enabled."""
        return self._features.split_flow

    @property
    def state(self) -> FireplaceState:
        """The state of this fireplace."""
        return self._state

    @property
    def features(self) -> FireplaceFeatures:
        """Featureset of this fireplace."""
        return self._features

    def set_features(self, features: set[str]) -> FireplaceFeatures:
        """Set all features from a list of feature strings."""
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
        """Execute a command that returns only success or failure."""
        result = await self.execute_command(command, parameter)

        return result[0] == ReturnCode.SUCCESS

    async def _ifc_cmd1(self) -> bool:
        """Call the IFC CMD1 function with the current fireplace state."""
        # NOTE: The BT controller does not actually pass through the ifc_power
        # bit to the IFC
        payload = bytearray(
            [
                0x0,
                self._state.ifc_power
                | (self._state.thermostat << 1)
                | (self._state.night_light_brightness << 4)
                | (self._state.pilot << 7),
            ]
        )
        result = await self._simple_command(EfireCommand.SET_IFC_CMD1, payload)

        _LOGGER.debug("[%s]: CMD1 command result: %s", self.name, result)
        return result

    async def _ifc_cmd2(self) -> bool:
        """Call the IFC CMD2 function with the current fireplace state."""
        data = (
            (self._state.split_flow << 7)
            | (self._state.blower_speed << 4)
            | (self._state.aux << 3)
            | self._state.flame_height
        )
        payload = bytearray([0x0, data])
        result = await self._simple_command(EfireCommand.SET_IFC_CMD2, payload)

        _LOGGER.debug("[%s]: CMD2 command result: %s", self.name, result)
        return result

    async def authenticate(self, password: str) -> bool:
        """Authenticate with the fireplace."""
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
    async def power(self, *, on: bool, compatibility_mode: bool | None = None) -> bool:
        """Set the power state on the fireplace."""
        compatibility_mode = (
            self._compatibility_mode
            if compatibility_mode is None
            else compatibility_mode
        )

        if compatibility_mode:
            # Do what the official app does
            _LOGGER.debug(
                "[%s]: Using compatible power on method (compatibility_mode=True)",
                self.name,
            )
            result = await self._simple_command(
                EfireCommand.SET_POWER, PowerState.ON if on else PowerState.OFF
            )

            if result:
                self._state.bt_power = on

                # Internal BT controller power command sets blower speed and
                # flame height to certain values upon on/off.
                # Reflect that in our state.
                if on:
                    self._state.flame_height = 6
                else:
                    self._state.blower_speed = 0
                    self._state.flame_height = 0
            return result

        # Custom power behavior implementation
        #
        # The BT controller doesn't let us write the power bit on the IFC.
        # But by setting flame height to 0 or non-zero we can power off/on
        # as well.
        # In doing this we can control flame and blower independently.
        if on and self._state.flame_height == 0:
            # Turning on without flame height assigned, might as well just
            # use proper power on then (which sets flame height to 6).
            self._state.flame_height = 6
            _LOGGER.debug(
                "[%s]: Using compatible power on method (compatibility_mode=False)",
                self.name,
            )

            return await self._simple_command(EfireCommand.SET_POWER, PowerState.ON)
        if not on and self._state.flame_height != 0:
            self._state.flame_height = 0
            if self._state.blower_speed == 0:
                # Blower is off already, might as well just use the proper
                # power off then.
                _LOGGER.debug(
                    "[%s]: Using compatible power off method"
                    " (compatibility_mode=False)",
                    self.name,
                )
                return await self._simple_command(
                    EfireCommand.SET_POWER, PowerState.OFF
                )
        _LOGGER.debug(
            "[%s]: Using non-compatible power off method (compatibility_mode=False)",
            self.name,
        )
        return await self._ifc_cmd2()

    @needs_auth
    async def power_on(self, *, compatibility_mode: bool | None = None) -> bool:
        """Power on the fireplace."""
        return await self.power(on=True, compatibility_mode=compatibility_mode)

    @needs_auth
    async def power_off(self, *, compatibility_mode: bool | None = None) -> bool:
        """Power off the fireplace."""
        return await self.power(on=False, compatibility_mode=compatibility_mode)

    @needs_auth
    async def set_night_light_brightness(self, brightness: int) -> bool:
        """Set the Night Light brightness."""
        if not 0 <= brightness <= MAX_NIGHT_LIGHT_BRIGHTNESS:
            msg = "Night Light brightness must be between 0 and 6"
            raise ValueError(msg)
        self._state.night_light_brightness = brightness
        return await self._ifc_cmd1()

    @needs_auth
    async def set_continuous_pilot(self, *, enabled: bool = True) -> bool:
        """Enable or disable the continuous pilot."""
        self._state.pilot = enabled
        return await self._ifc_cmd1()

    @needs_auth
    async def set_aux(self, *, enabled: bool) -> bool:
        """Enable or disable the AUX relay."""
        if not self._features.aux:
            msg = f"Fireplace {self.name} does not use AUX relay control"
            raise FeatureNotSupported(msg)
        self._state.aux = enabled
        return await self._ifc_cmd2()

    @needs_auth
    async def set_flame_height(self, flame_height: int) -> bool:
        """Set the flame height."""
        if not 0 <= flame_height <= MAX_FLAME_HEIGHT:
            msg = "Flame height must be between 0 and 6"
            raise ValueError(msg)
        # The eFIRE controller does not set the on state if we change
        # flame height from 0 to a non-zero value. However, the IFC
        # will ignite the burner and set the requested flame height.
        # To maintain consistent state we force the eFIRE controller on.
        # This has the annoying side-effect that flame height will be
        # set to max before being set to the desired value shortly after.
        if (
            self._compatibility_mode
            and self._state.flame_height == 0
            and flame_height > 0
        ):
            _LOGGER.debug(
                "[%s]: Turning on via flame_height setting, forcing controller on"
                " as well",
                self.name,
            )
            await self.power_on()
        self._state.flame_height = flame_height
        if flame_height == 0 and self._state.blower_speed == 0:
            _LOGGER.debug(
                "[%s]: Turning off fireplace from set_flame_height because blower is"
                " off too",
                self.name,
            )
            return await self.power_off(compatibility_mode=True)
        return await self._ifc_cmd2()

    @needs_auth
    async def set_blower_speed(self, blower_speed: int) -> bool:
        """Set the blower speed."""
        if not self._features.blower:
            msg = f"Fireplace {self.name} does not have a blower"
            raise FeatureNotSupported(msg)

        if not 0 <= blower_speed <= MAX_BLOWER_SPEED:
            msg = "Blower speed must be between 0 and 6"
            raise ValueError(msg)
        self._state.blower_speed = blower_speed
        if blower_speed == 0 and self._state.flame_height == 0:
            _LOGGER.debug(
                "[%s]: Turning off fireplace from set_blower_speed because flame is"
                " off too",
                self.name,
            )
            return await self.power_off(compatibility_mode=True)
        return await self._ifc_cmd2()

    @needs_auth
    async def set_split_flow(self, *, enabled: bool) -> bool:
        """Set the split flow valve state."""
        if not self._features.split_flow:
            msg = f"Fireplace {self.name} does not have a split flow valve"
            raise FeatureNotSupported(msg)

        self._state.split_flow = enabled
        return await self._ifc_cmd2()

    @needs_auth
    async def set_led_mode(self, light_mode: LedMode, *, on: bool = False) -> bool:
        """Set the LED mode/effect."""
        if not self._features.led_lights:
            msg = f"Fireplace {self.name} does not have a LED controller"
            raise FeatureNotSupported(msg)
        parameter = light_mode.setvalue

        # the value to disable modes is the value for enabling it + 5
        if not on:
            parameter = parameter + 0x5

        result = await self._simple_command(EfireCommand.SET_LED_MODE, parameter)
        return result == ReturnCode.SUCCESS

    @needs_auth
    async def set_timer(self, hours: int, minutes: int, *, enabled: bool) -> bool:
        """Set the timer."""
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
        """Set the LED color."""
        if not self._features.led_lights:
            msg = f"Fireplace {self.name} does not have a LED controller"
            raise FeatureNotSupported(msg)

        return await self._simple_command(
            EfireCommand.SET_LED_COLOR, bytes([color[0], color[1], color[2]])
        )

    @needs_auth
    async def set_led_state(self, *, on: bool) -> bool:
        """Set the LED power state."""
        if not self._features.led_lights:
            msg = f"Fireplace {self.name} does not have a LED controller"
            raise FeatureNotSupported(msg)

        return await self._simple_command(
            EfireCommand.SET_LED_POWER,
            LedState.ON.long  # type: ignore[attr-defined] # pylint: disable=no-member
            if on
            else LedState.OFF.long,  # type: ignore[attr-defined] # pylint: disable=no-member
        )

    @needs_auth
    async def led_on(self) -> bool:
        """Turn LEDs on."""
        return await self.set_led_state(on=True)

    @needs_auth
    async def led_off(self) -> bool:
        """Turn LEDs off."""
        return await self.set_led_state(on=False)

    @needs_auth
    async def query_aux_control(self) -> AuxControlState:
        """Query whether the remote is currently overriding Bluetooth control."""
        result = await self.execute_command(EfireCommand.GET_AUX_CTRL)
        _LOGGER.debug("[%s]: Aux Control State: %x", self.name, result)
        return AuxControlState(int.from_bytes(result, "big"))

    @needs_auth
    async def set_password(self, password: str) -> bool:
        """Set the password for authentication."""
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
        # untested
        """Reset the password on the controller."""
        return await self._simple_command(
            EfireCommand.PASSWORD_MGMT, PasswordAction.RESET
        )

    # E0
    @needs_auth
    async def update_led_state(self) -> None:
        """Update the power state of the LED Controller."""
        result = await self.execute_command(EfireCommand.GET_LED_STATE)

        self._state.led = result == LedState.ON.long  # type: ignore[attr-defined] # pylint: disable=no-member

    # E1
    @needs_auth
    async def update_led_color(self) -> None:
        """Update the state of the LED colors."""
        result = await self.execute_command(EfireCommand.GET_LED_COLOR)

        self._state.led_color = parse_led_color(result)

    # E2
    @needs_auth
    async def update_led_controller_mode(self) -> None:
        """Update the mode of the LED colors."""
        result = await self.execute_command(EfireCommand.GET_LED_MODE)

        self._state.led_mode = LedMode(bytes(result))

    # E3
    @needs_auth
    async def update_ifc_cmd1_state(self) -> None:
        """Update the state of the IFC CMD1 functions."""
        result = await self.execute_command(EfireCommand.GET_IFC_CMD1_STATE)

        if result[0] == ReturnCode.FAILURE:
            msg = f"Command failed with return code {result.hex()}"
            raise CommandFailedException(msg)
        (
            self._state.ifc_power,
            self._state.thermostat,  # thermostat is not used with eFIRE
            self._state.night_light_brightness,
            self._state.pilot,
        ) = parse_ifc_cmd1_state(result)

    # E4
    @needs_auth
    async def update_ifc_cmd2_state(self) -> None:
        """Update the state of the IFC CMD1 functions."""
        result = await self.execute_command(EfireCommand.GET_IFC_CMD2_STATE)
        (
            self._state.flame_height,
            self._state.blower_speed,
            self._state.aux,
            self._state.split_flow,
        ) = parse_ifc_cmd2_state(result)

    # E6
    @needs_auth
    async def update_timer_state(self) -> None:
        """Update the state of the timer."""
        result = await self.execute_command(EfireCommand.GET_TIMER)
        self._state.time_left, self._state.timer = parse_timer(result)

    # E7
    @needs_auth
    async def update_power_state(self) -> None:
        """Update the power state of the fireplace as seen from the BT controller."""
        result = await self.execute_command(EfireCommand.GET_POWER_STATE)

        self._state.bt_power = result[0] == PowerState.ON

    # EB
    @needs_auth
    async def update_led_controller_state(self) -> None:
        """Update the state of the LED Controller."""
        result = await self.execute_command(EfireCommand.GET_LED_CONTROLLER_STATE)

        (
            self._state.led,
            self._state.led_color,
            self._state.led_mode,
        ) = parse_led_controller_state(result)

    # EE
    @needs_auth
    async def update_remote_usage(self) -> None:
        """Update the remote control override state."""
        result = await self.execute_command(EfireCommand.GET_REMOTE_USAGE)

        self._state.remote_in_use = result == AuxControlState.USED

    # F2
    @needs_auth
    async def query_ble_version(self) -> str:
        """Update the BLE version information."""
        result = await self.execute_command(EfireCommand.GET_BLE_VERSION)

        return parse_ble_version(result)

    # F3
    @needs_auth
    async def query_mcu_version(self) -> str:
        """Update the MCU version information."""
        result = await self.execute_command(EfireCommand.GET_MCU_VERSION)

        return parse_mcu_version(result)

    async def update_state(self) -> None:
        """Update all state, depending on selected features."""
        await self.update_ifc_cmd1_state()
        await self.update_ifc_cmd2_state()
        if self._compatibility_mode:
            await self.update_power_state()
        if self._features.timer:
            await self.update_timer_state()
        if self._features.led_lights:
            await self.update_led_state()
            await self.update_led_color()
            await self.update_led_controller_mode()

    async def update_firmware_version(self) -> None:
        """Update firmware version strings."""
        self._state.mcu_version = await self.query_mcu_version()
        self._state.ble_version = await self.query_ble_version()
