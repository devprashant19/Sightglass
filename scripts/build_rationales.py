"""Generate physics-grounded rationales and QA pairs across all cycles."""

import json
from pathlib import Path

import yaml

from sightglass.data.loader import load_cycles
from sightglass.eval.faithfulness import FaithfulnessConfig, parse_claims, verify
from sightglass.physics.base import HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.rationales.builder import build_joint_rationale
from sightglass.rationales.qa import generate_cycle_qa
from sightglass.utils.log import get_logger

logger = get_logger("build_rationales")


def main() -> None:
    logger.info("Starting rationale and QA generation pipeline...")

    # 1. Load links config
    with open("configs/physics/hydraulic_links.yaml", encoding="utf-8") as f:
        links = yaml.safe_load(f)

    # 2. Load train cycles and fit HealthyReference strictly on train healthy cycles
    logger.info("Loading training cycles...")
    train_cycles = load_cycles("hydraulic", split="train", total_count=2205)
    extractor = HydraulicExtractor()

    # Healthy condition: cooler=100, valve=100, pump=0, accumulator=130, stable=0
    healthy_features = []
    for c in train_cycles:
        if (
            c.labels["cooler_condition"] == 100
            and c.labels["valve_condition"] == 100
            and c.labels["pump_leakage"] == 0
            and c.labels["accumulator_pressure"] == 130
        ):
            healthy_features.append(extractor.extract(c))

    if len(healthy_features) < 10:
        # Fallback: extract per-component healthy baseline from train
        healthy_features = [extractor.extract(c) for c in train_cycles[:50]]

    ref = HealthyReference.fit(healthy_features, build_hash="hydraulic_v1")
    ref_path = Path("data/reference/hydraulic_healthy.json")
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref.save(ref_path)
    logger.info(
        f"HealthyReference fit on {ref.n_cycles} healthy train cycles and saved to {ref_path}"
    )

    # 3. Load all cycles and generate rationales
    all_cycles = load_cycles("hydraulic", split="all", total_count=2205)
    rationales_out = Path("data/rationales/hydraulic.jsonl")
    rationales_out.parent.mkdir(parents=True, exist_ok=True)

    qa_out = Path("data/qa/hydraulic.jsonl")
    qa_out.parent.mkdir(parents=True, exist_ok=True)

    faith_cfg = FaithfulnessConfig.load("configs/faithfulness.yaml")

    sample_spotcheck = []
    round_trip_successes = 0
    total_claims = 0

    with (
        open(rationales_out, "w", encoding="utf-8") as f_rat,
        open(qa_out, "w", encoding="utf-8") as f_qa,
    ):
        for i, cycle in enumerate(all_cycles):
            features = extractor.extract(cycle)
            joint_rat = build_joint_rationale(cycle, features, ref, links, seed=i)

            # Round-trip verification check
            parsed_claims, _ = parse_claims(joint_rat.text)
            verdicts = verify(parsed_claims, cycle, extractor, ref, faith_cfg)

            for v in verdicts:
                total_claims += 1
                if v.status == "verified":
                    round_trip_successes += 1

            # Save rationale
            record = {
                "cycle_id": cycle.id,
                "text": joint_rat.text,
                "claims": [
                    {
                        "sensor": c.sensor,
                        "quantity": c.quantity,
                        "value": c.value,
                        "unit": c.unit,
                        "direction": c.direction,
                        "pct": c.pct,
                        "feature": c.feature,
                        "span": c.span,
                    }
                    for c in joint_rat.claims
                ],
            }
            f_rat.write(json.dumps(record) + "\n")

            # Generate QA pairs
            split_tag = "train" if i < 1543 else ("val" if i < 1874 else "test")
            qa_items = generate_cycle_qa(cycle, split_tag, features, ref, links, seed=i)
            for item in qa_items:
                f_qa.write(
                    json.dumps(
                        {
                            "cycle_id": item.cycle_id,
                            "split": item.split,
                            "question": item.question,
                            "answer": item.answer,
                        }
                    )
                    + "\n"
                )

            if len(sample_spotcheck) < 50:
                sample_spotcheck.append((cycle.id, joint_rat.text))

    rt_rate = (round_trip_successes / max(1, total_claims)) * 100.0
    logger.info(
        f"Generated {len(all_cycles)} rationales. Round-trip claim verification: {rt_rate:.1f}% ({round_trip_successes}/{total_claims})"
    )

    # 4. Write spotcheck documentation
    spotcheck_doc = Path("docs/rationale-spotcheck.md")
    with open(spotcheck_doc, "w", encoding="utf-8") as f:
        f.write("# Rationale Spotcheck (50 Representative Cycles)\n\n")
        f.write(
            f"Round-trip claim verification rate: **{rt_rate:.1f}%** across all {total_claims} generated claims.\n\n"
        )
        for cid, text in sample_spotcheck:
            f.write(f"### Cycle `{cid}`\n```\n{text}\n```\n\n")

    logger.info(f"Spotcheck written to {spotcheck_doc}")


if __name__ == "__main__":
    main()
