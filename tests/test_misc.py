"""Miscellaneous tests."""
from bleak.backends.device import BLEDevice
from bonaparte import Fireplace, FireplaceFeatures
import pytest

fp = Fireplace(BLEDevice("aa:bb:cc:dd:ee:ff", "Fireplace", details=None, rssi=0))

full_valid_set = {"aux", "blower", "led_lights", "night_light", "split_flow", "timer"}
partial_valid_set = {"blower", "night_light"}

full_invalid_set = {
    "aux",
    "blower",
    "led_lights",
    "foo",
    "night_light",
    "bar",
    "split_flow",
    "timer",
}
partial_invalid_set = {"blower", "foo", "night_light"}


def test_full_valid_featureset() -> None:
    """Test a set of all features that is valid."""
    fireplace_features = FireplaceFeatures()
    fireplace_features.aux = True
    fireplace_features.blower = True
    fireplace_features.led_lights = True
    fireplace_features.night_light = True
    fireplace_features.split_flow = True
    fireplace_features.timer = True
    assert fp.set_features(full_valid_set) == fireplace_features


def test_partial_valid_featureset() -> None:
    """Test a partial set of features that is valid."""
    fireplace_features = FireplaceFeatures()
    fireplace_features.aux = False
    fireplace_features.blower = True
    fireplace_features.led_lights = False
    fireplace_features.night_light = True
    fireplace_features.split_flow = False
    fireplace_features.timer = False
    assert fp.set_features(partial_valid_set) == fireplace_features


def test_full_invalid_featureset() -> None:
    """Test a set of all features that also has invalid entries."""
    with pytest.raises(
        ValueError,
        match=r"Invalid feature values found in input set: {'(foo|bar)', '(foo|bar)'}",
    ):
        fp.set_features(full_invalid_set)


def test_partial_invalid_featureset() -> None:
    """Test a partial set of features that also has invalid entries."""
    with pytest.raises(
        ValueError, match="Invalid feature value found in input set: {'foo'}"
    ):
        fp.set_features(partial_invalid_set)
