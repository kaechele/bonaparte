from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar

import async_timeout
from bleak import BleakClient
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

from .const import (
    FOOTER,
    HEADER,
    MIN_MESSAGE_LENGTH,
    READ_CHAR_UUID,
    REQUEST_HEADER,
    RESPONSE_HEADER,
    WRITE_CHAR_UUID,
)
from .exceptions import DisconnectedException, EfireMessageValueError, ResponseError
from .utils import build_message, checksum_message

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine

    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)


DISCONNECT_DELAY = 5

P = ParamSpec("P")
T = TypeVar("T")


def raise_if_not_connected(
    func: Callable[Concatenate[EfireDevice, P], Awaitable[T]]
) -> Callable[Concatenate[EfireDevice, P], Awaitable[T]]:
    """Define a wrapper to authenticate if we aren't yet."""

    async def _raise_if_not_connected(
        self: EfireDevice, *args: P.args, **kwargs: P.kwargs
    ) -> T:
        if not self._is_connected:  # pylint: disable=protected-access
            msg = "Fireplace is not connected"
            raise DisconnectedException(msg)
        return await func(self, *args, **kwargs)

    return _raise_if_not_connected


class EfireDevice:
    _ble_device: BLEDevice
    _client: BleakClient
    _connect_lock: asyncio.Lock
    _is_authenticated: bool
    _is_connected: bool
    _mac: str
    _notifications_started: bool
    _notify_future: asyncio.Future[bytes] | None
    _read_char: BleakGATTCharacteristic | None
    _write_char: BleakGATTCharacteristic | None
    _write_lock: asyncio.Lock
    name: str | None

    def __init__(
        self,
        ble_device: BLEDevice,
    ) -> None:
        self._ble_device = ble_device
        self._connect_lock = asyncio.Lock()
        self._is_authenticated = False
        self._is_connected = False
        self._mac = ble_device.address
        self._notifications_started = False
        self._write_lock = asyncio.Lock()

    @property
    def mac(self) -> str:
        return self._mac

    def disconnected_callback(self, client: BleakClient) -> None:  # noqa: ARG002
        """Callback for when the device is disconnected."""

        _LOGGER.warning("Disconnected from %s", self.name)
        self._is_connected = False

    async def connect(self, retry_attempts: int = 4) -> None:
        """Connects to the device."""

        if self._is_connected or self._connect_lock.locked():
            return

        async with self._connect_lock:
            try:
                self.name = self._ble_device.name
                _LOGGER.debug("Connecting to %s", self.name)

                self._client = await establish_connection(
                    client_class=BleakClient,
                    device=self._ble_device,
                    name=self._mac,
                    disconnected_callback=self.disconnected_callback,
                    max_attempts=retry_attempts,
                    use_services_cache=True,
                )

                self._write_char = self._client.services.get_characteristic(
                    WRITE_CHAR_UUID
                )
                if not self._write_char:
                    msg = (
                        f"[{self.name}]: Write characteristic not found:"
                        f" {WRITE_CHAR_UUID}"
                    )
                    raise BleakError(msg)  # noqa: TRY301

                self._read_char = self._client.services.get_characteristic(
                    READ_CHAR_UUID
                )
                if not self._write_char:
                    msg = (
                        f"[{self.name}]: Read characteristic not found:"
                        f" {READ_CHAR_UUID}"
                    )
                    raise BleakError(msg)  # noqa: TRY301

                self._is_connected = True

                _LOGGER.debug("Successfully connected to %s", self.name)

            except BleakError:
                _LOGGER.error("Failed to connect to %s", self.name)
                self._is_connected = False
            await self.start_notify()

    async def disconnect(self) -> None:
        """Disconnects the device."""
        await self._client.disconnect()

    def _validate_message(self, message: bytes | bytearray) -> None:
        # the minimum message consists of 6 bytes:
        # header, message_type, length, command, checksum, footer
        # the payload is optional and not used in query commands
        if len(message) < MIN_MESSAGE_LENGTH:
            msg = (
                f"Message too short. Got {len(message)} bytes, expected at least 6"
                " bytes"
            )
            raise EfireMessageValueError(msg)
        if message[0] != HEADER:
            msg = f"Unknown message header {message[0]}. Expected {HEADER}."
            raise EfireMessageValueError(msg)
        if message[1] not in [REQUEST_HEADER, RESPONSE_HEADER]:
            msg = (
                f"Unknown message type {message[1]:02x}. Expected"
                f" {REQUEST_HEADER:02x} or {RESPONSE_HEADER:02x}."
            )
            raise EfireMessageValueError(msg)
        if message[2] != len(message) - 3:
            msg = f"Incorrect message length {len(message)}. Expected {message[2]+3}."
            raise EfireMessageValueError(msg)
        if message[-2] != checksum_message(message):
            msg = (
                f"Invalid checksum {message[-2]}. "
                f"Calculated checksum {checksum_message(message)}."
            )
            raise EfireMessageValueError(msg)
        if message[-1] != FOOTER:
            msg = f"Invalid fooer {message[-1]}. Message should end with {FOOTER}."
            raise EfireMessageValueError(msg)

    async def start_notify(self) -> None:
        """Start notify."""
        if not self._notifications_started:
            _LOGGER.debug("%s: Starting notify for %s", self.name, type(self))
            try:
                await self._start_notify(self._notify)
            except BleakError as err:
                _LOGGER.debug("%s: Failed to start notify: %s", self.name, err)
                raise
            self._notifications_started = True

    async def _start_notify(
        self,
        callback: Callable[
            [BleakGATTCharacteristic, bytearray], Coroutine[Any, Any, None]
        ],
    ) -> None:
        """Start notify."""
        if not self._client.is_connected or not self._read_char:
            return
        try:
            await self._client.start_notify(self._read_char, callback)
            # Workaround for MacOS to allow restarting notify
        except ValueError:
            await self.stop_notify(self._read_char)
            if not self._client.is_connected:
                return
            await self._client.start_notify(self._read_char, callback)

    async def _notify(
        self, char: BleakGATTCharacteristic, message: bytearray  # noqa: ARG002
    ) -> None:
        _LOGGER.debug(
            "[%s]: Receiving response via notify: %s (waiting=%s)",
            self.name,
            message.hex(),
            bool(self._notify_future),
        )

        if not self._notify_future:
            # We have no consumer. We're done.
            return

        try:
            self._validate_message(message)
        except EfireMessageValueError as ex:
            self._notify_future.set_exception(ex)
            self._notify_future = None
            return
        self._notify_future.set_result(message)
        self._notify_future = None

    async def stop_notify(
        self, char: BleakGATTCharacteristic | None  # noqa: ARG002
    ) -> None:
        if not self._client.is_connected or not self._notifications_started:
            return
        _LOGGER.debug("[%s]: Stopping notify: %s", self.name, type(self))
        try:
            if self._read_char:
                await self._client.stop_notify(self._read_char)
        except EOFError as err:
            _LOGGER.debug("[%s]: D-Bus stopping notify: %s", self.name, err)
        except BleakError as err:
            _LOGGER.debug("[%s]: Bleak error stopping notify: %s", self.name, err)

    @raise_if_not_connected
    async def _write(
        self, payload: bytes | bytearray, retries: int = 3, timeout: int = 10
    ) -> bytes:
        async with self._write_lock:
            return await self._write_unsafe(payload, retries, timeout)

    @raise_if_not_connected
    async def _write_unsafe(
        self, message: bytes | bytearray, retries: int = 3, timeout: int = 10
    ) -> bytes:
        if not self._client.is_connected:
            msg = "Disconnected"
            raise BleakError(msg)

        result = b""

        for attempt in range(retries):
            future: asyncio.Future[bytes] = asyncio.Future()
            self._notify_future = future
            _LOGGER.debug(
                "[%s]: Writing message to %s: %s",
                self.name,
                self._write_char,
                message.hex(),
            )
            _LOGGER.debug("[%s]: Waiting for response", self.name)
            async with async_timeout.timeout(timeout):
                try:
                    if self._write_char:
                        await self._client.write_gatt_char(
                            self._write_char, message, response=True
                        )
                        result = await future
                except ResponseError:
                    if attempt == retries - 1:
                        raise
                    _LOGGER.debug("[%s]: Invalid response, retrying", self.name)
                    continue
                else:
                    break
        _LOGGER.debug("[%s]: Got response: %s", self.name, result.hex())
        return result

    @raise_if_not_connected
    async def execute_command(
        self, command: int, parameter: int | bytes | bytearray | None = None
    ) -> bytes:
        payload = bytearray([command])

        if parameter:
            # for convenience we allow using just a single hex value (aka int) as well
            if isinstance(parameter, int):
                payload = payload + bytes([parameter])
            else:
                payload = payload + parameter

        message = build_message(payload)
        self._validate_message(message)
        response = await self._write(message)
        self._validate_message(response)

        # return just the response payload sans overhead
        return response[4:-2]
