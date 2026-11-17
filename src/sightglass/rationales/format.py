"""Formatting utilities for numbers, percentages, and units in physical rationales."""

import math


def format_number(value: float, unit: str = "") -> str:
    """Format a numerical value to 3 significant figures without thousands separators."""
    if math.isnan(value) or math.isinf(value):
        return "0.0"

    abs_val = abs(value)
    if abs_val == 0.0:
        formatted = "0.0"
    elif abs_val >= 1000:
        formatted = f"{round(value):d}"
    elif abs_val >= 100:
        formatted = f"{value:.1f}" if value % 1 != 0 else f"{round(value):d}"
    elif abs_val >= 10:
        formatted = f"{value:.1f}"
    elif abs_val >= 1:
        formatted = f"{value:.2f}"
    else:
        # e.g., 0.0523
        formatted = f"{value:.3f}".rstrip("0").rstrip(".")

    # Avoid negative zero
    if formatted == "-0" or formatted == "-0.0":
        formatted = "0.0"

    return formatted


def format_pct(pct: float) -> str:
    """Format percentage to whole number."""
    return f"{round(abs(pct)):d}%"


def format_evidence_clause(
    sensor: str,
    quantity: str,
    value: float,
    unit: str,
    pct_diff: float,
    neutral_band: float = 2.0,
) -> str:
    """Format an evidence clause adhering strictly to the canonical grammar:

    <SENSOR> <quantity> <value> <unit> (<pct>% <above|below> healthy)
    <SENSOR> <quantity> <value> <unit> (within <pct>% of healthy)
    """
    val_str = format_number(value, unit)
    abs_pct = abs(pct_diff)

    if abs_pct <= neutral_band:
        clause = f"{sensor} {quantity} {val_str} {unit} (within {round(max(abs_pct, 1.0)):d}% of healthy)"
    elif pct_diff > 0:
        clause = f"{sensor} {quantity} {val_str} {unit} ({round(abs_pct):d}% above healthy)"
    else:
        clause = f"{sensor} {quantity} {val_str} {unit} ({round(abs_pct):d}% below healthy)"

    return clause

# Fix: eliminate ambiguous clause formatting in cooling efficiency claims
