"""Constants for Napoleon eFIRE devices."""

from __future__ import annotations

from enum import IntEnum, StrEnum

from aenum import MultiValueEnum

# Package format constants
HEADER = 0xAB
REQUEST_HEADER = 0xAA
RESPONSE_HEADER = 0xBB
FOOTER = 0x55

MIN_MESSAGE_LENGTH = 6
MAX_FLAME_HEIGHT = 6
MAX_NIGHT_LIGHT_BRIGHTNESS = 6
MAX_BLOWER_SPEED = 6

_BASE_UUID = "{:0>8}-0000-1000-8000-00805f9b34fb"
SERVICE_UUID = _BASE_UUID.format("ff00")
WRITE_CHAR_UUID = _BASE_UUID.format("ff01")
READ_CHAR_UUID = _BASE_UUID.format("ff02")
CONFIG_DESC_UUID = _BASE_UUID.format("2902")
MODEL_NBR_UUID = _BASE_UUID.format("2a00")


class Feature(StrEnum):
    """Enum encapsulating possible device features."""

    AUX = "aux"
    BLOWER = "blower"
    LED_LIGHTS = "led_lights"
    NIGHT_LIGHT = "night_light"
    SPLIT_FLOW = "split_flow"
    TIMER = "timer"


class EfireCommand(IntEnum):
    """Enum encapsulating device commands and their raw hex values."""

    SET_IFC_CMD1 = 0x27
    SET_IFC_CMD2 = 0x28
    RESET_PASSWORD = 0x3F
    SET_LED_POWER = 0xB1
    SET_LED_COLOR = 0xC1
    SET_TIMER = 0xC3
    SET_POWER = 0xC4
    SEND_PASSWORD = 0xC5
    PASSWORD_MGMT = 0xC6
    SYNC_TIME = 0xC7
    GET_LED_STATE = 0xE0
    GET_LED_COLOR = 0xE1
    GET_LED_MODE = 0xE2
    GET_IFC_CMD1_STATE = 0xE3
    GET_IFC_CMD2_STATE = 0xE4
    GET_TIMER = 0xE6
    GET_POWER_STATE = 0xE7
    PASSWORD_READ = 0xE8
    PASSWORD_SET = 0xE9
    TIME_SYNC = 0xEA
    GET_LED_CONTROLLER_STATE = 0xEB  # has not been seen while reverse engineering
    GET_REMOTE_USAGE = 0xEE
    SET_LED_MODE = 0xF1
    GET_BLE_VERSION = 0xF2
    GET_MCU_VERSION = 0xF3
    GET_AUX_CTRL = 0xF4
    SET_PASSWORD = 0xF5


class ReturnCode(IntEnum):
    """Enum encapsulating command return codes."""

    SUCCESS = 0x00
    FAILURE = 0x01


class PowerState(IntEnum):
    """Enum encapsulating device power states."""

    OFF = 0x00
    ON = 0xFF


class AuxControlState(IntEnum):
    """Enum encapsulating return values for remote control use."""

    USED = 0x00
    NOT_USED = 0xFF


class PasswordAction(IntEnum):
    """Enum encapsulating the values for password actions."""

    RESET = 0x3F
    SET = 0xF5


class PasswordCommandResult(IntEnum):
    """Enum encapsulating possible return values for password actions."""

    SET_SUCCESS = 0x00
    SET_FAILED = 0x01
    INVALID_PASSWORD = 0x19
    LOGIN_SUCCESS = 0x35


class PasswordSetResult(IntEnum):
    """Enum encapsulating return values for authentication requests."""

    FAILED = 0x25
    SUCCESS = 0x53


class LedState(MultiValueEnum):
    """Enum encapsulating LED controller state."""

    _init_ = "short long"

    OFF = 0x00, bytes([0, 0, 0])
    ON = 0xFF, bytes([0xFF, 0xFF, 0xFF])


class LedMode(MultiValueEnum):
    """Enum encapsulating LED controller modes."""

    _init_ = "short long setvalue"

    CYCLE = 0x01, bytes([0x01, 0x01, 0x01]), 0x20
    HOLD = 0x02, bytes([0x02, 0x02, 0x02]), 0x30
    EMBER_BED = 0xFF, bytes([0xFF, 0xFF, 0xFF]), 0x10
