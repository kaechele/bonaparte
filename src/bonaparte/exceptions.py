from __future__ import annotations


class EfireException(Exception):  # noqa: N818
    pass


class AuthError(EfireException):
    pass


class CommandFailedException(EfireException):
    pass


class DisconnectedException(EfireException):
    pass


class FeatureNotSupported(EfireException):
    pass


class ResponseError(EfireException):
    pass


class EfireMessageValueError(ValueError):
    pass


class CharacteristicMissingError(EfireException):
    pass
