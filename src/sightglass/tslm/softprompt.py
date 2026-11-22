"""A small time-series language model: native-rate sensor patches as soft prompts to a causal LM.

Each sensor is cut into ``N_PATCH`` equal windows at its native sampling rate (100 Hz pressure and
motor power, 10 Hz flow, 1 Hz temperature and the rest). A window becomes one token: its values,
normalised with the train-split statistics of that sensor, plus the window's mean and standard
deviation, go through a linear projection chosen by window length, then get a sensor embedding
and a position embedding. The tokens are placed before the text prompt, and the language model
writes the diagnosis and its evidence in the same clause grammar the checker reads.

No physics feature is computed for the model. Whatever numbers it writes, it has to read from the
series, which is what the checker then tests.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch
import torch.nn as nn

from sightglass.data.models import Cycle

N_PATCH = 12
PROMPT = "Diagnose this hydraulic cycle from its 17 sensors, citing the evidence.\n"


def fit_norm(cycles: list[Cycle]) -> dict[str, tuple[float, float]]:
    """Per-sensor mean and standard deviation over every value of the given (train) cycles."""
    out: dict[str, tuple[float, float]] = {}
    for s in sorted(cycles[0].signals):
        v = np.concatenate([c.signals[s].values.astype(np.float64) for c in cycles])
        out[s] = (float(v.mean()), float(v.std()) or 1.0)
    return out


def patch_lengths(cycle: Cycle) -> dict[str, int]:
    return {s: len(cycle.signals[s].values) // N_PATCH for s in sorted(cycle.signals)}


def cycle_patches(
    cycle: Cycle, norm: dict[str, tuple[float, float]], lengths: dict[str, int]
) -> dict[str, np.ndarray]:
    """{sensor: (N_PATCH, L + 2)} float32: normalised window values, window mean, window std."""
    out = {}
    for s, n in lengths.items():
        mu, sd = norm[s]
        x = (cycle.signals[s].values[: n * N_PATCH].astype(np.float64) - mu) / sd
        w = x.reshape(N_PATCH, n)
        out[s] = np.concatenate(
            [w, w.mean(axis=1, keepdims=True), w.std(axis=1, keepdims=True)], axis=1
        ).astype(np.float32)
    return out


class SeriesEncoder(nn.Module):
    """Sensor windows to ``len(sensors) * N_PATCH`` vectors in the language model's width."""

    def __init__(self, lengths: dict[str, int], d_model: int, hidden: int = 384) -> None:
        super().__init__()
        self.sensors = sorted(lengths)
        self.lengths = dict(lengths)
        self.proj = nn.ModuleDict({str(n): nn.Linear(n + 2, hidden) for n in set(lengths.values())})
        self.sensor_emb = nn.Embedding(len(self.sensors), hidden)
        self.pos_emb = nn.Embedding(N_PATCH, hidden)
        self.mix = nn.Sequential(
            nn.LayerNorm(hidden),
            nn.Linear(hidden, hidden),
            nn.GELU(),
            nn.Linear(hidden, d_model),
        )

    def forward(self, patches: dict[str, torch.Tensor]) -> torch.Tensor:
        pos = self.pos_emb.weight  # (N_PATCH, hidden)
        toks = []
        for i, s in enumerate(self.sensors):
            h = self.proj[str(self.lengths[s])](patches[s])  # (B, N_PATCH, hidden)
            toks.append(h + self.sensor_emb.weight[i] + pos)
        out: torch.Tensor = self.mix(torch.cat(toks, dim=1))
        return out


class SoftPromptTSLM(nn.Module):
    """SeriesEncoder in front of a Hugging Face causal language model."""

    def __init__(self, lm: Any, lengths: dict[str, int], prompt_ids: torch.Tensor) -> None:
        super().__init__()
        self.lm = lm
        self.encoder = SeriesEncoder(lengths, lm.config.hidden_size)
        self.register_buffer("prompt_ids", prompt_ids.long(), persistent=False)

    def _prefix(self, patches: dict[str, torch.Tensor]) -> torch.Tensor:
        series = self.encoder(patches)
        b = series.shape[0]
        emb = self.lm.get_input_embeddings()
        prompt = emb(self.prompt_ids).unsqueeze(0).expand(b, -1, -1)
        return torch.cat([series.to(prompt.dtype), prompt], dim=1)

    def forward(
        self, patches: dict[str, torch.Tensor], target_ids: torch.Tensor, target_mask: torch.Tensor
    ) -> torch.Tensor:
        """Mean cross-entropy over the target tokens only."""
        prefix = self._prefix(patches)
        tgt = self.lm.get_input_embeddings()(target_ids)
        embeds = torch.cat([prefix, tgt], dim=1)
        b, p = prefix.shape[0], prefix.shape[1]
        attn = torch.cat(
            [torch.ones(b, p, dtype=target_mask.dtype, device=target_mask.device), target_mask], 1
        )
        ignore = torch.full((b, p), -100, dtype=torch.long, device=target_ids.device)
        labels = torch.cat([ignore, target_ids.masked_fill(target_mask == 0, -100)], dim=1)
        loss: torch.Tensor = self.lm(inputs_embeds=embeds, attention_mask=attn, labels=labels).loss
        return loss

    @torch.no_grad()
    def generate(self, patches: dict[str, torch.Tensor], max_new_tokens: int = 320) -> torch.Tensor:
        prefix = self._prefix(patches)
        attn = torch.ones(prefix.shape[:2], dtype=torch.long, device=prefix.device)
        ids: torch.Tensor = self.lm.generate(
            inputs_embeds=prefix,
            attention_mask=attn,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=self.lm.config.eos_token_id,
        )
        return ids
