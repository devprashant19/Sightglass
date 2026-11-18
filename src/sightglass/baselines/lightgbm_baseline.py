"""B1: physics features + LightGBM, one classifier per component, tuned on the val split."""

import itertools

import lightgbm as lgb
import numpy as np
from sklearn.metrics import f1_score

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle
from sightglass.physics.base import Feature
from sightglass.physics.hydraulic import HydraulicExtractor

COMPONENTS = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]
GRID: dict[str, list[float]] = {
    "num_leaves": [15, 31],
    "n_estimators": [100, 300],
    "learning_rate": [0.05, 0.1],
}


class LightGBMBaseline:
    """Gradient boosting on the Phase 2 physics features."""

    def __init__(self, name: str = "B1_lightgbm", drop_virtual: bool = False) -> None:
        self.name = name
        self.drop_virtual = drop_virtual
        self.models: dict[str, lgb.LGBMClassifier] = {}
        self.feature_names: list[str] = []
        self.feature_importances: dict[str, dict[str, float]] = {}
        self.best_params: dict[str, dict[str, float]] = {}
        self.extractor = HydraulicExtractor()

    def matrix_from_features(self, feats: list[dict[str, Feature]]) -> np.ndarray:
        if not self.feature_names:
            self.feature_names = sorted(
                k for k, v in feats[0].items() if not (self.drop_virtual and v.virtual)
            )
        return np.array([[f[k].value for k in self.feature_names] for f in feats], dtype=np.float64)

    def _matrix(self, cycles: list[Cycle]) -> np.ndarray:
        return self.matrix_from_features([self.extractor.extract(c) for c in cycles])

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        X = self._matrix(train)
        Xv = self._matrix(val) if val else None
        self.fit_matrix(X, [c.labels for c in train], Xv, [c.labels for c in val], cfg.seed)

    def fit_matrix(
        self,
        X: np.ndarray,
        y_labels: list[dict[str, int]],
        Xv: np.ndarray | None,
        yv_labels: list[dict[str, int]],
        seed: int,
    ) -> None:
        """Grid-search each component on val macro-F1, then refit with the best settings."""
        for comp in COMPONENTS:
            y = np.array([lb[comp] for lb in y_labels])
            best_score, best_params = -1.0, {k: v[0] for k, v in GRID.items()}
            if Xv is not None:
                yv = np.array([lb[comp] for lb in yv_labels])
                for nl, ne, lr in itertools.product(*GRID.values()):
                    params = {"num_leaves": nl, "n_estimators": ne, "learning_rate": lr}
                    clf = lgb.LGBMClassifier(**params, random_state=seed, verbosity=-1)
                    clf.fit(X, y)
                    score = float(f1_score(yv, clf.predict(Xv), average="macro"))
                    if score > best_score:
                        best_score, best_params = score, params
            clf = lgb.LGBMClassifier(**best_params, random_state=seed, verbosity=-1)
            clf.fit(X, y)
            self.models[comp] = clf
            self.best_params[comp] = {**best_params, "val_macro_f1": best_score}
            gains = clf.booster_.feature_importance(importance_type="gain")
            self.feature_importances[comp] = {
                fn: float(g) for fn, g in zip(self.feature_names, gains, strict=True)
            }

    def predict_matrix(
        self, X: np.ndarray
    ) -> list[tuple[dict[str, int], dict[str, dict[int, float]]]]:
        preds = {c: m.predict(X) for c, m in self.models.items()}
        probs = {c: m.predict_proba(X) for c, m in self.models.items()}
        out = []
        for i in range(X.shape[0]):
            labels = {c: int(preds[c][i]) for c in self.models}
            pr = {
                c: {int(k): float(probs[c][i][j]) for j, k in enumerate(self.models[c].classes_)}
                for c in self.models
            }
            out.append((labels, pr))
        return out

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        res = self.predict_matrix(self._matrix(cycles))
        return [Prediction(c.id, lb, pr, None) for c, (lb, pr) in zip(cycles, res, strict=True)]
