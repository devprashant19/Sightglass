"""Run the baselines on the real UCI #447 build and write reproducible run folders.

results/baselines.json   one entry per baseline: status, seeds, per-component test macro-F1,
                         mean ± std across seeds, joint exact match, or a not_run reason.
results/ablations.json   B1 without virtual sensors, and B1 on a random split (leakage check).
"""

import argparse
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from sightglass.baselines.base import BaselineConfig, Prediction
from sightglass.baselines.cnn1d import CNN1DBaseline
from sightglass.baselines.gpt4o_plots import BaselineNotRunError, GPT4oPlotsBaseline
from sightglass.baselines.lightgbm_baseline import LightGBMBaseline
from sightglass.baselines.majority import MajorityBaseline
from sightglass.baselines.minirocket import MiniRocketBaseline
from sightglass.baselines.tokenized_llm import TokenizedLLMBaseline
from sightglass.data.loader import load_cycles
from sightglass.data.models import Cycle
from sightglass.eval.metrics import compute_component_metrics, compute_joint_exact_match
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha, init_run, make_run_id
from sightglass.utils.seed import set_all

logger = get_logger("run_baselines")
COMPONENTS = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]

REGISTRY: list[tuple[str, str, bool, list[int], Callable[[int], Any]]] = [
    # id, label, explains, seeds, factory
    ("B0_majority", "Majority class", False, [0], lambda s: MajorityBaseline()),
    (
        "B1_lightgbm",
        "Physics features + LightGBM",
        False,
        [0, 1, 2],
        lambda s: LightGBMBaseline(name="B1_lightgbm"),
    ),
    ("B2_minirocket", "MiniRocket + ridge", False, [0, 1, 2], lambda s: MiniRocketBaseline()),
    ("B3_cnn1d", "1D-CNN", False, [0, 1, 2], lambda s: CNN1DBaseline(epochs=15, batch_size=32)),
    ("B4_tokenized_llm", "Tokenized-text LLM", True, [0], lambda s: TokenizedLLMBaseline()),
    ("B5_gpt4o", "GPT-4o on plots", True, [0], lambda s: GPT4oPlotsBaseline()),
]


def score(test: list[Cycle], preds: list[Prediction]) -> dict[str, Any]:
    targets = {k: [c.labels[k] for c in test] for k in COMPONENTS}
    by_id = {p.cycle_id: p for p in preds}
    pred = {k: [by_id[c.id].labels[k] for c in test] for k in COMPONENTS}
    per = {k: compute_component_metrics(targets[k], pred[k]) for k in COMPONENTS}
    return {
        "macro_f1": {k: per[k]["macro_f1"] for k in COMPONENTS},
        "accuracy": {k: per[k]["accuracy"] for k in COMPONENTS},
        "mean_macro_f1": float(np.mean([per[k]["macro_f1"] for k in COMPONENTS])),
        "joint_exact_match": compute_joint_exact_match(targets, pred),
    }


def run_one(
    bid: str,
    factory: Callable[[int], Any],
    seed: int,
    train: list[Cycle],
    val: list[Cycle],
    test: list[Cycle],
    split: str,
) -> tuple[dict[str, Any], str]:
    set_all(seed)
    model = factory(seed)
    t0 = time.perf_counter()
    model.fit(train, val, BaselineConfig(name=bid, seed=seed))
    preds = model.predict(test)
    m = score(test, preds)
    m["seconds"] = round(time.perf_counter() - t0, 1)
    if hasattr(model, "best_params"):
        m["best_params"] = model.best_params
    if hasattr(model, "best_epoch"):
        m["best_epoch"] = model.best_epoch
    run_id = make_run_id("hydraulic", bid, f"{split}-test", seed)
    run_dir = init_run(run_id, {"baseline": bid, "seed": seed, "split": split})
    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps({"cycle_id": p.cycle_id, "labels": p.labels}) + "\n")
    if hasattr(model, "feature_importances") and model.feature_importances:
        with open(run_dir / "feature_importances.json", "w", encoding="utf-8") as f:
            json.dump(model.feature_importances, f, indent=2)
    return m, run_id


