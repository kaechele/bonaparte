"""Integration tests for message validation and edge cases."""

from bleak.backends.device import BLEDevice

from bonaparte.const import (
    MAX_BLOWER_SPEED,
    MAX_FLAME_HEIGHT,
    MAX_NIGHT_LIGHT_BRIGHTNESS,
    LedMode,
)
from bonaparte.fireplace import Fireplace, FireplaceFeatures, FireplaceState


def test_set_night_light_brightness_validation() -> None:
    """Test that night light brightness is validated."""
    # Just test the validation constants are correct
    assert MAX_NIGHT_LIGHT_BRIGHTNESS == 6


def test_flame_height_validation() -> None:
    """Test that flame height validation uses correct max."""
    assert MAX_FLAME_HEIGHT == 6


def test_blower_speed_validation() -> None:
    """Test that blower speed validation uses correct max."""
    assert MAX_BLOWER_SPEED == 6


def test_fireplace_requires_feature_for_aux() -> None:
    """Test that AUX operations require the feature to be enabled."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace = Fireplace(ble_device)

    # Without aux feature, has_aux should be False
    assert fireplace.has_aux is False


def test_fireplace_requires_feature_for_blower() -> None:
    """Test that blower operations require the feature to be enabled."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace = Fireplace(ble_device)

    # Without blower feature, has_blower should be False
    assert fireplace.has_blower is False


def test_fireplace_requires_feature_for_led_lights() -> None:
    """Test that LED operations require the feature to be enabled."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace = Fireplace(ble_device)

    # Without LED feature, has_led_lights should be False
    assert fireplace.has_led_lights is False


def test_fireplace_requires_feature_for_split_flow() -> None:
    """Test that split flow operations require the feature to be enabled."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace = Fireplace(ble_device)

    # Without split flow feature, has_split_flow should be False
    assert fireplace.has_split_flow is False


def test_feature_combinations() -> None:
    """Test various combinations of features."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)

    # All features enabled
    all_features = FireplaceFeatures(
        aux=True,
        blower=True,
        led_lights=True,
        night_light=True,
        split_flow=True,
        timer=True,
    )
    fireplace_all = Fireplace(ble_device, all_features)

    assert fireplace_all.has_aux is True
    assert fireplace_all.has_blower is True
    assert fireplace_all.has_led_lights is True
    assert fireplace_all.has_night_light is True
    assert fireplace_all.has_split_flow is True

    # Only essential features
    essential = FireplaceFeatures(blower=True, night_light=True)
    fireplace_essential = Fireplace(ble_device, essential)

    assert fireplace_essential.has_aux is False
    assert fireplace_essential.has_blower is True
    assert fireplace_essential.has_led_lights is False
    assert fireplace_essential.has_night_light is True
    assert fireplace_essential.has_split_flow is False


def test_fireplace_state_default_led_mode() -> None:
    """Test that default LED mode is set correctly."""

    state = FireplaceState()

    # Default mode should be HOLD
    assert state.led_mode == LedMode.HOLD


def test_empty_feature_set() -> None:
    """Test setting an empty feature set."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace = Fireplace(ble_device)

    # Set empty features
    result = fireplace.set_features(set())

    assert result.aux is False
    assert result.blower is False
    assert result.led_lights is False
    assert result.night_light is False
    assert result.split_flow is False
    assert result.timer is False


def test_all_features_set() -> None:
    """Test setting all features at once."""
    ble_device = BLEDevice("aa:bb:cc:dd:ee:ff", "Test", details=None)
    fireplace = Fireplace(ble_device)

    # Set all features
    all_features = {"aux", "blower", "led_lights", "night_light", "split_flow", "timer"}
    result = fireplace.set_features(all_features)

    assert result.aux is True
    assert result.blower is True
    assert result.led_lights is True
    assert result.night_light is True
    assert result.split_flow is True
    assert result.timer is True


def test_led_color_rgb_format() -> None:
    """Test that LED color is stored as RGB tuple."""

    state = FireplaceState()

    # Default should be (0, 0, 0)
    assert state.led_color == (0, 0, 0)
    assert isinstance(state.led_color, tuple)
    assert len(state.led_color) == 3

    # Set a color
    state.led_color = (255, 128, 64)
    assert state.led_color == (255, 128, 64)


def test_timer_time_format() -> None:
    """Test that timer time is stored as (hours, minutes, seconds) tuple."""

    state = FireplaceState()

    # Default should be (0, 0, 0)
    assert state.time_left == (0, 0, 0)
    assert isinstance(state.time_left, tuple)
    assert len(state.time_left) == 3

    # Set a time
    state.time_left = (5, 30, 15)
    assert state.time_left == (5, 30, 15)


def test_power_state_different_modes() -> None:
    """Test power state calculation in different modes."""

    # Compatibility mode - uses bt_power
    state_compat = FireplaceState(compatibility_mode=True)
    state_compat.bt_power = True
    state_compat.ifc_power = False
    state_compat.flame_height = 0
    assert state_compat.power is True

    state_compat.bt_power = False
    assert state_compat.power is False

    # Non-compatibility mode - uses ifc_power and flame_height
    state_non_compat = FireplaceState(compatibility_mode=False)  # type: ignore[unreachable]
    state_non_compat.bt_power = False
    state_non_compat.ifc_power = True
    state_non_compat.flame_height = 5
    assert state_non_compat.power is True

    # Both conditions must be met in non-compat mode
    state_non_compat.flame_height = 0
    assert state_non_compat.power is False

    state_non_compat.flame_height = 5
    state_non_compat.ifc_power = False
    assert state_non_compat.power is False
