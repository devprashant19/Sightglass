"""What-if perturbations: change named sensors of a real cycle, nothing else.

Types (the dashboard and API use the same names):
  flow         FS1 and FS2 scaled by (1 + amount/100)          amount in %, e.g. -10
  temperature  TS1..TS4 shifted by amount                       amount in °C, e.g. +4
  ripple       PS1..PS6 + (amount/100)·std·sin(2π·5 Hz·t)       amount in % of each sensor's std
Virtual sensors (CE, CP, SE) are left unchanged; the dashboard says so.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np

from sightglass.data.models import Cycle, Signal

PerturbationType = Literal["flow", "temperature", "ripple"]
_ALIASES = {"reduce_flow": "flow", "raise_temperature": "temperature", "add_ripple": "ripple"}
LIMITS: dict[str, tuple[float, float]] = {
    "flow": (-50.0, 50.0),
    "temperature": (-20.0, 20.0),
    "ripple": (0.0, 300.0),
}

GRID: list[tuple[str, float]] = (
    [("baseline", 0.0)]
    + [("flow", a) for a in (-5.0, -10.0, -15.0, -20.0)]
    + [("temperature", a) for a in (2.0, 4.0, 6.0, 8.0)]
    + [("ripple", a) for a in (25.0, 50.0, 100.0)]
)


@dataclass(frozen=True)
class PerturbationSpec:
    perturbation_type: str
    amount: float

    @property
    def kind(self) -> str:
        return _ALIASES.get(self.perturbation_type, self.perturbation_type)


def label_for(kind: str, amount: float) -> str:
    sign = "+" if amount > 0 else "−" if amount < 0 else "±"
    a = abs(amount)
    if kind == "flow":
        return f"FS1/FS2 {sign}{a:g}%"
    if kind == "temperature":
        return f"TS1–TS4 {sign}{a:g} °C"
    if kind == "ripple":
        return f"PS1–PS6 ripple {sign}{a:g}% of std"
    return "Unchanged cycle"


def validate(kind: str, amount: float) -> None:
    if kind not in LIMITS:
        raise ValueError(f"Unknown perturbation type {kind!r}; use flow, temperature or ripple.")
    lo, hi = LIMITS[kind]
    if not (lo <= amount <= hi) or not np.isfinite(amount):
        raise ValueError(f"{kind} amount {amount} outside [{lo}, {hi}].")


def apply_perturbation(cycle: Cycle, spec: PerturbationSpec) -> Cycle:
    kind = spec.kind
    validate(kind, spec.amount)
    new: dict[str, Signal] = {}
    for name, sig in cycle.signals.items():
        v = sig.values
        if kind == "flow" and name in ("FS1", "FS2"):
            v = (v * (1.0 + spec.amount / 100.0)).astype(np.float32)
        elif kind == "temperature" and name in ("TS1", "TS2", "TS3", "TS4"):
            v = (v + spec.amount).astype(np.float32)
        elif kind == "ripple" and name.startswith("PS"):
            t = np.arange(len(v)) / sig.rate_hz
            amp = (spec.amount / 100.0) * (float(np.std(v)) or 1.0)
            v = (v + amp * np.sin(2 * np.pi * 5.0 * t)).astype(np.float32)
        new[name] = Signal(sig.name, sig.source, sig.unit, sig.rate_hz, v)
    pert = [*cycle.meta.get("perturbations", []), {"type": kind, "amount": spec.amount}]
    return Cycle(cycle.id, new, dict(cycle.labels), {**cycle.meta, "perturbations": pert})


def apply_all(cycle: Cycle, perturbations: list[dict[str, float | str]] | None) -> Cycle:
    for p in perturbations or []:
        kind = str(p.get("type", ""))
        amount = float(p.get("amount", 0.0))
        if kind == "baseline" or amount == 0.0:
            continue
        cycle = apply_perturbation(cycle, PerturbationSpec(kind, amount))
    return cycle
