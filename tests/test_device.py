"""Test device interactions."""


import asyncio

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from flexmock import flexmock
import pytest

from bonaparte.const import EfireCommand, PasswordAction
import bonaparte.device
from bonaparte.device import EfireDevice
import bonaparte.exceptions

from .mock_messages import invalid_responses, request, response

TEST_RSSI_VALUE = 80
TEST_DEV_MAC = "aa:bb:cc:dd:ee:ff"
TEST_DEV_NAME = "Fireplace"


@pytest.fixture()
def fixture_bledevice_anonymous() -> BLEDevice:
    """Anonymous BLEDevice instance."""
    return BLEDevice(TEST_DEV_MAC, None, details=None, rssi=0)


@pytest.fixture()
def fixture_bledevice_named() -> BLEDevice:
    """Named BLEDevice instance."""
    return BLEDevice(TEST_DEV_MAC, TEST_DEV_NAME, details=None, rssi=0)


@pytest.fixture()
def fixture_adv_with_rssi() -> AdvertisementData:
    """AdvertisementData instance with RSSI set."""
    return AdvertisementData(
        local_name=None,
        manufacturer_data={},
        service_data={},
        service_uuids=[],
        rssi=TEST_RSSI_VALUE,
        tx_power=None,
        platform_data=(),
    )


@pytest.fixture()
def fixture_device_anonymous(fixture_bledevice_anonymous: BLEDevice) -> EfireDevice:
    """EfireDevice instance."""
    return EfireDevice(fixture_bledevice_anonymous)


@pytest.fixture()
def fixture_device_named(fixture_bledevice_named: BLEDevice) -> EfireDevice:
    """Named EfireDevice instance."""
    return EfireDevice(fixture_bledevice_named)


@pytest.fixture()
def fixture_device_with_rssi_adv(fixture_bledevice_anonymous: BLEDevice) -> EfireDevice:
    """EfireDevice instance with AdvertisementData including RSSI set."""
    adv = AdvertisementData(
        local_name=None,
        manufacturer_data={},
        service_data={},
        service_uuids=[],
        rssi=TEST_RSSI_VALUE,
        tx_power=None,
        platform_data=(),
    )
    return EfireDevice(ble_device=fixture_bledevice_anonymous, advertisement_data=adv)


