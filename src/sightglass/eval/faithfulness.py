"""Faithfulness checker: parse evidence clauses and verify every number against the signal.

Each claim is resolved to the feature with the same (sensor, quantity) that the physics
extractor computes for that cycle, recomputed from the native-rate signals, and compared with
the pre-registered tolerances in configs/faithfulness.yaml.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from sightglass.data.models import Cycle
from sightglass.physics.base import Extractor, Feature, HealthyReference

Status = Literal[
    "verified",
    "wrong_value",
    "wrong_direction",
    "unknown_sensor",
    "unknown_quantity",
    "unit_mismatch",
]

# Canonical clause grammar (see rationales/format.py):
#   <SENSOR> <quantity> <value> <unit> (<n>% <above|below> healthy)
#   <SENSOR> <quantity> <value> <unit> (within <n>% of healthy)
# and the same with σ (standard deviations) in place of %.
CANONICAL_CLAUSE_REGEX = re.compile(
    r"(?P<sensor>[A-Z][A-Z0-9_]*(?:[/\-][A-Z][A-Z0-9_]*)?)\s+"
    r"(?P<quantity>[a-z][a-z\- ]*?)\s+"
    r"(?P<value>[-+]?\d+(?:\.\d+)?)\s+"
    r"(?P<unit>[^\s()]+)\s+"
    r"\((?:within\s+(?P<within>\d+(?:\.\d+)?)(?P<within_unit>%|σ)\s+of\s+healthy"
    r"|(?P<dev>\d+(?:\.\d+)?)(?P<dev_unit>%|σ)\s+(?P<direction>above|below)\s+healthy)\)",
)

# Free-form numeric fragments (outside canonical clauses) for non-canonical outputs.
NUMERIC_FRAGMENT_REGEX = re.compile(r"[-+]?\d+(?:\.\d+)?")


@dataclass(frozen=True)
class ParsedClaim:
    """A claim extracted from rationale text."""

    component: str | None
    sensor: str
    quantity: str
    value: float
    unit: str
    direction: Literal["above", "below", "within"] | None
    pct: float | None  # deviation magnitude in percent, when basis == "pct"
    span: tuple[int, int]
    basis: Literal["pct", "sigma"] = "pct"
    sigma: float | None = None  # deviation magnitude in standard deviations (basis "sigma")


@dataclass(frozen=True)
class Verdict:
    """Verification verdict for one claim."""

    claim: ParsedClaim
    feature: str | None
    true_value: float | None
    true_pct: float | None
    value_ok: bool | None
    direction_ok: bool | None
    status: Status
    true_z: float | None = None
    window: tuple[float, float] | None = None


@dataclass(frozen=True)
class FaithfulnessConfig:
    """Tolerances pre-registered in configs/faithfulness.yaml."""

    relative_tolerance: float = 0.05
    absolute_floor: dict[str, float] | None = None
    pct_tolerance_points: float = 3.0
    pct_relative_tolerance: float = 0.05
    within_threshold_pct: float = 2.0
    direction_neutral_band_pct: float = 2.0
    sigma_tolerance: float = 0.3
    sigma_relative_tolerance: float = 0.05
    direction_neutral_band_sigma: float = 1.0

    @classmethod
    def load(cls, path: str | Path = "configs/faithfulness.yaml") -> "FaithfulnessConfig":
        p = Path(path)
        if not p.is_file():
            return cls()
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        d = cls()

        def num(key: str, default: float) -> float:
            return float(data.get(key, default))

        return cls(
            relative_tolerance=num("relative_tolerance", d.relative_tolerance),
            absolute_floor=data.get("absolute_floor", {}) or {},
            pct_tolerance_points=num("pct_tolerance_points", d.pct_tolerance_points),
            pct_relative_tolerance=num("pct_relative_tolerance", d.pct_relative_tolerance),
            within_threshold_pct=num("within_threshold_pct", d.within_threshold_pct),
            direction_neutral_band_pct=num(
                "direction_neutral_band_pct", d.direction_neutral_band_pct
            ),
            sigma_tolerance=num("sigma_tolerance", d.sigma_tolerance),
            sigma_relative_tolerance=num("sigma_relative_tolerance", d.sigma_relative_tolerance),
            direction_neutral_band_sigma=num(
                "direction_neutral_band_sigma", d.direction_neutral_band_sigma
            ),
        )


def parse_claims(text: str) -> tuple[list[ParsedClaim], list[str]]:
    """Extract canonical claims, plus any numeric fragments that are not part of one."""
    claims: list[ParsedClaim] = []
    spans: list[tuple[int, int]] = []
    for m in CANONICAL_CLAUSE_REGEX.finditer(text):
        start, end = m.span()
        spans.append((start, end))
        if m.group("within") is not None:
            direction: Literal["above", "below", "within"] = "within"
            mag = float(m.group("within"))
            unit_dev = m.group("within_unit")
        else:
            direction = "above" if m.group("direction") == "above" else "below"
            mag = float(m.group("dev"))
            unit_dev = m.group("dev_unit")
        sigma_basis = unit_dev == "σ"
        claims.append(
            ParsedClaim(
                component=None,
                sensor=m.group("sensor"),
                quantity=m.group("quantity").strip().lower(),
                value=float(m.group("value")),
                unit=m.group("unit"),
                direction=direction,
                pct=None if sigma_basis else mag,
                span=(start, end),
                basis="sigma" if sigma_basis else "pct",
                sigma=mag if sigma_basis else None,
            )
        )

    unparsed: list[str] = []
    for m in NUMERIC_FRAGMENT_REGEX.finditer(text):
        s, e = m.span()
        if any(a <= s and e <= b for a, b in spans):
            continue
        # Digits that belong to sensor names (PS1, TS2, ...) are not claims.
        if s > 0 and (text[s - 1].isalpha() or text[s - 1] == "_"):
            continue
        unparsed.append(m.group(0))
    return claims, unparsed


def _value_ok(stated: float, true: float, unit: str, cfg: FaithfulnessConfig) -> bool:
    floor = (cfg.absolute_floor or {}).get(unit, 0.0)
    return abs(stated - true) <= max(floor, cfg.relative_tolerance * abs(true), 1e-9)


def _deviation_ok(
    claim: ParsedClaim, true_pct: float, true_z: float, cfg: FaithfulnessConfig
) -> bool:
    if claim.basis == "sigma":
        mag = claim.sigma or 0.0
        if claim.direction == "within":
            return abs(true_z) <= max(mag, cfg.direction_neutral_band_sigma) + cfg.sigma_tolerance
        signed = true_z if claim.direction == "above" else -true_z
        tol = max(cfg.sigma_tolerance, cfg.sigma_relative_tolerance * abs(true_z))
        return signed > 0 and abs(mag - signed) <= tol

    mag = claim.pct or 0.0
    if claim.direction == "within":
        limit = max(mag, cfg.within_threshold_pct, cfg.direction_neutral_band_pct)
        return abs(true_pct) <= limit + cfg.pct_tolerance_points
    signed = true_pct if claim.direction == "above" else -true_pct
    tol = max(cfg.pct_tolerance_points, cfg.pct_relative_tolerance * abs(true_pct))
    return signed > 0 and abs(mag - signed) <= tol


def verify(
    claims: list[ParsedClaim],
    cycle: Cycle,
    extractor: Extractor,
    ref: HealthyReference,
    cfg: FaithfulnessConfig,
    features: dict[str, Feature] | None = None,
) -> list[Verdict]:
    """Verify parsed claims against features recomputed from the cycle's native-rate signals.

    ``features`` may be passed to reuse an extraction of the same cycle; it must come from
    ``extractor.extract(cycle)``.
    """
    feats = features if features is not None else extractor.extract(cycle)
    by_key = {(f.sensor, f.quantity.lower()): f for f in feats.values()}
    sensors = {f.sensor for f in feats.values()}
    out: list[Verdict] = []
    for claim in claims:
        f = by_key.get((claim.sensor, claim.quantity))
        if f is None:
            status: Status = "unknown_quantity" if claim.sensor in sensors else "unknown_sensor"
            out.append(Verdict(claim, None, None, None, False, False, status))
            continue
        true_pct = ref.pct_diff(f)
        true_z = ref.z(f)
        if claim.unit != f.unit:
            out.append(
                Verdict(
                    claim,
                    f.name,
                    f.value,
                    true_pct,
                    False,
                    False,
                    "unit_mismatch",
                    true_z,
                    f.window,
                )
            )
            continue
        v_ok = _value_ok(claim.value, f.value, f.unit, cfg)
        d_ok = _deviation_ok(claim, true_pct, true_z, cfg)
        if v_ok and d_ok:
            status = "verified"
        elif not v_ok:
            status = "wrong_value"
        else:
            status = "wrong_direction"
        out.append(Verdict(claim, f.name, f.value, true_pct, v_ok, d_ok, status, true_z, f.window))
    return out
