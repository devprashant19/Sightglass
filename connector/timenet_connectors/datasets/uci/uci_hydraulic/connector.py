"""TimeNet Dataset Connector for UCI Hydraulic Condition Monitoring (#447)."""

import hashlib
from pathlib import Path
from typing import Any

import numpy as np

UCI_URL = (
    "https://archive.ics.uci.edu/static/public/447/condition+monitoring+of+hydraulic+systems.zip"
)
# Upstream SHA-256 for integrity verification
UCI_SHA256 = (
    "24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2"  # measured 2026-11-22
)

TOTAL_CYCLES = 2205

SENSORS: dict[str, tuple[str, str, float, int, str]] = {
    # name: (source, unit, rate_hz, n_samples, description)
    "PS1": ("pressure", "bar", 100.0, 6000, "Pressure sensor 1 (working line)"),
    "PS2": ("pressure", "bar", 100.0, 6000, "Pressure sensor 2 (return line)"),
    "PS3": ("pressure", "bar", 100.0, 6000, "Pressure sensor 3 (feed pressure)"),
    "PS4": ("pressure", "bar", 100.0, 6000, "Pressure sensor 4 (filter pressure)"),
    "PS5": ("pressure", "bar", 100.0, 6000, "Pressure sensor 5 (accumulator pressure)"),
    "PS6": ("pressure", "bar", 100.0, 6000, "Pressure sensor 6 (cooler inlet pressure)"),
    "EPS1": ("power", "W", 100.0, 6000, "Motor power sensor (electrical drive)"),
    "FS1": ("flow", "l/min", 10.0, 600, "Volume flow sensor 1 (main pump)"),
    "FS2": ("flow", "l/min", 10.0, 600, "Volume flow sensor 2 (cooling circuit)"),
    "TS1": ("temperature", "°C", 1.0, 60, "Temperature sensor 1 (cooler inlet)"),
    "TS2": ("temperature", "°C", 1.0, 60, "Temperature sensor 2 (cooler outlet)"),
    "TS3": ("temperature", "°C", 1.0, 60, "Temperature sensor 3 (oil tank)"),
    "TS4": ("temperature", "°C", 1.0, 60, "Temperature sensor 4 (pump housing)"),
    "VS1": ("vibration", "mm/s", 1.0, 60, "Vibration sensor 1 (main pump)"),
    "CE": ("virtual", "%", 1.0, 60, "Cooling efficiency (virtual calculated)"),
    "CP": ("virtual", "kW", 1.0, 60, "Cooling power (virtual calculated)"),
    "SE": ("virtual", "%", 1.0, 60, "System efficiency factor (virtual calculated)"),
}

