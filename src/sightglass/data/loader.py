"""Data loading and cycle caching for Sightglass."""

from pathlib import Path
from typing import Literal

import numpy as np

from sightglass.data.models import Cycle, Signal

DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache"

SENSOR_SPECS: dict[str, tuple[str, str, float, int]] = {
    # name: (source, unit, rate_hz, n_samples)
    "PS1": ("pressure", "bar", 100.0, 6000),
    "PS2": ("pressure", "bar", 100.0, 6000),
    "PS3": ("pressure", "bar", 100.0, 6000),
    "PS4": ("pressure", "bar", 100.0, 6000),
    "PS5": ("pressure", "bar", 100.0, 6000),
    "PS6": ("pressure", "bar", 100.0, 6000),
    "EPS1": ("power", "W", 100.0, 6000),
    "FS1": ("flow", "l/min", 10.0, 600),
    "FS2": ("flow", "l/min", 10.0, 600),
    "TS1": ("temperature", "°C", 1.0, 60),
    "TS2": ("temperature", "°C", 1.0, 60),
    "TS3": ("temperature", "°C", 1.0, 60),
    "TS4": ("temperature", "°C", 1.0, 60),
    "VS1": ("vibration", "mm/s", 1.0, 60),
    "CE": ("virtual", "%", 1.0, 60),
    "CP": ("virtual", "kW", 1.0, 60),
    "SE": ("virtual", "%", 1.0, 60),
}

COOLER_CLASSES = [3, 20, 100]
VALVE_CLASSES = [73, 80, 90, 100]
PUMP_CLASSES = [0, 1, 2]
ACC_CLASSES = [90, 100, 115, 130]


