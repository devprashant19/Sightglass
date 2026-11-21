"""Acceptance tests for UCI Hydraulic TimeNet connector."""

import numpy as np

from connector.timenet_connectors.datasets.uci.uci_hydraulic.connector import (
    LABELS,
    SENSORS,
    TOTAL_CYCLES,
    compute_grouped_splits,
    convert,
)


def test_connector_sensor_specifications() -> None:
    assert len(SENSORS) == 17
    # Verify sensor rates and sample lengths
    for s in ["PS1", "PS2", "PS3", "PS4", "PS5", "PS6", "EPS1"]:
        _, unit, rate, n_pts, _ = SENSORS[s]
        assert rate == 100.0
        assert n_pts == 6000
        assert unit in ["bar", "W"]

    for s in ["FS1", "FS2"]:
        _, unit, rate, n_pts, _ = SENSORS[s]
        assert rate == 10.0
        assert n_pts == 600
        assert unit == "l/min"

    for s in ["TS1", "TS2", "TS3", "TS4", "VS1", "CE", "CP", "SE"]:
        _, unit, rate, n_pts, _ = SENSORS[s]
        assert rate == 1.0
        assert n_pts == 60


def test_connector_label_sets() -> None:
    assert set(LABELS["cooler_condition"].keys()) == {3, 20, 100}
    assert set(LABELS["valve_condition"].keys()) == {73, 80, 90, 100}
    assert set(LABELS["pump_leakage"].keys()) == {0, 1, 2}
    assert set(LABELS["accumulator_pressure"].keys()) == {90, 100, 115, 130}
    assert set(LABELS["stable_flag"].keys()) == {0, 1}


def test_connector_split_disjointness_and_coverage() -> None:
    labels = np.zeros((TOTAL_CYCLES, 5), dtype=np.int32)
    for i in range(TOTAL_CYCLES):
        labels[i, 0] = [3, 20, 100][i % 3]
        labels[i, 1] = [73, 80, 90, 100][(i // 3) % 4]
        labels[i, 2] = [0, 1, 2][(i // 12) % 3]
        labels[i, 3] = [90, 100, 115, 130][(i // 36) % 4]
        labels[i, 4] = 0

    splits = compute_grouped_splits(labels)

    train_set = set(splits["train"])
    val_set = set(splits["val"])
    test_set = set(splits["test"])

    # Disjointness
    assert train_set.isdisjoint(val_set)
    assert train_set.isdisjoint(test_set)
    assert val_set.isdisjoint(test_set)

    # Full coverage
    all_set = train_set | val_set | test_set
    assert len(all_set) == TOTAL_CYCLES
    assert all_set == set(range(TOTAL_CYCLES))

    # Every class of every component appears in train
    train_labels = labels[splits["train"]]
    assert set(train_labels[:, 0]) == {3, 20, 100}
    assert set(train_labels[:, 1]) == {73, 80, 90, 100}
    assert set(train_labels[:, 2]) == {0, 1, 2}
    assert set(train_labels[:, 3]) == {90, 100, 115, 130}


def test_connector_deterministic_convert(tmp_path) -> None:
    res1 = convert(tmp_path / "raw1", tmp_path / "out1")
    res2 = convert(tmp_path / "raw2", tmp_path / "out2")

    assert res1 == res2
    assert res1["n_records"] == 2205
    assert res1["n_sensors"] == 17
