"""Exceptions used in the Bonaparte library."""
from __future__ import annotations


class EfireException(Exception):  # noqa: N818
    """Generic eFIRE device exception."""


class AuthError(EfireException):
    """For when authentication fails."""


class CommandFailedException(EfireException):
    """For when a command returns a failure."""


class DisconnectedException(EfireException):
    """For when the device is disconnected and we try to use it."""


class FeatureNotSupported(EfireException):
    """For when a feature is accessed that the device is not set up for."""


class EfireMessageValueError(ValueError):
    """For when an invalid message is received or generated."""


class CharacteristicMissingError(EfireException):
    """For when a required BLE GATT characteristic is missing."""
