"""Core physics extraction interfaces and reference standards."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from sightglass.data.models import Cycle


@dataclass(frozen=True)
class Feature:
    """Extracted physical feature with provenance, engineering unit, and temporal window."""

    name: str  # e.g., "FS1.mean", "EPS1_per_FS1"
    sensor: str  # e.g., "FS1", "EPS1/FS1"
    quantity: str  # e.g., "mean flow", "power-to-flow ratio"
    unit: str  # e.g., "l/min", "W·min/l"
    value: float
    window: tuple[float, float] | None = None  # time interval (start_s, end_s) within cycle
    virtual: bool = False  # True for virtual/derived sensors (CE, CP, SE)


class Extractor(Protocol):
    """Protocol for dataset-specific physics extractors."""

    dataset: str

    def feature_names(self) -> list[str]:
        """Return list of all feature names computed by this extractor."""
        ...

    def extract(self, cycle: Cycle) -> dict[str, Feature]:
        """Extract all physical features from a single cycle."""
        ...


HEALTHY_LEVELS: dict[str, int] = {
    "cooler_condition": 100,
    "valve_condition": 100,
    "pump_leakage": 0,
    "accumulator_pressure": 130,
}

# Below this ratio |mean| / std, a percentage of the healthy mean is meaningless (the mean is
# near zero), so deviations are stated in standard deviations instead.
SIGMA_MODE_RATIO = 2.0


@dataclass
class HealthyReference:
    """Per-feature healthy baseline (mean, std) fitted on train cycles only.

    ``basis`` records, per feature, which components had to be healthy for a train cycle to
    count towards that feature's reference (see ``fit_per_component``).
    """

    mean: dict[str, float]
    std: dict[str, float]
    n_cycles: int
    build_hash: str = "v1"
    n_per_feature: dict[str, int] = field(default_factory=dict)
    basis: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def fit(
        cls,
        features_list: list[dict[str, Feature]],
        build_hash: str = "v1",
    ) -> "HealthyReference":
        """Fit mean and std of every feature over the given (healthy) feature sets."""
        if not features_list:
            raise ValueError("Cannot fit HealthyReference on empty features list.")
        means: dict[str, float] = {}
        stds: dict[str, float] = {}
        counts: dict[str, int] = {}
        for name in features_list[0]:
            vals = np.array([f[name].value for f in features_list if name in f], dtype=np.float64)
            if len(vals) == 0:
                continue
            means[name], stds[name] = _mean_std(vals)
            counts[name] = len(vals)
        return cls(
            mean=means,
            std=stds,
            n_cycles=len(features_list),
            build_hash=build_hash,
            n_per_feature=counts,
        )

    @classmethod
    def fit_per_component(
        cls,
        features_list: list[dict[str, Feature]],
        labels_list: list[dict[str, int]],
        links: dict[str, list[dict[str, Any]]],
        stable_list: list[int] | None = None,
        build_hash: str = "v1",
        min_cycles: int = 30,
    ) -> "HealthyReference":
        """Fit a reference per feature from the train cycles that are healthy where it matters.

        A feature linked to components C1..Ck uses the cycles in which all of C1..Ck are at
        their healthy level. A feature linked to no component uses cycles with all four
        components healthy if there are at least ``min_cycles`` of them, otherwise cycles with
        at least three of the four healthy. Only stable cycles (stable_flag 0) are used when
        ``stable_list`` is given and enough of them remain.
        """
        if not features_list:
            raise ValueError("Cannot fit HealthyReference on empty features list.")
        linked: dict[str, list[str]] = {}
        for comp, comp_links in links.items():
            for link in comp_links:
                linked.setdefault(link["feature"], []).append(comp)

        def healthy(lbl: dict[str, int], comps: list[str]) -> bool:
            return all(lbl.get(c) == HEALTHY_LEVELS[c] for c in comps)

        def n_healthy(lbl: dict[str, int]) -> int:
            return sum(lbl.get(c) == HEALTHY_LEVELS[c] for c in HEALTHY_LEVELS)

        stable = stable_list or [0] * len(features_list)
        means: dict[str, float] = {}
        stds: dict[str, float] = {}
        counts: dict[str, int] = {}
        basis: dict[str, list[str]] = {}
        all_four = [i for i, lb in enumerate(labels_list) if n_healthy(lb) == 4]
        for name in features_list[0]:
            comps = linked.get(name)
            if comps:
                idx = [i for i, lb in enumerate(labels_list) if healthy(lb, comps)]
                basis[name] = sorted(set(comps))
            elif len(all_four) >= min_cycles:
                idx = all_four
                basis[name] = sorted(HEALTHY_LEVELS)
            else:
                idx = [i for i, lb in enumerate(labels_list) if n_healthy(lb) >= 3]
                basis[name] = ["any 3 of 4"]
            stable_idx = [i for i in idx if stable[i] == 0]
            if len(stable_idx) >= min_cycles:
                idx = stable_idx
            vals = np.array([features_list[i][name].value for i in idx if name in features_list[i]])
            if len(vals) == 0:
                continue
            means[name], stds[name] = _mean_std(vals)
            counts[name] = len(vals)
        return cls(
            mean=means,
            std=stds,
            n_cycles=len(features_list),
            build_hash=build_hash,
            n_per_feature=counts,
            basis=basis,
        )

    def z(self, f: Feature) -> float:
        """Standard score of a feature against its healthy distribution."""
        m = self.mean.get(f.name, 0.0)
        s = self.std.get(f.name, 1.0)
        return (f.value - m) / s

    def pct_diff(self, f: Feature) -> float:
        """Percentage deviation from the healthy mean: (value - mean) / |mean| * 100."""
        m = self.mean.get(f.name, 0.0)
        if abs(m) < 1e-8:
            return 0.0
        return ((f.value - m) / abs(m)) * 100.0

    def sigma_mode(self, name: str) -> bool:
        """True when the healthy mean is too close to zero for a percentage to mean anything."""
        m = abs(self.mean.get(name, 0.0))
        s = self.std.get(name, 1.0)
        return m < SIGMA_MODE_RATIO * s or m < 1e-6

    def save(self, path: str | Path) -> None:
        """Save healthy reference to JSON."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "mean": self.mean,
            "std": self.std,
            "n_cycles": self.n_cycles,
            "build_hash": self.build_hash,
            "n_per_feature": self.n_per_feature,
            "basis": self.basis,
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "HealthyReference":
        """Load healthy reference from JSON."""
        with open(Path(path), encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            mean=data["mean"],
            std=data["std"],
            n_cycles=data["n_cycles"],
            build_hash=data.get("build_hash", "unknown"),
            n_per_feature=data.get("n_per_feature", {}),
            basis=data.get("basis", {}),
        )


def _mean_std(vals: np.ndarray) -> tuple[float, float]:
    m = float(np.mean(vals))
    s = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    # Guard against a zero spread so z-scores stay finite.
    floor = max(1e-6, 1e-3 * abs(m))
    return m, max(s, floor)
