"""Message related tests."""

from bonaparte.utils import build_message, checksum_message

from .mock_messages import request


def test_checksum() -> None:
    """Test checksum generation using known good messages."""
    for message in request.values():
        assert checksum_message(message) == message[-2]


def test_build_message() -> None:
    """Test building a message from a known good message."""
    # we use a known message, remove header, length, checksum and footer
    for message in request.values():
        assert build_message(message[3:-2]) == message
