"""Run all baseline models (B0 - B5) and save reproducible evaluation runs."""

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from sightglass.baselines.cnn1d import CNN1DBaseline
from sightglass.baselines.gpt4o_plots import GPT4oPlotsBaseline
from sightglass.baselines.lightgbm_baseline import LightGBMBaseline
from sightglass.baselines.majority import MajorityBaseline
from sightglass.baselines.minirocket import MiniRocketBaseline
from sightglass.baselines.tokenized_llm import TokenizedLLMBaseline
from sightglass.data.loader import load_cycles
from sightglass.eval.metrics import compute_component_metrics, compute_joint_exact_match
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha, init_run, make_run_id
from sightglass.utils.seed import set_all

logger = get_logger("run_baselines")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sightglass baseline models.")
    parser.add_argument("--config", type=str, default="configs/baselines/hydraulic.yaml")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0])
    parser.add_argument(
        "--sample_cycles",
        type=int,
        default=200,
        help="Number of cycles to evaluate for fast/CPU mode",
    )
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    dataset_name = cfg.get("dataset", "hydraulic")
    split_name = cfg.get("split", "grouped")
    seeds = args.seeds or cfg.get("seeds", [0])

    logger.info(
        f"Loading {dataset_name} cycles (split={split_name}, sample={args.sample_cycles})..."
    )
    train_cycles = load_cycles(
        dataset_name, split="train", split_name=split_name, total_count=args.sample_cycles
    )
    val_cycles = load_cycles(
        dataset_name, split="val", split_name=split_name, total_count=args.sample_cycles
    )
    test_cycles = load_cycles(
        dataset_name, split="test", split_name=split_name, total_count=args.sample_cycles
    )

    logger.info(
        f"Loaded {len(train_cycles)} train, {len(val_cycles)} val, {len(test_cycles)} test cycles."
    )

    components = ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"]
    targets_test = {comp: [c.labels[comp] for c in test_cycles] for comp in components}

    results_summary: dict[str, Any] = {
        "dataset": dataset_name,
        "split": split_name,
        "generated_by": "scripts/run_baselines.py",
        "git_sha": get_git_sha(),
        "baselines": {},
    }

    baseline_registry = [
        ("B0_majority", lambda seed: MajorityBaseline()),
        ("B1_lightgbm", lambda seed: LightGBMBaseline(name="B1_lightgbm", drop_virtual=False)),
        (
            "B1_lightgbm_no_virtual",
            lambda seed: LightGBMBaseline(name="B1_lightgbm_no_virtual", drop_virtual=True),
        ),
        ("B2_minirocket", lambda seed: MiniRocketBaseline(num_kernels=50, resample_len=60)),
        ("B3_cnn1d", lambda seed: CNN1DBaseline(epochs=3, batch_size=16)),
        ("B4_tokenized_llm", lambda seed: TokenizedLLMBaseline()),
        ("B5_gpt4o", lambda seed: GPT4oPlotsBaseline(sample_size=min(50, len(test_cycles)))),
    ]

    for b_name, b_factory in baseline_registry:
        logger.info(f"--- Running {b_name} ---")
        seed_macro_f1s = []
        seed_exact_matches = []
        last_metrics = None

        for seed in seeds:
            set_all(seed)
            model = b_factory(seed)
            from sightglass.baselines.base import BaselineConfig

            b_cfg = BaselineConfig(name=b_name, seed=seed)
            model.fit(train_cycles, val_cycles, b_cfg)
            preds = model.predict(test_cycles)

            if not preds:
                continue

            preds_dict = {comp: [p.labels.get(comp, 0) for p in preds] for comp in components}

            # Evaluate metrics
            comp_f1s = {}
            for comp in components:
                m = compute_component_metrics(targets_test[comp], preds_dict[comp])
                comp_f1s[comp] = m["macro_f1"]

            mean_f1 = float(np.mean(list(comp_f1s.values())))
            joint_em = compute_joint_exact_match(targets_test, preds_dict)

            seed_macro_f1s.append(mean_f1)
            seed_exact_matches.append(joint_em)

            last_metrics = {
                "macro_f1": {**comp_f1s, "mean": mean_f1},
                "joint_exact_match": joint_em,
            }

            # Initialize and write run artifacts
            run_id = make_run_id(dataset_name, b_name, "test", seed)
            run_dir = init_run(run_id, b_cfg.model_dump())
            with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
                json.dump(last_metrics, f, indent=2)

            with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
                for p in preds:
                    f.write(
                        json.dumps(
                            {
                                "cycle_id": p.cycle_id,
                                "labels": p.labels,
                                "rationale": p.rationale,
                            }
                        )
                        + "\n"
                    )

        if seed_macro_f1s and last_metrics:
            results_summary["baselines"][b_name] = {
                "seeds": seeds,
                "test": last_metrics,
                "test_mean_f1_avg": float(np.mean(seed_macro_f1s)),
                "test_mean_f1_std": float(np.std(seed_macro_f1s)),
                "test_joint_em_avg": float(np.mean(seed_exact_matches)),
            }
            logger.info(
                f"{b_name} Test Mean Macro-F1: {float(np.mean(seed_macro_f1s)):.3f}, "
                f"Joint Exact Match: {float(np.mean(seed_exact_matches)):.3f}"
            )

    # Save summary results/baselines.json
    res_dir = Path("results")
    res_dir.mkdir(parents=True, exist_ok=True)
    with open(res_dir / "baselines.json", "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    logger.info("Saved baseline results to results/baselines.json")


if __name__ == "__main__":
    main()
