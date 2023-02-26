from bleak.backends.device import BLEDevice
import pytest

from bonaparte import Fireplace, FireplaceFeatures

fp = Fireplace(BLEDevice("aa:bb:cc:dd:ee:ff", "Fireplace", delegate=""))

full_valid_set = {"aux", "blower", "led_lights", "night_light", "split_flow"}
partial_valid_set = {"blower", "night_light"}

full_invalid_set = {
    "aux",
    "blower",
    "led_lights",
    "foo",
    "night_light",
    "bar",
    "split_flow",
}
partial_invalid_set = {"blower", "foo", "night_light"}


def test_full_valid_featureset() -> None:
    fireplace_features = FireplaceFeatures()
    fireplace_features.aux = True
    fireplace_features.blower = True
    fireplace_features.led_lights = True
    fireplace_features.night_light = True
    fireplace_features.split_flow = True
    assert fp.set_features(full_valid_set) == fireplace_features


def test_partial_valid_featureset() -> None:
    fireplace_features = FireplaceFeatures()
    fireplace_features.aux = False
    fireplace_features.blower = True
    fireplace_features.led_lights = False
    fireplace_features.night_light = True
    fireplace_features.split_flow = False
    assert fp.set_features(partial_valid_set) == fireplace_features


def test_full_invalid_featureset() -> None:
    with pytest.raises(
        ValueError,
        match=r"Invalid feature values found in input set: {'(foo|bar)', '(foo|bar)'}",
    ):
        fp.set_features(full_invalid_set)


def test_partial_invalid_featureset() -> None:
    with pytest.raises(
        ValueError, match="Invalid feature value found in input set: {'foo'}"
    ):
        fp.set_features(partial_invalid_set)
