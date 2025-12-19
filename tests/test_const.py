"""Tests for constants and enums."""

from bonaparte.const import (
    CONFIG_DESC_UUID,
    FOOTER,
    HEADER,
    MAX_BLOWER_SPEED,
    MAX_FLAME_HEIGHT,
    MAX_NIGHT_LIGHT_BRIGHTNESS,
    MIN_MESSAGE_LENGTH,
    MODEL_NBR_UUID,
    READ_CHAR_UUID,
    REQUEST_HEADER,
    RESPONSE_HEADER,
    SERVICE_UUID,
    WRITE_CHAR_UUID,
    AuxControlState,
    EfireCommand,
    Feature,
    LedMode,
    LedState,
    PasswordAction,
    PasswordCommandResult,
    PasswordSetResult,
    PowerState,
    ReturnCode,
)


def test_efire_command_enum_values() -> None:
    """Test EfireCommand enum has expected values."""
    assert EfireCommand.SET_IFC_CMD1 == 0x27
    assert EfireCommand.SET_IFC_CMD2 == 0x28
    assert EfireCommand.SET_LED_POWER == 0xB1
    assert EfireCommand.SET_LED_COLOR == 0xC1
    assert EfireCommand.SET_TIMER == 0xC3
    assert EfireCommand.SET_POWER == 0xC4
    assert EfireCommand.SEND_PASSWORD == 0xC5
    assert EfireCommand.PASSWORD_MGMT == 0xC6
    assert EfireCommand.GET_LED_STATE == 0xE0
    assert EfireCommand.GET_LED_COLOR == 0xE1
    assert EfireCommand.GET_LED_MODE == 0xE2
    assert EfireCommand.GET_IFC_CMD1_STATE == 0xE3
    assert EfireCommand.GET_IFC_CMD2_STATE == 0xE4
    assert EfireCommand.GET_TIMER == 0xE6
    assert EfireCommand.GET_POWER_STATE == 0xE7
    assert EfireCommand.GET_LED_CONTROLLER_STATE == 0xEB
    assert EfireCommand.GET_REMOTE_USAGE == 0xEE
    assert EfireCommand.SET_LED_MODE == 0xF1
    assert EfireCommand.GET_BLE_VERSION == 0xF2
    assert EfireCommand.GET_MCU_VERSION == 0xF3
    assert EfireCommand.GET_AUX_CTRL == 0xF4
    assert EfireCommand.SET_PASSWORD == 0xF5


def test_return_code_enum() -> None:
    """Test ReturnCode enum values."""
    assert ReturnCode.SUCCESS == 0x00
    assert ReturnCode.FAILURE == 0x01


def test_power_state_enum() -> None:
    """Test PowerState enum values."""
    assert PowerState.OFF == 0x00
    assert PowerState.ON == 0xFF


def test_aux_control_state_enum() -> None:
    """Test AuxControlState enum values."""
    assert AuxControlState.USED == 0x00
    assert AuxControlState.NOT_USED == 0xFF


def test_password_action_enum() -> None:
    """Test PasswordAction enum values."""
    assert PasswordAction.RESET == 0x3F
    assert PasswordAction.SET == 0xF5


def test_password_command_result_enum() -> None:
    """Test PasswordCommandResult enum values."""
    assert PasswordCommandResult.SET_SUCCESS == 0x00
    assert PasswordCommandResult.SET_FAILED == 0x01
    assert PasswordCommandResult.INVALID_PASSWORD == 0x19
    assert PasswordCommandResult.LOGIN_SUCCESS == 0x35


def test_password_set_result_enum() -> None:
    """Test PasswordSetResult enum values."""
    assert PasswordSetResult.FAILED == 0x25
    assert PasswordSetResult.SUCCESS == 0x53


def test_feature_enum() -> None:
    """Test Feature enum values."""
    assert Feature.AUX == "aux"
    assert Feature.BLOWER == "blower"
    assert Feature.LED_LIGHTS == "led_lights"
    assert Feature.NIGHT_LIGHT == "night_light"
    assert Feature.SPLIT_FLOW == "split_flow"
    assert Feature.TIMER == "timer"


