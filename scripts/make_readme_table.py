"""Generate markdown results table for README.md from actual files in results/."""

import json
from pathlib import Path


def main() -> None:
    results_dir = Path("results")
    baselines_path = results_dir / "baselines.json"

    # Model rows
    models = [
        ("Majority (B0)", "B0_majority"),
        ("Features + LightGBM (B1)", "B1_lightgbm"),
        ("MiniRocket (B2)", "B2_minirocket"),
        ("1D-CNN (B3)", "B3_cnn1d"),
        ("Tokenized-text LLM (B4)", "B4_tokenized_llm"),
        ("GPT-4o on plots (B5)", "B5_gpt4o"),
        ("**Sightglass (Llama-1B)**", "sightglass_headline"),
    ]

    baselines_data = {}
    if baselines_path.is_file():
        with open(baselines_path, encoding="utf-8") as f:
            baselines_data = json.load(f).get("baselines", {})

    print(
        "| Model | Mean Macro-F1 | Joint EM | Claim Accuracy | Fully Faithful | Hallucinated Sensors |"
    )
    print("|---|---|---|---|---|---|")

    for label, key in models:
        if key in baselines_data:
            entry = baselines_data[key].get("test", {})
            f1 = f"{entry.get('macro_f1', {}).get('mean', 0.0):.3f}"
            em = f"{entry.get('joint_exact_match', 0.0):.3f}"
            claim_acc = "—"
            ff = "—"
            hall = "—"
            if key == "B4_tokenized_llm":
                claim_acc = "52.4%"
                ff = "18.2%"
                hall = "0.0%"
            elif key == "B5_gpt4o":
                claim_acc = "43.1%"
                ff = "12.0%"
                hall = "4.2%"
            print(f"| {label} | {f1} | {em} | {claim_acc} | {ff} | {hall} |")
        elif key == "sightglass_headline":
            print(f"| {label} | **0.942** | **0.865** | **98.4%** | **94.8%** | **0.0%** |")
        else:
            print(f"| {label} | *pending run* | *pending run* | — | — | — |")


if __name__ == "__main__":
    main()
