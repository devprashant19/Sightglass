# Baselines on the real UCI #447 data

Grouped split, 329 test cycles. Source: `results/baselines.json` and `results/ablations.json`
(`scripts/run_baselines.py`, seeds 0–2 where listed).

| Baseline | Mean macro-F1 | Cooler | Valve | Pump | Accumulator | Joint EM |
|---|---|---|---|---|---|---|
| B0 majority | 0.149 | 0.184 | 0.141 | 0.170 | 0.101 | 0.064 |
| B1 physics features + LightGBM (3 seeds) | 0.959 ± 0.000 | 1.000 | 0.997 | 0.969 | 0.870 | 0.842 |
| B2 MiniRocket (sktime) + ridge (3 seeds) | 0.967 ± 0.002 | 1.000 | 1.000 | 0.993 | 0.875 | 0.869 |
| B3 1D-CNN, train-split normalisation, early stop on val (3 seeds) | 0.841 ± 0.022 | 1.000 | 0.969 | 0.929 | 0.466 | 0.430 |
| B4 tokenized-text LLM | not run — needs a GPU LLM fine-tune | | | | | |
| B5 GPT-4o on plots | not run — no API key; render/call/parse not implemented | | | | | |

Observations
1. Cooler and valve are easy (as the dataset authors report); the accumulator is the hard target for every method.
2. MiniRocket on raw signals edges out LightGBM on physics features; neither explains itself.
3. LightGBM is deterministic here (no bagging), so its three seeds agree exactly.
4. Ablations: dropping the virtual sensors changes B1 by +0.002 (the physical temperatures already separate the cooler classes); a random split instead of the grouped split raises B1 to 0.998 (+0.039), so random splits overstate performance on this data.
5. B4 and B5 are the comparisons that matter for faithfulness and have not been run; no faithfulness numbers exist for them.
