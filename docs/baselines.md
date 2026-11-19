# Sightglass Baseline Evaluation Notes

## 1. Baseline Summary
Baselines establish performance bounds on the identical grouped split (`configs/baselines/hydraulic.yaml`):

- **B0 Majority Class:** Simple empirical mode baseline setting lower bound for macro-F1.
- **B1 Features + LightGBM:** High-performance tabular gradient boosting on physical features.
- **B1 Ablation (No Virtual Sensors):** Excludes calculated virtual channels (`CE`, `CP`, `SE`). Confirms that while virtual channels inflate cooler classification macro-F1, physical sensors (`TS1.mean`, `TS1.slope`, `cooler.delta_t`) alone provide solid discriminatory power.
- **B2 MiniRocket:** Random convolutional kernels over resampled raw multi-channel time series.
- **B3 1D-CNN:** 4-block multi-task convolutional neural network trained on normalized 10 Hz channels.
- **B4 Tokenized-Text LLM:** Language model fine-tuned on raw numbers serialized into tokenized text prompts.
- **B5 GPT-4o on Plots:** Zero-shot multimodal evaluation on sensor plots for a 200-cycle stratified test sample.

## 2. Key Observations
1. **Accuracy vs. Explainability:** Classical models (LightGBM) achieve high macro-F1 on hydraulic component fault classification, but are black boxes that cannot provide natural-language evidence verifiable against physical sensor streams.
2. **Virtual Sensor Impact:** Inclusion of virtual sensors (`CE`, `CP`, `SE`) inflates cooler condition accuracy. Removing them reduces cooler macro-F1 moderately, highlighting why Sightglass prioritizes primary physical sensors in its rationale ranking.
3. **Faithfulness Gap:** While LLMs without temporal inductive bias (B4 and B5) can output text, they frequently hallucinate numeric values and cited sensor directions. Sightglass closes this gap by enforcing physical verification.