def test_led_state_multi_value_enum() -> None:
    """Test LedState multi-value enum."""
    # Test short values
    assert LedState.OFF.short == 0x00
    assert LedState.ON.short == 0xFF

    # Test long values
    assert LedState.OFF.long == bytes([0, 0, 0])
    assert LedState.ON.long == bytes([0xFF, 0xFF, 0xFF])

    # Test that we can create enum from any of the values
    assert LedState(0x00) == LedState.OFF
    assert LedState(0xFF) == LedState.ON
    assert LedState(bytes([0, 0, 0])) == LedState.OFF
    assert LedState(bytes([0xFF, 0xFF, 0xFF])) == LedState.ON


def test_led_mode_multi_value_enum() -> None:
    """Test LedMode multi-value enum."""
    # Test short values
    assert LedMode.CYCLE.short == 0x01
    assert LedMode.HOLD.short == 0x02
    assert LedMode.EMBER_BED.short == 0xFF

    # Test long values
    assert LedMode.CYCLE.long == bytes([0x01, 0x01, 0x01])
    assert LedMode.HOLD.long == bytes([0x02, 0x02, 0x02])
    assert LedMode.EMBER_BED.long == bytes([0xFF, 0xFF, 0xFF])

    # Test setvalue
    assert LedMode.CYCLE.setvalue == 0x20
    assert LedMode.HOLD.setvalue == 0x30
    assert LedMode.EMBER_BED.setvalue == 0x10

    # Test that we can create enum from any of the values
    assert LedMode(0x01) == LedMode.CYCLE
    assert LedMode(0x02) == LedMode.HOLD
    assert LedMode(0xFF) == LedMode.EMBER_BED

    assert LedMode(bytes([0x01, 0x01, 0x01])) == LedMode.CYCLE
    assert LedMode(bytes([0x02, 0x02, 0x02])) == LedMode.HOLD
    assert LedMode(bytes([0xFF, 0xFF, 0xFF])) == LedMode.EMBER_BED

    assert LedMode(0x20) == LedMode.CYCLE
    assert LedMode(0x30) == LedMode.HOLD
    assert LedMode(0x10) == LedMode.EMBER_BED


def test_led_mode_setvalue_unique() -> None:
    """Test that LedMode setvalue is unique for each mode."""
    setvalues = [
        LedMode.CYCLE.setvalue,
        LedMode.HOLD.setvalue,
        LedMode.EMBER_BED.setvalue,
    ]
    assert len(setvalues) == len(set(setvalues))


def test_constants() -> None:
    """Test various protocol constants."""

    assert HEADER == 0xAB
    assert REQUEST_HEADER == 0xAA
    assert RESPONSE_HEADER == 0xBB
    assert FOOTER == 0x55
    assert MIN_MESSAGE_LENGTH == 6
    assert MAX_FLAME_HEIGHT == 6
    assert MAX_NIGHT_LIGHT_BRIGHTNESS == 6
    assert MAX_BLOWER_SPEED == 6


def test_uuid_constants() -> None:
    """Test UUID constants."""

    # Check UUID format (should be 36 characters with hyphens)
    assert len(SERVICE_UUID) == 36
    assert len(WRITE_CHAR_UUID) == 36
    assert len(READ_CHAR_UUID) == 36
    assert len(CONFIG_DESC_UUID) == 36
    assert len(MODEL_NBR_UUID) == 36

    # Check they all have the same base
    base_suffix = "-0000-1000-8000-00805f9b34fb"
    assert SERVICE_UUID.endswith(base_suffix)
    assert WRITE_CHAR_UUID.endswith(base_suffix)
    assert READ_CHAR_UUID.endswith(base_suffix)
    assert CONFIG_DESC_UUID.endswith(base_suffix)
    assert MODEL_NBR_UUID.endswith(base_suffix)


def test_enum_member_count() -> None:
    """Test that enums have the expected number of members."""
    assert len(ReturnCode) == 2
    assert len(PowerState) == 2
    assert len(AuxControlState) == 2
    assert len(PasswordAction) == 2
    assert len(PasswordCommandResult) == 4
    assert len(PasswordSetResult) == 2
    assert len(Feature) == 6
    assert len(LedState) == 2
    assert len(LedMode) == 3


def test_int_enum_comparison() -> None:
    """Test that IntEnum members can be compared with ints."""
    assert ReturnCode.SUCCESS == 0
    assert PowerState.ON == 255
    assert EfireCommand.SET_POWER == 196
