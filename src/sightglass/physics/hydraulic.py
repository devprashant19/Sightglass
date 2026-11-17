"""Physics feature extraction for the hydraulic test rig."""

from typing import ClassVar

import numpy as np
from scipy import signal

from sightglass.data.models import Cycle
from sightglass.physics.base import Feature


class HydraulicExtractor:
    """Extracts domain-grounded physical features from a 60-second hydraulic cycle."""

    dataset: str = "hydraulic"

    PRESSURE_SENSORS: ClassVar[list[str]] = ["PS1", "PS2", "PS3", "PS4", "PS5", "PS6"]
    TEMP_SENSORS: ClassVar[list[str]] = ["TS1", "TS2", "TS3", "TS4"]
    FLOW_SENSORS: ClassVar[list[str]] = ["FS1", "FS2"]
    POWER_SENSORS: ClassVar[list[str]] = ["EPS1"]
    VIB_SENSORS: ClassVar[list[str]] = ["VS1"]
    VIRTUAL_SENSORS: ClassVar[list[str]] = ["CE", "CP", "SE"]

    def feature_names(self) -> list[str]:
        names: list[str] = []
        for s in self.PRESSURE_SENSORS:
            names.extend([f"{s}.mean", f"{s}.peak", f"{s}.ripple", f"{s}.rise_time"])
        names.append("PS1_PS2.lag")
        for s in self.FLOW_SENSORS:
            names.append(f"{s}.mean")
        for s in self.POWER_SENSORS:
            names.append(f"{s}.mean")
        names.append("EPS1_per_FS1")
        for s in self.TEMP_SENSORS:
            names.extend([f"{s}.mean", f"{s}.slope"])
        names.append("cooler.delta_t")
        for s in self.VIB_SENSORS:
            names.extend([f"{s}.mean", f"{s}.peak"])
        for s in self.VIRTUAL_SENSORS:
            names.append(f"{s}.mean")
        return names

    def extract(self, cycle: Cycle) -> dict[str, Feature]:
        features: dict[str, Feature] = {}
        sigs = cycle.signals

        # 1. Pressure sensors (PS1 - PS6, 100 Hz, 6000 samples)
        for s in self.PRESSURE_SENSORS:
            if s in sigs:
                arr = sigs[s].values
                dt = 1.0 / sigs[s].rate_hz
                m_val = float(np.mean(arr))
                p_val = float(np.max(arr))
                r_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0

                features[f"{s}.mean"] = Feature(
                    name=f"{s}.mean",
                    sensor=s,
                    quantity="mean pressure",
                    unit="bar",
                    value=m_val,
                    window=(0.0, 60.0),
                )
                features[f"{s}.peak"] = Feature(
                    name=f"{s}.peak",
                    sensor=s,
                    quantity="peak pressure",
                    unit="bar",
                    value=p_val,
                    window=(0.0, 60.0),
                )
                features[f"{s}.ripple"] = Feature(
                    name=f"{s}.ripple",
                    sensor=s,
                    quantity="pressure ripple",
                    unit="bar",
                    value=r_val,
                    window=(0.0, 60.0),
                )

                # Rise time: 10% to 90% of the primary pressure step in cycle
                min_p = float(np.min(arr))
                span = p_val - min_p
                if span > 1.0:
                    t10 = np.where(arr >= min_p + 0.10 * span)[0]
                    t90 = np.where(arr >= min_p + 0.90 * span)[0]
                    idx10 = int(t10[0]) if len(t10) > 0 else 0
                    idx90 = int(t90[0]) if len(t90) > 0 else len(arr) - 1
                    rise_time_s = max(0.01, float(idx90 - idx10) * dt)
                else:
                    rise_time_s = 0.50

                features[f"{s}.rise_time"] = Feature(
                    name=f"{s}.rise_time",
                    sensor=s,
                    quantity="pressure rise time",
                    unit="s",
                    value=rise_time_s,
                    window=(0.0, 15.0),
                )

        # Cross-correlation lag between PS1 and PS2
        if "PS1" in sigs and "PS2" in sigs:
            p1 = sigs["PS1"].values
            p2 = sigs["PS2"].values
            dt = 1.0 / sigs["PS1"].rate_hz
            corr = signal.correlate(p2 - np.mean(p2), p1 - np.mean(p1), mode="same", method="fft")
            lags = signal.correlation_lags(len(p2), len(p1), mode="same")
            lag_idx = int(lags[np.argmax(corr)])
            lag_s = abs(float(lag_idx * dt))
            features["PS1_PS2.lag"] = Feature(
                name="PS1_PS2.lag",
                sensor="PS1/PS2",
                quantity="valve switching lag",
                unit="s",
                value=lag_s,
                window=(2.0, 10.0),
            )

        # 2. Flow sensors (FS1, FS2, 10 Hz, 600 samples)
        for s in self.FLOW_SENSORS:
            if s in sigs:
                arr = sigs[s].values
                features[f"{s}.mean"] = Feature(
                    name=f"{s}.mean",
                    sensor=s,
                    quantity="mean volume flow",
                    unit="l/min",
                    value=float(np.mean(arr)),
                    window=(0.0, 60.0),
                )

        # 3. Motor power (EPS1, 100 Hz, 6000 samples)
        if "EPS1" in sigs:
            arr = sigs["EPS1"].values
            eps_mean = float(np.mean(arr))
            features["EPS1.mean"] = Feature(
                name="EPS1.mean",
                sensor="EPS1",
                quantity="mean motor power",
                unit="W",
                value=eps_mean,
                window=(0.0, 60.0),
            )

            # Leakage indicator: Power per unit flow
            if "FS1" in sigs:
                fs1_mean = float(np.mean(sigs["FS1"].values))
                power_flow_ratio = eps_mean / max(0.1, fs1_mean)
                features["EPS1_per_FS1"] = Feature(
                    name="EPS1_per_FS1",
                    sensor="EPS1/FS1",
                    quantity="power-to-flow ratio",
                    unit="W·min/l",
                    value=float(power_flow_ratio),
                    window=(0.0, 60.0),
                )

        # 4. Temperature sensors (TS1 - TS4, 1 Hz, 60 samples)
        for s in self.TEMP_SENSORS:
            if s in sigs:
                arr = sigs[s].values
                t = np.arange(len(arr)) / 60.0  # minutes
                if len(arr) > 1:
                    slope_val = float(np.polyfit(t, arr, 1)[0])  # °C / min
                else:
                    slope_val = 0.0

                features[f"{s}.mean"] = Feature(
                    name=f"{s}.mean",
                    sensor=s,
                    quantity="mean temperature",
                    unit="°C",
                    value=float(np.mean(arr)),
                    window=(0.0, 60.0),
                )
                features[f"{s}.slope"] = Feature(
                    name=f"{s}.slope",
                    sensor=s,
                    quantity="temperature slope",
                    unit="°C/min",
                    value=slope_val,
                    window=(0.0, 60.0),
                )

        # Cooler delta T: TS1 (cooler inlet) minus TS2 (cooler outlet)
        if "TS1" in sigs and "TS2" in sigs:
            delta_t = float(np.mean(sigs["TS1"].values) - np.mean(sigs["TS2"].values))
            features["cooler.delta_t"] = Feature(
                name="cooler.delta_t",
                sensor="TS1-TS2",
                quantity="cooler temperature difference",
                unit="°C",
                value=delta_t,
                window=(0.0, 60.0),
            )

        # 5. Vibration (VS1, 1 Hz, 60 samples)
        if "VS1" in sigs:
            arr = sigs["VS1"].values
            features["VS1.mean"] = Feature(
                name="VS1.mean",
                sensor="VS1",
                quantity="mean vibration",
                unit="mm/s",
                value=float(np.mean(arr)),
                window=(0.0, 60.0),
            )
            features["VS1.peak"] = Feature(
                name="VS1.peak",
                sensor="VS1",
                quantity="peak vibration",
                unit="mm/s",
                value=float(np.max(arr)),
                window=(0.0, 60.0),
            )

        # 6. Virtual sensors (CE, CP, SE, 1 Hz, 60 samples)
        virtual_quantities = {
            "CE": ("cooling efficiency", "%"),
            "CP": ("cooling power", "kW"),
            "SE": ("system efficiency factor", "%"),
        }
        for s, (q, u) in virtual_quantities.items():
            if s in sigs:
                arr = sigs[s].values
                features[f"{s}.mean"] = Feature(
                    name=f"{s}.mean",
                    sensor=s,
                    quantity=q,
                    unit=u,
                    value=float(np.mean(arr)),
                    window=(0.0, 60.0),
                    virtual=True,
                )

        return features
