"""Tests for Fireplace class functionality."""

from bleak.backends.device import BLEDevice
import pytest

from bonaparte import Fireplace, FireplaceFeatures, FireplaceState


def test_fireplace_initialization() -> None:
    """Test that Fireplace initializes correctly."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    assert fireplace.name == "TestFireplace"
    assert fireplace.address == "aa:bb:cc:dd:ee:ff"
    assert isinstance(fireplace.state, FireplaceState)
    assert isinstance(fireplace.features, FireplaceFeatures)


def test_fireplace_initialization_with_features() -> None:
    """Test that Fireplace initializes with custom features."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    features = FireplaceFeatures(blower=True, led_lights=True)
    fireplace = Fireplace(ble_device, features)

    assert fireplace.has_blower is True
    assert fireplace.has_led_lights is True
    assert fireplace.has_aux is False
    assert fireplace.has_night_light is False
    assert fireplace.has_split_flow is False


def test_fireplace_state_compatibility_mode() -> None:
    """Test FireplaceState compatibility mode."""
    # Default compatibility mode (True)
    state_compat = FireplaceState(compatibility_mode=True)
    state_compat.bt_power = True
    state_compat.ifc_power = False
    state_compat.flame_height = 0
    assert state_compat.power is True  # Uses bt_power

    # Non-compatibility mode
    state_non_compat = FireplaceState(compatibility_mode=False)
    state_non_compat.bt_power = False
    state_non_compat.ifc_power = True
    state_non_compat.flame_height = 5
    assert state_non_compat.power is True  # Uses ifc_power and flame_height

    # Non-compatibility mode with flame off
    state_non_compat.flame_height = 0
    assert state_non_compat.power is False


def test_fireplace_has_feature_properties() -> None:
    """Test feature property accessors."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    features = FireplaceFeatures(
        aux=True,
        blower=True,
        led_lights=True,
        night_light=True,
        split_flow=True,
        timer=True,
    )
    fireplace = Fireplace(ble_device, features)

    assert fireplace.has_aux is True
    assert fireplace.has_blower is True
    assert fireplace.has_led_lights is True
    assert fireplace.has_night_light is True
    assert fireplace.has_split_flow is True


def test_set_features_from_set() -> None:
    """Test setting features from a set of strings."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    # Set specific features
    result = fireplace.set_features({"blower", "led_lights"})

    assert result.blower is True
    assert result.led_lights is True
    assert result.aux is False
    assert result.night_light is False
    assert result.split_flow is False
    assert result.timer is False

    # Verify it's applied to the fireplace
    assert fireplace.has_blower is True
    assert fireplace.has_led_lights is True


def test_set_features_invalid_feature() -> None:
    """Test that setting invalid features raises an error."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    with pytest.raises(ValueError, match="Invalid feature value found"):
        fireplace.set_features({"blower", "invalid_feature"})


def test_set_features_multiple_invalid() -> None:
    """Test that setting multiple invalid features raises an error."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    with pytest.raises(ValueError, match="Invalid feature values found"):
        fireplace.set_features({"blower", "foo", "bar"})


def test_fireplace_features_dataclass() -> None:
    """Test FireplaceFeatures dataclass behavior."""
    # Default initialization
    features = FireplaceFeatures()
    assert features.aux is False
    assert features.blower is False
    assert features.led_lights is False
    assert features.night_light is False
    assert features.split_flow is False
    assert features.timer is False

    # Custom initialization
    features = FireplaceFeatures(blower=True, timer=True)
    assert features.aux is False
    assert features.blower is True
    assert features.led_lights is False
    assert features.night_light is False
    assert features.split_flow is False
    assert features.timer is True


def test_fireplace_state_dataclass() -> None:
    """Test FireplaceState dataclass initialization and defaults."""
    state = FireplaceState()

    assert state.aux is False
    assert state.ble_version == ""
    assert state.blower_speed == 0
    assert state.bt_power is False
    assert state.flame_height == 0
    assert state.ifc_power is False
    assert state.led_color == (0, 0, 0)
    assert state.led is False
    assert state.mcu_version == ""
    assert state.night_light_brightness == 0
    assert state.pilot is False
    assert state.remote_in_use is False
    assert state.split_flow is False
    assert state.thermostat is False
    assert state.time_left == (0, 0, 0)
    assert state.timer is False


def test_fireplace_feature_not_supported_aux() -> None:
    """Test that accessing aux without the feature raises an error."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)  # No features enabled

    assert fireplace.has_aux is False


def test_fireplace_feature_not_supported_blower() -> None:
    """Test that blower feature check works correctly."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    assert fireplace.has_blower is False

    # Enable blower
    fireplace.set_features({"blower"})
    assert fireplace.has_blower is True


def test_fireplace_feature_not_supported_led_lights() -> None:
    """Test that LED lights feature check works correctly."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    assert fireplace.has_led_lights is False

    # Enable LED lights
    fireplace.set_features({"led_lights"})
    assert fireplace.has_led_lights is True


def test_fireplace_feature_not_supported_split_flow() -> None:
    """Test that split flow feature check works correctly."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    assert fireplace.has_split_flow is False

    # Enable split flow
    fireplace.set_features({"split_flow"})
    assert fireplace.has_split_flow is True


def test_fireplace_compatibility_mode_default() -> None:
    """Test that compatibility mode is True by default."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    # The compatibility mode is stored in the state
    assert fireplace.state._compatibility_mode is True  # noqa: SLF001


def test_fireplace_compatibility_mode_disabled() -> None:
    """Test that compatibility mode can be disabled."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device, compatibility_mode=False)

    assert fireplace.state._compatibility_mode is False  # noqa: SLF001


def test_fireplace_state_updates() -> None:
    """Test that fireplace state can be updated."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "TestFireplace", details=None)
    fireplace = Fireplace(ble_device)

    # Update various state fields
    fireplace.state.bt_power = True
    fireplace.state.flame_height = 5
    fireplace.state.blower_speed = 3
    fireplace.state.led_color = (255, 128, 0)

    assert fireplace.state.bt_power is True
    assert fireplace.state.flame_height == 5
    assert fireplace.state.blower_speed == 3
    assert fireplace.state.led_color == (255, 128, 0)
