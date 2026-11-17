"""Rationale generation: canonical evidence clauses computed from the cycle's own signals.

The builder explains a given label (the true label when building training targets, or the
predicted label when the engine explains its own diagnosis). Every number it writes comes from
the physics extractor and the healthy reference, so the faithfulness checker can recompute it.
"""

import zlib
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from sightglass.data.models import Cycle
from sightglass.physics.base import HEALTHY_LEVELS, Feature, HealthyReference
from sightglass.rationales.format import format_evidence_clause
from sightglass.rationales.templates import HydraulicReasoningTemplates as T

COMPONENTS = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]

COMPONENT_NAMES: dict[str, dict[int, str]] = {
    "cooler_condition": {
        3: "close to total failure",
        20: "reduced efficiency",
        100: "full efficiency",
    },
    "valve_condition": {
        100: "optimal",
        90: "small lag",
        80: "severe lag",
        73: "close to total failure",
    },
    "pump_leakage": {0: "no leakage", 1: "weak leakage", 2: "severe leakage"},
    "accumulator_pressure": {
        130: "optimal",
        115: "slightly reduced",
        100: "severely reduced",
        90: "close to total failure",
    },
}

COMPONENT_HEADER = {
    "cooler_condition": "Cooler",
    "valve_condition": "Valve",
    "pump_leakage": "Pump leakage",
    "accumulator_pressure": "Accumulator",
}

SIGMA_BAND = 1.0  # |z| below this is "within the healthy spread"


@dataclass(frozen=True)
class Claim:
    """One verifiable claim inside a rationale."""

    sensor: str
    quantity: str
    value: float
    unit: str
    direction: Literal["above", "below", "within"]
    pct: float | None
    feature: str
    span: tuple[int, int]  # character offsets in the rationale text
    basis: Literal["pct", "sigma"] = "pct"
    sigma: float | None = None
    component: str = ""


@dataclass(frozen=True)
class Paragraph:
    component: str
    label_value: int
    label_name: str
    span: tuple[int, int]


@dataclass(frozen=True)
class Rationale:
    """A diagnosis rationale with its structured claims."""

    cycle_id: str
    component: str  # a component id, or "joint"
    label_value: int
    label_name: str
    text: str
    claims: list[Claim]
    template_id: str
    paragraphs: list[Paragraph] = field(default_factory=list)


def stable_seed(*parts: object) -> int:
    """Deterministic 31-bit seed (Python's hash() is salted per process)."""
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8")) & 0x7FFFFFFF


def _interpretation(component: str, label: int, k: int) -> str:
    if component == "cooler_condition":
        pool = (
            T.COOLER_FAIL if label == 3 else T.COOLER_REDUCED if label == 20 else T.COOLER_OPTIMAL
        )
    elif component == "valve_condition":
        pool = (
            T.VALVE_LAG_SEVERE
            if label in (73, 80)
            else T.VALVE_LAG_SMALL
            if label == 90
            else T.VALVE_OPTIMAL
        )
    elif component == "pump_leakage":
        pool = (
            T.PUMP_LEAK_SEVERE if label == 2 else T.PUMP_LEAK_WEAK if label == 1 else T.PUMP_OPTIMAL
        )
    else:
        pool = (
            T.ACCUMULATOR_SEVERELY_REDUCED
            if label in (90, 100)
            else T.ACCUMULATOR_SLIGHTLY_REDUCED
            if label == 115
            else T.ACCUMULATOR_OPTIMAL
        )
    return pool[k % len(pool)]


def select_evidence(
    features: dict[str, Feature],
    ref: HealthyReference,
    links: list[dict[str, Any]],
    healthy: bool,
    drop_virtual: bool = False,
) -> list[Feature]:
    """Pick the linked features that best show the label's evidence.

    Faulty label: features deviating in the link's direction beyond the healthy spread first
    (physical sensors before virtual ones, then by |z|), up to three. Healthy label: the linked
    features closest to healthy, up to two.
    """
    cands: list[tuple[dict[str, Any], Feature, float]] = []
    for lk in links:
        if not lk.get("kept", True):
            continue
        f = features.get(lk["feature"])
        if f is None or (drop_virtual and f.virtual):
            continue
        cands.append((lk, f, ref.z(f)))
    if healthy:
        cands.sort(key=lambda c: (c[1].virtual, abs(c[2])))
        return [c[1] for c in cands[:2]]

    def matches(c: tuple[dict[str, Any], Feature, float]) -> bool:
        return abs(c[2]) > SIGMA_BAND and (c[2] > 0) == (c[0]["direction"] == "up")

    cands.sort(key=lambda c: (not matches(c), c[1].virtual, -abs(c[2])))
    return [c[1] for c in cands[:3]]


