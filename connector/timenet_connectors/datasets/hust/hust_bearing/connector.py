"""TimeNet Dataset Connector for HUST High-Frequency Bearing Dataset.

SYNTHETIC STAND-IN: generates fake records with the expected shapes; the real dataset is not
downloaded or converted yet. Nothing reported in this repository uses it.
"""

from pathlib import Path
from typing import Any

import numpy as np

HUST_URL = "https://data.mendeley.com/public-files/datasets/cbv7jyx4p9/files/hust_bearing.zip"
HUST_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

BEARING_GEOMETRIES = {
    "ER16K": {
        "pitch_diameter_mm": 38.52,
        "ball_diameter_mm": 7.94,
        "n_balls": 9,
        "contact_angle_deg": 0.0,
    },
    "6205_2RS": {
        "pitch_diameter_mm": 39.04,
        "ball_diameter_mm": 7.94,
        "n_balls": 9,
        "contact_angle_deg": 0.0,
    },
    "6207_2RS": {
        "pitch_diameter_mm": 53.50,
        "ball_diameter_mm": 11.11,
        "n_balls": 9,
        "contact_angle_deg": 0.0,
    },
}

DEFECT_TYPES = [
    "healthy",
    "inner_race",
    "outer_race",
    "ball",
    "cage",
    "combined",
]

WORKING_CONDITIONS = ["C1_1000rpm_0kN", "C2_1500rpm_2kN", "C3_1800rpm_4kN"]


class HUSTBearingConnector:
    """TimeNet BaseConnector implementation for HUST Bearings."""

    dataset_name = "hust_bearing"
    version = "1.0.0"

    def __init__(self, raw_dir: str | Path | None = None) -> None:
        self.raw_dir = Path(raw_dir) if raw_dir else Path("data/raw/hust_bearing")
        self.processed_dir = Path("data/processed/hust_bearing")

    def download(self, force: bool = False) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def convert(self, seed: int = 42) -> dict[str, Any]:
        """Convert HUST raw recordings into TimeNet TimeF format with leave-one-condition-out splits."""
        records = []
        rng = np.random.default_rng(seed)

        # 99 recordings: 5 bearing types, 6 defect types, 3 working conditions
        rec_id = 0
        for b_name, _geo in BEARING_GEOMETRIES.items():
            for defect in DEFECT_TYPES:
                for cond in WORKING_CONDITIONS:
                    if rec_id >= 99:
                        break
                    # Simulation of 51.2 kHz vibration (1 second = 51,200 points for smoke test)
                    fs = 51200.0
                    t = np.arange(10240) / fs
                    fr = 25.0 if "1500" in cond else (16.67 if "1000" in cond else 30.0)
                    sig = rng.normal(0, 0.5, size=len(t))

                    # If defect, add characteristic periodic impacts
                    if defect == "outer_race":
                        bpfo = (9 / 2) * fr * (1 - (7.94 / 38.52))
                        sig += 1.5 * np.sin(2 * np.pi * bpfo * t)

                    rec = {
                        "id": f"hust_bearing_{rec_id:03d}",
                        "recording_index": rec_id,
                        "bearing_type": b_name,
                        "defect_type": defect,
                        "working_condition": cond,
                        "shaft_speed_hz": fr,
                        "signals": {
                            "VIB": {
                                "rate_hz": fs,
                                "unit": "m/s^2",
                                "source": "accelerometer",
                                "values": sig.astype(np.float32),
                            }
                        },
                    }
                    records.append(rec)
                    rec_id += 1

        # Leave-one-condition-out splits: Train on C1 & C2, test on C3
        train_recs = [r["id"] for r in records if r["working_condition"] != "C3_1800rpm_4kN"]
        val_recs = [r["id"] for r in records if r["working_condition"] == "C2_1500rpm_2kN"][:15]
        test_recs = [r["id"] for r in records if r["working_condition"] == "C3_1800rpm_4kN"]

        return {
            "records": records,
            "splits": {
                "train": [rid for rid in train_recs if rid not in val_recs],
                "val": val_recs,
                "test": test_recs,
            },
        }


CONNECTOR = HUSTBearingConnector()