def summarise(
    bid: str,
    label: str,
    explains: bool,
    runs: list[dict[str, Any]],
    run_ids: list[str],
    seeds: list[int],
) -> dict[str, Any]:
    f1s = [r["mean_macro_f1"] for r in runs]
    return {
        "id": bid,
        "label": label,
        "explains": explains,
        "status": "done",
        "seeds": seeds,
        "run_ids": run_ids,
        "mean_macro_f1": float(np.mean(f1s)),
        "mean_macro_f1_std": float(np.std(f1s)),
        "joint_exact_match": float(np.mean([r["joint_exact_match"] for r in runs])),
        "per_component": {k: float(np.mean([r["macro_f1"][k] for r in runs])) for k in COMPONENTS},
        "seconds": float(np.mean([r["seconds"] for r in runs])),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="*", help="run only these baseline ids")
    ap.add_argument("--skip-ablations", action="store_true")
    args = ap.parse_args()

    train = load_cycles("hydraulic", split="train")
    val = load_cycles("hydraulic", split="val")
    test = load_cycles("hydraulic", split="test")
    logger.info(f"grouped split: {len(train)} train, {len(val)} val, {len(test)} test")

    out_path = Path("results/baselines.json")
    prev = json.loads(out_path.read_text(encoding="utf-8")) if out_path.is_file() else {}
    prev_rows = {r["id"]: r for r in prev.get("baselines", []) if isinstance(r, dict)}
    rows: list[dict[str, Any]] = []
    for bid, label, explains, seeds, factory in REGISTRY:
        if args.only and bid not in args.only:
            if bid in prev_rows:
                rows.append(prev_rows[bid])
            continue
        logger.info(f"--- {bid} ---")
        runs, ids = [], []
        try:
            for s in seeds:
                m, rid = run_one(bid, factory, s, train, val, test, "grouped")
                runs.append(m)
                ids.append(rid)
                logger.info(
                    f"{bid} seed {s}: mean macro-F1 {m['mean_macro_f1']:.3f} ({m['seconds']} s)"
                )
            rows.append(summarise(bid, label, explains, runs, ids, seeds))
        except BaselineNotRunError as e:
            logger.info(f"{bid} not run: {e}")
            rows.append(
                {
                    "id": bid,
                    "label": label,
                    "explains": explains,
                    "status": "not_run",
                    "reason": str(e),
                }
            )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "dataset": "hydraulic",
                "split": "grouped",
                "synthetic": False,
                "generated_by": "scripts/run_baselines.py",
                "git_sha": get_git_sha(),
                "n_test": len(test),
                "baselines": rows,
            },
            f,
            indent=2,
        )
    logger.info(f"wrote {out_path}")

    if args.skip_ablations:
        return
    ref = next(r for r in rows if r["id"] == "B1_lightgbm")
    abl: list[dict[str, Any]] = []
    m, rid = run_one(
        "B1_lightgbm_no_virtual",
        lambda s: LightGBMBaseline(drop_virtual=True),
        0,
        train,
        val,
        test,
        "grouped",
    )
    abl.append(
        {
            "id": "no_virtual",
            "label": "B1 without virtual sensors (CE, CP, SE)",
            "run_id": rid,
            "mean_macro_f1": m["mean_macro_f1"],
            "per_component": m["macro_f1"],
            "delta_mean_macro_f1": m["mean_macro_f1"] - ref["mean_macro_f1"],
        }
    )
    rtrain = load_cycles("hydraulic", split="train", split_name="random")
    rval = load_cycles("hydraulic", split="val", split_name="random")
    rtest = load_cycles("hydraulic", split="test", split_name="random")
    m, rid = run_one("B1_lightgbm", lambda s: LightGBMBaseline(), 0, rtrain, rval, rtest, "random")
    abl.append(
        {
            "id": "random_split",
            "label": "B1 on a random split instead of the grouped split",
            "run_id": rid,
            "mean_macro_f1": m["mean_macro_f1"],
            "per_component": m["macro_f1"],
            "delta_mean_macro_f1": m["mean_macro_f1"] - ref["mean_macro_f1"],
            "note": "A positive delta means random splits make the task look easier.",
        }
    )
    with open("results/ablations.json", "w", encoding="utf-8") as f:
        json.dump({"reference": "B1_lightgbm (grouped split)", "ablations": abl}, f, indent=2)
    logger.info("wrote results/ablations.json")


if __name__ == "__main__":
    main()
