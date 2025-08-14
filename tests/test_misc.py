"""Miscellaneous tests."""

# ruff: noqa: PLR2004

from bleak.backends.device import BLEDevice
import pytest

from bonaparte import Fireplace, FireplaceFeatures
from bonaparte.const import LedMode, LedState

fp = Fireplace(BLEDevice("aa:bb:cc:dd:ee:ff", "Fireplace", details=None))

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


def test_led_state_enum() -> None:
    """LED state multi value enum works when instantiated with any of the values."""
    assert LedState.ON.short == 0xFF
    assert LedState.ON.long == bytes([0xFF, 0xFF, 0xFF])

    assert LedState.OFF.short == 0x00
    assert LedState.OFF.long == bytes([0, 0, 0])

    assert LedState(LedState.ON.short) == LedState.ON
    assert LedState(LedState.ON.long) == LedState.ON

    assert LedState(LedState.OFF.short) == LedState.OFF
    assert LedState(LedState.OFF.long) == LedState.OFF


def test_led_mode_enum() -> None:
    """LED mode multi value enum works when instantiated with any of the values."""
    assert LedMode.CYCLE.short == 0x01
    assert LedMode.CYCLE.long == bytes([0x01, 0x01, 0x01])
    assert LedMode.CYCLE.setvalue == 0x20

    assert LedMode(LedMode.CYCLE.short) == LedMode.CYCLE
    assert LedMode(LedMode.CYCLE.long) == LedMode.CYCLE
    assert LedMode(LedMode.CYCLE.setvalue) == LedMode.CYCLE

    assert LedMode.HOLD.short == 0x02
    assert LedMode.HOLD.long == bytes([0x02, 0x02, 0x02])
    assert LedMode.HOLD.setvalue == 0x30

    assert LedMode(LedMode.HOLD.short) == LedMode.HOLD
    assert LedMode(LedMode.HOLD.long) == LedMode.HOLD
    assert LedMode(LedMode.HOLD.setvalue) == LedMode.HOLD

    assert LedMode.EMBER_BED.short == 0xFF
    assert LedMode.EMBER_BED.long == bytes([0xFF, 0xFF, 0xFF])
    assert LedMode.EMBER_BED.setvalue == 0x10

    assert LedMode(LedMode.EMBER_BED.short) == LedMode.EMBER_BED
    assert LedMode(LedMode.EMBER_BED.long) == LedMode.EMBER_BED
    assert LedMode(LedMode.EMBER_BED.setvalue) == LedMode.EMBER_BED
