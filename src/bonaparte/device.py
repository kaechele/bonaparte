"""A generic device class for Napoleon eFIRE devices."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar

from bleak.exc import BleakDBusError, BleakError
from bleak_retry_connector import (
    BLEAK_RETRY_EXCEPTIONS as BLEAK_EXCEPTIONS,
    BleakClientWithServiceCache,
    BleakNotFoundError,
    establish_connection,
    retry_bluetooth_connection_error,
)

from .const import (
    FOOTER,
    HEADER,
    MIN_MESSAGE_LENGTH,
    READ_CHAR_UUID,
    REQUEST_HEADER,
    RESPONSE_HEADER,
    WRITE_CHAR_UUID,
)
from .exceptions import (
    CharacteristicMissingError,
    DisconnectedException,
    EfireMessageValueError,
)
from .utils import build_message, checksum_message

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop, Task
    from collections.abc import Awaitable, Callable

    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice
    from bleak.backends.scanner import AdvertisementData

_LOGGER = logging.getLogger(__name__)


DISCONNECT_DELAY = 120
DEFAULT_ATTEMPTS = 3
BLEAK_BACKOFF_TIME = 0.25

P = ParamSpec("P")
T = TypeVar("T")


def raise_if_not_connected(
    func: Callable[Concatenate[EfireDevice, P], Awaitable[T]],
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
    """A generic eFIRE Device."""

    _ble_device: BLEDevice
    _client: BleakClientWithServiceCache | None = None
    _connect_lock: asyncio.Lock
    _is_connected: bool
    _address: str
    _notifications_started: bool
    _notify_future: asyncio.Future[bytes] | None
    _read_char: BleakGATTCharacteristic | None
    _write_char: BleakGATTCharacteristic | None
    _write_lock: asyncio.Lock
    _advertisement_data: AdvertisementData | None

    def __init__(
        self, ble_device: BLEDevice, advertisement_data: AdvertisementData | None = None
    ) -> None:
        """Initialize the eFIRE Device."""
        self._address = ble_device.address
        self._advertisement_data = advertisement_data
        self._ble_device = ble_device
        self._connect_lock = asyncio.Lock()
        self._disconnect_timer: asyncio.TimerHandle | None = None
        self._disconnect_callbacks: list[Callable[[Any], None]] = []
        self._expected_disconnect = False
        self._is_connected = False
        self._loop: AbstractEventLoop | None = None
        self._notifications_started = False
        self._write_lock = asyncio.Lock()

    @property
    def name(self) -> str:
        """Device name or, if unavailable, the device address."""
        return self._ble_device.name or self._ble_device.address

    @property
    def address(self) -> str:
        """The device's Bluetooth MAC address."""
        return self._address

    @property
    def rssi(self) -> int | None:
        """Get the RSSI of the device."""
        if self._advertisement_data:
            return self._advertisement_data.rssi
        return None

    def set_ble_device_and_advertisement_data(
        self, ble_device: BLEDevice, advertisement_data: AdvertisementData
    ) -> None:
        """Set the BLE Device and advertisement data."""
        self._ble_device = ble_device
        self._advertisement_data = advertisement_data

    async def _ensure_connected(self) -> None:
        """Connect to the device and ensure we stay connected."""
        if self._connect_lock.locked():
            _LOGGER.debug(
                "[%s]: Connection already in progress, waiting for it to complete;"
                " RSSI: %s",
                self.name,
                self.rssi,
            )

        if self._client and self._client.is_connected:
            self._reset_disconnect_timer()
            return

        async with self._connect_lock:
            # Check again while holding the lock
            if self._client and self._client.is_connected:
                self._reset_disconnect_timer()
                return
            _LOGGER.debug("[%s]: Connecting; RSSI: %s", self.name, self.rssi)
            client = await establish_connection(
                BleakClientWithServiceCache,
                self._ble_device,
                self.name,
                self._disconnected,
                use_services_cache=True,
                ble_device_callback=lambda: self._ble_device,
            )
            _LOGGER.debug("[%s]: Connected; RSSI: %s", self.name, self.rssi)
            self._write_char = client.services.get_characteristic(WRITE_CHAR_UUID)
            self._read_char = client.services.get_characteristic(READ_CHAR_UUID)

            self._client = client
            self._reset_disconnect_timer()

            _LOGGER.debug(
                "[%s]: Subscribe to notifications; RSSI: %s", self.name, self.rssi
            )

            if self._read_char is None:
                msg = "Read Characteristic missing, aborting mission"
                raise CharacteristicMissingError(msg)
            await client.start_notify(self._read_char, self._notification_handler)

    def _reset_disconnect_timer(self) -> None:
        """Reset disconnect timer."""
        if self._disconnect_timer:
            self._disconnect_timer.cancel()
        self._expected_disconnect = False
        if not self._loop:
            self._loop = asyncio.get_running_loop()
        self._disconnect_timer = self._loop.call_later(
            DISCONNECT_DELAY, self._timed_disconnect
        )

    def _disconnected(self, _client: BleakClientWithServiceCache) -> None:
        """Disconnected callback."""
        pending_response = (
            self._notify_future is not None and not self._notify_future.done()
        )

        if self._expected_disconnect and not pending_response:
            _LOGGER.debug(
                "[%s]: Disconnected from device; RSSI: %s", self.name, self.rssi
            )
            return

        _LOGGER.warning(
            "[%s]: Device unexpectedly disconnected; RSSI: %s",
            self.name,
            self.rssi,
        )

        if pending_response:
            # self._notify_future cannot be None if pending_response is true,
            # but mypy doesn't know that, hence:
            assert self._notify_future is not None  # noqa: S101 # nosec
            msg = "Disconnected while response from device was pending"
            self._notify_future.set_exception(DisconnectedException(msg))

        for callback in self._disconnect_callbacks:
            callback(self)

    def _register_disconnect_callback(
        self, callback: Callable[[AnyEfireDevice], None]
    ) -> Callable[[], None]:
        def unregister() -> None:
            self._disconnect_callbacks.remove(callback)

        self._disconnect_callbacks.append(callback)
        return unregister

    def _timed_disconnect(self) -> Task[None]:
        """Disconnect from device."""
        self._disconnect_timer = None
        return asyncio.create_task(self._execute_timed_disconnect())

    async def _execute_timed_disconnect(self) -> None:
        """Execute timed disconnection."""
        _LOGGER.debug(
            "[%s]: Disconnecting after timeout of %s",
            self.name,
            DISCONNECT_DELAY,
        )
        await self.disconnect()

    async def disconnect(self) -> None:
        """Disconnect from device."""
        async with self._connect_lock:
            read_char = self._read_char
            client = self._client
            self._expected_disconnect = True
            self._client = None
            self._read_char = None
            self._write_char = None
            if client and client.is_connected:
                if read_char:
                    await client.stop_notify(read_char)
                await client.disconnect()

            for callback in self._disconnect_callbacks:
                callback(self)

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

    async def _notification_handler(
        self, _char: BleakGATTCharacteristic, message: bytearray
    ) -> None:
        _LOGGER.debug(
            "[%s]: Receiving response via notify: %s (expected=%s)",
            self.name,
            message.hex(" "),
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

    @retry_bluetooth_connection_error(DEFAULT_ATTEMPTS)
    async def _execute_locked(self, message: bytes | bytearray) -> bytes:
        """Send command to device and read response."""
        if not self._write_char:
            msg = "Write characteristic missing"
            raise CharacteristicMissingError(msg)

        if not self._client:
            msg = "Client is not initialized"
            raise BleakError(msg)

        try:
            future: asyncio.Future[bytes] = asyncio.Future()
            self._notify_future = future

            await self._client.write_gatt_char(self._write_char, message, response=True)
            result = await future
        except BleakDBusError as ex:
            # Disconnect so we can reset state and try again
            await asyncio.sleep(BLEAK_BACKOFF_TIME)
            _LOGGER.debug(
                "[%s]: RSSI: %s; Backing off %ss; Disconnecting due to error: %s",
                self.name,
                self.rssi,
                BLEAK_BACKOFF_TIME,
                ex,
            )
            await self.disconnect()
            raise
        except BleakError as ex:
            # Disconnect so we can reset state and try again
            _LOGGER.debug(
                "[%s]: RSSI: %s; Disconnecting due to error: %s",
                self.name,
                self.rssi,
                ex,
            )
            await self.disconnect()
            raise
        except DisconnectedException as ex:
            _LOGGER.debug(
                "[%s]: RSSI: %s; Disconnecting with response pending: %s",
                self.name,
                self.rssi,
                ex,
            )
            raise
        return result

    async def _execute(
        self,
        message: bytes | bytearray,
    ) -> bytes:
        """Send command to device and read response."""
        await self._ensure_connected()

        _LOGGER.debug(
            "[%s]: Sending message %s",
            self.name,
            message.hex(" "),
        )
        if self._write_lock.locked():
            _LOGGER.debug(
                "[%s]: Operation already in progress, waiting for it to complete;"
                " RSSI: %s",
                self.name,
                self.rssi,
            )
        async with self._write_lock:
            try:
                return await self._execute_locked(message)
            except BleakNotFoundError:
                _LOGGER.exception(
                    "[%s]: device not found, no longer in range, or poor RSSI: %s",
                    self.name,
                    self.rssi,
                )
                raise
            except CharacteristicMissingError as ex:
                _LOGGER.debug(
                    "[%s]: characteristic missing: %s; RSSI: %s",
                    self.name,
                    ex,
                    self.rssi,
                    exc_info=True,
                )
                raise
            except BLEAK_EXCEPTIONS:
                _LOGGER.debug("[%s]: communication failed", self.name, exc_info=True)
                raise

    async def execute_command(
        self, command: int, parameter: int | bytes | bytearray | None = None
    ) -> bytes:
        """Execute a command on the device."""
        payload = bytearray([command])

        if parameter:
            # for convenience we allow using just a single hex value (aka int) as well
            if isinstance(parameter, int):
                payload = payload + bytes([parameter])
            else:
                payload = payload + parameter

        message = build_message(payload)
        self._validate_message(message)
        response = await self._execute(message)
        self._validate_message(response)

        # return just the response payload sans overhead
        return response[4:-2]


AnyEfireDevice = TypeVar("AnyEfireDevice", bound=EfireDevice)
