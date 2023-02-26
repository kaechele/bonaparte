"""Parsing related tests."""

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

from .mock_messages import response


def test_ble_version_parser() -> None:
    """Test parsing the BLE version from a known message."""
    assert parse_ble_version(response["ble_version"][4:-2]) == "8"


def test_led_color_parser() -> None:
    """Test parsing the LED colors from a known message."""
    assert parse_led_color(response["led_color_0000ff"][4:-2]) == (0, 2, 255)


def test_led_controller_parser() -> None:
    """Test parsing the LED controller state from a known message."""
    assert parse_led_controller_state(response["led_controller_state"][4:-2]) == (
        True,
        (0, 0, 255),
        LedMode.HOLD,
    )


def test_mcu_version_parser() -> None:
    """Test parsing the MCU version from a known message."""
    assert parse_mcu_version(response["mcu_version"][4:-2]) == "1.14"


def test_off_state_parser() -> None:
    """Test parsing the power off state from a known message."""
    assert parse_ifc_cmd1_state(response["off_state_all_off"][4:-2]) == (False, 0, 0)


def test_on_state_parser() -> None:
    """Test parsing the on state from a known message."""
    assert parse_ifc_cmd2_state(response["on_state_all_off"][4:-2]) == (
        False,
        False,
        0,
        0,
    )


def test_timer_parser() -> None:
    """Test parsing the timer state from a known message."""
    assert parse_timer(response["timer_201455_on"][4:-2]) == ((20, 14, 55), True)
