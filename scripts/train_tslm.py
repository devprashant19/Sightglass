"""Train and evaluate the soft-prompt time-series language model (B6).

  python scripts/train_tslm.py train                  # train split; best epoch by validation loss
  python scripts/train_tslm.py evaluate --split val   # write rationales for val, check every claim
  python scripts/train_tslm.py evaluate --split test  # once, after every choice was made on val

The model is SmolLM2-135M with sensor windows as soft prompts (src/sightglass/tslm/softprompt.py).
It is trained to write the four-line diagnosis with evidence in the checker's clause grammar, from
the train-split rationales in data/rationales/hydraulic.jsonl. Its claims are checked with the
engine's own extractor, healthy reference, tolerances and consistency checker, so "verified" means
the same thing for both. Results go to results/tslm_<split>.json and a run folder.

Needs the optional extra: uv pip install -r requirements-tslm.txt (a CUDA GPU is used if present).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from pydantic import BaseModel, ConfigDict
from sklearn.metrics import f1_score

from sightglass.data.loader import load_cycles
from sightglass.engine import ENGINE_PATH, Engine
from sightglass.rationales.builder import COMPONENT_NAMES, COMPONENTS
from sightglass.tslm.softprompt import (
    PROMPT,
    SoftPromptTSLM,
    cycle_patches,
    fit_norm,
    patch_lengths,
)
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha, init_run, make_run_id
from sightglass.utils.seed import set_all

logger = get_logger("train_tslm")
CONFIG = Path("configs/train/softprompt_smollm135m.yaml")
RATIONALES = Path("data/rationales/hydraulic.jsonl")
MODEL_NAME = "B6_softprompt_tslm"


class TrainCfg(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_name: str
    backbone: str
    backbone_revision: str
    seed: int
    epochs: int
    batch_size: int
    grad_accum: int
    lr_encoder: float
    lr_lm: float
    warmup_steps: int
    max_new_tokens: int
    gen_batch_size: int
    checkpoint_dir: str
    label_weight: float = 1.0  # loss weight on the level names ("Valve: small lag.")


def load_cfg(path: Path = CONFIG) -> TrainCfg:
    with open(path, encoding="utf-8") as f:
        return TrainCfg(**yaml.safe_load(f))


def device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model(cfg: TrainCfg, lengths: dict[str, int]) -> tuple[SoftPromptTSLM, Any]:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(cfg.backbone, revision=cfg.backbone_revision)
    lm = AutoModelForCausalLM.from_pretrained(
        cfg.backbone, revision=cfg.backbone_revision, dtype=torch.float32
    )
    prompt_ids = torch.tensor(tok(PROMPT, add_special_tokens=False).input_ids)
    return SoftPromptTSLM(lm, lengths, prompt_ids), tok


def stack_patches(cycles: list, norm: dict, lengths: dict) -> dict[str, np.ndarray]:
    per = [cycle_patches(c, norm, lengths) for c in cycles]
    return {s: np.stack([p[s] for p in per]) for s in lengths}


def to_dev(p: dict[str, np.ndarray], idx: np.ndarray, dev: torch.device) -> dict[str, torch.Tensor]:
    return {s: torch.from_numpy(v[idx]).to(dev) for s, v in p.items()}


def encode_targets(tok: Any, texts: list[str]) -> tuple[torch.Tensor, torch.Tensor]:
    ids = [tok(t, add_special_tokens=False).input_ids + [tok.eos_token_id] for t in texts]
    n = max(len(x) for x in ids)
    out = torch.full((len(ids), n), tok.eos_token_id, dtype=torch.long)
    mask = torch.zeros((len(ids), n), dtype=torch.long)
    for i, x in enumerate(ids):
        out[i, : len(x)] = torch.tensor(x)
        mask[i, : len(x)] = 1
    return out, mask


def label_weights(tok: Any, texts: list[str], weight: float, n: int) -> torch.Tensor:
    """Per-token weights: ``weight`` on the tokens of each line's level name, 1 elsewhere."""
    out = torch.ones((len(texts), n))
    for i, t in enumerate(texts):
        spans = [m.span(1) for m in re.finditer(r"(?m)^[^:\n]+:\s*([^.\n]+)\.", t)]
        enc = tok(t, add_special_tokens=False, return_offsets_mapping=True)
        for j, (a, b) in enumerate(enc["offset_mapping"]):
            if any(a < e and s < b for s, e in spans):
                out[i, j] = weight
    return out


def rationale_texts() -> dict[str, str]:
    with open(RATIONALES, encoding="utf-8") as f:
        return {r["cycle_id"]: r["text"] for r in map(json.loads, f)}


