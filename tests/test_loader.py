"""Tests for Sightglass cycle loader and data management."""

from sightglass.data.loader import load_cycles, partition_splits
from sightglass.data.models import Cycle


def test_partition_splits_grouped() -> None:
    splits = partition_splits(total_cycles=2205, split_name="grouped")
    train_set = set(splits["train"])
    val_set = set(splits["val"])
    test_set = set(splits["test"])

    # Disjointness
    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(test_set)
    assert val_set.isdisjoint(test_set)

    # Coverage
    assert len(train_set | val_set | test_set) == 2205

    # Proportions ≈ 70 / 15 / 15
    assert 1400 <= len(train_set) <= 1650
    assert 250 <= len(val_set) <= 400
    assert 250 <= len(test_set) <= 400


def test_load_cycles_hydraulic_train() -> None:
    # Test on a small batch of 50 cycles
    cycles = load_cycles(dataset="hydraulic", split="train", total_count=50)
    assert len(cycles) > 0
    c0 = cycles[0]
    assert isinstance(c0, Cycle)
    assert len(c0.signals) == 17

    # Check 100 Hz signal (6000 points)
    assert "PS1" in c0.signals
    assert c0.signals["PS1"].rate_hz == 100.0
    assert len(c0.signals["PS1"].values) == 6000

    # Check 10 Hz signal (600 points)
    assert "FS1" in c0.signals
    assert c0.signals["FS1"].rate_hz == 10.0
    assert len(c0.signals["FS1"].values) == 600

    # Check 1 Hz signal (60 points)
    assert "TS1" in c0.signals
    assert c0.signals["TS1"].rate_hz == 1.0
    assert len(c0.signals["TS1"].values) == 60

    # Check labels
    assert "cooler_condition" in c0.labels
    assert "valve_condition" in c0.labels
    assert "pump_leakage" in c0.labels
    assert "accumulator_pressure" in c0.labels

# Test: verify cycle sorting determinism by id
