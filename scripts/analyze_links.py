"""Measure which physics features really respond to each component, on the TRAIN split only.

For every (component, candidate feature) pair from the physics table in phases/02:
  * Cliff's delta between the healthy class and the most severe class (positive = the feature
    rises as the fault gets worse),
  * Kruskal–Wallis H test across all classes of the component (Bonferroni-corrected),
  * a stratified check: within groups that share the other three components' levels, the median
    moves in the same direction in at least 75% of the groups that have both classes.
A link is kept when |delta| >= 0.33, p_corrected < 0.01, the measured direction matches the
expected physics, and the stratified check agrees. Writes configs/physics/hydraulic_links.yaml.
"""

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from scipy import stats

from sightglass.data.loader import load_cycles
from sightglass.physics.base import HEALTHY_LEVELS
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.utils.log import get_logger

logger = get_logger("analyze_links")

THRESHOLDS = {"min_abs_delta": 0.33, "max_p_corrected": 0.01, "min_strata_agreement": 0.75}

MOST_SEVERE = {
    "cooler_condition": 3,
    "valve_condition": 73,
    "pump_leakage": 2,
    "accumulator_pressure": 90,
}

# Expected physics (phases/02 step 2): feature -> direction as the fault gets worse.
CANDIDATES: dict[str, dict[str, str]] = {
    "cooler_condition": {
        "TS1.mean": "up",
        "TS2.mean": "up",
        "TS3.mean": "up",
        "TS4.mean": "up",
        "TS1.slope": "up",
        "cooler.delta_t": "down",
        "CE.mean": "down",
        "CP.mean": "down",
    },
    "valve_condition": {
        "PS1.rise_time": "up",
        "PS2.rise_time": "up",
        "PS1_PS2.lag": "up",
        "PS1.mean": "down",
        "PS2.mean": "down",
    },
    "pump_leakage": {
        "EPS1_per_FS1": "up",
        "FS1.mean": "down",
        "SE.mean": "down",
        "VS1.mean": "up",
    },
    "accumulator_pressure": {
        "PS1.ripple": "up",
        "PS2.ripple": "up",
        "PS3.ripple": "up",
        "PS4.ripple": "up",
        "PS5.ripple": "up",
        "PS6.ripple": "up",
        "PS1.peak": "down",
        "PS2.peak": "down",
    },
}

COMPONENTS = list(HEALTHY_LEVELS)


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """P(a > b) - P(a < b), via the Mann–Whitney U statistic."""
    u = stats.mannwhitneyu(a, b, alternative="two-sided").statistic
    return float(2.0 * u / (len(a) * len(b)) - 1.0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="configs/physics/hydraulic_links.yaml")
    args = ap.parse_args()

    train = load_cycles("hydraulic", split="train")
    ex = HydraulicExtractor()
    feats = [ex.extract(c) for c in train]
    labels = np.array([[c.labels[k] for k in COMPONENTS] for c in train])
    n_tests = sum(len(v) for v in CANDIDATES.values())
    logger.info(f"{len(train)} train cycles, {n_tests} candidate links")

    out: dict[str, list[dict[str, Any]]] = {}
    for ci, comp in enumerate(COMPONENTS):
        y = labels[:, ci]
        others = [j for j in range(4) if j != ci]
        rows: list[dict[str, Any]] = []
        for name, expected in CANDIDATES[comp].items():
            x = np.array([f[name].value for f in feats], dtype=np.float64)
            healthy = x[y == HEALTHY_LEVELS[comp]]
            severe = x[y == MOST_SEVERE[comp]]
            delta = cliffs_delta(severe, healthy)
            groups = [x[y == v] for v in np.unique(y)]
            p = float(stats.kruskal(*groups).pvalue)
            p_corr = min(1.0, p * n_tests)

            agree = total = 0
            strata = {tuple(r) for r in labels[:, others]}
            for s in strata:
                m = np.all(labels[:, others] == np.array(s), axis=1)
                h, sv = x[m & (y == HEALTHY_LEVELS[comp])], x[m & (y == MOST_SEVERE[comp])]
                if len(h) >= 5 and len(sv) >= 5:
                    total += 1
                    agree += int((np.median(sv) > np.median(h)) == (delta > 0))
            agreement = agree / total if total else None

            measured = "up" if delta > 0 else "down"
            kept = (
                abs(delta) >= THRESHOLDS["min_abs_delta"]
                and p_corr < THRESHOLDS["max_p_corrected"]
                and measured == expected
                and (agreement is None or agreement >= THRESHOLDS["min_strata_agreement"])
            )
            f0 = feats[0][name]
            rows.append(
                {
                    "feature": name,
                    "sensor": f0.sensor,
                    "quantity": f0.quantity,
                    "unit": f0.unit,
                    "direction": expected,
                    "measured_direction": measured,
                    "effect": round(delta, 3),
                    "p_value": float(f"{p_corr:.3g}"),
                    "strata_agreement": None if agreement is None else round(agreement, 3),
                    "strata_tested": total,
                    "kept": bool(kept),
                    "virtual": bool(f0.virtual),
                }
            )
            logger.info(
                f"{comp:22s} {name:16s} delta={delta:+.3f} p={p_corr:.2g} "
                f"strata={agree}/{total} kept={kept}"
            )
        rows.sort(key=lambda r: (not r["kept"], -abs(r["effect"])))
        out[comp] = rows

    header = (
        "# Physical links between features and components, MEASURED on the train split\n"
        "# by scripts/analyze_links.py (do not edit by hand; rerun the script).\n"
        f"# Kept when |Cliff's delta| >= {THRESHOLDS['min_abs_delta']}, Bonferroni-corrected\n"
        f"# Kruskal-Wallis p < {THRESHOLDS['max_p_corrected']}, measured direction == expected\n"
        f"# physics, and stratified agreement >= {THRESHOLDS['min_strata_agreement']}.\n"
        "# effect = Cliff's delta (most severe class vs healthy class).\n"
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)
    for comp, rows in out.items():
        logger.info(f"{comp}: kept {sum(r['kept'] for r in rows)}/{len(rows)}")


if __name__ == "__main__":
    main()