def mean_loss(model: SoftPromptTSLM, P: dict, T: torch.Tensor, M: torch.Tensor, bs: int) -> float:
    dev = device()
    model.eval()
    tot, n = 0.0, 0
    with torch.no_grad(), torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == "cuda"):
        for i in range(0, len(T), bs):
            idx = np.arange(i, min(i + bs, len(T)))
            loss = model(to_dev(P, idx, dev), T[idx].to(dev), M[idx].to(dev))
            tot += float(loss) * len(idx)
            n += len(idx)
    model.train()
    return tot / max(1, n)


def train(cfg: TrainCfg) -> None:
    set_all(cfg.seed)
    dev = device()
    texts = rationale_texts()
    tr = load_cycles("hydraulic", split="train")
    va = load_cycles("hydraulic", split="val")
    if any(c.meta.get("synthetic") for c in tr):
        raise SystemExit("Synthetic cycles loaded: build the real data first (make data).")
    norm = fit_norm(tr)  # train split only
    lengths = patch_lengths(tr[0])
    model, tok = build_model(cfg, lengths)
    model.to(dev)
    if dev.type == "cuda":
        model.lm.gradient_checkpointing_enable()
    Ptr, Pva = stack_patches(tr, norm, lengths), stack_patches(va, norm, lengths)
    Ttr, Mtr = encode_targets(tok, [texts[c.id] for c in tr])
    Tva, Mva = encode_targets(tok, [texts[c.id] for c in va])
    Wtr = (
        label_weights(tok, [texts[c.id] for c in tr], cfg.label_weight, Ttr.shape[1])
        if cfg.label_weight != 1.0
        else None
    )
    logger.info(f"{len(tr)} train / {len(va)} val cycles, {len(lengths)} sensors, device {dev}")

    opt = torch.optim.AdamW(
        [
            {"params": model.encoder.parameters(), "lr": cfg.lr_encoder},
            {"params": model.lm.parameters(), "lr": cfg.lr_lm},
        ],
        weight_decay=0.01,
    )
    steps = cfg.epochs * math.ceil(len(tr) / (cfg.batch_size * cfg.grad_accum))

    def lr_scale(step: int) -> float:
        if step < cfg.warmup_steps:
            return (step + 1) / cfg.warmup_steps
        frac = (step - cfg.warmup_steps) / max(1, steps - cfg.warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * min(1.0, frac)))

    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_scale)
    scaler = torch.amp.GradScaler(enabled=dev.type == "cuda")
    ckpt = Path(cfg.checkpoint_dir)
    ckpt.mkdir(parents=True, exist_ok=True)
    run_id = make_run_id("hydraulic", "softprompt-tslm", "grouped-train", cfg.seed)
    run_dir = init_run(run_id, cfg.model_dump())
    history: list[dict[str, Any]] = []
    best = math.inf
    rng = np.random.default_rng(cfg.seed)
    step = 0
    t0 = time.time()
    for epoch in range(cfg.epochs):
        order = rng.permutation(len(tr))
        running: list[float] = []
        for bi, i in enumerate(range(0, len(order), cfg.batch_size)):
            idx = order[i : i + cfg.batch_size]
            with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == "cuda"):
                w = None if Wtr is None else Wtr[idx].to(dev)
                loss = model(to_dev(Ptr, idx, dev), Ttr[idx].to(dev), Mtr[idx].to(dev), w)
            scaler.scale(loss / cfg.grad_accum).backward()
            running.append(float(loss.detach()))
            if (bi + 1) % cfg.grad_accum == 0:
                scaler.unscale_(opt)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)
                sched.step()
                step += 1
                if step % 25 == 0:
                    logger.info(
                        f"epoch {epoch} step {step}/{steps} loss {np.mean(running[-50:]):.4f} "
                        f"({time.time() - t0:.0f}s)"
                    )
        val = mean_loss(model, Pva, Tva, Mva, cfg.batch_size)
        rec = {"epoch": epoch, "train_loss": float(np.mean(running)), "val_loss": val}
        history.append(rec)
        logger.info(f"epoch {epoch}: train {rec['train_loss']:.4f}, val {val:.4f}")
        if val < best:
            best = val
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "norm": norm,
                    "lengths": lengths,
                    "epoch": epoch,
                    "val_loss": val,
                    "config": cfg.model_dump(),
                },
                ckpt / "best.pt",
            )
    meta = {"history": history, "best_val_loss": best, "seconds": round(time.time() - t0)}
    meta["device"] = torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu"
    (run_dir / "metrics.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (ckpt / "train_history.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def evaluate(cfg: TrainCfg, split: str) -> None:
    dev = device()
    state = torch.load(Path(cfg.checkpoint_dir) / "best.pt", map_location="cpu", weights_only=False)
    model, tok = build_model(cfg, state["lengths"])
    model.load_state_dict(state["model_state"], strict=False)
    model.to(dev).eval()
    engine = Engine.load(ENGINE_PATH)
    cycles = load_cycles("hydraulic", split=split)
    P = stack_patches(cycles, state["norm"], state["lengths"])
    texts: list[str] = []
    t0 = time.time()
    for i in range(0, len(cycles), cfg.gen_batch_size):
        idx = np.arange(i, min(i + cfg.gen_batch_size, len(cycles)))
        with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == "cuda"):
            out = model.generate(to_dev(P, idx, dev), cfg.max_new_tokens)
        texts += [t.strip() for t in tok.batch_decode(out, skip_special_tokens=True)]
        logger.info(f"generated {len(texts)}/{len(cycles)} ({time.time() - t0:.0f}s)")
    gen_seconds = time.time() - t0

    run_id = make_run_id("hydraulic", "softprompt-tslm", f"grouped-{split}", cfg.seed)
    run_dir = init_run(run_id, {**cfg.model_dump(), "split": split, "epoch": state["epoch"]})
    rows = []
    with (
        open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f,
        open(Path("results", f"tslm_{split}_rationales.jsonl"), "w", encoding="utf-8") as g,
    ):
        for c, text in zip(cycles, texts, strict=True):
            pred = engine.check_rationale(c, text, MODEL_NAME)
            labels = {k: pred["labels"][k]["value"] for k in COMPONENTS}
            rows.append((c, labels, pred["claims"], pred["consistency"], pred["unparsed_numbers"]))
            f.write(json.dumps({"cycle_id": c.id, **pred}, ensure_ascii=False) + "\n")
            g.write(json.dumps({"cycle_id": c.id, "rationale": text}, ensure_ascii=False) + "\n")

    per = {}
    for k in COMPONENTS:
        truth = [c.labels[k] for c, *_ in rows]
        pred = [-1 if lab[k] is None else lab[k] for _, lab, *_ in rows]
        classes = sorted(COMPONENT_NAMES[k])
        per[k] = {
            "macro_f1": float(
                f1_score(truth, pred, labels=classes, average="macro", zero_division=0)
            ),
            "accuracy": float(np.mean(np.array(truth) == np.array(pred))),
        }
    n = len(rows)
    exact = np.mean([all(lab[k] == c.labels[k] for k in COMPONENTS) for c, lab, *_ in rows])
    format_ok = np.mean([all(lab[k] is not None for k in COMPONENTS) for _, lab, *_ in rows])
    claims = [cl for *_, cls, _, _ in rows for cl in cls]
    total = len(claims)
    status: dict[str, int] = {}
    for cl in claims:
        status[cl["status"]] = status.get(cl["status"], 0) + 1
    fully = sum(bool(cls) and all(x["status"] == "verified" for x in cls) for *_, cls, _, _ in rows)
    cons_pct = {k: 100.0 * float(np.mean([r[3][k] for r in rows])) for k in COMPONENTS}
    result = {
        "run_id": run_id,
        "model": MODEL_NAME,
        "backbone": f"{cfg.backbone}@{cfg.backbone_revision}",
        "split": split,
        "n_cycles": n,
        "git_sha": get_git_sha(),
        "trained_epochs_best": state["epoch"],
        "best_val_loss": state["val_loss"],
        "generation_seconds": round(gen_seconds),
        "device": torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu",
        "diagnosis": {
            "mean_macro_f1": float(np.mean([per[k]["macro_f1"] for k in COMPONENTS])),
            "joint_exact_match": float(exact),
            "per_component": per,
            "format_ok_pct": 100.0 * float(format_ok),
        },
        "faithfulness": {
            "claim_accuracy": 100.0 * status.get("verified", 0) / max(1, total),
            "value_accuracy": 100.0 * sum(c["value_ok"] for c in claims) / max(1, total),
            "direction_accuracy": 100.0 * sum(c["direction_ok"] for c in claims) / max(1, total),
            "hallucinated_sensor_rate": 100.0 * status.get("unknown_sensor", 0) / max(1, total),
            "unparsed_numbers": sum(len(r[4]) for r in rows),
            "claims_per_rationale": total / max(1, n),
            "fully_faithful_pct": 100.0 * fully / max(1, n),
            "consistency_pct": float(np.mean(list(cons_pct.values()))),
            "consistency_per_component": cons_pct,
            "total_claims": total,
            "status_counts": status,
        },
    }
    (run_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    Path("results", f"tslm_{split}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    d, fa = result["diagnosis"], result["faithfulness"]
    logger.info(
        f"{split}: mean macro-F1 {d['mean_macro_f1']:.4f}, exact {d['joint_exact_match']:.4f}, "
        f"format {d['format_ok_pct']:.1f}%, claims verified {fa['claim_accuracy']:.1f}% "
        f"of {total}, fully faithful {fa['fully_faithful_pct']:.1f}%"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["train", "evaluate"])
    ap.add_argument("--split", choices=["val", "test"], default="val")
    ap.add_argument("--config", type=Path, default=CONFIG)
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    if a.command == "train":
        train(cfg)
    else:
        evaluate(cfg, a.split)


if __name__ == "__main__":
    main()