class TestProperties:
    """Test device instance properties."""

    def test_device_name_available(self, fixture_device_named: EfireDevice) -> None:
        """Test whether the device name is returned correctly through the property."""
        assert fixture_device_named.name == TEST_DEV_NAME

    def test_device_name_unavailable(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Test whether the device MAC is returned if a name is not available."""
        assert fixture_device_anonymous.name == TEST_DEV_MAC

    def test_device_address(self, fixture_device_anonymous: EfireDevice) -> None:
        """Test whether the device MAC is returned correctly through the property."""
        assert fixture_device_anonymous.address == TEST_DEV_MAC

    def test_device_rssi_unavailable_from_adv_data(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Verify that None is returned if no RSSI data is in the AdvertisementData."""
        assert fixture_device_anonymous.rssi is None

    def test_device_rssi_available_from_adv_data(
        self,
        fixture_device_with_rssi_adv: EfireDevice,
    ) -> None:
        """Verify that RSSI is returned if RSSI data is in the AdvertisementData."""
        assert fixture_device_with_rssi_adv.rssi == TEST_RSSI_VALUE

    def test_set_ble_device_and_advertisement_data(
        self,
        fixture_device_anonymous: EfireDevice,
        fixture_bledevice_named: BLEDevice,
        fixture_adv_with_rssi: AdvertisementData,
    ) -> None:
        """Verify that BLEDevice and AdvertisementData replacement works."""
        dev = fixture_device_anonymous
        assert dev.rssi is None
        assert dev.name == TEST_DEV_MAC
        dev.set_ble_device_and_advertisement_data(
            ble_device=fixture_bledevice_named, advertisement_data=fixture_adv_with_rssi
        )
        assert dev.rssi == TEST_RSSI_VALUE
        assert dev.name == TEST_DEV_NAME


class TestEnsureConnected:
    """Test connection functionality."""

    @pytest.mark.asyncio()
    async def test_device_ensure_connected_locked(
        self,
        fixture_device_with_rssi_adv: EfireDevice,
    ) -> None:
        """Verify that error is thrown when the connection is locked."""
        dev = fixture_device_with_rssi_adv
        flexmock(bonaparte.device._LOGGER).should_receive("debug").with_args(
            "[%s]: Connection already in progress, waiting for it to complete; RSSI: %s",  # noqa: E501
            TEST_DEV_MAC,
            TEST_RSSI_VALUE,
        ).once()
        await dev._connect_lock.acquire()
        task = asyncio.ensure_future(dev._ensure_connected())
        await asyncio.sleep(0)
        task.cancel()

    @pytest.mark.asyncio()
    async def test_device_ensure_connected_with_client_already_connected(
        self,
        fixture_device_with_rssi_adv: EfireDevice,
    ) -> None:
        """Verify disconnect timer is reset if already connected."""
        dev = fixture_device_with_rssi_adv
        flexmock(dev).should_receive("_reset_disconnect_timer").once()
        dev._client = flexmock(is_connected=True)
        await dev._ensure_connected()


class TestCommandExecution:
    """Test command execution functionality."""

    @pytest.mark.asyncio()
    async def test_execute_command_with_no_params(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Verify that commands without parameters can be called."""
        dev = fixture_device_anonymous

        async def mock_execute(message: bytes | bytearray) -> bytes:
            return response["ble_version"]

        dev._execute = mock_execute

        assert (
            await dev.execute_command(EfireCommand.GET_BLE_VERSION)
            == response["ble_version"][4:-2]
        )

    @pytest.mark.asyncio()
    async def test_execute_command_with_bytearray_params(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Test commands with bytearray as parameters."""
        dev = fixture_device_anonymous

        async def mock_execute(message: bytes | bytearray) -> bytes:
            return response["login_success"]

        dev._execute = mock_execute

        assert (
            await dev.execute_command(
                request["login_1234"][3], request["login_1234"][4:7]
            )
            == response["login_success"][4:-2]
        )

    @pytest.mark.asyncio()
    async def test_execute_command_with_int_param(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Test commands with single int as parameter."""
        dev = fixture_device_anonymous

        async def mock_execute(message: bytes | bytearray) -> bytes:
            return response["password_mgmt_success"]

        dev._execute = mock_execute

        assert (
            await dev.execute_command(EfireCommand.PASSWORD_MGMT, PasswordAction.RESET)
            == response["password_mgmt_success"][4:-2]
        )


class TestValidateMessage:
    """Tests for message validation."""

    def test_validate_message_with_valid_message(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message valid."""
        try:
            fixture_device_anonymous._validate_message(response["ble_version"])
        except Exception as exc:
            pytest.fail(f"Exception raised {exc}")

    def test_validate_message_with_short_message(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message too short."""
        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
            match="Message too short. Got 0 bytes, expected at least 6 bytes.",
        ):
            fixture_device_anonymous._validate_message(bytes([]))

    def test_validate_message_with_invalid_header(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message with invalid header."""
        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
            match="Unknown message header 187. Expected 171.",
        ):
            fixture_device_anonymous._validate_message(
                invalid_responses["invalid_header"]
            )

    def test_validate_message_with_invalid_msg_type_header(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message with invalid message type header."""
        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
            match="Unknown message type ab. Expected aa or bb.",
        ):
            fixture_device_anonymous._validate_message(
                invalid_responses["invalid_msg_type_header"]
            )

    def test_validate_message_with_incorrect_length(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message with incorrect length."""
        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
            match="Incorrect message length 9. Expected 6.",
        ):
            fixture_device_anonymous._validate_message(
                invalid_responses["incorrect_length"]
            )

    def test_validate_message_with_invalid_checksum(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message with invalid checksum."""
        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
            match="Invalid checksum 0. Calculated checksum 252.",
        ):
            fixture_device_anonymous._validate_message(
                invalid_responses["invalid_checksum"]
            )

    def test_validate_message_with_invalid_footer(
        self, fixture_device_anonymous: EfireDevice
    ) -> None:
        """Message Validation Test: Message with invalid footer."""
        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
            match="Invalid footer 68. Message should end with 85.",
        ):
            fixture_device_anonymous._validate_message(
                invalid_responses["invalid_footer"]
            )


class TestNotificationHandler:
    """Tests for the BLE notification handling."""

    @pytest.mark.asyncio()
    async def test_notification_handler_with_no_listener(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Testing handler with no listener attached."""
        # Ensure we return early and never call _validate_message
        flexmock(fixture_device_anonymous).should_receive("_validate_message").never()
        await fixture_device_anonymous._notification_handler(
            None, bytearray(response["ble_version"])
        )

    @pytest.mark.asyncio()
    async def test_notification_handler_with_valid_response(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Testing handler with valid response received."""
        # Ensure we return early and never call _validate_message
        future: asyncio.Future[bytes] = asyncio.Future()
        fixture_device_anonymous._notify_future = future
        await fixture_device_anonymous._notification_handler(
            None, bytearray(response["ble_version"])
        )
        result = future.result()
        assert future.done()
        assert result == response["ble_version"]

    @pytest.mark.asyncio()
    async def test_notification_handler_with_invalid_response(
        self,
        fixture_device_anonymous: EfireDevice,
    ) -> None:
        """Testing handler with invalid response received."""
        # Ensure we return early and never call _validate_message

        future: asyncio.Future[bytes] = asyncio.Future()
        fixture_device_anonymous._notify_future = future
        await fixture_device_anonymous._notification_handler(
            None, bytearray(invalid_responses["invalid_header"])
        )

        with pytest.raises(
            bonaparte.exceptions.EfireMessageValueError,
        ):
            future.result()

        assert (
            future.exception().__class__ == bonaparte.exceptions.EfireMessageValueError
        )
        assert fixture_device_anonymous._notify_future is None
