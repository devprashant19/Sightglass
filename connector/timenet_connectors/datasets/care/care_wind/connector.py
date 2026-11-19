"""TimeNet Dataset Connector for CARE Wind Turbine SCADA Telemetry.

SYNTHETIC STAND-IN: generates fake records with the expected shapes; the real dataset is not
downloaded or converted yet. Nothing reported in this repository uses it.
"""

from pathlib import Path
from typing import Any

import numpy as np

CARE_URL = "https://example.com/care_wind.zip"
CARE_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

TURBINES = ["WTG01", "WTG02", "WTG03", "WTG04", "WTG05", "WTG06"]
COMPONENTS = ["normal", "gearbox", "generator", "main_bearing", "transformer"]


class CAREWindConnector:
    """TimeNet BaseConnector implementation for CARE Wind SCADA."""

    dataset_name = "care_wind"
    version = "1.0.0"

    def __init__(self, raw_dir: str | Path | None = None) -> None:
        self.raw_dir = Path(raw_dir) if raw_dir else Path("data/raw/care_wind")
        self.processed_dir = Path("data/processed/care_wind")

    def download(self, force: bool = False) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def convert(self, seed: int = 42) -> dict[str, Any]:
        """Convert CARE SCADA time series into TimeNet TimeF format with turbine-grouped splits."""
        records = []
        rng = np.random.default_rng(seed)

        # 10-minute sampling rate = 6 samples / hour = 144 samples / day
        # 30-day monitoring period per turbine record = 4,320 timesteps
        n_steps = 4320
        fs = 1.0 / 600.0  # ~0.001667 Hz

        for turbine_id in TURBINES:
            # Synthetic realistic SCADA series
            wind = np.clip(rng.weibull(2.0, size=n_steps) * 8.0, 0.0, 25.0)
            power = np.clip((wind**3) * 1.5, 0.0, 2000.0)
            amb = 15.0 + 5.0 * np.sin(np.linspace(0, 2 * np.pi * 30, n_steps))

            # Expected gearbox temperature: function of power and ambient
            gearbox_expected = amb + 0.02 * power + rng.normal(0, 1.0, size=n_steps)

            # Introduce an overheating fault in WTG05 & WTG06 (test turbines) in second half
            has_fault = turbine_id in ["WTG05", "WTG06"]
            gearbox_measured = gearbox_expected.copy()
            if has_fault:
                # Drift upwards starting day 18 (step 2592)
                drift_steps = np.arange(n_steps - 2592)
                gearbox_measured[2592:] += 0.005 * drift_steps  # rising trend up to +8.6 °C

            rec = {
                "id": f"care_{turbine_id}",
                "turbine_id": turbine_id,
                "n_steps": n_steps,
                "has_fault": has_fault,
                "fault_component": "gearbox" if has_fault else "normal",
                "fault_start_step": 3600 if has_fault else None,  # Fault occurs on day 25
                "signals": {
                    "active_power_kw": {
                        "rate_hz": fs,
                        "unit": "kW",
                        "values": power.astype(np.float32),
                    },
                    "wind_speed_ms": {
                        "rate_hz": fs,
                        "unit": "m/s",
                        "values": wind.astype(np.float32),
                    },
                    "ambient_temp_c": {
                        "rate_hz": fs,
                        "unit": "°C",
                        "values": amb.astype(np.float32),
                    },
                    "gearbox_bearing_temp_c": {
                        "rate_hz": fs,
                        "unit": "°C",
                        "values": gearbox_measured.astype(np.float32),
                    },
                },
            }
            records.append(rec)

        # Disjoint turbine-level split: WTG01-WTG03 train, WTG04 val, WTG05-WTG06 test
        splits = {
            "train": ["care_WTG01", "care_WTG02", "care_WTG03"],
            "val": ["care_WTG04"],
            "test": ["care_WTG05", "care_WTG06"],
        }

        return {"records": records, "splits": splits}


CONNECTOR = CAREWindConnector()
