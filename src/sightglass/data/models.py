"""Data structures and loading interface for Sightglass."""

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class Signal:
    """A single sensor time series with native rate and engineering unit."""

    name: str  # e.g., "PS1"
    source: str  # e.g., "pressure", "flow", "temperature", "power", "vibration", "virtual"
    unit: str  # e.g., "bar", "l/min", "°C", "W", "mm/s", "%", "kW"
    rate_hz: float  # e.g., 100.0, 10.0, 1.0
    values: np.ndarray  # float32, shape (n_samples,)


@dataclass(frozen=True)
class Cycle:
    """One operational cycle (or window) with its signals and ground truth labels."""

    id: str  # e.g., "hydraulic-01423"
    signals: dict[str, Signal]
    labels: dict[str, int]  # e.g., {"cooler_condition": 20, ...}
    meta: dict[str, Any]  # e.g., {"cycle_index": 1423, "stable_flag": 0}

# Formatted: clean type annotations and field docstrings
