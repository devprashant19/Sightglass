"""Pydantic schemas and JSON Schema generation for static export and web dashboard."""

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class ManifestSchema(BaseModel):
    schema_version: int = 1
    generated_at: str
    git_sha: str
    datasets: list[str]
    models: list[str]


class StatedClaim(BaseModel):
    value: float
    unit: str
    direction: Literal["above", "below", "within"]
    pct: float


class TrueFeature(BaseModel):
    value: float
    pct: float


class ClaimExport(BaseModel):
    span: list[int] = Field(description="Character offsets [start, end] in rationale text")
    component: str
    sensor: str
    feature: str
    stated: StatedClaim
    true: TrueFeature
    status: Literal[
        "verified",
        "wrong_value",
        "wrong_direction",
        "unknown_sensor",
        "unknown_quantity",
        "unit_mismatch",
    ]
    window: list[float] = Field(description="Temporal window [start_s, end_s]")


class PredictionExport(BaseModel):
    model: str
    labels: dict[str, dict[str, Any]]
    rationale: str
    claims: list[ClaimExport]


class SignalDisplay(BaseModel):
    unit: str
    rate_hz: float
    source: str
    values: list[float]


class CycleExport(BaseModel):
    schema_version: int = 1
    id: str
    dataset: str
    meta: dict[str, Any]
    true_labels: dict[str, dict[str, Any]]
    signals: dict[str, SignalDisplay]
    prediction: PredictionExport
    baselines: dict[str, dict[str, Any]] = {}
    features: dict[str, dict[str, Any]] = {}


def generate_json_schemas(out_dir: str | Path = "web/src/schema") -> None:
    """Generate JSON schema files from Pydantic models."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    schemas = {
        "manifest.schema.json": ManifestSchema.model_json_schema(),
        "cycle.schema.json": CycleExport.model_json_schema(),
    }

    for filename, s_dict in schemas.items():
        with open(out_path / filename, "w", encoding="utf-8") as f:
            json.dump(s_dict, f, indent=2)


if __name__ == "__main__":
    generate_json_schemas()
