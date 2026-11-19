"""Sightglass model adaptation and OpenTSLM model wrapper."""

from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from sightglass.utils.log import get_logger

logger = get_logger("tslm_model")


class SmokeTemporalAdapter(nn.Module):
    """Lightweight temporal projection adapter for CPU smoke training and testing."""

    def __init__(self, in_features: int = 17, hidden_dim: int = 128, vocab_size: int = 1000):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, in_features)
        h = self.encoder(x)
        return self.head(h)


class SightglassModel:
    """Unified Sightglass TSLM model wrapper."""

    def __init__(
        self,
        backbone: str = "meta-llama/Llama-3.2-1B",
        variant: str = "flamingo",
        device: str = "cpu",
        is_smoke: bool = False,
    ):
        self.backbone = backbone
        self.variant = variant
        self.device = device
        self.is_smoke = is_smoke
        self.model: Any = None
        self._init_model()

    def _init_model(self) -> None:
        if self.is_smoke or self.device == "cpu":
            logger.info(f"Initializing CPU smoke model for {self.backbone} ({self.variant})...")
            self.model = SmokeTemporalAdapter().to(self.device)
        else:
            try:
                from opentslm.model.llm.OpenTSLMFlamingo import OpenTSLMFlamingo

                logger.info(
                    f"Loading OpenTSLMFlamingo with backbone {self.backbone} on {self.device}..."
                )
                self.model = OpenTSLMFlamingo(device=self.device, llm_id=self.backbone)
            except Exception as e:
                logger.warning(f"Could not load OpenTSLM ({e}); falling back to standard adapter.")
                self.model = SmokeTemporalAdapter().to(self.device)

    def save_checkpoint(self, path: str | Path, epoch: int, step: int) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "epoch": epoch,
                "step": step,
                "model_state": self.model.state_dict(),
                "backbone": self.backbone,
                "variant": self.variant,
            },
            p,
        )
        logger.info(f"Saved checkpoint to {p}")

    def load_checkpoint(self, path: str | Path) -> None:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {p}")
        checkpoint = torch.load(p, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state"])
        logger.info(f"Loaded checkpoint from {p} (epoch {checkpoint.get('epoch')})")
