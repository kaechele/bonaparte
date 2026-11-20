"""Tests for device.py functionality."""

import asyncio
from unittest.mock import AsyncMock, patch

from bleak.backends.device import BLEDevice
import pytest

from bonaparte.const import FOOTER, HEADER, EfireCommand
from bonaparte.device import EfireDevice
from bonaparte.exceptions import EfireMessageValueError

from .mock_messages import response


@pytest.mark.asyncio
async def test_execute_command_ignores_unsolicited_notification() -> None:
    """Test a pending command waits for a response with the same command ID."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))
    write_complete = asyncio.Event()
    client = AsyncMock()
    client.write_gatt_char.side_effect = lambda *_args, **_kwargs: write_complete.set()
    device._client = client  # noqa: SLF001
    device._write_char = object()  # noqa: SLF001

    with patch.object(device, "_ensure_connected", new_callable=AsyncMock):
        command = asyncio.create_task(
            device.execute_command(EfireCommand.GET_IFC_CMD1_STATE)
        )
        await write_complete.wait()

        device._notification_handler(  # noqa: SLF001
            None,
            bytearray.fromhex("ab bb 04 ee 00 ea 55"),
        )
        await asyncio.sleep(0)
        assert not command.done()

        device._notification_handler(  # noqa: SLF001
            None,
            bytearray(response["cmd1_state_power_on"]),
        )

        assert await command == bytes([0x00, 0x01])


def test_message_validation_too_short() -> None:
    """Test that messages that are too short raise an error."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Message with only 5 bytes (minimum is 6)
    short_message = bytes([0xAB, 0xAA, 0x03, 0xE6, 0xE5])

    with pytest.raises(
        EfireMessageValueError,
        match="Message too short. Got 5 bytes, expected at least 6 bytes",
    ):
        device._validate_message(short_message)  # noqa: SLF001


def test_message_validation_wrong_header() -> None:
    """Test that messages with wrong header raise an error."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Message with wrong header byte (0xAC instead of 0xAB)
    wrong_header = bytes([0xAC, 0xAA, 0x03, 0xE6, 0xE5, 0x55])

    with pytest.raises(
        EfireMessageValueError, match=f"Unknown message header.*Expected {HEADER}"
    ):
        device._validate_message(wrong_header)  # noqa: SLF001


def test_message_validation_wrong_message_type() -> None:
    """Test that messages with wrong message type raise an error."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Message with wrong message type (0xCC instead of 0xAA or 0xBB)
    wrong_type = bytes([0xAB, 0xCC, 0x03, 0xE6, 0xE5, 0x55])

    with pytest.raises(EfireMessageValueError, match="Unknown message type.*Expected"):
        device._validate_message(wrong_type)  # noqa: SLF001


def test_message_validation_wrong_length() -> None:
    """Test that messages with incorrect length field raise an error."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Message claims length of 5 but is actually 6 bytes long
    wrong_length = bytes([0xAB, 0xAA, 0x05, 0xE6, 0xE5, 0x55])

    with pytest.raises(EfireMessageValueError, match="Incorrect message length"):
        device._validate_message(wrong_length)  # noqa: SLF001


def test_message_validation_wrong_checksum() -> None:
    """Test that messages with incorrect checksum raise an error."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Valid message but with wrong checksum
    wrong_checksum = bytes(
        [0xAB, 0xAA, 0x03, 0xE6, 0x00, 0x55]
    )  # Checksum should be 0xE5

    with pytest.raises(EfireMessageValueError, match="Invalid checksum"):
        device._validate_message(wrong_checksum)  # noqa: SLF001


def test_message_validation_wrong_footer() -> None:
    """Test that messages with incorrect footer raise an error."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Valid message but with wrong footer
    wrong_footer = bytes([0xAB, 0xAA, 0x03, 0xE6, 0xE5, 0x44])  # Footer should be 0x55

    with pytest.raises(
        EfireMessageValueError, match=f"Invalid.*Message should end with {FOOTER}"
    ):
        device._validate_message(wrong_footer)  # noqa: SLF001


def test_message_validation_valid_request() -> None:
    """Test that valid request messages pass validation."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Valid request message
    valid_request = bytes.fromhex("ab aa 03 e6 e5 55")

    # Should not raise any exception
    device._validate_message(valid_request)  # noqa: SLF001


def test_message_validation_valid_response() -> None:
    """Test that valid response messages pass validation."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None))

    # Valid response message
    valid_response = bytes.fromhex("ab bb 04 c5 35 f4 55")

    # Should not raise any exception
    device._validate_message(valid_response)  # noqa: SLF001


def test_device_name() -> None:
    """Test that device name property works correctly."""
    # Device with name
    device_with_name = EfireDevice(
        BLEDevice("aa:bb:cc:dd:ee:ff", "TestDevice", details=None)
    )
    assert device_with_name.name == "TestDevice"

    # Device without name (should return address)
    device_without_name = EfireDevice(
        BLEDevice("aa:bb:cc:dd:ee:ff", None, details=None)
    )
    assert device_without_name.name == "aa:bb:cc:dd:ee:ff"


def test_device_address() -> None:
    """Test that device address property works correctly."""
    device = EfireDevice(BLEDevice("aa:bb:cc:dd:ee:ff", "TestDevice", details=None))
    assert device.address == "aa:bb:cc:dd:ee:ff"
