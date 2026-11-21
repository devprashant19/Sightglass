---
language:
- en
license: mit
tags:
- time-series
- foundation-model
- open-tslm
- predictive-maintenance
- industrial-iot
- explainable-ai
datasets:
- uci_hydraulic
metrics:
- macro-f1
- claim-accuracy
- joint-exact-match
---

# Model Card for Sightglass

Sightglass is an explainable Time-Series Language Model (TSLM) designed for industrial machine-health diagnosis. Given raw, multi-rate sensor time-series waveforms, Sightglass generates natural language diagnostic assessments where every stated numerical value is grounded in physical features and verified by a deterministic faithfulness checker.

## Model Details

- **Model Name:** Sightglass
- **Version:** 1.0.0
- **Model Type:** Multimodal Time-Series Language Model (1D Temporal CNN Patch Tokenizer + Gated Cross-Attention + Autoregressive LLM Backbone)
- **Backbone Architectures:** Llama-3.2-1B / Gemma-3-270M
- **Upstream Frameworks:** TimeNet (TimeF data format), OpenTSLM (Flamingo temporal conditioning)
- **Developed by:** Team Sightglass (Prashant Dev et al.)
- **Licence:** MIT (Code & Model Weights), CC BY 4.0 (UCI Hydraulic Dataset #447)

## Intended Use

- **Primary Use Case:** Maintenance decision support for plant engineers and operators monitoring industrial hydraulic systems, high-pressure test benches, and fluid-power circuits.
- **Out-of-Scope Use:** Sightglass is **not** an emergency safety shutdown system and should **not** replace physical pressure relief valves or statutory safety inspections. Maintenance technicians must always review cited signal evidence before taking high-risk action.

## Training Data & Group-Based Splitting

- **Dataset:** UCI Hydraulic System Condition Monitoring (#447).
- **Sensors:** 17 time-series channels (PS1–PS6 pressure @ 100 Hz, EPS1 motor power @ 100 Hz, FS1–FS2 flow @ 10 Hz, TS1–TS4 temperature @ 1 Hz, VS1 vibration @ 1 Hz, CE/CP/SE virtual @ 1 Hz).
- **Split Strategy:** Strict grouped-split by cycle index (70% train, 15% validation, 15% test). Never split by random window, preventing neighbor autocorrelation leakage.

## Evaluation & Faithfulness Metrics

Tolerances and evaluation rules were pre-registered in `configs/faithfulness.yaml` (Commit SHA: `2308207`).

| Metric | Sightglass (Llama-1B) | Tokenized LLM (B4) | GPT-4o on Plots (B5) |
|---|---|---|---|
| **Mean Macro-F1** | **0.942** | 0.136 | 0.412 |
| **Joint Exact Match** | **0.885** | 0.000 | 0.125 |
| **Claim Accuracy** | **98.4%** | 52.4% | 43.1% |
| **Fully Faithful Rationales** | **94.2%** | 18.2% | 12.0% |
| **Hallucinated Sensor Rate** | **0.0%** | 0.0% | 4.2% |

## Ethical Considerations & Limitations

- **Laboratory Bench vs Real World:** The model was trained on a single physical test bench operating in repetitive 60-second actuation sequences. Continuous streaming operation across variable-speed machinery requires temporal window aggregation.
- **Verification First:** Explanations cite native signal calculations. Operators should inspect the highlighted sensor and time window in the Sightglass Explorer to confirm physical findings.
