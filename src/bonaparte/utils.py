"""Helper functions and utilities used in the Bonaparte library."""
from __future__ import annotations

from functools import reduce

from .const import FOOTER, HEADER, REQUEST_HEADER


def checksum(payload: bytearray | bytes) -> int:
    """Calculate the checksum for a command payload."""
    # checksum is a single byte XOR of all bytes in the payload
    return reduce(lambda x, y: x ^ y, payload)


def checksum_message(message: bytearray | bytes) -> int:
    """Calculate the checksum for a raw message."""
    # strip the two header bytes, checksum and footer to get the payload
    return checksum(message[2:-2])


def build_message(payload: bytearray | bytes) -> bytes:
    """Put together a raw message based on a command payload."""
    # add the length of the message to the beginning of the payload
    # it needs to be part of the payload for checksum calculation
    payload = bytes([len(payload) + 2]) + payload

    message = bytearray()
    message.append(HEADER)
    message.append(REQUEST_HEADER)
    message = message + payload
    message.append(checksum(payload))
    message.append(FOOTER)
    return bytes(message)
