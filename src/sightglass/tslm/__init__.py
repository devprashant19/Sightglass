"""Sightglass Time-Series Language Model (TSLM) module."""

from sightglass.tslm.generate import generate_diagnosis
from sightglass.tslm.model import SightglassModel
from sightglass.tslm.prompt import (
    build_prompt_and_series,
    compute_normalisation_statistics,
    downsample_signals,
)
from sightglass.tslm.train import train

__all__ = [
    "SightglassModel",
    "downsample_signals",
    "compute_normalisation_statistics",
    "build_prompt_and_series",
    "generate_diagnosis",
    "train",
]
