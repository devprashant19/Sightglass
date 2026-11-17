"""Rationale generation with canonical evidence clauses and physics interpretation."""

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from sightglass.data.models import Cycle
from sightglass.physics.base import Feature, HealthyReference
from sightglass.rationales.format import format_evidence_clause
from sightglass.rationales.templates import HydraulicReasoningTemplates

COMPONENT_NAMES = {
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


@dataclass(frozen=True)
class Claim:
    """A single verifiable physical claim within a rationale."""

    sensor: str
    quantity: str
    value: float
    unit: str
    direction: Literal["above", "below", "within"]
    pct: float
    feature: str  # e.g., "TS1.mean"
    span: tuple[int, int]  # (start_char, end_char) in rationale text


@dataclass(frozen=True)
class Rationale:
    """Full diagnosis rationale with structured, verifiable evidence claims."""

    cycle_id: str
    component: str  # specific component or "joint"
    label_value: int
    label_name: str
    text: str
    claims: list[Claim]
    template_id: str


def build_component_rationale(
    cycle: Cycle,
    features: dict[str, Feature],
    ref: HealthyReference,
    links: list[dict[str, Any]],
    component: str,
    rng: np.random.Generator,
) -> Rationale:
    """Construct a diagnosis rationale for a single component with verifiable evidence clauses."""
    comp_header = COMPONENT_HEADER[component]
    label_val = cycle.labels.get(component, 0)
    label_str = COMPONENT_NAMES[component].get(label_val, str(label_val))

    # Rank linked features by absolute z-score deviation from healthy
    ranked_links = []
    for link in links:
        feat_name = link["feature"]
        if feat_name in features:
            f = features[feat_name]
            z_score = abs(ref.z(f))
            ranked_links.append((z_score, link, f))

    ranked_links.sort(key=lambda x: x[0], reverse=True)
    top_features = [item[2] for item in ranked_links[:3]]

    # Format evidence clauses
    clause_texts: list[str] = []
    claims_meta: list[dict[str, Any]] = []

    for f in top_features:
        pct_diff = ref.pct_diff(f)
        abs_pct = abs(pct_diff)
        if abs_pct <= 2.0:
            direction: Literal["above", "below", "within"] = "within"
        elif pct_diff > 0:
            direction = "above"
        else:
            direction = "below"

        clause_str = format_evidence_clause(f.sensor, f.quantity, f.value, f.unit, pct_diff)
        clause_texts.append(clause_str)
        claims_meta.append(
            {
                "sensor": f.sensor,
                "quantity": f.quantity,
                "value": f.value,
                "unit": f.unit,
                "direction": direction,
                "pct": float(round(abs_pct)),
                "feature": f.name,
                "clause_str": clause_str,
            }
        )

    # Select varied physics interpretation
    template_idx = int(rng.integers(0, 3))
    if component == "cooler_condition":
        if label_val == 3:
            interp = HydraulicReasoningTemplates.COOLER_FAIL[template_idx]
        elif label_val == 20:
            interp = HydraulicReasoningTemplates.COOLER_REDUCED[template_idx]
        else:
            interp = HydraulicReasoningTemplates.COOLER_OPTIMAL[template_idx]
    elif component == "valve_condition":
        if label_val in (73, 80):
            interp = HydraulicReasoningTemplates.VALVE_LAG_SEVERE[template_idx]
        elif label_val == 90:
            interp = HydraulicReasoningTemplates.VALVE_LAG_SMALL[template_idx]
        else:
            interp = HydraulicReasoningTemplates.VALVE_OPTIMAL[template_idx]
    elif component == "pump_leakage":
        if label_val == 2:
            interp = HydraulicReasoningTemplates.PUMP_LEAK_SEVERE[template_idx]
        elif label_val == 1:
            interp = HydraulicReasoningTemplates.PUMP_LEAK_WEAK[template_idx]
        else:
            interp = HydraulicReasoningTemplates.PUMP_OPTIMAL[template_idx]
    else:  # accumulator_pressure
        if label_val in (90, 100):
            interp = HydraulicReasoningTemplates.ACCUMULATOR_SEVERELY_REDUCED[template_idx]
        elif label_val == 115:
            interp = HydraulicReasoningTemplates.ACCUMULATOR_SLIGHTLY_REDUCED[template_idx]
        else:
            interp = HydraulicReasoningTemplates.ACCUMULATOR_OPTIMAL[template_idx]

    # Assemble text and calculate exact character spans
    prefix = f"{comp_header}: {label_str}. Evidence: "
    text = prefix
    claims: list[Claim] = []

    for i, meta in enumerate(claims_meta):
        clause_str = meta["clause_str"]
        start_idx = len(text)
        text += clause_str
        end_idx = len(text)

        claims.append(
            Claim(
                sensor=meta["sensor"],
                quantity=meta["quantity"],
                value=meta["value"],
                unit=meta["unit"],
                direction=meta["direction"],
                pct=meta["pct"],
                feature=meta["feature"],
                span=(start_idx, end_idx),
            )
        )
        if i < len(claims_meta) - 1:
            text += "; "

    text += f". {interp}"

    return Rationale(
        cycle_id=cycle.id,
        component=component,
        label_value=label_val,
        label_name=label_str,
        text=text,
        claims=claims,
        template_id=f"{component}_t{template_idx}",
    )


def build_joint_rationale(
    cycle: Cycle,
    features: dict[str, Feature],
    ref: HealthyReference,
    all_links: dict[str, list[dict[str, Any]]],
    seed: int = 0,
) -> Rationale:
    """Build a multi-component joint diagnosis rationale."""
    component_order = [
        "cooler_condition",
        "valve_condition",
        "pump_leakage",
        "accumulator_pressure",
    ]
    paragraphs: list[str] = []
    all_claims: list[Claim] = []
    char_offset = 0

    for comp in component_order:
        # Deterministic seed per cycle and component
        sub_seed = (abs(hash(f"{cycle.id}_{comp}_{seed}"))) % (2**31)
        rng = np.random.default_rng(sub_seed)
        r = build_component_rationale(cycle, features, ref, all_links.get(comp, []), comp, rng)

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
                    span=(c.span[0] + char_offset, c.span[1] + char_offset),
                )
            )
        paragraphs.append(r.text)
        char_offset += len(r.text) + 1  # newline separator

    joint_text = "\n".join(paragraphs)

    return Rationale(
        cycle_id=cycle.id,
        component="joint",
        label_value=0,
        label_name="joint_condition",
        text=joint_text,
        claims=all_claims,
        template_id="joint_v1",
    )
