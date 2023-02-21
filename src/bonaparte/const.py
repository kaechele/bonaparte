from __future__ import annotations

from enum import IntEnum
import sys

from aenum import MultiValueEnum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from aenum import StrEnum

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
    AUX = "aux"
    BLOWER = "blower"
    LED_LIGHTS = "led_lights"
    NIGHT_LIGHT = "night_light"
    SPLIT_FLOW = "split_flow"


class EfireCommand(IntEnum):
    """Command names to hex value Enum Class."""

    OFF_STATE_CMDS = 0x27
    ON_STATE_CMDS = 0x28
    RESET_PASSWORD = 0x3F
    LED_POWER = 0xB1
    LED_COLOR = 0xC1
    TIMER = 0xC3
    POWER = 0xC4
    SEND_PASSWORD = 0xC5
    PASSWORD_MGMT = 0xC6
    SYNC_TIME = 0xC7
    LED_MODE = 0xF1
    BLE_VERSION = 0xF2
    MCU_VERSION = 0xF3
    QUERY_AUX_CTRL = 0xF4
    SET_PASSWORD = 0xF5


class ResponseCode(IntEnum):
    """Response type names to hex value Enum Class."""

    PASSWORD_ACTION = 0xC5
    LED_STATE = 0xE0
    LED_COLOR = 0xE1
    LED_MODE = 0xE2
    OFF_STATE_CMDS = 0xE3
    ON_STATE_CMDS = 0xE4
    TIMER = 0xE6
    POWER_STATE = 0xE7
    PASSWORD_READ = 0xE8
    PASSWORD_SET = 0xE9
    TIME_SYNC = 0xEA
    LED_CONTROLLER_STATE = 0xEB  # never appears
    REMOTE_USAGE = 0xEE
    BLE_VERSION = 0xF2
    MCU_VERSION = 0xF3


class ReturnCode(IntEnum):
    SUCCESS = 0x00
    FAILURE = 0x01


class PowerState(IntEnum):
    OFF = 0x00
    ON = 0xFF


class AuxControlState(IntEnum):
    USED = 0x00
    NOT_USED = 0xFF


class PasswordAction(IntEnum):
    RESET = 0x3F
    SET = 0xF5


class PasswordCommandResult(IntEnum):
    SET_SUCCESS = 0x00
    SET_FAILED = 0x01
    INVALID_PASSWORD = 0x19
    LOGIN_SUCCESS = 0x35


class PasswordSetResult(IntEnum):
    FAILED = 0x25
    SUCCESS = 0x53


class LedState(MultiValueEnum):
    _init_ = "short long"
    OFF = 0x00, "0x000000"
    ON = 0xFF, 0xFFFFFF


class LedMode(MultiValueEnum):
    _init_ = "short long setvalue"
    CYCLE = 0x01, 0x010101, 0x20
    HOLD = 0x02, 0x020202, 0x30
    EMBER_BED = 0xFF, 0xFFFFFF, 0x10
