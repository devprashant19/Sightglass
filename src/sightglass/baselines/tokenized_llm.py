"""B4: tokenized-text LLM baseline (same backbone as the TSLM, signals written as text).

Needs a GPU LLM fine-tune. An earlier version predicted the majority class with fixed text;
it was removed so it cannot be mistaken for a result.
"""

import numpy as np

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.baselines.gpt4o_plots import BaselineNotRunError
from sightglass.data.models import Cycle


class TokenizedLLMBaseline:
    name: str = "B4_tokenized_llm"

    def __init__(self, target_downsample_pts: int = 60) -> None:
        self.target_downsample_pts = target_downsample_pts

    def format_prompt(self, cycle: Cycle) -> str:
        """Sensors as text numbers with one decimal place (the B4 input format)."""
        lines = ["You are a machine-health diagnostic assistant.", "Diagnose this hydraulic cycle:"]
        for s_name in sorted(cycle.signals):
            sig = cycle.signals[s_name]
            idx = np.linspace(0, len(sig.values) - 1, self.target_downsample_pts).astype(int)
            lines.append(f"{s_name} ({sig.unit}): " + " ".join(f"{v:.1f}" for v in sig.values[idx]))
        lines.append("Question: Diagnose this hydraulic cycle.")
        return "\n".join(lines)

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        raise BaselineNotRunError("needs GPU LLM fine-tune (LoRA on the TSLM backbone); not run.")

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        raise BaselineNotRunError("needs GPU LLM fine-tune; not run.")
