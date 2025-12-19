"""Additional tests for parser edge cases and error handling."""

from bonaparte.const import LedMode
from bonaparte.parser import (
    parse_ble_version,
    parse_ifc_cmd1_state,
    parse_ifc_cmd2_state,
    parse_led_color,
    parse_led_controller_state,
    parse_mcu_version,
    parse_timer,
)


def test_parse_ble_version_different_values() -> None:
    """Test BLE version parser with different version numbers."""
    # Version 1
    assert parse_ble_version(bytes([0x00, 0x01, 0x00])) == "1"

    # Version 10
    assert parse_ble_version(bytes([0x00, 0x0A, 0x00])) == "10"

    # Version 255
    assert parse_ble_version(bytes([0x00, 0xFF, 0x00])) == "255"

    # Version 0
    assert parse_ble_version(bytes([0x00, 0x00, 0x00])) == "0"


def test_parse_mcu_version_different_values() -> None:
    """Test MCU version parser with different version numbers."""
    # Version 0.00
    assert parse_mcu_version(bytes([0x00, 0x00, 0x00])) == "0.00"

    # Version 2.35
    assert parse_mcu_version(bytes([0x02, 0x03, 0x05])) == "2.35"

    # Version 10.99
    assert parse_mcu_version(bytes([0x0A, 0x09, 0x09])) == "10.99"


def test_parse_ifc_cmd1_all_features_on() -> None:
    """Test parsing CMD1 with all features enabled."""
    # Power on, thermostat on, night light max (7), pilot on
    # Byte format: pilot(7) | night_light(6-4) | thermostat(1) | power(0)
    # 10000001 = 0x81 (power on, pilot off)
    # 11110011 = 0xF3 (power on, thermostat on, night light 7, pilot on)
    power, _thermostat, night_light, pilot = parse_ifc_cmd1_state(bytes([0x00, 0xF3]))
    assert power is True
    assert pilot is True
    assert night_light == 7


def test_parse_ifc_cmd1_mixed_features() -> None:
    """Test parsing CMD1 with mixed feature states."""
    # Power on, night light level 3, other features off
    # 00110001 = 0x31
    power, thermostat, night_light, pilot = parse_ifc_cmd1_state(bytes([0x00, 0x31]))
    assert power is True
    assert thermostat is False
    assert night_light == 3
    assert pilot is False


def test_parse_ifc_cmd2_all_features_enabled() -> None:
    """Test parsing CMD2 with all features at maximum."""
    # split_flow(7) | blower_speed(6-4) | aux(3) | flame_height(2-0)
    # Max all: 11111111 = 0xFF
    flame, blower, aux, split = parse_ifc_cmd2_state(bytes([0x00, 0xFF]))
    assert flame == 7
    assert blower == 7
    assert aux is True
    assert split is True


def test_parse_ifc_cmd2_mixed_values() -> None:
    """Test parsing CMD2 with specific values."""
    # split_flow off, blower 3, aux on, flame 5
    # 00111101 = 0x3D
    flame, blower, aux, split = parse_ifc_cmd2_state(bytes([0x00, 0x3D]))
    assert flame == 5
    assert blower == 3
    assert aux is True
    assert split is False


def test_parse_timer_off() -> None:
    """Test parsing timer in off state."""
    time_left, enabled = parse_timer(bytes([0x00, 0x00, 0x00]))
    assert time_left == (0, 0, 0)
    assert enabled is False


def test_parse_timer_various_times() -> None:
    """Test parsing timer with various time values."""
    # 5 hours, 30 minutes, timer on
    time_left, enabled = parse_timer(bytes([0x05, 0x1E, 0x01]))
    assert time_left == (5, 30, 0)
    assert enabled is True

    # 23 hours, 59 minutes, 45 seconds, timer on
    time_left, enabled = parse_timer(bytes([0x17, 0x3B, 0x03, 0x2D]))
    assert time_left == (23, 59, 45)
    assert enabled is True


def test_parse_timer_on_value_3() -> None:
    """Test that timer is considered on when value is 3."""
    _time_left, enabled = parse_timer(bytes([0x01, 0x02, 0x03]))
    assert enabled is True


def test_parse_led_color_extremes() -> None:
    """Test LED color parser with extreme values."""
    # All black (0, 0, 0)
    assert parse_led_color(bytes([0x00, 0x00, 0x00])) == (0, 0, 0)

    # All white (255, 255, 255)
    assert parse_led_color(bytes([0xFF, 0xFF, 0xFF])) == (255, 255, 255)

    # Pure red
    assert parse_led_color(bytes([0xFF, 0x00, 0x00])) == (255, 0, 0)

    # Pure green
    assert parse_led_color(bytes([0x00, 0xFF, 0x00])) == (0, 255, 0)

    # Pure blue
    assert parse_led_color(bytes([0x00, 0x00, 0xFF])) == (0, 0, 255)


def test_parse_led_color_common_colors() -> None:
    """Test LED color parser with common colors."""
    # Yellow (255, 255, 0)
    assert parse_led_color(bytes([0xFF, 0xFF, 0x00])) == (255, 255, 0)

    # Cyan (0, 255, 255)
    assert parse_led_color(bytes([0x00, 0xFF, 0xFF])) == (0, 255, 255)

    # Magenta (255, 0, 255)
    assert parse_led_color(bytes([0xFF, 0x00, 0xFF])) == (255, 0, 255)


def test_parse_led_controller_state_off() -> None:
    """Test LED controller state when off."""
    # LED off, black color, HOLD mode
    state, color, mode = parse_led_controller_state(
        bytes([0x00, 0x00, 0x00, 0x00, 0x02])
    )
    assert state is False
    assert color == (0, 0, 0)
    assert mode == LedMode.HOLD


def test_parse_led_controller_state_on_cycle() -> None:
    """Test LED controller state when on in CYCLE mode."""
    # LED on, red color, CYCLE mode
    state, color, mode = parse_led_controller_state(
        bytes([0xFF, 0xFF, 0x00, 0x00, 0x01])
    )
    assert state is True
    assert color == (255, 0, 0)
    assert mode == LedMode.CYCLE


def test_parse_led_controller_state_ember_bed() -> None:
    """Test LED controller state with EMBER_BED mode."""
    # LED on, white color, EMBER_BED mode
    state, color, mode = parse_led_controller_state(
        bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    )
    assert state is True
    assert color == (255, 255, 255)
    assert mode == LedMode.EMBER_BED


def test_parse_functions_with_bytearray() -> None:
    """Test that all parsers work with bytearray input."""
    # BLE version
    assert parse_ble_version(bytearray([0x00, 0x08, 0x00])) == "8"

    # MCU version
    assert parse_mcu_version(bytearray([0x01, 0x01, 0x04])) == "1.14"

    # LED color
    assert parse_led_color(bytearray([0x00, 0x02, 0xFF])) == (0, 2, 255)

    # Timer
    time_left, enabled = parse_timer(bytearray([0x14, 0x0E, 0x01, 0x37]))
    assert time_left == (20, 14, 55)
    assert enabled is True
