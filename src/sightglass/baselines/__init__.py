"""Baseline models package for Sightglass."""

from sightglass.baselines.base import Baseline, BaselineConfig, Prediction
from sightglass.baselines.cnn1d import CNN1DBaseline
from sightglass.baselines.gpt4o_plots import GPT4oPlotsBaseline
from sightglass.baselines.lightgbm_baseline import LightGBMBaseline
from sightglass.baselines.majority import MajorityBaseline
from sightglass.baselines.minirocket import MiniRocketBaseline
from sightglass.baselines.tokenized_llm import TokenizedLLMBaseline

__all__ = [
    "Baseline",
    "BaselineConfig",
    "Prediction",
    "MajorityBaseline",
    "LightGBMBaseline",
    "MiniRocketBaseline",
    "CNN1DBaseline",
    "TokenizedLLMBaseline",
    "GPT4oPlotsBaseline",
]
