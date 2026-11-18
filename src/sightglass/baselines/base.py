"""Shared baseline protocol and prediction interfaces."""

from dataclasses import dataclass
from typing import Any, Protocol

from sightglass.data.models import Cycle
from sightglass.utils.config import StrictConfig


@dataclass
class Prediction:
    """Standardized prediction output for any baseline or model."""

    cycle_id: str
    labels: dict[str, int]  # e.g., {"cooler_condition": 20, ...}
    probs: dict[str, dict[int, float]] | None = None  # class probabilities per component
    rationale: str | None = None  # natural language explanation (B4, B5, TSLM)


class BaselineConfig(StrictConfig):
    """Configuration options for baseline evaluation."""

    name: str = "baseline"
    drop_virtual: bool = False
    seed: int = 42
    extra: dict[str, Any] = {}


class Baseline(Protocol):
    """Protocol satisfied by all baseline models."""

    name: str

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        """Fit baseline on train cycles, using val for tuning / early stopping."""
        ...

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        """Generate predictions for a list of cycles."""
        ...
