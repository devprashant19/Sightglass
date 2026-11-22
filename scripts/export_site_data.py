"""Export the dashboard data (schema_version 2) from real runs.

web/public/data/       real UCI #447 test cycles, diagnosed by the Sightglass engine
web/public/data-mock/  5 synthetic cycles, "mock": true, for UI development only

Inputs: data/build/hydraulic (connector build), data/models/engine.pkl (scripts/train_engine.py),
results/*.json (scripts/run_baselines.py, build_rationales.py, evaluate.py).
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from sightglass.data.loader import load_cycles, load_manifest, load_splits
from sightglass.data.models import Cycle
from sightglass.engine import ENGINE_PATH, MODEL_NAME, Engine, sig4
from sightglass.export.perturb import GRID, label_for
from sightglass.physics.base import HEALTHY_LEVELS
from sightglass.rationales.builder import COMPONENT_NAMES, COMPONENTS
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha

logger = get_logger("export_site_data")
SCHEMA = 2
TSLM_NAME = "Sightglass TSLM (soft-prompt SmolLM2-135M)"
CITATION = (
    'N. Helwig, E. Pignanelli, A. Schütze, "Condition Monitoring of a Complex Hydraulic System '
    'Using Multivariate Statistics", Proc. I2MTC-2015, Pisa, Italy, 2015. '
    "doi:10.1109/I2MTC.2015.7151267"
)
UCI_URL = (
    "https://archive.ics.uci.edu/static/public/447/condition+monitoring+of+hydraulic+systems.zip"
)
SOURCE: dict[str, Any] = {
    "name": "UCI #447 Condition monitoring of hydraulic systems",
    "url": UCI_URL,
    "page": "https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems",
    "sha256": None,  # filled from the build manifest
    "licence": "CC BY 4.0",
    "citation": CITATION,
}


def clean(dest: Path) -> None:
    """Remove previously exported files (folders stay: a dev server may be watching them)."""
    if dest.exists():
        for p in sorted(dest.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()


def dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def display_signals(c: Cycle) -> dict[str, Any]:
    out = {}
    for name, s in c.signals.items():
        v = s.values.astype(np.float64)
        rate = s.rate_hz
        if rate > 10:
            k = int(rate // 10)
            v = v[: len(v) // k * k].reshape(-1, k).mean(axis=1)
            rate = 10.0
        out[name] = {
            "unit": s.unit,
            "rate_hz": rate,
            "source": s.source,
            "values": [float(f"{x:.4g}") for x in v],
        }
    return out


def labels_json(lb: dict[str, int]) -> dict[str, Any]:
    return {k: {"value": int(lb[k]), "name": COMPONENT_NAMES[k][int(lb[k])]} for k in COMPONENTS}


def cycle_file(
    engine: Engine, c: Cycle, mock: bool, tslm_text: str | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    d = engine.diagnose(c)
    feats = d.pop("_features")
    d.pop("latency_ms", None)
    ref = engine.ref
    doc = {
        "schema_version": SCHEMA,
        "mock": mock,
        "synthetic": bool(c.meta.get("synthetic")),
        "id": c.id,
        "dataset": "hydraulic",
        "meta": {"cycle_index": c.meta["cycle_index"], "stable_flag": c.meta["stable_flag"]},
        "true_labels": labels_json(c.labels),
        "prediction": d,
        "signals": display_signals(c),
        "features": {
            n: {
                "value": sig4(f.value),
                "unit": f.unit,
                "sensor": f.sensor,
                "quantity": f.quantity,
                "z": sig4(ref.z(f)),
                "pct": sig4(ref.pct_diff(f)),
                "virtual": f.virtual,
                "window": list(f.window) if f.window else None,
            }
            for n, f in feats.items()
        },
        "reference": {
            n: {
                "mean": sig4(ref.mean[n]),
                "std": sig4(ref.std[n]),
                "n": ref.n_per_feature.get(n),
                "basis": ref.basis.get(n),
            }
            for n in feats
            if n in ref.mean
        },
    }
    pl = {k: v["value"] for k, v in d["labels"].items()}
    item = {
        "id": c.id,
        "cycle_index": c.meta["cycle_index"],
        "stable_flag": c.meta["stable_flag"],
        "true_labels": dict(c.labels),
        "predicted_labels": pl,
        "correct": int(sum(pl[k] == c.labels[k] for k in COMPONENTS)),
        "total_claims": len(d["claims"]),
        "verified_claims": sum(cl["status"] == "verified" for cl in d["claims"]),
        "is_faithful": bool(d["claims"]) and all(cl["status"] == "verified" for cl in d["claims"]),
        "consistent": all(d["consistency"].values()),
        "healthy": all(c.labels[k] == HEALTHY_LEVELS[k] for k in COMPONENTS),
        "n_healthy": int(sum(c.labels[k] == HEALTHY_LEVELS[k] for k in COMPONENTS)),
    }
    if tslm_text is not None:
        # The TSLM's own text, re-checked here by the engine's checker (not copied verdicts).
        t = engine.check_rationale(c, tslm_text, TSLM_NAME)
        doc["tslm_prediction"] = t
        item["tslm_correct"] = int(sum(t["labels"][k]["value"] == c.labels[k] for k in COMPONENTS))
        item["tslm_total_claims"] = len(t["claims"])
        item["tslm_verified_claims"] = sum(cl["status"] == "verified" for cl in t["claims"])
    return doc, item


def whatif(engine: Engine, c: Cycle, mock: bool) -> dict[str, Any]:
    grid = []
    for kind, amount in GRID:
        d = engine.diagnose(c, [] if kind == "baseline" else [{"type": kind, "amount": amount}])
        grid.append(
            {
                "type": kind,
                "amount": amount,
                "label": label_for(kind, amount),
                "prediction": {
                    "labels": d["labels"],
                    "rationale": d["rationale"],
                    "paragraphs": d["paragraphs"],
                    "claims": d["claims"],
                    "consistency": d["consistency"],
                },
            }
        )
    return {
        "schema_version": SCHEMA,
        "cycle_id": c.id,
        "mock": mock,
        "note": "Real engine run on the perturbed signals. Virtual sensors (CE, CP, SE) are "
        "not changed by the perturbation.",
        "grid": grid,
    }


def export(
    dest: Path,
    engine: Engine,
    cycles: list[Cycle],
    mock: bool,
    n_whatif: int,
    tslm_texts: dict[str, str] | None = None,
) -> None:
    clean(dest)
    hyd = dest / "hydraulic"
    items = []
    for c in cycles:
        doc, item = cycle_file(engine, c, mock, (tslm_texts or {}).get(c.id))
        dump(hyd / "cycles" / f"{c.id}.json", doc)
        items.append(item)
    dump(
        hyd / "index.json",
        {
            "schema_version": SCHEMA,
            "mock": mock,
            "synthetic": bool(cycles and cycles[0].meta.get("synthetic")),
            "split": "test",
            "cycles": items,
        },
    )

    # What-if: the test cycles closest to healthy (most healthy components, then most
    # verified claims), so the perturbations show a component tipping into a fault.
    picks = sorted(items, key=lambda it: (-it["n_healthy"], -it["correct"], it["id"]))[:n_whatif]
    by_id = {c.id: c for c in cycles}
    for it in picks:
        dump(hyd / "whatif" / f"{it['id']}.json", whatif(engine, by_id[it["id"]], mock))
    dump(
        hyd / "whatif" / "index.json",
        {"schema_version": SCHEMA, "mock": mock, "cycles": [it["id"] for it in picks]},
    )
    logger.info(f"{dest}: {len(items)} cycles, {len(picks)} what-if grids")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="web/public/data")
    ap.add_argument("--mock-out", default="web/public/data-mock")
    args = ap.parse_args()

    R = Path("results")

    def load(name: str) -> Any:
        return json.loads((R / name).read_text(encoding="utf-8"))

    engine = Engine.load(ENGINE_PATH)
    summary = load("summary.json")
    ev = load("eval_engine.json")
    baselines = load("baselines.json")["baselines"]
    ablations = (
        json.loads((R / "ablations.json").read_text(encoding="utf-8")).get("ablations", [])
        if (R / "ablations.json").is_file()
        else []
    )
    failures = load("failures.json")
    with open("configs/physics/hydraulic_links.yaml", encoding="utf-8") as f:
        all_links = yaml.safe_load(f)
    manifest = load_manifest()
    splits = load_splits()
    SOURCE["sha256"] = manifest.get("sha256")

    test = load_cycles("hydraulic", split="test")
    out = Path(args.out)
    tslm_file = R / "tslm_test_rationales.jsonl"
    tslm_texts = None
    if summary["tslm"]["status"] == "done" and tslm_file.is_file():
        with open(tslm_file, encoding="utf-8") as f:
            tslm_texts = {r["cycle_id"]: r["rationale"] for r in map(json.loads, f)}
    export(out, engine, test, mock=False, n_whatif=6, tslm_texts=tslm_texts)

    now = datetime.now(UTC).isoformat(timespec="seconds")
    sha = get_git_sha()
    dump(
        out / "manifest.json",
        {
            "schema_version": SCHEMA,
            "mock": False,
            "synthetic": False,
            "generated_at": now,
            "git_sha": sha,
            "source": SOURCE,
            "models": [
                {"id": "engine", "name": MODEL_NAME, "status": "done"},
                {
                    "id": "tslm",
                    "name": TSLM_NAME,
                    "status": summary["tslm"]["status"],
                    "reason": summary["tslm"].get("reason"),
                },
                {
                    "id": "opentslm",
                    "name": "OpenTSLM-Flamingo fine-tune",
                    "status": summary["opentslm"]["status"],
                    "reason": summary["opentslm"]["reason"],
                },
            ],
            "datasets": [
                {"id": "hydraulic", "status": "real"},
                {
                    "id": "bearing",
                    "status": "not_run",
                    "reason": "Round 2: connector is a synthetic stand-in; not run on real HUST data yet.",
                },
                {
                    "id": "wind",
                    "status": "not_run",
                    "reason": "Round 3: connector is a synthetic stand-in; not run on real CARE data yet.",
                },
            ],
        },
    )
    dump(out / "summary.json", {**summary, "schema_version": SCHEMA, "mock": False})
    dump(
        out / "hydraulic" / "results.json",
        {
            "schema_version": SCHEMA,
            "mock": False,
            "engine": {
                "model": MODEL_NAME,
                "n_test_cycles": ev["n_test_cycles"],
                **ev["diagnosis"],
                "faithfulness": ev["faithfulness"],
                "stable_subset": ev["stable_subset"],
            },
            "baselines": baselines,
            "ablations": ablations,
        },
    )
    dump(
        out / "hydraulic" / "links.json",
        {
            "schema_version": SCHEMA,
            **{
                comp: [
                    {
                        k: lk.get(k)
                        for k in (
                            "feature",
                            "sensor",
                            "quantity",
                            "unit",
                            "direction",
                            "measured_direction",
                            "effect",
                            "p_value",
                            "strata_agreement",
                            "strata_tested",
                            "kept",
                            "virtual",
                        )
                    }
                    for lk in rows
                ]
                for comp, rows in all_links.items()
            },
        },
    )
    dump(
        out / "hydraulic" / "dataset.json",
        {
            "schema_version": SCHEMA,
            "sensors": [{"name": n, **s} for n, s in manifest["sensors"].items()],
            "labels": {k: {str(v): nm for v, nm in COMPONENT_NAMES[k].items()} for k in COMPONENTS},
            "split": {
                "method": "grouped by the four-label condition tuple",
                "reason": "Conditions repeat through the run (144 unique combinations), so whole "
                "combinations go to one split; every class of every component is in "
                "train. Neighbouring cycles are highly correlated, so a random split "
                "would leak.",
                "train": len(splits["train"]),
                "val": len(splits["val"]),
                "test": len(splits["test"]),
            },
            "source": SOURCE,
            "build": {"n_records": manifest["n_records"], "sha256": manifest.get("sha256")},
            "timenet_pr": None,
            "timenet_pr_status": "not opened yet",
            "load_snippet": "from sightglass.data import load_cycles\n"
            "test = load_cycles('hydraulic', split='test')  # real UCI #447 build\n"
            "print(test[0].id, test[0].labels)",
        },
    )
    dump(
        out / "hydraulic" / "failures.json",
        {
            "schema_version": SCHEMA,
            "mock": False,
            "n_test_cycles": ev["n_test_cycles"],
            "failures": failures,
        },
    )

    # Mock copy: 5 synthetic cycles through the real engine, clearly marked.
    mock = Path(args.mock_out)
    syn = load_cycles("hydraulic", split="test", synthetic=True, total_count=60)[:5]
    export(mock, engine, syn, mock=True, n_whatif=2)
    for name in ("summary.json",):
        dump(mock / name, {**summary, "schema_version": SCHEMA, "mock": True})
    dump(
        mock / "manifest.json",
        {
            "schema_version": SCHEMA,
            "mock": True,
            "synthetic": True,
            "generated_at": now,
            "git_sha": sha,
            "source": SOURCE,
            "note": "Synthetic cycles for UI development only.",
        },
    )
    for name in ("results.json", "links.json", "dataset.json", "failures.json"):
        src = out / "hydraulic" / name
        doc = json.loads(src.read_text(encoding="utf-8"))
        dump(mock / "hydraulic" / name, {**doc, "mock": True})

    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    logger.info(f"exported {out} ({size / 1e6:.1f} MB) and {mock}")


if __name__ == "__main__":
    main()
