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


N_FIXTURE = 144  # one cycle per label combination


def _fixture_raw(tmp_path):  # type: ignore[no-untyped-def]
    """Small synthetic stand-in files with the real shapes (CI must not download 77 MB)."""
    rng = np.random.default_rng(0)
    n_rec = N_FIXTURE
    raw = tmp_path / "raw"
    raw.mkdir()
    for name, (_s, _u, _r, n, _d) in SENSORS.items():
        np.savetxt(
            raw / f"{name}.txt",
            rng.normal(size=(n_rec, n)).astype("float32"),
            delimiter="	",
            fmt="%.3f",
        )
    lab = np.zeros((n_rec, 5), dtype=int)
    for i in range(n_rec):
        lab[i] = [
            [3, 20, 100][i % 3],
            [73, 80, 90, 100][(i // 3) % 4],
            [0, 1, 2][(i // 12) % 3],
            [90, 100, 115, 130][(i // 36) % 4],
            i % 2,
        ]
    np.savetxt(raw / "profile.txt", lab, delimiter="	", fmt="%d")
    return raw


def test_connector_deterministic_convert(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import hashlib
    import json

    raw = _fixture_raw(tmp_path)
    res1 = convert(raw, tmp_path / "out1", N_FIXTURE)
    res2 = convert(raw, tmp_path / "out2", N_FIXTURE)
    assert res1 == res2
    assert res1["n_records"] == N_FIXTURE and res1["n_sensors"] == 17
    for name in ["PS1.npy", "labels.npy", "splits.json"]:
        h1 = hashlib.sha256((tmp_path / "out1" / name).read_bytes()).hexdigest()
        h2 = hashlib.sha256((tmp_path / "out2" / name).read_bytes()).hexdigest()
        assert h1 == h2
    splits = json.loads((tmp_path / "out1" / "splits.json").read_text())["grouped"]
    assert len(set(splits["train"]) | set(splits["val"]) | set(splits["test"])) == N_FIXTURE
    assert np.load(tmp_path / "out1" / "PS1.npy").shape == (N_FIXTURE, 6000)


def test_convert_rejects_bad_shapes(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import pytest

    raw = _fixture_raw(tmp_path)
    np.savetxt(raw / "TS1.txt", np.zeros((10, 60)), delimiter="	")
    with pytest.raises(ValueError, match="TS1"):
        convert(raw, tmp_path / "out", N_FIXTURE)
