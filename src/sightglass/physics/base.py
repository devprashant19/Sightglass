"""Core physics extraction interfaces and reference standards."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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


@dataclass
class HealthyReference:
    """Baseline reference distribution computed strictly from healthy training cycles."""

    mean: dict[str, float]
    std: dict[str, float]
    n_cycles: int
    build_hash: str = "v1"

    @classmethod
    def fit(
        cls,
        features_list: list[dict[str, Feature]],
        build_hash: str = "v1",
    ) -> "HealthyReference":
        """Fit baseline mean and std across healthy training feature sets."""
        if not features_list:
            raise ValueError("Cannot fit HealthyReference on empty features list.")

        feature_names = list(features_list[0].keys())
        means: dict[str, float] = {}
        stds: dict[str, float] = {}

        for name in feature_names:
            vals = np.array([f[name].value for f in features_list if name in f], dtype=np.float64)
            if len(vals) == 0:
                continue
            m = float(np.mean(vals))
            s = float(np.std(vals, ddof=1)) if len(vals) > 1 else 1e-6
            means[name] = m
            stds[name] = s if s > 1e-8 else 1e-6

        return cls(mean=means, std=stds, n_cycles=len(features_list), build_hash=build_hash)

    def z(self, f: Feature) -> float:
        """Compute standard z-score against healthy distribution."""
        m = self.mean.get(f.name, 0.0)
        s = self.std.get(f.name, 1.0)
        return (f.value - m) / s

    def pct_diff(self, f: Feature) -> float:
        """Percentage deviation from healthy baseline: (value - mean) / |mean| * 100."""
        m = self.mean.get(f.name, 0.0)
        if abs(m) < 1e-8:
            return 0.0
        return ((f.value - m) / abs(m)) * 100.0

    def save(self, path: str | Path) -> None:
        """Save healthy reference to JSON."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "mean": self.mean,
            "std": self.std,
            "n_cycles": self.n_cycles,
            "build_hash": self.build_hash,
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "HealthyReference":
        """Load healthy reference from JSON."""
        p = Path(path)
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            mean=data["mean"],
            std=data["std"],
            n_cycles=data["n_cycles"],
            build_hash=data.get("build_hash", "unknown"),
        )
