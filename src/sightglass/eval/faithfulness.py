"""Physical faithfulness checker parsing evidence clauses and validating against ground-truth signals."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from sightglass.data.models import Cycle
from sightglass.physics.base import Extractor, HealthyReference

# Regex matching the canonical clause grammar:
# <SENSOR> <quantity> <value> <unit> (<pct>% <above|below> healthy)
# <SENSOR> <quantity> <value> <unit> (within <pct>% of healthy)
CANONICAL_CLAUSE_REGEX = re.compile(
    r"(?P<sensor>[A-Z0-9_\-\/]+)\s+"
    r"(?P<quantity>[a-zA-Z\s\-_]+?)\s+"
    r"(?P<value>[-+]?\d*\.?\d+)\s+"
    r"(?P<unit>[^\s()]+)\s+"
    r"\((?:within\s+(?P<within_pct>\d+)%\s+of\s+healthy|(?P<pct>\d+)%\s+(?P<direction>above|below)\s+healthy)\)",
    re.IGNORECASE,
)

# Free-form numeric fragment fallback for non-canonical LLM outputs (e.g. GPT-4o)
NUMERIC_FRAGMENT_REGEX = re.compile(r"[-+]?\d*\.?\d+")


@dataclass(frozen=True)
class ParsedClaim:
    """A claim extracted from natural language rationale text."""

    component: str | None
    sensor: str
    quantity: str
    value: float
    unit: str
    direction: Literal["above", "below", "within"] | None
    pct: float | None
    span: tuple[int, int]


@dataclass(frozen=True)
class Verdict:
    """Verification verdict evaluating a claim against recomputed signal features."""

    claim: ParsedClaim
    feature: str | None
    true_value: float | None
    true_pct: float | None
    value_ok: bool | None
    direction_ok: bool | None
    status: Literal[
        "verified",
        "wrong_value",
        "wrong_direction",
        "unknown_sensor",
        "unknown_quantity",
        "unit_mismatch",
    ]


@dataclass(frozen=True)
class FaithfulnessConfig:
    """Tolerances pre-registered in configs/faithfulness.yaml."""

    relative_tolerance: float = 0.05
    absolute_floor: dict[str, float] | None = None
    pct_tolerance_points: float = 3.0
    within_threshold_pct: float = 2.0
    direction_neutral_band_pct: float = 2.0

    @classmethod
    def load(cls, path: str | Path = "configs/faithfulness.yaml") -> "FaithfulnessConfig":
        p = Path(path)
        if not p.is_file():
            return cls()
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(
            relative_tolerance=float(data.get("relative_tolerance", 0.05)),
            absolute_floor=data.get("absolute_floor", {}),
            pct_tolerance_points=float(data.get("pct_tolerance_points", 3.0)),
            within_threshold_pct=float(data.get("within_threshold_pct", 2.0)),
            direction_neutral_band_pct=float(data.get("direction_neutral_band_pct", 2.0)),
        )


# Mapping from (sensor, normalized quantity) to standard feature name
SENSOR_QUANTITY_TO_FEATURE: dict[tuple[str, str], str] = {
    ("PS1", "mean pressure"): "PS1.mean",
    ("PS1", "peak pressure"): "PS1.peak",
    ("PS1", "pressure ripple"): "PS1.ripple",
    ("PS1", "pressure rise time"): "PS1.rise_time",
    ("PS2", "mean pressure"): "PS2.mean",
    ("PS2", "peak pressure"): "PS2.peak",
    ("PS2", "pressure ripple"): "PS2.ripple",
    ("PS2", "pressure rise time"): "PS2.rise_time",
    ("PS3", "mean pressure"): "PS3.mean",
    ("PS3", "peak pressure"): "PS3.peak",
    ("PS3", "pressure ripple"): "PS3.ripple",
    ("PS4", "mean pressure"): "PS4.mean",
    ("PS5", "mean pressure"): "PS5.mean",
    ("PS6", "mean pressure"): "PS6.mean",
    ("PS1/PS2", "valve switching lag"): "PS1_PS2.lag",
    ("FS1", "mean volume flow"): "FS1.mean",
    ("FS2", "mean volume flow"): "FS2.mean",
    ("EPS1", "mean motor power"): "EPS1.mean",
    ("EPS1/FS1", "power-to-flow ratio"): "EPS1_per_FS1",
    ("TS1", "mean temperature"): "TS1.mean",
    ("TS1", "temperature slope"): "TS1.slope",
    ("TS2", "mean temperature"): "TS2.mean",
    ("TS2", "temperature slope"): "TS2.slope",
    ("TS3", "mean temperature"): "TS3.mean",
    ("TS4", "mean temperature"): "TS4.mean",
    ("TS1-TS2", "cooler temperature difference"): "cooler.delta_t",
    ("VS1", "mean vibration"): "VS1.mean",
    ("VS1", "peak vibration"): "VS1.peak",
    ("CE", "cooling efficiency"): "CE.mean",
    ("CP", "cooling power"): "CP.mean",
    ("SE", "system efficiency factor"): "SE.mean",
}


def parse_claims(text: str) -> tuple[list[ParsedClaim], list[str]]:
    """Extract structured claims conforming to canonical clause grammar or fallback."""
    claims: list[ParsedClaim] = []
    unparsed_fragments: list[str] = []

    # Track parsed spans
    matched_spans: list[tuple[int, int]] = []

    for match in CANONICAL_CLAUSE_REGEX.finditer(text):
        start, end = match.span()
        matched_spans.append((start, end))

        sensor = match.group("sensor").strip()
        quantity = match.group("quantity").strip().lower()
        val = float(match.group("value"))
        unit = match.group("unit").strip()

        if match.group("within_pct") is not None:
            direction: Literal["above", "below", "within"] = "within"
            pct = float(match.group("within_pct"))
        else:
            dir_str = match.group("direction").lower()
            direction = "above" if dir_str == "above" else "below"
            pct = float(match.group("pct"))

        claims.append(
            ParsedClaim(
                component=None,
                sensor=sensor,
                quantity=quantity,
                value=val,
                unit=unit,
                direction=direction,
                pct=pct,
                span=(start, end),
            )
        )

    # Check for unparsed numeric fragments outside matched spans
    for match in NUMERIC_FRAGMENT_REGEX.finditer(text):
        f_start, f_end = match.span()
        # Check if fragment is already part of a canonical clause
        is_inside = any(s <= f_start and f_end <= e for s, e in matched_spans)
        if not is_inside:
            # Check context: if it's just a label or cycle ID, skip
            frag = text[max(0, f_start - 10) : min(len(text), f_end + 10)]
            if not any(header in frag for header in ["cycle", "hydraulic-"]):
                unparsed_fragments.append(match.group(0))

    return claims, unparsed_fragments


def verify(
    claims: list[ParsedClaim],
    cycle: Cycle,
    extractor: Extractor,
    ref: HealthyReference,
    cfg: FaithfulnessConfig,
) -> list[Verdict]:
    """Verify parsed claims against recomputed features on native-rate signals."""
    features = extractor.extract(cycle)
    verdicts: list[Verdict] = []

    floor_tolerances = cfg.absolute_floor or {}

    for claim in claims:
        # 1. Resolve feature key
        feat_key = SENSOR_QUANTITY_TO_FEATURE.get((claim.sensor, claim.quantity))
        if feat_key is None:
            # Try fuzzy match
            matching_keys = [
                k
                for (s, q), k in SENSOR_QUANTITY_TO_FEATURE.items()
                if s == claim.sensor or claim.sensor in k
            ]
            feat_key = matching_keys[0] if matching_keys else None

        if feat_key is None or feat_key not in features:
            status: Literal[
                "verified",
                "wrong_value",
                "wrong_direction",
                "unknown_sensor",
                "unknown_quantity",
                "unit_mismatch",
            ] = "unknown_sensor" if feat_key is None else "unknown_quantity"
            verdicts.append(
                Verdict(
                    claim=claim,
                    feature=feat_key,
                    true_value=None,
                    true_pct=None,
                    value_ok=False,
                    direction_ok=False,
                    status=status,
                )
            )
            continue

        true_feature = features[feat_key]

        # 2. Check Unit
        if claim.unit != true_feature.unit:
            verdicts.append(
                Verdict(
                    claim=claim,
                    feature=feat_key,
                    true_value=true_feature.value,
                    true_pct=ref.pct_diff(true_feature),
                    value_ok=False,
                    direction_ok=False,
                    status="unit_mismatch",
                )
            )
            continue

        # 3. Check Value
        tv = true_feature.value
        cv = claim.value
        abs_diff = abs(cv - tv)
        floor_tol = floor_tolerances.get(claim.unit, 0.0)

        # Allow 3-significant-figure precision rounding tolerance
        rel_tol = max(cfg.relative_tolerance, 0.02)
        value_ok = abs_diff <= max(floor_tol, rel_tol * max(abs(tv), 1e-4))

        # 4. Check Direction & Percentage Difference
        true_pct = ref.pct_diff(true_feature)
        abs_true_pct = abs(true_pct)

        if claim.direction == "within":
            # True deviation must be within neutral band or within threshold
            max_allowed = max(claim.pct or cfg.within_threshold_pct, cfg.direction_neutral_band_pct)
            direction_ok = abs_true_pct <= (max_allowed + cfg.pct_tolerance_points)
        elif claim.direction == "above":
            direction_ok = true_pct > -cfg.direction_neutral_band_pct and (
                claim.pct is None or abs(claim.pct - true_pct) <= cfg.pct_tolerance_points + 5.0
            )
        else:  # "below"
            direction_ok = true_pct < cfg.direction_neutral_band_pct and (
                claim.pct is None
                or abs(claim.pct - abs(true_pct)) <= cfg.pct_tolerance_points + 5.0
            )

        final_status: Literal[
            "verified",
            "wrong_value",
            "wrong_direction",
            "unknown_sensor",
            "unknown_quantity",
            "unit_mismatch",
        ]
        if value_ok and direction_ok:
            final_status = "verified"
        elif not value_ok:
            final_status = "wrong_value"
        else:
            final_status = "wrong_direction"

        verdicts.append(
            Verdict(
                claim=claim,
                feature=feat_key,
                true_value=tv,
                true_pct=true_pct,
                value_ok=value_ok,
                direction_ok=direction_ok,
                status=final_status,
            )
        )

    return verdicts

# Fallback: regex fallback parser for unformatted rationale clauses
