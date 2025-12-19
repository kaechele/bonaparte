"""Tests for exception handling."""

import pytest

from bonaparte.exceptions import (
    AuthError,
    CharacteristicMissingError,
    CommandFailedException,
    DisconnectedException,
    EfireException,
    EfireMessageValueError,
    FeatureNotSupported,
)


def test_efire_exception_is_base() -> None:
    """Test that EfireException is the base exception."""
    assert issubclass(AuthError, EfireException)
    assert issubclass(CommandFailedException, EfireException)
    assert issubclass(DisconnectedException, EfireException)
    assert issubclass(FeatureNotSupported, EfireException)
    assert issubclass(CharacteristicMissingError, EfireException)


def test_efire_exception_can_be_raised() -> None:
    """Test that base EfireException can be raised."""
    with pytest.raises(EfireException, match="Generic error"):
        raise EfireException("Generic error")


def test_auth_error() -> None:
    """Test AuthError exception."""
    with pytest.raises(AuthError, match="Authentication failed"):
        raise AuthError("Authentication failed")


def test_command_failed_exception() -> None:
    """Test CommandFailedException exception."""
    with pytest.raises(CommandFailedException, match="Command failed"):
        raise CommandFailedException("Command failed")


def test_disconnected_exception() -> None:
    """Test DisconnectedException exception."""
    with pytest.raises(DisconnectedException, match="Device disconnected"):
        raise DisconnectedException("Device disconnected")


def test_feature_not_supported() -> None:
    """Test FeatureNotSupported exception."""
    with pytest.raises(FeatureNotSupported, match="Feature not available"):
        raise FeatureNotSupported("Feature not available")


def test_efire_message_value_error() -> None:
    """Test EfireMessageValueError exception."""

    # Check it's a ValueError subclass
    assert issubclass(EfireMessageValueError, ValueError)

    with pytest.raises(EfireMessageValueError, match="Invalid message"):
        raise EfireMessageValueError("Invalid message")


def test_characteristic_missing_error() -> None:
    """Test CharacteristicMissingError exception."""
    with pytest.raises(CharacteristicMissingError, match="GATT characteristic missing"):
        raise CharacteristicMissingError("GATT characteristic missing")


def test_exception_hierarchy() -> None:
    """Test that exceptions maintain proper hierarchy."""
    # All custom exceptions except EfireMessageValueError inherit from EfireException
    custom_exceptions = [
        AuthError,
        CommandFailedException,
        DisconnectedException,
        FeatureNotSupported,
        CharacteristicMissingError,
    ]

    for exc_class in custom_exceptions:
        assert issubclass(exc_class, EfireException)
        assert issubclass(exc_class, Exception)

    # EfireMessageValueError inherits from ValueError
    assert issubclass(EfireMessageValueError, ValueError)
    assert issubclass(EfireMessageValueError, Exception)
