"""Sightglass inference API: the real engine, live, on real UCI #447 cycles.

  GET  /api/health          model, version, data source, git SHA, number of cycles
  GET  /api/cycles/{id}     a stored test cycle in the dashboard's cycle-file shape
  POST /api/diagnose        {cycle_id, perturbations:[{type, amount}]} -> fresh diagnosis

The engine (data/models/engine.pkl, from scripts/train_engine.py) and the dataset build are
loaded once at start-up. Every answer is recomputed and its claims verified on the request.
"""

import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from sightglass.data.loader import build_available, load_cycle, load_manifest, load_splits
from sightglass.engine import ENGINE_PATH, MODEL_NAME, Engine
from sightglass.export.perturb import LIMITS
from sightglass.utils.runs import get_git_sha

VERSION = "1.1.0"
START = time.time()
WEB_DATA = Path(os.environ.get("SIGHTGLASS_WEB_DATA", "web/public/data"))

app = FastAPI(
    title="Sightglass API",
    version=VERSION,
    description="Machine-health diagnoses with every number checked against the signal.",
)
origins = os.environ.get(
    "SIGHTGLASS_ALLOWED_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class State:
    engine: Engine | None = None
    error: str | None = None
    test_ids: set[str] = set()
    manifest: dict[str, Any] = {}


def _init() -> None:
    try:
        if not build_available():
            raise FileNotFoundError("dataset build missing (run `make data`)")
        if not ENGINE_PATH.is_file():
            raise FileNotFoundError(f"{ENGINE_PATH} missing (run scripts/train_engine.py)")
        State.engine = Engine.load(ENGINE_PATH)
        State.manifest = load_manifest()
        State.test_ids = {f"hydraulic-{i:05d}" for i in load_splits()["test"]}
    except Exception as e:  # reported by /api/health; endpoints answer 503
        State.error = str(e)


_init()

# ---------- rate limit: 30 requests / minute / client ----------
_HITS: dict[str, deque[float]] = defaultdict(deque)
RATE = int(os.environ.get("SIGHTGLASS_RATE_PER_MIN", "30"))


def _limit(request: Request) -> None:
    key = request.client.host if request.client else "anon"
    q = _HITS[key]
    now = time.time()
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= RATE:
        raise HTTPException(status_code=429, detail="Too many requests; try again in a minute.")
    q.append(now)


def _engine() -> Engine:
    if State.engine is None:
        raise HTTPException(status_code=503, detail=f"Engine unavailable: {State.error}")
    return State.engine


def _index(cycle_id: str) -> int:
    if cycle_id not in State.test_ids:
        raise HTTPException(status_code=404, detail=f"{cycle_id} is not a test cycle.")
    return int(cycle_id.split("-")[1])


class Perturbation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["baseline", "flow", "temperature", "ripple"]
    amount: float = Field(ge=-50, le=300)


class DiagnoseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cycle_id: str = Field(pattern=r"^hydraulic-\d{5}$")
    perturbations: list[Perturbation] = Field(default_factory=list, max_length=3)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok" if State.engine else "unavailable",
        "error": State.error,
        "model": MODEL_NAME,
        "version": VERSION,
        "data_source": "UCI #447 hydraulic test rig (real data)" if State.engine else None,
        "synthetic": bool(State.engine and State.engine.synthetic),
        "sha256": State.manifest.get("sha256"),
        "git_sha": get_git_sha(),
        "cycles": len(State.test_ids),
        "uptime_s": round(time.time() - START, 1),
        "perturbation_limits": LIMITS,
    }


@app.get("/api/cycles/{cycle_id}")
def get_cycle(cycle_id: str, request: Request) -> dict[str, Any]:
    _limit(request)
    _engine()
    _index(cycle_id)
    p = WEB_DATA / "hydraulic" / "cycles" / f"{cycle_id}.json"
    if not p.is_file():
        raise HTTPException(
            status_code=404, detail="Cycle not exported; run scripts/export_site_data.py"
        )
    import json

    data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return data


@app.post("/api/diagnose")
def diagnose(req: DiagnoseRequest, request: Request) -> dict[str, Any]:
    _limit(request)
    engine = _engine()
    idx = _index(req.cycle_id)
    pert = []
    for p in req.perturbations:
        if p.type == "baseline":
            continue
        lo, hi = LIMITS[p.type]
        if not lo <= p.amount <= hi:
            raise HTTPException(status_code=422, detail=f"{p.type} amount must be in [{lo}, {hi}]")
        pert.append({"type": p.type, "amount": p.amount})
    cycle = load_cycle(idx)
    d = engine.diagnose(cycle, pert)
    d.pop("_features", None)
    return {"cycle_id": req.cycle_id, "true_labels": dict(cycle.labels), **d}
