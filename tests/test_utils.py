"""Additional tests for utility functions."""

import pytest

from bonaparte.utils import build_message, checksum, checksum_message


def test_checksum_empty() -> None:
    """Test checksum with empty payload."""
    with pytest.raises(
        ValueError,
        match="Payload must contain at least one byte for checksum calculation",
    ):
        checksum(bytes([]))

    with pytest.raises(
        ValueError,
        match="Payload must contain at least one byte for checksum calculation",
    ):
        checksum(bytearray([]))


def test_checksum_single_byte() -> None:
    """Test checksum with single byte."""
    assert checksum(bytes([0xFF])) == 0xFF
    assert checksum(bytes([0x00])) == 0x00
    assert checksum(bytes([0x42])) == 0x42


def test_checksum_two_bytes() -> None:
    """Test checksum with two bytes - XOR operation."""
    # 0xFF XOR 0x00 = 0xFF
    assert checksum(bytes([0xFF, 0x00])) == 0xFF

    # 0x42 XOR 0x42 = 0x00
    assert checksum(bytes([0x42, 0x42])) == 0x00

    # 0xAA XOR 0x55 = 0xFF
    assert checksum(bytes([0xAA, 0x55])) == 0xFF


def test_checksum_multiple_bytes() -> None:
    """Test checksum with multiple bytes."""
    # 0x01 XOR 0x02 XOR 0x03 = 0x00
    assert checksum(bytes([0x01, 0x02, 0x03])) == 0x00

    # Test with known message payload
    assert checksum(bytes([0x03, 0xE6])) == 0xE5


def test_checksum_bytearray_input() -> None:
    """Test that checksum works with bytearray input."""
    payload = bytearray([0x03, 0xE6])
    assert checksum(payload) == 0xE5


def test_checksum_message_strips_overhead() -> None:
    """Test that checksum_message strips header, footer, and checksum."""
    # Message format: HEADER, MSG_TYPE, LENGTH, PAYLOAD..., CHECKSUM, FOOTER
    # Message: AB AA 03 E6 E5 55
    # Should calculate checksum on: 03 E6
    message = bytes.fromhex("ab aa 03 e6 e5 55")
    assert checksum_message(message) == 0xE5


def test_checksum_message_different_messages() -> None:
    """Test checksum_message with various messages."""
    # Login success message
    message1 = bytes.fromhex("ab bb 04 c5 35 f4 55")
    assert checksum_message(message1) == 0xF4

    # BLE version message
    message2 = bytes.fromhex("ab bb 06 f2 00 08 00 fc 55")
    assert checksum_message(message2) == 0xFC


def test_build_message_simple_payload() -> None:
    """Test building a message from a simple payload."""
    # Payload: E6 (query timer command)
    payload = bytes([0xE6])

    # Expected message: AB AA 03 E6 E5 55
    # Where: AB = header, AA = request type, 03 = length, E6 = command,
    #        E5 = checksum, 55 = footer
    expected = bytes.fromhex("ab aa 03 e6 e5 55")

    assert build_message(payload) == expected


def test_build_message_with_parameter() -> None:
    """Test building a message with command and parameter."""
    # Payload: C5 31 32 33 34 (login with password "1234")
    payload = bytes([0xC5, 0x31, 0x32, 0x33, 0x34])

    # Expected message: AB AA 07 C5 31 32 33 34 C6 55
    expected = bytes.fromhex("ab aa 07 c5 31 32 33 34 c6 55")

    assert build_message(payload) == expected


def test_build_message_bytearray_input() -> None:
    """Test that build_message works with bytearray input."""
    payload = bytearray([0xE6])
    expected = bytes.fromhex("ab aa 03 e6 e5 55")

    assert build_message(payload) == expected


def test_build_message_empty_payload() -> None:
    """Test building a message with empty payload."""
    # Even with empty payload, we need header, length, checksum, footer
    payload = bytes([])

    # Expected: AB AA 02 02 55
    # Length is 2 (length byte + empty payload)
    # Checksum of [02] = 02
    expected = bytes([0xAB, 0xAA, 0x02, 0x02, 0x55])

    assert build_message(payload) == expected


def test_build_message_length_calculation() -> None:
    """Test that message length is calculated correctly."""
    # Payload of 5 bytes
    payload = bytes([0xC5, 0x31, 0x32, 0x33, 0x34])

    message = build_message(payload)

    # Length field should be at index 2
    # Length = 1 (length byte itself) + 5 (payload) + 1 (checksum) = 7
    # But the function adds 2 to payload length: len(payload) + 2
    assert message[2] == len(payload) + 2


def test_build_and_checksum_consistency() -> None:
    """Test that built messages have correct checksums."""
    payloads = [
        bytes([0xE6]),
        bytes([0xC5, 0x31, 0x32, 0x33, 0x34]),
        bytes([0xF2]),
        bytes([0xE3]),
    ]

    for payload in payloads:
        message = build_message(payload)
        calculated_checksum = checksum_message(message)
        actual_checksum = message[-2]  # Second to last byte

        assert calculated_checksum == actual_checksum


def test_roundtrip_message_building() -> None:
    """Test that we can extract payload from built message."""
    original_payload = bytes([0xC5, 0x31, 0x32, 0x33, 0x34])

    # Build message
    message = build_message(original_payload)

    # Extract payload (skip header, msg type, length; remove checksum and footer)
    extracted_payload = message[3:-2]

    # The extracted payload should match original
    assert extracted_payload == original_payload
