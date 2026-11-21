"""Unit tests for faithfulness claim parsing, verification, and corruption detection."""

import yaml

from sightglass.eval.faithfulness import (
    FaithfulnessConfig,
    ParsedClaim,
    parse_claims,
    verify,
)
from sightglass.physics.base import HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.rationales.builder import build_joint_rationale


def test_canonical_clause_parser() -> None:
    text = (
        "Cooler: reduced efficiency. Evidence: "
        "TS1 mean temperature 51.4 °C (12% above healthy); "
        "CE cooling efficiency 62.1 % (24% below healthy); "
        "TS2 mean temperature 44.0 °C (within 1% of healthy)."
    )
    claims, unparsed = parse_claims(text)
    assert len(claims) == 3

    c0 = claims[0]
    assert c0.sensor == "TS1"
    assert c0.quantity == "mean temperature"
    assert c0.value == 51.4
    assert c0.unit == "°C"
    assert c0.direction == "above"
    assert c0.pct == 12.0

    c1 = claims[1]
    assert c1.sensor == "CE"
    assert c1.direction == "below"
    assert c1.pct == 24.0

    c2 = claims[2]
    assert c2.direction == "within"
    assert c2.pct == 1.0


def test_faithfulness_round_trip_and_corruption() -> None:
    # 1. Setup sample cycle
    from sightglass.data.loader import load_cycles

    cycles = load_cycles("hydraulic", split="train", total_count=20)
    c0 = cycles[0]
    extractor = HydraulicExtractor()
    features = extractor.extract(c0)

    # 2. Fit HealthyReference
    all_feats = [extractor.extract(c) for c in cycles]
    ref = HealthyReference.fit(all_feats)

    # 3. Load links
    with open("configs/physics/hydraulic_links.yaml", encoding="utf-8") as f:
        links = yaml.safe_load(f)

    joint_rat = build_joint_rationale(c0, features, ref, links, seed=0)
    cfg = FaithfulnessConfig.load("configs/faithfulness.yaml")

    # Round trip test
    parsed_claims, _ = parse_claims(joint_rat.text)
    assert len(parsed_claims) > 0
    verdicts = verify(parsed_claims, c0, extractor, ref, cfg)

    # Verify 100% of generated claims pass
    assert all(v.status == "verified" for v in verdicts)

    # Corruption test: perturb a claim by +25%
    corrupt_claim = ParsedClaim(
        component=parsed_claims[0].component,
        sensor=parsed_claims[0].sensor,
        quantity=parsed_claims[0].quantity,
        value=parsed_claims[0].value * 1.25,  # corrupted by 25%
        unit=parsed_claims[0].unit,
        direction=parsed_claims[0].direction,
        pct=parsed_claims[0].pct,
        span=parsed_claims[0].span,
    )
    corrupt_verdicts = verify([corrupt_claim], c0, extractor, ref, cfg)
    assert corrupt_verdicts[0].status == "wrong_value"
    assert corrupt_verdicts[0].value_ok is False
