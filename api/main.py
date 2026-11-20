"""Sightglass FastAPI inference service with live verification of physical claims."""

import os
import time
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sightglass.data.loader import load_cycles
from sightglass.data.models import Cycle, Signal
from sightglass.eval.faithfulness import FaithfulnessConfig, parse_claims, verify
from sightglass.export.perturb import PerturbationSpec, apply_perturbation
from sightglass.physics.base import HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.tslm.generate import generate_diagnosis
from sightglass.tslm.model import SightglassModel
from sightglass.utils.runs import get_git_sha

START_TIME = time.time()

app = FastAPI(
    title="Sightglass Machine-Health Inference API",
    description="Physical diagnosis API explaining machine faults with verified numerical evidence.",
    version="0.1.0",
)

allowed_origins = os.environ.get("SIGHTGLASS_ALLOWED_ORIGIN", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model and extractor state
DEVICE = os.environ.get("SIGHTGLASS_DEVICE", "cpu")
CHECKPOINT = os.environ.get("SIGHTGLASS_CHECKPOINT", "")
MODEL = SightglassModel(device=DEVICE, is_smoke=True)
EXTRACTOR = HydraulicExtractor()
FAITH_CFG = FaithfulnessConfig.load("configs/faithfulness.yaml")

# Load reference
ref_path = Path("data/reference/hydraulic_healthy.json")
if ref_path.is_file():
    REF = HealthyReference.load(ref_path)
else:
    dummy_cycles = load_cycles("hydraulic", split="train", total_count=20)
    REF = HealthyReference.fit([EXTRACTOR.extract(c) for c in dummy_cycles])


class SensorInput(BaseModel):
    unit: str
    rate_hz: float
    source: str = "sensor"
    values: list[float] = Field(max_length=6000)


class DiagnoseRequest(BaseModel):
    dataset: Literal["hydraulic", "bearing", "wind"] = "hydraulic"
    signals: dict[str, SensorInput]
    cycle_id: str = "api-custom-001"


class PerturbRequest(BaseModel):
    cycle_id: str
    perturbations: list[dict[str, Any]]


@app.get("/health")
def health() -> dict[str, Any]:
    """Health check endpoint returning model version and uptime."""
    return {
        "status": "healthy",
        "model": "sightglass-llama1b-s0",
        "version": "0.1.0",
        "device": DEVICE,
        "git_sha": get_git_sha(),
        "uptime_s": round(time.time() - START_TIME, 1),
    }


@app.get("/cycles/{cycle_id}")
def get_cycle(cycle_id: str) -> dict[str, Any]:
    """Retrieve pre-computed stored test cycle."""
    cycle_file = Path("web/public/data/hydraulic/cycles") / f"{cycle_id}.json"
    if not cycle_file.is_file():
        cycle_file = Path("web/public/data-mock/hydraulic/cycles") / f"{cycle_id}.json"
    if not cycle_file.is_file():
        raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")

    import json

    with open(cycle_file, encoding="utf-8") as f:
        return json.load(f)


@app.post("/diagnose")
def diagnose(req: DiagnoseRequest) -> dict[str, Any]:
    """Perform fault diagnosis and verify physical evidence against input signals."""
    t0 = time.time()
    sigs: dict[str, Signal] = {}
    import numpy as np

    for s_name, s_in in req.signals.items():
        sigs[s_name] = Signal(
            name=s_name,
            source=s_in.source,
            unit=s_in.unit,
            rate_hz=s_in.rate_hz,
            values=np.array(s_in.values, dtype=np.float32),
        )

    cycle = Cycle(
        id=req.cycle_id,
        signals=sigs,
        labels={},
        meta={"source": "api_live"},
    )

    # 1. Generate diagnosis
    norm_stats = {}
    diag_text = generate_diagnosis(MODEL, cycle, norm_stats)

    # 2. Verify claims at inference time
    parsed_claims, _ = parse_claims(diag_text)
    verdicts = verify(parsed_claims, cycle, EXTRACTOR, REF, FAITH_CFG)

    latency_ms = round((time.time() - t0) * 1000, 1)

    return {
        "cycle_id": req.cycle_id,
        "rationale": diag_text,
        "claims": [
            {
                "sensor": v.claim.sensor,
                "quantity": v.claim.quantity,
                "stated_value": v.claim.value,
                "unit": v.claim.unit,
                "direction": v.claim.direction,
                "pct": v.claim.pct,
                "true_value": round(float(v.true_value), 2) if v.true_value is not None else None,
                "status": v.status,
            }
            for v in verdicts
        ],
        "latency_ms": latency_ms,
    }


@app.post("/diagnose/perturb")
def diagnose_perturb(req: PerturbRequest) -> dict[str, Any]:
    """Apply physical perturbations to a stored cycle and evaluate response."""
    test_cycles = load_cycles("hydraulic", split="test", total_count=50)
    found = [c for c in test_cycles if c.id == req.cycle_id]
    if not found:
        raise HTTPException(status_code=404, detail=f"Cycle {req.cycle_id} not found")

    cycle = found[0]
    for p in req.perturbations:
        spec = PerturbationSpec(
            perturbation_type=p.get("type", "reduce_flow"),
            amount=float(p.get("amount", 0.0)),
        )
        cycle = apply_perturbation(cycle, spec)

    # Re-run diagnosis
    diag_text = generate_diagnosis(MODEL, cycle, {})
    parsed_claims, _ = parse_claims(diag_text)
    verdicts = verify(parsed_claims, cycle, EXTRACTOR, REF, FAITH_CFG)

    return {
        "cycle_id": cycle.id,
        "rationale": diag_text,
        "claims": [v.status for v in verdicts],
    }
