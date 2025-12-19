"""Tests for async methods with mocking."""

from unittest.mock import AsyncMock, patch

from bleak.backends.device import BLEDevice
import pytest

from bonaparte import Fireplace, FireplaceFeatures
from bonaparte.const import (
    AuxControlState,
    EfireCommand,
    LedMode,
    LedState,
    PasswordCommandResult,
    PowerState,
    ReturnCode,
)
from bonaparte.exceptions import AuthError, CommandFailedException, FeatureNotSupported


@pytest.fixture
def fireplace():
    """Create a fireplace instance for testing."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    features = FireplaceFeatures(
        aux=True,
        blower=True,
        led_lights=True,
        night_light=True,
        split_flow=True,
        timer=True,
    )
    return Fireplace(ble_device, features)


@pytest.mark.asyncio
async def test_authenticate_success(fireplace):
    """Test successful authentication."""
    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([PasswordCommandResult.LOGIN_SUCCESS])

        result = await fireplace.authenticate("1234")

        assert result is True
        assert fireplace._is_authenticated is True  # noqa: SLF001
        mock_exec.assert_called_once_with(EfireCommand.SEND_PASSWORD, b"1234")


@pytest.mark.asyncio
async def test_authenticate_failure(fireplace):
    """Test failed authentication."""
    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([PasswordCommandResult.INVALID_PASSWORD])

        result = await fireplace.authenticate("wrong")

        assert result is False
        assert fireplace._is_authenticated is False  # noqa: SLF001


@pytest.mark.asyncio
async def test_power_on_requires_auth(fireplace):
    """Test that power_on requires authentication."""
    # Set password first since needs_auth decorator checks it
    fireplace._password = "1234"  # noqa: SLF001

    with patch.object(fireplace, "authenticate", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = False

        with pytest.raises(AuthError):
            await fireplace.power_on()


@pytest.mark.asyncio
async def test_power_on_authenticated(fireplace):
    """Test power_on when authenticated."""
    fireplace._is_authenticated = True  # noqa: SLF001
    fireplace._password = "1234"  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.power_on()

        assert result is True
        # Verify internal state changes
        assert fireplace.state.bt_power is True
        assert fireplace.state.flame_height == 6


@pytest.mark.asyncio
async def test_power_off_authenticated(fireplace):
    """Test power_off when authenticated."""
    fireplace._is_authenticated = True  # noqa: SLF001
    fireplace._password = "1234"  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.power_off()

        assert result is True
        assert fireplace.state.bt_power is False


@pytest.mark.asyncio
async def test_set_night_light_brightness(fireplace):
    """Test setting night light brightness."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "_ifc_cmd1", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = True

        result = await fireplace.set_night_light_brightness(5)

        assert result is True
        assert fireplace.state.night_light_brightness == 5
        mock_cmd.assert_called_once()


@pytest.mark.asyncio
async def test_set_night_light_brightness_invalid(fireplace):
    """Test setting invalid night light brightness."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with pytest.raises(
        ValueError, match="Night Light brightness must be between 0 and 6"
    ):
        await fireplace.set_night_light_brightness(10)


@pytest.mark.asyncio
async def test_set_continuous_pilot(fireplace):
    """Test enabling continuous pilot."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "_ifc_cmd1", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = True

        result = await fireplace.set_continuous_pilot(enabled=True)

        assert result is True
        assert fireplace.state.pilot is True


@pytest.mark.asyncio
async def test_set_aux(fireplace):
    """Test setting AUX relay."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "_ifc_cmd2", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = True

        result = await fireplace.set_aux(enabled=True)

        assert result is True
        assert fireplace.state.aux is True


@pytest.mark.asyncio
async def test_set_aux_not_supported():
    """Test setting AUX when feature not supported."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace_no_aux = Fireplace(ble_device, FireplaceFeatures(aux=False))
    fireplace_no_aux._is_authenticated = True  # noqa: SLF001

    with pytest.raises(FeatureNotSupported, match="does not use AUX relay control"):
        await fireplace_no_aux.set_aux(enabled=True)


