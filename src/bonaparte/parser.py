"""Parsers used in the Bonaparte library."""
from __future__ import annotations

from .const import LedMode, LedState


def parse_ble_version(payload: bytes | bytearray) -> str:
    """Return a string of the BLE version."""
    return str(payload[1])


def parse_mcu_version(payload: bytes | bytearray) -> str:
    """Return a string of the MCU version."""
    return f"{payload[0]}.{payload[1]}{payload[2]}"


def parse_ifc_cmd1_state(payload: bytes | bytearray) -> tuple[bool, int, int]:
    """Parse the fireplace state from an IFC CMD1 response."""
    pilot = bool((payload[1] >> 7) & 1)
    night_light = (payload[1] >> 4) & 7
    main_mode = payload[1] & 2
    return pilot, night_light, main_mode


def parse_ifc_cmd2_state(payload: bytes | bytearray) -> tuple[bool, bool, int, int]:
    """Parse the fireplace state from an IFC CMD2 response."""
    split_flow = bool((payload[1] >> 7) & 1)
    aux = bool((payload[1] >> 3) & 1)
    blower_speed = (payload[1] >> 4) & 7
    flame_height = payload[1] & 7
    return split_flow, aux, blower_speed, flame_height


def parse_timer(payload: bytes | bytearray) -> tuple[tuple[int, int, int], bool]:
    """Parse timer state."""
    hours = payload[0]
    minutes = payload[1]
    seconds = payload[3] if len(payload) > 3 else 0  # noqa: PLR2004
    timer_on = payload[2] == 1 or payload[2] == 3  # noqa: PLR2004

    return (hours, minutes, seconds), timer_on


def parse_led_color(payload: bytes | bytearray) -> tuple[int, int, int]:
    """Parse the LED color as RGB."""
    return int(payload[0] & 0xFF), int(payload[1] & 0xFF), int(payload[2] & 0xFF)


def parse_led_controller_state(
    payload: bytes | bytearray,
) -> tuple[bool, tuple[int, int, int], LedMode]:
    """Parse the LED Controller state."""
    light_state = payload[0] == LedState.ON.short  # type: ignore[attr-defined] # noqa: E501 pylint: disable=no-member
    light_color = (
        int(payload[1] & 0xFF),
        int(payload[2] & 0xFF),
        int(payload[3] & 0xFF),
    )
    light_mode = LedMode(payload[4])  # pyright: ignore

    return light_state, light_color, light_mode
