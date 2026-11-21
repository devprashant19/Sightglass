"""B1: Physical Features + LightGBM baseline."""

import lightgbm as lgb
import numpy as np

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle
from sightglass.physics.hydraulic import HydraulicExtractor


class LightGBMBaseline:
    """Gradient boosting trained on extracted physical features."""

    def __init__(self, name: str = "B1_lightgbm", drop_virtual: bool = False) -> None:
        self.name = name
        self.drop_virtual = drop_virtual
        self.models: dict[str, lgb.LGBMClassifier] = {}
        self.feature_names: list[str] = []
        self.feature_importances: dict[str, dict[str, float]] = {}
        self.extractor = HydraulicExtractor()

    def _extract_matrix(self, cycles: list[Cycle]) -> tuple[np.ndarray, list[str]]:
        rows = []
        feat_names = None
        for c in cycles:
            feats = self.extractor.extract(c)
            if self.drop_virtual:
                feats = {k: v for k, v in feats.items() if not v.virtual}
            if feat_names is None:
                feat_names = sorted(feats.keys())
            rows.append([feats[k].value for k in feat_names])
        return np.array(rows, dtype=np.float32), (feat_names or [])

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        X_train, feat_names = self._extract_matrix(train)
        self.feature_names = feat_names

        components = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]

        for comp in components:
            y_train = np.array([c.labels[comp] for c in train])
            clf = lgb.LGBMClassifier(
                n_estimators=50,
                learning_rate=0.08,
                random_state=cfg.seed,
                verbosity=-1,
            )
            clf.fit(X_train, y_train)
            self.models[comp] = clf

            # Store feature importances (gain)
            importances = clf.booster_.feature_importance(importance_type="gain")
            self.feature_importances[comp] = {
                fn: float(imp) for fn, imp in zip(feat_names, importances, strict=False)
            }

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        X, _ = self._extract_matrix(cycles)
        preds: list[Prediction] = []

        comp_preds: dict[str, np.ndarray] = {}
        comp_probs: dict[str, np.ndarray] = {}

        for comp, clf in self.models.items():
            comp_preds[comp] = clf.predict(X)
            comp_probs[comp] = clf.predict_proba(X)

        for i, c in enumerate(cycles):
            labels = {comp: int(comp_preds[comp][i]) for comp in self.models}
            probs = {
                comp: {
                    int(cls): float(comp_probs[comp][i][idx])
                    for idx, cls in enumerate(self.models[comp].classes_)
                }
                for comp in self.models
            }
            preds.append(
                Prediction(
                    cycle_id=c.id,
                    labels=labels,
                    probs=probs,
                    rationale=None,
                )
            )
        return preds