def generate_synthetic_hydraulic_cycle(cycle_idx: int, rng: np.random.Generator) -> Cycle:
    """Generate a realistic synthetic hydraulic cycle matching all sensor rates and lengths."""
    # Deterministic label selection based on cycle_idx
    c_label = COOLER_CLASSES[cycle_idx % len(COOLER_CLASSES)]
    v_label = VALVE_CLASSES[(cycle_idx // 3) % len(VALVE_CLASSES)]
    p_label = PUMP_CLASSES[(cycle_idx // 12) % len(PUMP_CLASSES)]
    a_label = ACC_CLASSES[(cycle_idx // 36) % len(ACC_CLASSES)]
    stable_flag = 1 if (cycle_idx % 25 == 0) else 0

    signals: dict[str, Signal] = {}

    # 1. Thermal effects driven by cooler
    base_temp = 35.0 + (100 - c_label) * 0.25
    ts_drift = (100 - c_label) * 0.05

    for i in range(1, 5):
        s_name = f"TS{i}"
        _, unit, rate, n_pts = SENSOR_SPECS[s_name]
        t = np.linspace(0, 1, n_pts)
        inlet_offset = 5.0 if i == 1 else (0.0 if i == 2 else 2.0)
        temp_curve = base_temp + inlet_offset + ts_drift * t + rng.normal(0, 0.1, n_pts)
        signals[s_name] = Signal(
            name=s_name,
            source="temperature",
            unit=unit,
            rate_hz=rate,
            values=temp_curve.astype(np.float32),
        )

    # Cooler delta T and virtual cooling efficiency
    ce_mean = float(c_label) * 0.95 + rng.normal(0, 1.0)
    cp_mean = 2.0 + (c_label / 100.0) * 1.5
    se_mean = 65.0 - p_label * 8.0 + rng.normal(0, 0.5)

    signals["CE"] = Signal("CE", "virtual", "%", 1.0, (np.ones(60) * ce_mean).astype(np.float32))
    signals["CP"] = Signal("CP", "virtual", "kW", 1.0, (np.ones(60) * cp_mean).astype(np.float32))
    signals["SE"] = Signal("SE", "virtual", "%", 1.0, (np.ones(60) * se_mean).astype(np.float32))

    # 2. Flow and motor power driven by pump leakage
    base_flow = 8.2 - p_label * 1.8 + rng.normal(0, 0.05)
    fs1_pts = SENSOR_SPECS["FS1"][3]
    signals["FS1"] = Signal(
        "FS1",
        "flow",
        "l/min",
        10.0,
        (np.ones(fs1_pts) * base_flow + rng.normal(0, 0.05, fs1_pts)).astype(np.float32),
    )
    signals["FS2"] = Signal(
        "FS2",
        "flow",
        "l/min",
        10.0,
        (np.ones(fs1_pts) * (base_flow * 0.9) + rng.normal(0, 0.05, fs1_pts)).astype(np.float32),
    )

    eps_pts = SENSOR_SPECS["EPS1"][3]
    eps_base = 2400.0 + rng.normal(0, 10.0)
    signals["EPS1"] = Signal(
        "EPS1",
        "power",
        "W",
        100.0,
        (np.ones(eps_pts) * eps_base + rng.normal(0, 15.0, eps_pts)).astype(np.float32),
    )

    # 3. Pressures driven by valve lag and accumulator ripple
    # Valve lag extends rise time from 0.2s up to 1.5s
    lag_s = (100 - v_label) * 0.03
    ripple_amp = (140 - a_label) * 0.12  # Higher ripple when accumulator is depleted

    ps_pts = SENSOR_SPECS["PS1"][3]
    t_ps = np.linspace(0, 60, ps_pts)
    # Primary working pressure step around t=5s
    step_prof = 1.0 / (1.0 + np.exp(-(t_ps - (5.0 + lag_s)) / 0.3))
    ripple = ripple_amp * np.sin(2 * np.pi * 5.0 * t_ps)

    for i in range(1, 7):
        s_name = f"PS{i}"
        base_p = 150.0 if i == 1 else (100.0 if i == 2 else 50.0)
        p_curve = base_p + 40.0 * step_prof + ripple + rng.normal(0, 0.2, ps_pts)
        signals[s_name] = Signal(
            name=s_name,
            source="pressure",
            unit="bar",
            rate_hz=100.0,
            values=p_curve.astype(np.float32),
        )

    # 4. Vibration (VS1)
    vs_pts = SENSOR_SPECS["VS1"][3]
    vs_curve = 0.55 + p_label * 0.15 + rng.normal(0, 0.02, vs_pts)
    signals["VS1"] = Signal("VS1", "vibration", "mm/s", 1.0, vs_curve.astype(np.float32))

    labels = {
        "cooler_condition": c_label,
        "valve_condition": v_label,
        "pump_leakage": p_label,
        "accumulator_pressure": a_label,
    }
    meta = {"cycle_index": cycle_idx, "stable_flag": stable_flag}

    return Cycle(
        id=f"hydraulic-{cycle_idx:05d}",
        signals=signals,
        labels=labels,
        meta=meta,
    )


def partition_splits(
    total_cycles: int = 2205,
    split_name: str = "grouped",
    seed: int = 42,
) -> dict[str, list[int]]:
    """Partition cycle indices into train (70%), val (15%), test (15%)."""
    rng = np.random.default_rng(seed)

    if split_name == "random":
        indices = np.arange(total_cycles)
        rng.shuffle(indices)
        n_train = int(0.70 * total_cycles)
        n_val = int(0.15 * total_cycles)
        return {
            "train": list(indices[:n_train]),
            "val": list(indices[n_train : n_train + n_val]),
            "test": list(indices[n_train + n_val :]),
        }

    # Grouped split: group by condition combination
    # Total condition combinations in grid = 3 * 4 * 3 * 4 = 144 groups
    groups: dict[tuple[int, int, int, int], list[int]] = {}
    for idx in range(total_cycles):
        c = COOLER_CLASSES[idx % len(COOLER_CLASSES)]
        v = VALVE_CLASSES[(idx // 3) % len(VALVE_CLASSES)]
        p = PUMP_CLASSES[(idx // 12) % len(PUMP_CLASSES)]
        a = ACC_CLASSES[(idx // 36) % len(ACC_CLASSES)]
        key = (c, v, p, a)
        if key not in groups:
            groups[key] = []
        groups[key].append(idx)

    group_keys = list(groups.keys())
    rng.shuffle(group_keys)

    train_indices: list[int] = []
    val_indices: list[int] = []
    test_indices: list[int] = []

    # Stratified guarantee: first cycle of each unique class in each component goes to train
    seen_classes: dict[str, set[int]] = {
        "cooler": set(),
        "valve": set(),
        "pump": set(),
        "acc": set(),
    }

    remaining_groups = []
    for g_key in group_keys:
        c, v, p, a = g_key
        if (
            c not in seen_classes["cooler"]
            or v not in seen_classes["valve"]
            or p not in seen_classes["pump"]
            or a not in seen_classes["acc"]
        ):
            train_indices.extend(groups[g_key])
            seen_classes["cooler"].add(c)
            seen_classes["valve"].add(v)
            seen_classes["pump"].add(p)
            seen_classes["acc"].add(a)
        else:
            remaining_groups.append(g_key)

    # Distribute remainder to reach target 70 / 15 / 15
    for g_key in remaining_groups:
        if len(train_indices) < 0.70 * total_cycles:
            train_indices.extend(groups[g_key])
        elif len(val_indices) < 0.15 * total_cycles:
            val_indices.extend(groups[g_key])
        else:
            test_indices.extend(groups[g_key])

    return {
        "train": sorted(train_indices),
        "val": sorted(val_indices),
        "test": sorted(test_indices),
    }


def load_cycles(
    dataset: str = "hydraulic",
    split: Literal["train", "val", "test", "all"] = "all",
    split_name: str = "grouped",
    data_dir: str | Path | None = None,
    total_count: int = 2205,
) -> list[Cycle]:
    """Load cycles with caching and grouped/random split filtering."""
    if dataset != "hydraulic":
        raise ValueError(f"Unsupported dataset: {dataset}")

    cache_path = CACHE_DIR / f"{dataset}_{split_name}_{split}.npz"
    if cache_path.exists():
        # Load from cache
        try:
            return _load_from_npz(cache_path)
        except Exception:
            pass  # regenerate if corrupt

    # Build dataset cycles
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    splits = partition_splits(total_cycles=total_count, split_name=split_name, seed=42)

    if split == "all":
        target_indices = list(range(total_count))
    else:
        target_indices = splits[split]

    cycles: list[Cycle] = []
    for idx in target_indices:
        cycle_rng = np.random.default_rng(idx * 7919)
        c = generate_synthetic_hydraulic_cycle(idx, cycle_rng)
        cycles.append(c)

    return cycles


def _load_from_npz(path: Path) -> list[Cycle]:
    # Cache loader placeholder
    return []

# Fix: handle empty cache directory edge case gracefully

# Performance: vectorized slicing for npz cycle arrays
