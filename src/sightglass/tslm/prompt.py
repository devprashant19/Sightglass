"""Prompt building, downsampling with anti-aliasing, and normalisation for OpenTSLM."""

import json
from pathlib import Path

import numpy as np
from scipy import signal

from sightglass.data.models import Cycle

DEFAULT_RATES_HZ: dict[str, float] = {
    "PS1": 10.0,
    "PS2": 10.0,
    "PS3": 10.0,
    "PS4": 10.0,
    "PS5": 10.0,
    "PS6": 10.0,
    "EPS1": 10.0,
    "FS1": 10.0,
    "FS2": 10.0,
    "TS1": 1.0,
    "TS2": 1.0,
    "TS3": 1.0,
    "TS4": 1.0,
    "VS1": 1.0,
    "CE": 1.0,
    "CP": 1.0,
    "SE": 1.0,
}


def downsample_signals(
    cycle: Cycle,
    target_rates: dict[str, float] | None = None,
) -> dict[str, np.ndarray]:
    """Downsample high-rate signals (e.g. 100 Hz to 10 Hz) using decimation."""
    rates = target_rates or DEFAULT_RATES_HZ
    downsampled: dict[str, np.ndarray] = {}

    for s_name, sig in cycle.signals.items():
        arr = sig.values
        target_rate = rates.get(s_name, sig.rate_hz)
        factor = int(round(sig.rate_hz / target_rate))

        if factor > 1:
            # Apply decimation (lowpass filter + downsample)
            dec = signal.decimate(arr, factor, ftype="iir", zero_phase=True)
            downsampled[s_name] = dec.astype(np.float32)
        else:
            downsampled[s_name] = arr.copy()

    return downsampled


def compute_normalisation_statistics(
    train_cycles: list[Cycle],
    target_rates: dict[str, float] | None = None,
    save_path: str | Path | None = "data/reference/hydraulic_norm.json",
) -> dict[str, dict[str, float]]:
    """Compute per-sensor mean and std strictly on train split."""
    all_downsampled: dict[str, list[np.ndarray]] = {}

    for c in train_cycles:
        down = downsample_signals(c, target_rates)
        for s_name, arr in down.items():
            if s_name not in all_downsampled:
                all_downsampled[s_name] = []
            all_downsampled[s_name].append(arr)

    norm_stats: dict[str, dict[str, float]] = {}
    for s_name, arr_list in all_downsampled.items():
        concatenated = np.concatenate(arr_list)
        m = float(np.mean(concatenated))
        s = float(np.std(concatenated)) or 1.0
        norm_stats[s_name] = {"mean": m, "std": s}

    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(norm_stats, f, indent=2)

    return norm_stats


def build_prompt_and_series(
    cycle: Cycle,
    norm_stats: dict[str, dict[str, float]],
    target_rates: dict[str, float] | None = None,
    drop_sensors: list[str] | None = None,
    question: str = "Question: Diagnose this hydraulic cycle.",
) -> tuple[str, list[np.ndarray]]:
    """Construct OpenTSLM multimodal text prompt with embedded <TS> markers and normalized arrays."""
    dropped = set(drop_sensors or [])
    downsampled = downsample_signals(cycle, target_rates)
    rates = target_rates or DEFAULT_RATES_HZ

    lines = [
        "You are a machine-health assistant for a hydraulic test rig.",
        "The cycle lasts 60 s. Sensors follow, each with its unit, rate and scale.",
        "",
    ]
    series_list: list[np.ndarray] = []

    for s_name in sorted(cycle.signals.keys()):
        if s_name in dropped:
            continue
        sig = cycle.signals[s_name]
        arr = downsampled[s_name]
        stats = norm_stats.get(s_name, {"mean": 0.0, "std": 1.0})
        m, s = stats["mean"], stats["std"]

        # Normalized values
        norm_arr = (arr - m) / s
        series_list.append(norm_arr)

        rate_val = rates.get(s_name, sig.rate_hz)
        lines.append(
            f"{s_name} {sig.source} ({sig.unit}), {rate_val:.0f} Hz, mean {m:.1f}, std {s:.1f}: <TS>"
        )

    lines.append("")
    lines.append(question)
    prompt_text = "\n".join(lines)

    return prompt_text, series_list
