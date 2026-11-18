"""B2: MiniRocket multivariate time-series baseline."""

import numpy as np
from sklearn.linear_model import RidgeClassifierCV

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle


class MiniRocketBaseline:
    """Multivariate random convolutional kernel feature baseline."""

    name: str = "B2_minirocket"

    def __init__(self, num_kernels: int = 200, resample_len: int = 60) -> None:
        self.num_kernels = num_kernels
        self.resample_len = resample_len
        self.models: dict[str, RidgeClassifierCV] = {}
        self.weights: np.ndarray | None = None
        self.biases: np.ndarray | None = None

    def _downsample_signals(self, cycles: list[Cycle]) -> np.ndarray:
        """Resample all 17 sensors to a uniform length (e.g., 60 points)."""
        sensors = sorted(cycles[0].signals.keys())
        all_data = []

        for c in cycles:
            cycle_channels = []
            for s in sensors:
                vals = c.signals[s].values
                if len(vals) == self.resample_len:
                    res = vals
                else:
                    idx = np.linspace(0, len(vals) - 1, self.resample_len).astype(int)
                    res = vals[idx]
                cycle_channels.append(res)
            all_data.append(cycle_channels)

        return np.array(all_data, dtype=np.float32)  # (N, n_channels, length)

    def _transform(self, X: np.ndarray, seed: int = 42) -> np.ndarray:
        """Fast multivariate random convolution transform (MiniRocket style)."""
        N, C, L = X.shape
        if self.weights is None:
            rng = np.random.default_rng(seed)
            # Random weights of length 9 across channels
            k_len = min(9, L)
            self.weights = rng.choice([-1.0, 2.0], size=(self.num_kernels, C, k_len))
            self.biases = rng.uniform(-1.0, 1.0, size=(self.num_kernels,))

        features = np.zeros((N, self.num_kernels * 2), dtype=np.float32)
        k_len = self.weights.shape[2]

        for i in range(N):
            sample = X[i]  # (C, L)
            for k in range(self.num_kernels):
                # 1D convolution across valid positions
                conv_out = np.zeros(L - k_len + 1, dtype=np.float32)
                for c in range(C):
                    conv_out += np.convolve(sample[c], self.weights[k, c, ::-1], mode="valid")
                conv_out += self.biases[k]

                # Proportion of positive values (PPV) and max value
                ppv = float(np.mean(conv_out > 0))
                max_v = float(np.max(conv_out))
                features[i, 2 * k] = ppv
                features[i, 2 * k + 1] = max_v

        return features

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        X_raw = self._downsample_signals(train)
        X_feats = self._transform(X_raw, seed=cfg.seed)

        components = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]
        for comp in components:
            y = np.array([c.labels[comp] for c in train])
            clf = RidgeClassifierCV(alphas=np.logspace(-3, 3, 7))
            clf.fit(X_feats, y)
            self.models[comp] = clf

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        X_raw = self._downsample_signals(cycles)
        X_feats = self._transform(X_raw)

        preds: list[Prediction] = []
        comp_preds = {comp: clf.predict(X_feats) for comp, clf in self.models.items()}

        for i, c in enumerate(cycles):
            labels = {comp: int(comp_preds[comp][i]) for comp in self.models}
            preds.append(
                Prediction(
                    cycle_id=c.id,
                    labels=labels,
                    probs=None,
                    rationale=None,
                )
            )
        return preds

# Validation: verify B2 MiniRocket feature transformation consistency