def build_component_rationale(
    cycle: Cycle,
    features: dict[str, Feature],
    ref: HealthyReference,
    links: list[dict[str, Any]],
    component: str,
    rng: np.random.Generator,
    label: int | None = None,
    drop_virtual: bool = False,
) -> Rationale:
    """Explain ``label`` (default: the cycle's true label) for one component."""
    label_val = int(cycle.labels.get(component, 0) if label is None else label)
    label_str = COMPONENT_NAMES[component].get(label_val, str(label_val))
    healthy = label_val == HEALTHY_LEVELS[component]
    chosen = select_evidence(features, ref, links, healthy, drop_virtual)

    k = int(rng.integers(0, 3))
    text = f"{COMPONENT_HEADER[component]}: {label_str}. Evidence: "
    claims: list[Claim] = []
    for i, f in enumerate(chosen):
        pct = ref.pct_diff(f)
        z = ref.z(f)
        sigma = ref.sigma_mode(f.name)
        clause = format_evidence_clause(
            f.sensor, f.quantity, f.value, f.unit, pct, z=z, sigma=sigma, sigma_band=SIGMA_BAND
        )
        if sigma:
            direction: Literal["above", "below", "within"] = (
                "within" if abs(z) < SIGMA_BAND else "above" if z > 0 else "below"
            )
        else:
            direction = "within" if abs(pct) <= 2.0 else "above" if pct > 0 else "below"
        start = len(text)
        text += clause
        claims.append(
            Claim(
                sensor=f.sensor,
                quantity=f.quantity,
                value=f.value,
                unit=f.unit,
                direction=direction,
                pct=None if sigma else float(round(abs(pct))),
                feature=f.name,
                span=(start, len(text)),
                basis="sigma" if sigma else "pct",
                sigma=round(abs(z), 1) if sigma else None,
                component=component,
            )
        )
        if i < len(chosen) - 1:
            text += "; "
    if not chosen:
        text += "no linked sensor feature available"
    text += f". {_interpretation(component, label_val, k)}"

    return Rationale(
        cycle_id=cycle.id,
        component=component,
        label_value=label_val,
        label_name=label_str,
        text=text,
        claims=claims,
        template_id=f"{component}_t{k}",
        paragraphs=[Paragraph(component, label_val, label_str, (0, len(text)))],
    )


def build_joint_rationale(
    cycle: Cycle,
    features: dict[str, Feature],
    ref: HealthyReference,
    all_links: dict[str, list[dict[str, Any]]],
    seed: int = 0,
    labels: dict[str, int] | None = None,
    drop_virtual: bool = False,
) -> Rationale:
    """Four paragraphs (cooler, valve, pump, accumulator) joined by newlines."""
    paragraphs: list[str] = []
    all_claims: list[Claim] = []
    paras: list[Paragraph] = []
    offset = 0
    for comp in COMPONENTS:
        rng = np.random.default_rng(stable_seed(cycle.id, comp, seed))
        lbl = None if labels is None else labels[comp]
        r = build_component_rationale(
            cycle, features, ref, all_links.get(comp, []), comp, rng, lbl, drop_virtual
        )
        for c in r.claims:
            all_claims.append(
                Claim(
                    sensor=c.sensor,
                    quantity=c.quantity,
                    value=c.value,
                    unit=c.unit,
                    direction=c.direction,
                    pct=c.pct,
                    feature=c.feature,
                    span=(c.span[0] + offset, c.span[1] + offset),
                    basis=c.basis,
                    sigma=c.sigma,
                    component=comp,
                )
            )
        paras.append(Paragraph(comp, r.label_value, r.label_name, (offset, offset + len(r.text))))
        paragraphs.append(r.text)
        offset += len(r.text) + 1

    return Rationale(
        cycle_id=cycle.id,
        component="joint",
        label_value=0,
        label_name="joint_condition",
        text="\n".join(paragraphs),
        claims=all_claims,
        template_id="joint_v2",
        paragraphs=paras,
    )
