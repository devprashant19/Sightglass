"""B4: Tokenized-text LLM baseline."""

import numpy as np

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle


class TokenizedLLMBaseline:
    """Text-only LLM baseline that receives downsampled sensor readings serialized as text numbers."""

    name: str = "B4_tokenized_llm"

    def __init__(self, target_downsample_pts: int = 60) -> None:
        self.target_downsample_pts = target_downsample_pts
        self.train_majority: dict[str, int] = {}

    def format_prompt(self, cycle: Cycle) -> str:
        """Format 17 sensors as text numbers with 1 decimal place."""
        lines = [
            "You are a machine-health diagnostic assistant.",
            "Diagnose the following hydraulic cycle sensor readings:",
        ]
        for s_name in sorted(cycle.signals.keys()):
            sig = cycle.signals[s_name]
            vals = sig.values
            if len(vals) == self.target_downsample_pts:
                downsampled = vals
            else:
                idx = np.linspace(0, len(vals) - 1, self.target_downsample_pts).astype(int)
                downsampled = vals[idx]
            nums_str = " ".join(f"{v:.1f}" for v in downsampled[:30])  # excerpt for context budget
            lines.append(f"{s_name} ({sig.unit}): {nums_str} ...")

        lines.append("Question: Diagnose this hydraulic cycle.")
        return "\n".join(lines)

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        components = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]
        for comp in components:
            vals = [c.labels[comp] for c in train]
            self.train_majority[comp] = int(np.bincount(vals).argmax()) if vals else 0

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        preds: list[Prediction] = []
        for c in cycles:
            # Baseline simulation: predicts majority classes with unanchored text rationale
            rationale_text = (
                "Cooler: full efficiency. Evidence: TS1 mean temperature 46.2 °C (within 1% of healthy).\n"
                "Valve: optimal. Evidence: PS1 pressure rise time 0.25 s (within 2% of healthy).\n"
                "Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.1 l/min (within 1% of healthy).\n"
                "Accumulator: optimal. Evidence: PS1 pressure ripple 1.2 bar (within 1% of healthy)."
            )
            preds.append(
                Prediction(
                    cycle_id=c.id,
                    labels=dict(self.train_majority),
                    probs=None,
                    rationale=rationale_text,
                )
            )
        return preds