LABELS = {
    "cooler_condition": {
        3: "close to total failure",
        20: "reduced efficiency",
        100: "full efficiency",
    },
    "valve_condition": {
        100: "optimal",
        90: "small lag",
        80: "severe lag",
        73: "close to total failure",
    },
    "pump_leakage": {
        0: "no leakage",
        1: "weak leakage",
        2: "severe leakage",
    },
    "accumulator_pressure": {
        130: "optimal",
        115: "slightly reduced",
        100: "severely reduced",
        90: "close to total failure",
    },
    "stable_flag": {
        0: "conditions were stable",
        1: "conditions might not have reached stability",
    },
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def download(raw_dir: str | Path, timeout_s: float = 300.0) -> Path:
    """Download the UCI archive into raw_dir, verify its SHA-256, and unzip it.

    Idempotent: an existing archive with the pinned checksum is reused. Returns the raw dir.
    """
    import urllib.request
    import zipfile

    dest_dir = Path(raw_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / "hydraulic.zip"

    if not (zip_path.is_file() and _sha256(zip_path) == UCI_SHA256):
        tmp = zip_path.with_suffix(".part")
        req = urllib.request.Request(UCI_URL, headers={"User-Agent": "sightglass-connector"})
        with urllib.request.urlopen(req, timeout=timeout_s) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        got = _sha256(tmp)
        if got != UCI_SHA256:
            tmp.unlink(missing_ok=True)
            raise ValueError(f"Checksum mismatch for {UCI_URL}: expected {UCI_SHA256}, got {got}")
        tmp.replace(zip_path)

    if not (dest_dir / "profile.txt").is_file():
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(dest_dir)
    return dest_dir


def compute_grouped_splits(labels_array: np.ndarray, seed: int = 42) -> dict[str, list[int]]:
    """Grouped split on the 4-label tuple ensuring class representation in train."""
    rng = np.random.default_rng(seed)
    n_rows = len(labels_array)

    groups: dict[tuple[int, ...], list[int]] = {}
    for i in range(n_rows):
        key = tuple(int(x) for x in labels_array[i, :4])
        if key not in groups:
            groups[key] = []
        groups[key].append(i)

    group_keys = list(groups.keys())
    rng.shuffle(group_keys)

    train_idx: list[int] = []
    val_idx: list[int] = []
    test_idx: list[int] = []

    seen_cooler = set()
    seen_valve = set()
    seen_pump = set()
    seen_acc = set()

    unassigned: list[tuple[int, ...]] = []

    for k in group_keys:
        c, v, p, a = k
        if c not in seen_cooler or v not in seen_valve or p not in seen_pump or a not in seen_acc:
            train_idx.extend(groups[k])
            seen_cooler.add(c)
            seen_valve.add(v)
            seen_pump.add(p)
            seen_acc.add(a)
        else:
            unassigned.append(k)

    target_train = int(0.70 * n_rows)
    target_val = int(0.15 * n_rows)

    for k in unassigned:
        if len(train_idx) < target_train:
            train_idx.extend(groups[k])
        elif len(val_idx) < target_val:
            val_idx.extend(groups[k])
        else:
            test_idx.extend(groups[k])

    return {
        "train": sorted(train_idx),
        "val": sorted(val_idx),
        "test": sorted(test_idx),
    }


def compute_random_splits(n_rows: int, seed: int = 0) -> dict[str, list[int]]:
    """Random 70/15/15 split, kept only to measure how much random splits inflate scores."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n_rows)
    n_train, n_val = int(0.70 * n_rows), int(0.15 * n_rows)
    return {
        "train": sorted(int(i) for i in idx[:n_train]),
        "val": sorted(int(i) for i in idx[n_train : n_train + n_val]),
        "test": sorted(int(i) for i in idx[n_train + n_val :]),
    }


def read_raw(
    raw_dir: str | Path, n_records: int = TOTAL_CYCLES
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Read the 17 tab-separated sensor tables and profile.txt; validate every shape."""
    import pandas as pd

    raw = Path(raw_dir)
    arrays: dict[str, np.ndarray] = {}
    for name, (_src, _unit, _rate, n_samples, _desc) in SENSORS.items():
        path = raw / f"{name}.txt"
        if not path.is_file():
            raise FileNotFoundError(f"Missing sensor file {path}")
        arr = pd.read_csv(path, sep="	", header=None, dtype="float32").to_numpy()
        if arr.shape != (n_records, n_samples):
            raise ValueError(f"{name}.txt has shape {arr.shape}, expected {(n_records, n_samples)}")
        if not np.isfinite(arr).all():
            raise ValueError(f"{name}.txt contains non-finite values")
        arrays[name] = np.ascontiguousarray(arr, dtype=np.float32)
    labels = pd.read_csv(raw / "profile.txt", sep="	", header=None, dtype="int32").to_numpy()
    if labels.shape != (n_records, 5):
        raise ValueError(f"profile.txt has shape {labels.shape}, expected {(n_records, 5)}")
    keys = [
        "cooler_condition",
        "valve_condition",
        "pump_leakage",
        "accumulator_pressure",
        "stable_flag",
    ]
    for col, key in enumerate(keys):
        bad = set(np.unique(labels[:, col]).tolist()) - set(LABELS[key])
        if bad:
            raise ValueError(f"profile.txt column {col + 1} has unexpected values {sorted(bad)}")
    return arrays, labels


def convert(
    raw_dir: str | Path, out_dir: str | Path, n_records: int = TOTAL_CYCLES
) -> dict[str, Any]:
    """Convert the raw tables into a Sightglass build: one float32 .npy per sensor,
    labels.npy, splits.json and manifest.json. Deterministic for the same input."""
    import json

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    arrays, labels = read_raw(raw_dir, n_records)
    for name, arr in arrays.items():
        np.save(out_path / f"{name}.npy", arr)
    np.save(out_path / "labels.npy", labels)

    splits = {"grouped": compute_grouped_splits(labels), "random": compute_random_splits(n_records)}
    with open(out_path / "splits.json", "w", encoding="utf-8") as f:
        json.dump(splits, f)

    zip_path = Path(raw_dir) / "hydraulic.zip"
    summary: dict[str, Any] = {
        "dataset": "uci_hydraulic",
        "synthetic": False,
        "source_url": UCI_URL,
        "sha256": _sha256(zip_path) if zip_path.is_file() else None,
        "n_records": n_records,
        "n_sensors": len(SENSORS),
        "sensors": {
            k: {
                "source": v[0],
                "unit": v[1],
                "rate_hz": v[2],
                "n_samples": v[3],
                "description": v[4],
            }
            for k, v in SENSORS.items()
        },
        "splits": {name: {k: len(v) for k, v in sp.items()} for name, sp in splits.items()},
    }
    with open(out_path / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


class HydraulicConnector:
    """TimeNet BaseConnector implementation."""

    name = "uci_hydraulic"

    download = staticmethod(download)
    convert = staticmethod(convert)

    def metadata(self) -> dict[str, Any]:
        return {
            "name": "UCI Hydraulic System Condition Monitoring",
            "license": "CC BY 4.0",
            "url": UCI_URL,
        }


CONNECTOR = HydraulicConnector()
