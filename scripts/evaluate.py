"""Evaluate the Sightglass engine on the real test split and build results/summary.json.

Every number in summary.json is copied or computed from result files written by scripts:
  results/baselines.json, results/ablations.json  (scripts/run_baselines.py)
  results/checker_validation.json                 (scripts/build_rationales.py)
  results/eval_engine.json, faithfulness_engine.json, failures.json  (this script)
"""

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import f1_score

from sightglass.data.loader import load_cycles, load_manifest, load_splits
from sightglass.engine import ENGINE_PATH, MODEL_NAME, Engine
from sightglass.eval.metrics import compute_component_metrics, compute_joint_exact_match
from sightglass.physics.base import HEALTHY_LEVELS
from sightglass.rationales.builder import COMPONENT_HEADER, COMPONENT_NAMES, COMPONENTS
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha, init_run, make_run_id

logger = get_logger("evaluate")
R = Path("results")


def bootstrap(fn: Any, n: int, resamples: int = 1000, seed: int = 0) -> list[float]:
    rng = np.random.default_rng(seed)
    vals = [fn(rng.integers(0, n, n)) for _ in range(resamples)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def tslm_summary() -> dict[str, Any]:
    """The soft-prompt TSLM's test result (scripts/train_tslm.py evaluate --split test)."""
    p = R / "tslm_test.json"
    if not p.is_file():
        return {
            "status": "pending",
            "reason": "Train with scripts/train_tslm.py, choose on val, then evaluate on test.",
        }
    t = json.loads(p.read_text(encoding="utf-8"))
    d, fa = t["diagnosis"], t["faithfulness"]
    return {
        "status": "done",
        "model": t["model"],
        "backbone": t["backbone"],
        "run_id": t["run_id"],
        "device": t["device"],
        "n_test_cycles": t["n_cycles"],
        "mean_macro_f1": d["mean_macro_f1"],
        "joint_exact_match": d["joint_exact_match"],
        "per_component": d["per_component"],
        "format_ok_pct": d["format_ok_pct"],
        "claim_accuracy": fa["claim_accuracy"],
        "value_accuracy": fa["value_accuracy"],
        "direction_accuracy": fa["direction_accuracy"],
        "hallucinated_sensor_rate": fa["hallucinated_sensor_rate"],
        "fully_faithful_pct": fa["fully_faithful_pct"],
        "consistency_pct": fa["consistency_pct"],
        "claims_per_rationale": fa["claims_per_rationale"],
        "total_claims": fa["total_claims"],
        "verified_claims": fa["status_counts"].get("verified", 0),
        "status_counts": fa["status_counts"],
        "note": "The model writes every number itself from the raw series; the checker "
        "recomputes each one. Unlike the engine, nothing here verifies by construction.",
    }


def failure_summary(
    c_id: str,
    truth: dict[str, int],
    pred: dict[str, int],
    bad_claims: list[dict[str, Any]],
    inconsistent: list[str],
) -> str:
    parts = []
    for k in COMPONENTS:
        if truth[k] != pred[k]:
            parts.append(
                f"{COMPONENT_HEADER[k]} predicted '{COMPONENT_NAMES[k][pred[k]]}' but the true "
                f"label is '{COMPONENT_NAMES[k][truth[k]]}'"
            )
    if bad_claims:
        names = ", ".join(
            f"{b['sensor']} {b['quantity']} ({b['status'].replace('_', ' ')})"
            for b in bad_claims[:3]
        )
        parts.append(f"{len(bad_claims)} claim(s) did not verify: {names}")
    if inconsistent:
        parts.append(
            "the cited evidence does not support the label for "
            + ", ".join(COMPONENT_HEADER[k].lower() for k in inconsistent)
        )
    return f"{c_id}: " + "; ".join(parts) + "."


def main() -> None:
    engine = Engine.load(ENGINE_PATH) if ENGINE_PATH.is_file() else Engine.train()
    test = load_cycles("hydraulic", split="test")
    logger.info(f"Evaluating the engine on {len(test)} real test cycles")

    rows = []
    run_id = make_run_id("hydraulic", "engine", "grouped-test", 0)
    run_dir = init_run(run_id, {"model": MODEL_NAME, "split": "grouped", "seed": 0})
    with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
        for c in test:
            d = engine.diagnose(c)
            d.pop("_features")
            rows.append((c, d))
            f.write(
                json.dumps(
                    {
                        "cycle_id": c.id,
                        "labels": {k: v["value"] for k, v in d["labels"].items()},
                        "rationale": d["rationale"],
                        "claims": [
                            {"sensor": x["sensor"], "feature": x["feature"], "status": x["status"]}
                            for x in d["claims"]
                        ],
                        "consistency": d["consistency"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    truth = {k: np.array([c.labels[k] for c, _ in rows]) for k in COMPONENTS}
    pred = {k: np.array([d["labels"][k]["value"] for _, d in rows]) for k in COMPONENTS}
    per = {}
    for k in COMPONENTS:
        m = compute_component_metrics(truth[k], pred[k])
        classes = sorted(COMPONENT_NAMES[k])
        from sklearn.metrics import confusion_matrix

        m["confusion_matrix"] = confusion_matrix(truth[k], pred[k], labels=classes).tolist()
        m["classes"] = [{"value": v, "name": COMPONENT_NAMES[k][v]} for v in classes]
        per[k] = m
    mean_f1 = float(np.mean([per[k]["macro_f1"] for k in COMPONENTS]))
    joint = compute_joint_exact_match(
        {k: list(v) for k, v in truth.items()}, {k: list(v) for k, v in pred.items()}
    )
    n = len(rows)
    f1_ci = bootstrap(
        lambda ix: np.mean(
            [
                f1_score(truth[k][ix], pred[k][ix], average="macro", zero_division=0)
                for k in COMPONENTS
            ]
        ),
        n,
    )
    em_vec = np.all([truth[k] == pred[k] for k in COMPONENTS], axis=0).astype(float)
    em_ci = bootstrap(lambda ix: em_vec[ix].mean(), n)

    claims = [cl for _, d in rows for cl in d["claims"]]
    total = len(claims)
    verified = sum(cl["status"] == "verified" for cl in claims)
    value_ok = sum(cl["value_ok"] for cl in claims)
    dir_ok = sum(cl["direction_ok"] for cl in claims)
    halluc = sum(cl["status"] == "unknown_sensor" for cl in claims)
    unparsed = sum(len(d["unparsed_numbers"]) for _, d in rows)
    fully = sum(
        bool(d["claims"]) and all(cl["status"] == "verified" for cl in d["claims"]) for _, d in rows
    )
    cons = {k: float(np.mean([d["consistency"][k] for _, d in rows])) for k in COMPONENTS}
    status_counts: dict[str, int] = {}
    for cl in claims:
        status_counts[cl["status"]] = status_counts.get(cl["status"], 0) + 1

    faith = {
        "claim_accuracy": 100.0 * verified / max(1, total),
        "value_accuracy": 100.0 * value_ok / max(1, total),
        "direction_accuracy": 100.0 * dir_ok / max(1, total),
        "hallucinated_sensor_rate": 100.0 * halluc / max(1, total),
        "unparsed_numbers": unparsed,
        "claims_per_rationale": total / max(1, n),
        "fully_faithful_pct": 100.0 * fully / max(1, n),
        "consistency_pct": 100.0 * float(np.mean(list(cons.values()))),
        "consistency_per_component": {k: 100.0 * v for k, v in cons.items()},
        "total_claims": total,
        "verified_claims": verified,
        "status_counts": status_counts,
    }
    ev = {
        "run_id": run_id,
        "model": MODEL_NAME,
        "split": "grouped",
        "n_test_cycles": n,
        "synthetic": engine.synthetic,
        "git_sha": get_git_sha(),
        "diagnosis": {
            "mean_macro_f1": mean_f1,
            "mean_macro_f1_ci95": f1_ci,
            "joint_exact_match": joint,
            "joint_exact_match_ci95": em_ci,
            "components": per,
        },
        "faithfulness": faith,
        "stable_subset": {},
    }
    for flag in (0, 1):
        ix = np.array([c.meta["stable_flag"] == flag for c, _ in rows])
        if ix.any():
            ev["stable_subset"][str(flag)] = {
                "n": int(ix.sum()),
                "mean_macro_f1": float(
                    np.mean(
                        [
                            f1_score(truth[k][ix], pred[k][ix], average="macro", zero_division=0)
                            for k in COMPONENTS
                        ]
                    )
                ),
            }
    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=2)
    with open(R / "eval_engine.json", "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=2)
    with open(R / "faithfulness_engine.json", "w", encoding="utf-8") as f:
        json.dump(
            [{"cycle_id": c.id, **cl} for c, d in rows for cl in d["claims"]], f, ensure_ascii=False
        )

    failures = []
    for c, d in rows:
        pl = {k: v["value"] for k, v in d["labels"].items()}
        bad = [cl for cl in d["claims"] if cl["status"] != "verified"]
        inc = [k for k in COMPONENTS if not d["consistency"][k]]
        wrong = [k for k in COMPONENTS if pl[k] != c.labels[k]]
        if not (bad or inc or wrong):
            continue
        tags = []
        for k in wrong:
            order = sorted(COMPONENT_NAMES[k])
            adj = abs(order.index(pl[k]) - order.index(c.labels[k])) == 1
            tags.append("wrong_severity_adjacent" if adj else "wrong_severity")
        tags += sorted({cl["status"] for cl in bad})
        if inc:
            tags.append("inconsistent")
        failures.append(
            {
                "cycle_id": c.id,
                "tags": sorted(set(tags)),
                "components": wrong,
                "inconsistent_components": inc,
                "true_labels": dict(c.labels),
                "pred_labels": pl,
                "summary": failure_summary(c.id, c.labels, pl, bad, inc),
            }
        )
    with open(R / "failures.json", "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2, ensure_ascii=False)
    logger.info(
        f"engine: mean macro-F1 {mean_f1:.3f}, joint EM {joint:.3f}, claims "
        f"{verified}/{total} verified, {len(failures)} failure cases"
    )
    write_summary(ev)


def write_summary(ev: dict[str, Any]) -> None:
    def load(name: str) -> Any:
        p = R / name
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None

    manifest = load_manifest()
    splits = load_splits()
    checker = load("checker_validation.json") or {}
    baselines = (load("baselines.json") or {}).get("baselines", [])
    ablations = (load("ablations.json") or {}).get("ablations", [])
    training = load("engine_training.json") or {}
    labels = np.load(Path("data/build/hydraulic/labels.npy"))
    d = ev["diagnosis"]
    f = ev["faithfulness"]
    gpt = next((b for b in baselines if b["id"] == "B5_gpt4o"), None)
    summary = {
        "generated_by": "scripts/evaluate.py",
        "git_sha": get_git_sha(),
        "synthetic": bool(ev.get("synthetic")),
        "dataset": {
            "cycles": int(manifest["n_records"]),
            "sensors": int(manifest["n_sensors"]),
            "samples_per_cycle": int(sum(s["n_samples"] for s in manifest["sensors"].values())),
            "components": 4,
            "unique_conditions": int(len({tuple(r) for r in labels[:, :4].tolist()})),
            "train": len(splits["train"]),
            "val": len(splits["val"]),
            "test": len(splits["test"]),
            "healthy_all_four": int(
                sum(
                    all(r[i] == v for i, v in enumerate(HEALTHY_LEVELS.values()))
                    for r in labels.tolist()
                )
            ),
            "healthy_reference_n": training.get("healthy_reference", {}).get("n_per_feature", {}),
        },
        "engine": {
            "model": MODEL_NAME,
            "mean_macro_f1": d["mean_macro_f1"],
            "mean_macro_f1_ci95": d["mean_macro_f1_ci95"],
            "joint_exact_match": d["joint_exact_match"],
            "joint_exact_match_ci95": d["joint_exact_match_ci95"],
            "per_component": {
                k: {"macro_f1": v["macro_f1"], "accuracy": v["accuracy"]}
                for k, v in d["components"].items()
            },
            **{
                k: f[k]
                for k in (
                    "claim_accuracy",
                    "value_accuracy",
                    "direction_accuracy",
                    "fully_faithful_pct",
                    "consistency_pct",
                    "claims_per_rationale",
                    "total_claims",
                    "verified_claims",
                    "hallucinated_sensor_rate",
                    "consistency_per_component",
                )
            },
            "n_test_cycles": ev["n_test_cycles"],
            "note": "Claims are computed from the signal by the rationale engine, so near-100% "
            "claim accuracy is expected by construction; it shows the checker and the "
            "engine agree, not that a language model is faithful.",
        },
        "checker": {
            "roundtrip_pct": checker.get("roundtrip_pct"),
            "roundtrip_claims": checker.get("roundtrip_claims"),
            "n_rationales": checker.get("n_rationales"),
            "corruption_caught_pct": checker.get("corruption_caught_pct"),
            "n_corrupted": checker.get("n_corrupted"),
            "direction_flip_caught_pct": checker.get("direction_flip_caught_pct"),
            "n_direction_flipped": checker.get("n_direction_flipped"),
            "tolerance_rel": checker.get("tolerance_rel"),
        },
        "tslm": tslm_summary(),
        "opentslm": {
            "label": "OpenTSLM-Flamingo fine-tune (Llama-3.2 1B)",
            "status": "pending",
            "reason": "OpenTSLM-Flamingo fine-tuning needs a GPU with about 20 GB for "
            "Llama-3.2 1B; it has not been run. Its outputs will go through the "
            "same checker.",
        },
        "gpt4o": {
            "status": gpt["status"] if gpt else "not_run",
            "reason": (gpt or {}).get("reason", "not run"),
        },
        "baselines": baselines,
        "ablations": ablations,
    }
    with open(R / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    logger.info("wrote results/summary.json")


if __name__ == "__main__":
    main()
