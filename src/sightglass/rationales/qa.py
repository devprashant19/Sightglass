"""Question-answering dataset generation for hydraulic fault diagnosis."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from sightglass.data.models import Cycle
from sightglass.physics.base import Feature, HealthyReference
from sightglass.rationales.builder import (
    Claim,
    build_component_rationale,
    build_joint_rationale,
)


@dataclass(frozen=True)
class QAItem:
    """A question-answering training/eval example."""

    cycle_id: str
    split: str
    question: str
    answer: str
    claims: list[Claim]


def generate_cycle_qa(
    cycle: Cycle,
    split: str,
    features: dict[str, Feature],
    ref: HealthyReference,
    links: dict[str, list[dict[str, Any]]],
    seed: int = 0,
) -> list[QAItem]:
    """Generate QA pairs for a single cycle spanning different question modalities."""
    items: list[QAItem] = []
    rng = np.random.default_rng(seed)

    # 1. Full diagnosis question
    full_q_variants = [
        "Diagnose this hydraulic cycle.",
        "Perform a complete machine-health diagnosis for this hydraulic test cycle.",
        "Analyze the sensor readings and state the condition of all hydraulic components.",
    ]
    joint_rat = build_joint_rationale(cycle, features, ref, links, seed=seed)
    q1 = str(rng.choice(full_q_variants))
    items.append(
        QAItem(
            cycle_id=cycle.id,
            split=split,
            question=q1,
            answer=joint_rat.text,
            claims=joint_rat.claims,
        )
    )

    # 2. Component-specific questions
    comp_questions = {
        "cooler_condition": [
            "What is the condition of the hydraulic cooler?",
            "Assess the thermal health of the cooler.",
        ],
        "valve_condition": [
            "What is the condition of the main hydraulic valve?",
            "Check the directional valve for switching lag.",
        ],
        "pump_leakage": [
            "Is there internal pump leakage?",
            "What is the leakage state of the hydraulic pump?",
        ],
        "accumulator_pressure": [
            "What is the condition of the hydraulic accumulator?",
            "Assess the pressure dampening and pre-charge of the accumulator.",
        ],
    }

    for comp, q_list in comp_questions.items():
        comp_rat = build_component_rationale(cycle, features, ref, links.get(comp, []), comp, rng)
        q = str(rng.choice(q_list))
        items.append(
            QAItem(
                cycle_id=cycle.id,
                split=split,
                question=q,
                answer=comp_rat.text,
                claims=comp_rat.claims,
            )
        )

    # 3. Overall health check
    is_healthy = all(
        (
            cycle.labels.get("cooler_condition") == 100,
            cycle.labels.get("valve_condition") == 100,
            cycle.labels.get("pump_leakage") == 0,
            cycle.labels.get("accumulator_pressure") == 130,
        )
    )
    if is_healthy:
        ans3 = "Yes, this hydraulic cycle is operating in nominal healthy condition across all four components."
        claims3: list[Claim] = []
    else:
        faulty = []
        if cycle.labels.get("cooler_condition") != 100:
            faulty.append("cooler")
        if cycle.labels.get("valve_condition") != 100:
            faulty.append("valve")
        if cycle.labels.get("pump_leakage") != 0:
            faulty.append("pump")
        if cycle.labels.get("accumulator_pressure") != 130:
            faulty.append("accumulator")
        ans3 = f"No, this cycle exhibits component faults in: {', '.join(faulty)}."
        claims3 = []

    items.append(
        QAItem(
            cycle_id=cycle.id,
            split=split,
            question="Is this cycle healthy?",
            answer=ans3,
            claims=claims3,
        )
    )

    return items