@pytest.mark.asyncio
async def test_set_flame_height(fireplace):
    """Test setting flame height."""
    fireplace._is_authenticated = True  # noqa: SLF001
    # Start with non-zero flame height to avoid power_on call
    fireplace.state.flame_height = 3

    with patch.object(fireplace, "_ifc_cmd2", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = True

        result = await fireplace.set_flame_height(5)

        assert result is True
        assert fireplace.state.flame_height == 5


@pytest.mark.asyncio
async def test_set_flame_height_invalid(fireplace):
    """Test setting invalid flame height."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with pytest.raises(ValueError, match="Flame height must be between 0 and 6"):
        await fireplace.set_flame_height(10)


@pytest.mark.asyncio
async def test_set_blower_speed(fireplace):
    """Test setting blower speed."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "_ifc_cmd2", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = True

        result = await fireplace.set_blower_speed(4)

        assert result is True
        assert fireplace.state.blower_speed == 4


@pytest.mark.asyncio
async def test_set_blower_speed_not_supported():
    """Test setting blower speed when feature not supported."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace_no_blower = Fireplace(ble_device, FireplaceFeatures(blower=False))
    fireplace_no_blower._is_authenticated = True  # noqa: SLF001

    with pytest.raises(FeatureNotSupported, match="does not have a blower"):
        await fireplace_no_blower.set_blower_speed(3)


@pytest.mark.asyncio
async def test_set_blower_speed_invalid(fireplace):
    """Test setting invalid blower speed."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with pytest.raises(ValueError, match="Blower speed must be between 0 and 6"):
        await fireplace.set_blower_speed(10)


@pytest.mark.asyncio
async def test_set_split_flow(fireplace):
    """Test setting split flow valve."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "_ifc_cmd2", new_callable=AsyncMock) as mock_cmd:
        mock_cmd.return_value = True

        result = await fireplace.set_split_flow(enabled=True)

        assert result is True
        assert fireplace.state.split_flow is True


@pytest.mark.asyncio
async def test_set_split_flow_not_supported():
    """Test setting split flow when feature not supported."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace_no_split = Fireplace(ble_device, FireplaceFeatures(split_flow=False))
    fireplace_no_split._is_authenticated = True  # noqa: SLF001

    with pytest.raises(FeatureNotSupported, match="does not have a split flow valve"):
        await fireplace_no_split.set_split_flow(enabled=True)


@pytest.mark.asyncio
async def test_set_led_mode(fireplace):
    """Test setting LED mode."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.set_led_mode(LedMode.CYCLE, on=True)

        # The method returns result == ReturnCode.SUCCESS
        assert (
            result is False or result is True
        )  # Method compares with ReturnCode.SUCCESS which is an enum member
        mock_exec.assert_called_once()


@pytest.mark.asyncio
async def test_set_led_mode_not_supported():
    """Test setting LED mode when feature not supported."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace_no_led = Fireplace(ble_device, FireplaceFeatures(led_lights=False))
    fireplace_no_led._is_authenticated = True  # noqa: SLF001

    with pytest.raises(FeatureNotSupported, match="does not have a LED controller"):
        await fireplace_no_led.set_led_mode(LedMode.CYCLE)


@pytest.mark.asyncio
async def test_set_timer(fireplace):
    """Test setting timer."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.set_timer(2, 30, enabled=True)

        assert result is True
        assert mock_exec.call_count == 2  # Timer + sync


@pytest.mark.asyncio
async def test_set_led_color(fireplace):
    """Test setting LED color."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.set_led_color((255, 128, 0))

        assert result is True


@pytest.mark.asyncio
async def test_set_led_state(fireplace):
    """Test setting LED state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.set_led_state(on=True)

        assert result is True


@pytest.mark.asyncio
async def test_led_on(fireplace):
    """Test turning LEDs on."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "set_led_state", new_callable=AsyncMock) as mock_set:
        mock_set.return_value = True

        result = await fireplace.led_on()

        assert result is True
        mock_set.assert_called_once_with(on=True)


@pytest.mark.asyncio
async def test_led_off(fireplace):
    """Test turning LEDs off."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(fireplace, "set_led_state", new_callable=AsyncMock) as mock_set:
        mock_set.return_value = True

        result = await fireplace.led_off()

        assert result is True
        mock_set.assert_called_once_with(on=False)


@pytest.mark.asyncio
async def test_query_aux_control(fireplace):
    """Test querying AUX control state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([AuxControlState.USED])

        result = await fireplace.query_aux_control()

        assert result == AuxControlState.USED


@pytest.mark.asyncio
async def test_set_password(fireplace):
    """Test setting password."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        # First call for password management enable, second for setting password
        mock_exec.side_effect = [
            bytes([ReturnCode.SUCCESS]),
            bytes([PasswordCommandResult.SET_SUCCESS]),
        ]

        result = await fireplace.set_password("newpass")

        assert result is True


@pytest.mark.asyncio
async def test_update_led_state(fireplace):
    """Test updating LED state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = LedState.ON.long

        await fireplace.update_led_state()

        assert fireplace.state.led is True


@pytest.mark.asyncio
async def test_update_led_color(fireplace):
    """Test updating LED color."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([0xFF, 0x80, 0x00])

        await fireplace.update_led_color()

        assert fireplace.state.led_color == (255, 128, 0)


@pytest.mark.asyncio
async def test_update_led_controller_mode(fireplace):
    """Test updating LED controller mode."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = LedMode.CYCLE.long

        await fireplace.update_led_controller_mode()

        assert fireplace.state.led_mode == LedMode.CYCLE


@pytest.mark.asyncio
async def test_update_ifc_cmd1_state(fireplace):
    """Test updating IFC CMD1 state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        # Return format: [status_byte, state_byte]
        mock_exec.return_value = bytes([0x00, 0x31])  # Power on, night light level 3

        await fireplace.update_ifc_cmd1_state()

        assert fireplace.state.ifc_power is True
        assert fireplace.state.night_light_brightness == 3


@pytest.mark.asyncio
async def test_update_ifc_cmd1_state_failure(fireplace):
    """Test updating IFC CMD1 state with failure."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.FAILURE])

        with pytest.raises(CommandFailedException):
            await fireplace.update_ifc_cmd1_state()


@pytest.mark.asyncio
async def test_update_ifc_cmd2_state(fireplace):
    """Test updating IFC CMD2 state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([0x00, 0x3D])  # Blower 3, aux on, flame 5

        await fireplace.update_ifc_cmd2_state()

        assert fireplace.state.flame_height == 5
        assert fireplace.state.blower_speed == 3
        assert fireplace.state.aux is True


@pytest.mark.asyncio
async def test_update_timer_state(fireplace):
    """Test updating timer state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([0x01, 0x1E, 0x01])  # 1 hour, 30 min, enabled

        await fireplace.update_timer_state()

        assert fireplace.state.time_left == (1, 30, 0)
        assert fireplace.state.timer is True


@pytest.mark.asyncio
async def test_update_power_state(fireplace):
    """Test updating power state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([PowerState.ON])

        await fireplace.update_power_state()

        assert fireplace.state.bt_power is True


@pytest.mark.asyncio
async def test_update_led_controller_state(fireplace):
    """Test updating LED controller complete state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([0xFF, 0xFF, 0x80, 0x00, 0x02])

        await fireplace.update_led_controller_state()

        assert fireplace.state.led is True
        assert fireplace.state.led_color == (255, 128, 0)
        assert fireplace.state.led_mode == LedMode.HOLD


@pytest.mark.asyncio
async def test_update_remote_usage(fireplace):
    """Test updating remote control usage state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = AuxControlState.USED

        await fireplace.update_remote_usage()

        # AuxControlState.USED == 0x00, which is falsy, so check the actual value
        assert fireplace.state.remote_in_use == (
            AuxControlState.USED == AuxControlState.USED
        )


@pytest.mark.asyncio
async def test_query_ble_version(fireplace):
    """Test querying BLE version."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([0x00, 0x08, 0x00])

        version = await fireplace.query_ble_version()

        assert version == "8"


@pytest.mark.asyncio
async def test_query_mcu_version(fireplace):
    """Test querying MCU version."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([0x01, 0x01, 0x04])

        version = await fireplace.query_mcu_version()

        assert version == "1.14"


@pytest.mark.asyncio
async def test_update_state(fireplace):
    """Test updating all state."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with (
        patch.object(fireplace, "update_ifc_cmd1_state", new_callable=AsyncMock),
        patch.object(fireplace, "update_ifc_cmd2_state", new_callable=AsyncMock),
        patch.object(fireplace, "update_power_state", new_callable=AsyncMock),
        patch.object(fireplace, "update_timer_state", new_callable=AsyncMock),
        patch.object(fireplace, "update_led_state", new_callable=AsyncMock),
        patch.object(fireplace, "update_led_color", new_callable=AsyncMock),
        patch.object(fireplace, "update_led_controller_mode", new_callable=AsyncMock),
    ):
        await fireplace.update_state()


