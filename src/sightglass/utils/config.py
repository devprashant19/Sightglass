"""Configuration loading and validation with Pydantic."""

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class StrictConfig(BaseModel):
    """Base class for all Sightglass configs forbidding unknown fields."""

    model_config = ConfigDict(extra="forbid")


def load_config(path: str | Path, model_cls: type[T]) -> T:
    """Load a YAML config file into a validated Pydantic model. Unknown keys raise an error."""
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return model_cls.model_validate(data)
