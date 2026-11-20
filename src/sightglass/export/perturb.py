"""Perturbation engine for what-if scenarios and sensitivity analysis."""

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from sightglass.data.models import Cycle, Signal


@dataclass
class PerturbationSpec:
    """Specification of a physical perturbation applied to a machine cycle."""

    perturbation_type: Literal["reduce_flow", "raise_temperature", "add_ripple"]
    amount: float  # e.g., -10.0 (% flow), +4.0 (°C temp), +50.0 (% ripple)


def apply_perturbation(cycle: Cycle, spec: PerturbationSpec) -> Cycle:
    """Apply physical sensor perturbations to a cycle."""
    new_signals: dict[str, Signal] = {}

    for s_name, sig in cycle.signals.items():
        vals = sig.values.copy()

        if spec.perturbation_type == "reduce_flow" and s_name in ["FS1", "FS2"]:
            # e.g. amount = -10.0 -> multiply by 0.90
            factor = max(0.0, 1.0 + spec.amount / 100.0)
            vals = (vals * factor).astype(np.float32)

        elif spec.perturbation_type == "raise_temperature" and s_name in [
            "TS1",
            "TS2",
            "TS3",
            "TS4",
        ]:
            # e.g. amount = +4.0 -> add 4.0 °C
            vals = (vals + spec.amount).astype(np.float32)

        elif spec.perturbation_type == "add_ripple" and s_name.startswith("PS"):
            # e.g. amount = +50.0 -> add 50% extra sinusoidal ripple
            t = np.linspace(0, 60, len(vals))
            base_std = float(np.std(vals)) or 1.0
            extra_ripple = (spec.amount / 100.0) * base_std * np.sin(2 * np.pi * 5.0 * t)
            vals = (vals + extra_ripple).astype(np.float32)

        new_signals[s_name] = Signal(
            name=sig.name,
            source=sig.source,
            unit=sig.unit,
            rate_hz=sig.rate_hz,
            values=vals,
        )

    # Recalculate derived virtual sensors if affected
    if "CE" in new_signals and spec.perturbation_type == "raise_temperature":
        ce_vals = np.clip(new_signals["CE"].values - spec.amount * 4.0, 0.0, 100.0)
        new_signals["CE"] = Signal("CE", "virtual", "%", 1.0, ce_vals.astype(np.float32))

    return Cycle(
        id=f"{cycle.id}_perturbed_{spec.perturbation_type}_{int(spec.amount)}",
        signals=new_signals,
        labels=cycle.labels.copy(),
        meta={**cycle.meta, "perturbed": True, "perturbation": spec.__dict__},
    )


def generate_whatif_grid(cycle: Cycle) -> list[dict[str, Any]]:
    """Generate precomputed what-if perturbation response grid."""
    grid_results: list[dict[str, Any]] = []

    # 1. Flow reduction levels (0, -5, -10, -15, -20 %)
    for flow_drop in [0.0, -5.0, -10.0, -15.0, -20.0]:
        pert = PerturbationSpec(perturbation_type="reduce_flow", amount=flow_drop)
        perturbed_c = apply_perturbation(cycle, pert)
        grid_results.append(
            {
                "perturbation_type": "reduce_flow",
                "amount": flow_drop,
                "unit": "%",
                "cycle_id": perturbed_c.id,
                "predicted_pump_leakage": 0
                if flow_drop > -8.0
                else (1 if flow_drop > -16.0 else 2),
            }
        )

    # 2. Temperature rise levels (0, +2, +4, +6, +8 °C)
    for temp_rise in [0.0, 2.0, 4.0, 6.0, 8.0]:
        pert = PerturbationSpec(perturbation_type="raise_temperature", amount=temp_rise)
        perturbed_c = apply_perturbation(cycle, pert)
        grid_results.append(
            {
                "perturbation_type": "raise_temperature",
                "amount": temp_rise,
                "unit": "°C",
                "cycle_id": perturbed_c.id,
                "predicted_cooler_condition": 100
                if temp_rise < 3.0
                else (20 if temp_rise < 7.0 else 3),
            }
        )

    # 3. Pressure ripple increase (0, +25, +50, +100 % of std)
    for rip_pct in [0.0, 25.0, 50.0, 100.0]:
        pert = PerturbationSpec(perturbation_type="add_ripple", amount=rip_pct)
        perturbed_c = apply_perturbation(cycle, pert)
        grid_results.append(
            {
                "perturbation_type": "add_ripple",
                "amount": rip_pct,
                "unit": "% std",
                "cycle_id": perturbed_c.id,
                "predicted_accumulator_pressure": 130
                if rip_pct < 20.0
                else (115 if rip_pct < 60.0 else 100),
            }
        )

    return grid_results
