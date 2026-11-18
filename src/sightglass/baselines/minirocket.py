"""B2: MiniRocket (sktime MiniRocketMultivariate) + ridge classifier on raw signals."""

from typing import Any

import numpy as np
from sklearn.linear_model import RidgeClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle

COMPONENTS = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]


class MiniRocketBaseline:
    """All 17 sensors bin-averaged to a common length, MiniRocket features, ridge per component."""

    name: str = "B2_minirocket"

    def __init__(self, num_kernels: int = 10000, resample_len: int = 60) -> None:
        self.num_kernels = num_kernels
        self.resample_len = resample_len
        self.transform: Any = None
        self.models: dict[str, Any] = {}
        self.sensors: list[str] = []

    def _panel(self, cycles: list[Cycle]) -> np.ndarray:
        if not self.sensors:
            self.sensors = sorted(cycles[0].signals)
        L = self.resample_len
        out = np.empty((len(cycles), len(self.sensors), L), dtype=np.float32)
        for i, c in enumerate(cycles):
            for j, s in enumerate(self.sensors):
                v = c.signals[s].values
                out[i, j] = v[: len(v) // L * L].reshape(L, -1).mean(axis=1)
        return out

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        from sktime.transformations.panel.rocket import MiniRocketMultivariate

        self.transform = MiniRocketMultivariate(num_kernels=self.num_kernels, random_state=cfg.seed)
        F = self.transform.fit_transform(self._panel(train))
        for comp in COMPONENTS:
            y = np.array([c.labels[comp] for c in train])
            clf = make_pipeline(StandardScaler(), RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)))
            clf.fit(F, y)
            self.models[comp] = clf

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        F = self.transform.transform(self._panel(cycles))
        preds = {c: m.predict(F) for c, m in self.models.items()}
        return [
            Prediction(cy.id, {c: int(preds[c][i]) for c in self.models}, None, None)
            for i, cy in enumerate(cycles)
        ]
