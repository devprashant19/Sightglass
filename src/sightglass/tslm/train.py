"""TSLM fine-tuning entry point.

Two modes:
  * smoke (CPU, or train.smoke: true): real gradient steps on a tiny adapter over downsampled,
    train-normalised series. It proves data loading, normalisation, checkpointing and resume
    work. It writes losses only, never predictions, and its numbers are not model results.
  * full (GPU + OpenTSLM installed): fine-tunes OpenTSLM-Flamingo. The curriculum trainer from
    OpenTSLM must be wired in here; until then this mode raises instead of pretending.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml

from sightglass.data.loader import load_cycles
from sightglass.tslm.model import SightglassModel
from sightglass.tslm.prompt import compute_normalisation_statistics
from sightglass.utils.log import get_logger
from sightglass.utils.runs import init_run, make_run_id
from sightglass.utils.seed import set_all

logger = get_logger("tslm_train")

COOLER_INDEX = {3: 0, 20: 1, 100: 2}


def _smoke_tensors(
    cycles: list, norm: dict[str, dict[str, float]]
) -> tuple[torch.Tensor, torch.Tensor]:
    sensors = sorted(cycles[0].signals)
    xs = []
    for c in cycles:
        chans = []
        for s in sensors:
            v = c.signals[s].values
            idx = np.linspace(0, len(v) - 1, 60).astype(int)
            st = norm.get(s, {"mean": 0.0, "std": 1.0})
            chans.append((v[idx] - st["mean"]) / (st["std"] or 1.0))
        xs.append(np.stack(chans, axis=-1))
    x = torch.tensor(np.array(xs, dtype=np.float32))
    y = torch.tensor([COOLER_INDEX[c.labels["cooler_condition"]] for c in cycles])
    return x, y


def train(config_path: str, seed: int = 0) -> str:
    set_all(seed)
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    run_name = cfg.get("run_name", "hydraulic_flamingo_smoke")
    dataset_name = cfg.get("dataset", "hydraulic")
    model_cfg = cfg.get("model", {})
    train_cfg = cfg.get("train", {})
    epochs = int(train_cfg.get("epochs", 2))
    device = "cuda" if torch.cuda.is_available() and train_cfg.get("device") != "cpu" else "cpu"
    is_smoke = bool(train_cfg.get("smoke", False)) or device == "cpu"
    run_id = make_run_id(dataset_name, run_name, model_cfg.get("variant", "flamingo"), seed)

    if not is_smoke:
        raise NotImplementedError(
            "Full OpenTSLM-Flamingo fine-tuning is not wired in yet: connect OpenTSLM's curriculum "
            "trainer here (see docs/opentslm-notes.md and phases/04-finetuning.md)."
        )

    n = int(train_cfg.get("smoke_cycles", 64))
    train_cycles = load_cycles(dataset_name, split="train", total_count=n)
    norm_path = Path("data/reference/hydraulic_norm.json")
    norm = compute_normalisation_statistics(
        load_cycles(dataset_name, split="train"), save_path=norm_path
    )

    model = SightglassModel(
        backbone=model_cfg.get("backbone", "google/gemma-3-270m"),
        variant=model_cfg.get("variant", "flamingo"),
        device="cpu",
        is_smoke=True,
    )
    ckpt_dir = Path("checkpoints") / run_id
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    latest = ckpt_dir / "latest.pt"
    if latest.is_file():
        model.load_checkpoint(latest)

    x, y = _smoke_tensors(train_cycles, norm)
    opt = torch.optim.AdamW(model.model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    losses: list[float] = []
    for epoch in range(epochs):
        model.model.train()
        opt.zero_grad()
        logits = model.model(x).mean(dim=1)[:, :3]  # pooled over time, 3 cooler classes
        loss = loss_fn(logits, y)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        logger.info(f"[smoke] epoch {epoch + 1}/{epochs} loss {losses[-1]:.4f}")
        model.save_checkpoint(ckpt_dir / f"epoch_{epoch + 1}.pt", epoch=epoch + 1, step=epoch + 1)
        model.save_checkpoint(latest, epoch=epoch + 1, step=epoch + 1)

    run_dir = init_run(run_id, cfg)
    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "smoke": True,
                "train_loss": losses,
                "n_cycles": len(train_cycles),
                "note": "Training-loop smoke test only. Not a model result.",
            },
            f,
            indent=2,
        )
    return run_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune the Sightglass TSLM.")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    train(args.config, seed=args.seed)


if __name__ == "__main__":
    main()