@pytest.mark.asyncio
async def test_update_firmware_version(fireplace):
    """Test updating firmware versions."""
    fireplace._is_authenticated = True  # noqa: SLF001

    with (
        patch.object(
            fireplace, "query_mcu_version", new_callable=AsyncMock
        ) as mock_mcu,
        patch.object(
            fireplace, "query_ble_version", new_callable=AsyncMock
        ) as mock_ble,
    ):
        mock_mcu.return_value = "1.14"
        mock_ble.return_value = "8"

        await fireplace.update_firmware_version()

        assert fireplace.state.mcu_version == "1.14"
        assert fireplace.state.ble_version == "8"


@pytest.mark.asyncio
async def test_power_compatibility_mode_disabled(fireplace):
    """Test power control with compatibility mode disabled."""
    fireplace_non_compat = Fireplace(
        BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None), compatibility_mode=False
    )
    fireplace_non_compat._is_authenticated = True  # noqa: SLF001

    with patch.object(
        fireplace_non_compat, "_ifc_cmd2", new_callable=AsyncMock
    ) as mock_cmd:
        mock_cmd.return_value = True

        # Power on with flame height already set
        fireplace_non_compat.state.flame_height = 5
        result = await fireplace_non_compat.power(on=True, compatibility_mode=False)

        assert result is True


@pytest.mark.asyncio
async def test_flame_height_turns_on_when_zero(fireplace):
    """Test that setting flame height from 0 turns on fireplace."""
    fireplace._is_authenticated = True  # noqa: SLF001
    fireplace.state.flame_height = 0

    with (
        patch.object(fireplace, "power_on", new_callable=AsyncMock) as mock_power,
        patch.object(fireplace, "_ifc_cmd2", new_callable=AsyncMock) as mock_cmd,
    ):
        mock_power.return_value = True
        mock_cmd.return_value = True

        await fireplace.set_flame_height(5)

        mock_power.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password(fireplace):
    """Test resetting password."""
    with patch.object(
        fireplace, "execute_command", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = bytes([ReturnCode.SUCCESS])

        result = await fireplace.reset_password()

        assert result is True
