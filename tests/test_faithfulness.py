"""Faithfulness parser, verifier, σ-form clauses and consistency (synthetic fixtures)."""

import dataclasses

from sightglass.data.loader import load_cycles
from sightglass.engine import fit_reference, load_links
from sightglass.eval.consistency import ConsistencyChecker
from sightglass.eval.faithfulness import FaithfulnessConfig, _deviation_ok, parse_claims, verify
from sightglass.physics.base import Feature, HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.rationales.builder import build_joint_rationale
from sightglass.rationales.format import format_evidence_clause


def test_canonical_clause_parser_pct_and_sigma() -> None:
    text = (
        "Cooler: reduced efficiency. Evidence: "
        "TS1 mean temperature 51.4 °C (12% above healthy); "
        "CE cooling efficiency 62.1 % (24% below healthy); "
        "TS2 mean temperature 44.0 °C (within 1% of healthy).\n"
        "Valve: small lag. Evidence: PS1/PS2 valve switching lag 0.42 s (3.1σ above healthy); "
        "TS1 temperature slope 0.02 °C/min (within 1.0σ of healthy)."
    )
    claims, unparsed = parse_claims(text)
    assert [c.sensor for c in claims] == ["TS1", "CE", "TS2", "PS1/PS2", "TS1"]
    assert claims[0].quantity == "mean temperature" and claims[0].value == 51.4
    assert claims[0].unit == "°C" and claims[0].direction == "above" and claims[0].pct == 12.0
    assert claims[1].direction == "below" and claims[1].pct == 24.0
    assert claims[2].direction == "within" and claims[2].pct == 1.0
    assert claims[3].basis == "sigma" and claims[3].sigma == 3.1 and claims[3].pct is None
    assert claims[4].direction == "within" and claims[4].basis == "sigma"
    assert unparsed == []


def test_sigma_clause_format() -> None:
    assert (
        format_evidence_clause("TS1", "temperature slope", 0.53, "°C/min", 9e6, z=3.14, sigma=True)
        == "TS1 temperature slope 0.53 °C/min (3.1σ above healthy)"
    )
    assert format_evidence_clause(
        "TS1", "temperature slope", 0.01, "°C/min", 0.0, z=-0.4, sigma=True
    ).endswith("(within 1.0σ of healthy)")


def test_stated_distance_from_healthy_is_checked() -> None:
    """A claim with the right value but the wrong "N% above healthy" must not verify."""
    cfg = FaithfulnessConfig.load()
    (pct,), _ = parse_claims("Evidence: TS1 mean temperature 51.4 °C (60% above healthy).")
    assert _deviation_ok(pct, 60.0, 5.0, cfg)
    assert _deviation_ok(pct, 62.0, 5.0, cfg)
    assert not _deviation_ok(pct, 5.0, 0.5, cfg), "true +5%: a stated 60% is wrong"
    assert not _deviation_ok(pct, -60.0, -5.0, cfg), "true -60%: wrong side of healthy"
    (sig,), _ = parse_claims("Evidence: TS1 temperature slope 0.53 °C/min (3.1σ above healthy).")
    assert _deviation_ok(sig, 0.0, 3.1, cfg)
    assert not _deviation_ok(sig, 0.0, 0.6, cfg), "true 0.6σ: a stated 3.1σ is wrong"


def _setup() -> tuple[list, HydraulicExtractor, HealthyReference, dict, FaithfulnessConfig]:
    cycles = load_cycles("hydraulic", split="train", synthetic=True, total_count=200)
    ex = HydraulicExtractor()
    links = load_links()
    ref = fit_reference(cycles, [ex.extract(c) for c in cycles], links)
    return cycles, ex, ref, links, FaithfulnessConfig.load()


def test_round_trip_and_corruption() -> None:
    cycles, ex, ref, links, cfg = _setup()
    for c in cycles[:10]:
        feats = ex.extract(c)
        r = build_joint_rationale(c, feats, ref, links, seed=0)
        claims, _ = parse_claims(r.text)
        assert len(claims) == len(r.claims) > 0
        verdicts = verify(claims, c, ex, ref, cfg)
        assert all(v.status == "verified" for v in verdicts), [v.status for v in verdicts]
        bad = dataclasses.replace(claims[0], value=claims[0].value * 1.25)
        assert verify([bad], c, ex, ref, cfg)[0].status == "wrong_value"
        flip = "below" if claims[0].direction == "above" else "above"
        if claims[0].direction != "within":
            wrong = dataclasses.replace(claims[0], direction=flip)
            assert verify([wrong], c, ex, ref, cfg)[0].status == "wrong_direction"


def test_unknown_sensor_and_quantity() -> None:
    cycles, ex, ref, _, cfg = _setup()
    claims, _ = parse_claims(
        "XS9 mean pressure 10.0 bar (5% above healthy); PS1 mean flux 10.0 bar (5% above healthy)"
    )
    v = verify(claims, cycles[0], ex, ref, cfg)
    assert [x.status for x in v] == ["unknown_sensor", "unknown_quantity"]


def test_per_component_reference_uses_healthy_cycles() -> None:
    f = lambda v: {"TS1.mean": Feature("TS1.mean", "TS1", "mean temperature", "°C", v)}  # noqa: E731
    feats = [f(40.0), f(42.0), f(60.0)]
    labels = [
        {
            "cooler_condition": 100,
            "valve_condition": 90,
            "pump_leakage": 0,
            "accumulator_pressure": 130,
        },
        {
            "cooler_condition": 100,
            "valve_condition": 100,
            "pump_leakage": 1,
            "accumulator_pressure": 90,
        },
        {
            "cooler_condition": 3,
            "valve_condition": 100,
            "pump_leakage": 0,
            "accumulator_pressure": 130,
        },
    ]
    links = {"cooler_condition": [{"feature": "TS1.mean", "direction": "up"}]}
    ref = HealthyReference.fit_per_component(feats, labels, links, min_cycles=1)
    assert ref.mean["TS1.mean"] == 41.0  # only cooler-healthy cycles
    assert ref.basis["TS1.mean"] == ["cooler_condition"]


def test_consistency_rule() -> None:
    cycles, ex, ref, links, cfg = _setup()
    checker = ConsistencyChecker(cfg=cfg)
    c = next(x for x in cycles if x.labels["cooler_condition"] == 3)
    feats = ex.extract(c)
    r = build_joint_rationale(c, feats, ref, links, seed=0)
    claims, _ = parse_claims(r.text)
    cooler = [
        v
        for v, cl in zip(verify(claims, c, ex, ref, cfg), r.claims, strict=True)
        if cl.component == "cooler_condition"
    ]
    # The same evidence cannot support both a failed and a healthy cooler.
    assert checker.check("cooler_condition", 3, cooler) != checker.check(
        "cooler_condition", 100, cooler
    )
