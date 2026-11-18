"""B5: GPT-4o zero-shot on multi-sensor plots.

Not implemented yet: it needs plot rendering, an OpenAI API call per cycle and response parsing.
An earlier version returned fixed text; it was removed so no fake GPT-4o numbers can appear.
"""

import os

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle


class BaselineNotRunError(NotImplementedError):
    """Raised by baselines that cannot run in this environment; the reason is reported."""


class GPT4oPlotsBaseline:
    name: str = "B5_gpt4o"

    def __init__(self, sample_size: int = 200):
        self.sample_size = sample_size

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise BaselineNotRunError(
                "OPENAI_API_KEY is not set, so the GPT-4o baseline was not run."
            )
        raise BaselineNotRunError(
            "The GPT-4o plot baseline (render, call, parse) is not implemented yet."
        )

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        raise BaselineNotRunError("GPT-4o baseline was not run.")
