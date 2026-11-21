"""B0: Majority class baseline."""

from collections import Counter

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle


class MajorityBaseline:
    """Predicts the empirical mode (most common class) from the training split."""

    name: str = "B0_majority"

    def __init__(self) -> None:
        self.majority_classes: dict[str, int] = {}

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        components = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]
        for comp in components:
            counts = Counter(c.labels[comp] for c in train if comp in c.labels)
            if counts:
                self.majority_classes[comp] = counts.most_common(1)[0][0]
            else:
                self.majority_classes[comp] = 0

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        preds: list[Prediction] = []
        for c in cycles:
            preds.append(
                Prediction(
                    cycle_id=c.id,
                    labels=dict(self.majority_classes),
                    probs=None,
                    rationale=None,
                )
            )
        return preds
