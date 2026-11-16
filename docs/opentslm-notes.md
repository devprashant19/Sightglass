# OpenTSLM Architecture & Fine-Tuning Notes

*Verified against upstream `OpenTSLM/OpenTSLM` at commit `2968f4b891baab4307f7e9d0043e87677b593a30`.*

## 1. Model Architectures: Flamingo vs Soft-Prompt (SP)
OpenTSLM integrates raw time series natively into pretrained Large Language Models:
- **`OpenTSLMFlamingo` (Preferred for multi-series):**
  - Inserts gated cross-attention layers into language model decoder layers (every $n$ layers, default 1).
  - Uses `CNNTokenizer` to patch and encode time-series signals into latent representations.
  - Places special tokens `<image>` (standing in for temporal modalities) and `<|endofchunk|>` into the token stream.
  - Memory consumption stays roughly flat with long time horizons because cross-attention attends over temporal patch latents rather than expanding the causal text sequence window.
- **`OpenTSLMSP` (Soft-Prompt):**
  - Prepends projected time-series embeddings directly into the LLM prefix.
  - Context size grows rapidly with multiple multivariate channels and long sequences (>60 GB VRAM on long inputs).

## 2. Checkpoints & Model Lineage
Pretrained weights on HuggingFace Hub follow the pattern `OpenTSLM/{base_model}-{dataset}-{model_type}`:
- Supported Base Models:
  - `meta-llama/Llama-3.2-1B` (primary headline model)
  - `meta-llama/Llama-3.2-3B`
  - `google/gemma-3-270m` (lightweight smoke/CPU model)
  - `google/gemma-3-1b-pt`
- Published Curricula Stages:
  1. `tsqa` (Time Series Question Answering)
  2. `m4` (Time Series Captioning)
  3. `har` (HAR Chain-of-Thought)
  4. `sleep` (Sleep Stage Classification)
  5. `ecg` (ECG Question Answering)

## 3. Multivariate Input & Prompt Formatting
- Multivariate series are passed using `FullPrompt` combining:
  - `pre_prompt`: Task instructions, sensor metadata, and scaling factors.
  - `text_time_series_prompt_list`: List of `TextTimeSeriesPrompt(text="PS1: ", time_series=array)`.
  - `post_prompt`: The target question (e.g., "Question: Diagnose this hydraulic cycle.").
- Training entry point: `curriculum_learning.py`, using Hugging Face Accelerate, AdamW optimizer, and token loss masked to answer targets only.
