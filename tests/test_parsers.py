from bonaparte.const import LedMode
from bonaparte.parser import (
    parse_ble_version,
    parse_led_color,
    parse_led_controller_state,
    parse_mcu_version,
    parse_off_state,
    parse_on_state,
    parse_timer,
)

from .mock_messages import response


def test_ble_version_parser():
    assert parse_ble_version(response["ble_version"][4:-2]) == "8"


def test_led_color_parser():
    assert parse_led_color(response["led_color_0000ff"][4:-2]) == (0, 2, 255)


def test_led_controller_parser():
    assert parse_led_controller_state(response["led_controller_state"][4:-2]) == (
        True,
        (0, 0, 255),
        LedMode.HOLD,
    )


def test_mcu_version_parser():
    assert parse_mcu_version(response["mcu_version"][4:-2]) == "1.14"


def test_off_state_parser():
    assert parse_off_state(response["off_state_all_off"][4:-2]) == (False, 0, 0)


def test_on_state_parser():
    assert parse_on_state(response["on_state_all_off"][4:-2]) == (False, False, 0, 0)


def test_timer_parser():
    assert parse_timer(response["timer_201455_on"][4:-2]) == ((20, 14, 55), True)
