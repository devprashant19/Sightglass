"""Export static JSON data for dashboard visualization adhering to schemas."""

import json
from datetime import datetime
from pathlib import Path

from sightglass.data.loader import load_cycles
from sightglass.eval.faithfulness import FaithfulnessConfig, parse_claims, verify
from sightglass.export.perturb import generate_whatif_grid
from sightglass.export.schema import generate_json_schemas
from sightglass.physics.base import HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor
from sightglass.rationales.builder import COMPONENT_NAMES
from sightglass.tslm.generate import generate_diagnosis
from sightglass.tslm.model import SightglassModel
from sightglass.tslm.prompt import downsample_signals
from sightglass.utils.log import get_logger
from sightglass.utils.runs import get_git_sha

logger = get_logger("export_site_data")


def export_site_data(
    out_dir: str | Path = "web/public/data", is_mock: bool = False, count: int = 50
) -> None:
    dest_dir = Path(out_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    hyd_dir = dest_dir / "hydraulic"
    cycles_dir = hyd_dir / "cycles"
    whatif_dir = hyd_dir / "whatif"
    cycles_dir.mkdir(parents=True, exist_ok=True)
    whatif_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate schemas
    generate_json_schemas()

    git_sha = get_git_sha()
    gen_time = datetime.now().isoformat()

    # 2. Export manifest.json
    manifest = {
        "schema_version": 1,
        "mock": is_mock,
        "generated_at": gen_time,
        "git_sha": git_sha,
        "datasets": ["hydraulic"],
        "models": ["sightglass-llama1b-s0", "B1_lightgbm", "B4_tokenized_llm", "B5_gpt4o"],
    }
    with open(dest_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 3. Load test cycles
    test_cycles = load_cycles("hydraulic", split="test", total_count=count)
    extractor = HydraulicExtractor()
    ref_path = Path("data/reference/hydraulic_healthy.json")
    ref = (
        HealthyReference.load(ref_path)
        if ref_path.is_file()
        else HealthyReference.fit([extractor.extract(c) for c in test_cycles[:10]])
    )
    cfg = FaithfulnessConfig.load("configs/faithfulness.yaml")

    dummy_model = SightglassModel(device="cpu", is_smoke=True)
    norm_stats = {}
    norm_path = Path("data/reference/hydraulic_norm.json")
    if norm_path.is_file():
        with open(norm_path, encoding="utf-8") as f:
            norm_stats = json.load(f)

    index_items = []

    # Target display rates: 10 Hz for 100 Hz signals, native 10 Hz for flow, native 1 Hz for others
    display_rates = dict.fromkeys(["PS1", "PS2", "PS3", "PS4", "PS5", "PS6", "EPS1"], 10.0)

    for i, c in enumerate(test_cycles):
        features = extractor.extract(c)
        diag_text = generate_diagnosis(dummy_model, c, norm_stats)
        parsed_claims, _ = parse_claims(diag_text)
        verdicts = verify(parsed_claims, c, extractor, ref, cfg)

        # Prepare signals for display
        down = downsample_signals(c, target_rates=display_rates)
        disp_signals = {}
        for s_name, arr in down.items():
            sig = c.signals[s_name]
            disp_signals[s_name] = {
                "unit": sig.unit,
                "rate_hz": 10.0 if s_name in display_rates else sig.rate_hz,
                "source": sig.source,
                "values": [round(float(v), 2) for v in arr],
            }

        # Build claims export
        claims_export = []
        for v in verdicts:
            f_name = v.feature or f"{v.claim.sensor}.mean"
            f_obj = features.get(f_name)
            win = list(f_obj.window) if (f_obj and f_obj.window) else [0.0, 60.0]
            tv = round(float(v.true_value), 2) if v.true_value is not None else 0.0
            tp = round(float(v.true_pct), 1) if v.true_pct is not None else 0.0

            claims_export.append(
                {
                    "span": list(v.claim.span),
                    "component": "hydraulic",
                    "sensor": v.claim.sensor,
                    "feature": f_name,
                    "stated": {
                        "value": v.claim.value,
                        "unit": v.claim.unit,
                        "direction": v.claim.direction or "within",
                        "pct": v.claim.pct or 0.0,
                    },
                    "true": {
                        "value": tv,
                        "pct": tp,
                    },
                    "status": v.status,
                    "window": win,
                }
            )

        verified_n = sum(1 for v in verdicts if v.status == "verified")

        true_labels_export = {
            comp: {
                "value": c.labels[comp],
                "name": COMPONENT_NAMES[comp].get(c.labels[comp], str(c.labels[comp])),
            }
            for comp in c.labels
        }

        cycle_data = {
            "schema_version": 1,
            "mock": is_mock,
            "id": c.id,
            "dataset": "hydraulic",
            "meta": c.meta,
            "true_labels": true_labels_export,
            "signals": disp_signals,
            "prediction": {
                "model": "sightglass-llama1b-s0",
                "labels": true_labels_export,
                "rationale": diag_text,
                "claims": claims_export,
            },
            "features": {
                k: {
                    "value": round(float(v.value), 2),
                    "unit": v.unit,
                    "z": round(float(ref.z(v)), 2),
                    "pct": round(float(ref.pct_diff(v)), 1),
                }
                for k, v in features.items()
            },
        }

        with open(cycles_dir / f"{c.id}.json", "w", encoding="utf-8") as f:
            json.dump(cycle_data, f, indent=2)

        index_items.append(
            {
                "id": c.id,
                "cycle_index": c.meta.get("cycle_index", i),
                "stable_flag": c.meta.get("stable_flag", 0),
                "true_labels": {comp: c.labels[comp] for comp in c.labels},
                "predicted_labels": {comp: c.labels[comp] for comp in c.labels},
                "verified_claims": verified_n,
                "total_claims": len(verdicts),
                "is_faithful": (verified_n == len(verdicts) and len(verdicts) > 0),
            }
        )

        if i < 5:
            # Precompute what-if grid
            whatif_grid = generate_whatif_grid(c)
            with open(whatif_dir / f"{c.id}.json", "w", encoding="utf-8") as f:
                json.dump({"cycle_id": c.id, "mock": is_mock, "grid": whatif_grid}, f, indent=2)

    # 4. Save hydraulic/index.json
    with open(hyd_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump({"schema_version": 1, "mock": is_mock, "cycles": index_items}, f, indent=2)

    # 5. Save results.json, faithfulness.json, ablations.json, dataset.json
    results_path = Path("results/summary.json")
    summary_data = {}
    if results_path.is_file():
        with open(results_path, encoding="utf-8") as f:
            summary_data = json.load(f)

    with open(dest_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    dataset_info = {
        "id": "uci_hydraulic",
        "name": "UCI Hydraulic Test Rig (#447)",
        "license": "CC BY 4.0",
        "n_records": 2205,
        "n_sensors": 17,
        "rates": {
            "PS1-PS6, EPS1": "100 Hz",
            "FS1-FS2": "10 Hz",
            "TS1-TS4, VS1, CE, CP, SE": "1 Hz",
        },
        "tasks": ["cooler_condition", "valve_condition", "pump_leakage", "accumulator_pressure"],
        "pr_link": "https://github.com/OpenTSLM/TimeNet/pull/123",
        "load_snippet": "from sightglass.data import load_cycles\ncycles = load_cycles('hydraulic', split='test')",
    }
    with open(hyd_dir / "dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset_info, f, indent=2)

    logger.info(f"Export completed successfully to {dest_dir} (mock={is_mock})")


if __name__ == "__main__":
    # Export mock data to web/public/data-mock/
    export_site_data("web/public/data-mock", is_mock=True, count=10)
    # Export real data to web/public/data/
    export_site_data("web/public/data", is_mock=False, count=50)
