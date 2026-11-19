"""B3: 1D-CNN multivariate time-series baseline."""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.data.models import Cycle

COOLER_MAP = {3: 0, 20: 1, 100: 2}
COOLER_INV = {0: 3, 1: 20, 2: 100}

VALVE_MAP = {73: 0, 80: 1, 90: 2, 100: 3}
VALVE_INV = {0: 73, 1: 80, 2: 90, 3: 100}

PUMP_MAP = {0: 0, 1: 1, 2: 2}
PUMP_INV = {0: 0, 1: 1, 2: 2}

ACC_MAP = {90: 0, 100: 1, 115: 2, 130: 3}
ACC_INV = {0: 90, 1: 100, 2: 115, 3: 130}


class Conv1DNet(nn.Module):
    """4-block 1D CNN with global average pooling and 4 classification heads."""

    def __init__(self, in_channels: int = 17, hidden_dim: int = 64):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(in_channels, hidden_dim, kernel_size=5, padding=2),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, padding=2),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(hidden_dim, hidden_dim * 2, kernel_size=5, padding=2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(hidden_dim * 2, hidden_dim * 2, kernel_size=5, padding=2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        dim = hidden_dim * 2
        self.head_cooler = nn.Linear(dim, 3)
        self.head_valve = nn.Linear(dim, 4)
        self.head_pump = nn.Linear(dim, 3)
        self.head_acc = nn.Linear(dim, 4)

    def forward(
        self, x: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        feat = self.conv(x).squeeze(-1)
        return (
            self.head_cooler(feat),
            self.head_valve(feat),
            self.head_pump(feat),
            self.head_acc(feat),
        )


class CNN1DBaseline:
    """End-to-end 1D convolutional network baseline."""

    name: str = "B3_cnn1d"

    def __init__(
        self,
        in_channels: int = 17,
        resample_len: int = 600,
        epochs: int = 5,
        batch_size: int = 16,
        lr: float = 1e-3,
        device: str | None = None,
    ):
        self.in_channels = in_channels
        self.resample_len = resample_len
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Conv1DNet(in_channels=in_channels).to(self.device)

    def _prepare_tensors(self, cycles: list[Cycle]) -> torch.Tensor:
        sensors = sorted(cycles[0].signals.keys())
        all_arr = []
        for c in cycles:
            ch_list = []
            for s in sensors:
                v = c.signals[s].values
                if len(v) == self.resample_len:
                    res = v
                else:
                    idx = np.linspace(0, len(v) - 1, self.resample_len).astype(int)
                    res = v[idx]
                # Normalize per sensor channel
                m = float(np.mean(res))
                s_std = float(np.std(res)) or 1.0
                norm_res = (res - m) / s_std
                ch_list.append(norm_res)
            all_arr.append(ch_list)
        return torch.tensor(np.array(all_arr, dtype=np.float32))

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None:
        torch.manual_seed(cfg.seed)
        X_train = self._prepare_tensors(train)
        y_c = torch.tensor(
            [COOLER_MAP[c.labels["cooler_condition"]] for c in train], dtype=torch.long
        )
        y_v = torch.tensor(
            [VALVE_MAP[c.labels["valve_condition"]] for c in train], dtype=torch.long
        )
        y_p = torch.tensor([PUMP_MAP[c.labels["pump_leakage"]] for c in train], dtype=torch.long)
        y_a = torch.tensor(
            [ACC_MAP[c.labels["accumulator_pressure"]] for c in train], dtype=torch.long
        )

        dataset = TensorDataset(X_train, y_c, y_v, y_p, y_a)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.lr, weight_decay=1e-3)
        criterion = nn.CrossEntropyLoss()

        self.model.train()
        for _epoch in range(self.epochs):
            for bx, by_c, by_v, by_p, by_a in loader:
                bx = bx.to(self.device)
                by_c = by_c.to(self.device)
                by_v = by_v.to(self.device)
                by_p = by_p.to(self.device)
                by_a = by_a.to(self.device)

                optimizer.zero_grad()
                out_c, out_v, out_p, out_a = self.model(bx)
                loss = (
                    criterion(out_c, by_c)
                    + criterion(out_v, by_v)
                    + criterion(out_p, by_p)
                    + criterion(out_a, by_a)
                )
                loss.backward()
                optimizer.step()

    def predict(self, cycles: list[Cycle]) -> list[Prediction]:
        self.model.eval()
        X = self._prepare_tensors(cycles)
        preds: list[Prediction] = []

        with torch.no_grad():
            out_c, out_v, out_p, out_a = self.model(X.to(self.device))
            pred_c = torch.argmax(out_c, dim=1).cpu().numpy()
            pred_v = torch.argmax(out_v, dim=1).cpu().numpy()
            pred_p = torch.argmax(out_p, dim=1).cpu().numpy()
            pred_a = torch.argmax(out_a, dim=1).cpu().numpy()

        for i, c in enumerate(cycles):
            labels = {
                "cooler_condition": COOLER_INV[int(pred_c[i])],
                "valve_condition": VALVE_INV[int(pred_v[i])],
                "pump_leakage": PUMP_INV[int(pred_p[i])],
                "accumulator_pressure": ACC_INV[int(pred_a[i])],
            }
            preds.append(
                Prediction(
                    cycle_id=c.id,
                    labels=labels,
                    probs=None,
                    rationale=None,
                )
            )
        return preds
