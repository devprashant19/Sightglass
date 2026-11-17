"""Formatting utilities for numbers, deviations and units in physical rationales."""

import math


def format_number(value: float, unit: str = "") -> str:
    """Format a value to at most 3 significant figures (no thousands separators)."""
    if math.isnan(value) or math.isinf(value):
        return "0.0"

    abs_val = abs(value)
    if abs_val == 0.0:
        formatted = "0.0"
    elif abs_val >= 1000:
        formatted = f"{round(value):d}"
    elif abs_val >= 100:
        formatted = f"{round(value):d}"
    elif abs_val >= 10:
        formatted = f"{value:.1f}"
    elif abs_val >= 1:
        formatted = f"{value:.2f}"
    else:
        formatted = f"{value:.3g}"
        if "e" in formatted:
            formatted = f"{value:.4f}"

    if formatted in ("-0", "-0.0", "-0.00"):
        formatted = "0.0"
    return formatted


def format_pct(pct: float) -> str:
    """Format percentage to whole number."""
    return f"{round(abs(pct)):d}%"


def format_sigma(z: float) -> str:
    """Format a standard score to one decimal place, e.g. 3.1σ."""
    return f"{abs(z):.1f}σ"


def format_evidence_clause(
    sensor: str,
    quantity: str,
    value: float,
    unit: str,
    pct_diff: float,
    neutral_band: float = 2.0,
    z: float | None = None,
    sigma: bool = False,
    sigma_band: float = 1.0,
) -> str:
    """Format an evidence clause in the canonical grammar.

    Percentage form (healthy mean well away from zero):
        <SENSOR> <quantity> <value> <unit> (<pct>% <above|below> healthy)
        <SENSOR> <quantity> <value> <unit> (within <pct>% of healthy)
    Standard-deviation form (healthy mean near zero, e.g. slopes and lags):
        <SENSOR> <quantity> <value> <unit> (<z>σ <above|below> healthy)
        <SENSOR> <quantity> <value> <unit> (within 1.0σ of healthy)
    """
    head = f"{sensor} {quantity} {format_number(value, unit)} {unit}"
    if sigma:
        zz = z or 0.0
        if abs(zz) < sigma_band:
            return f"{head} (within {sigma_band:.1f}σ of healthy)"
        side = "above" if zz > 0 else "below"
        return f"{head} ({format_sigma(zz)} {side} healthy)"

    abs_pct = abs(pct_diff)
    if abs_pct <= neutral_band:
        return f"{head} (within {round(max(abs_pct, 1.0)):d}% of healthy)"
    side = "above" if pct_diff > 0 else "below"
    return f"{head} ({round(abs_pct):d}% {side} healthy)"
