# Day 14 Results Post: Sightglass Benchmark & Submission

### Platform: X (Twitter)
Sightglass is live for Round 1 of the TimeNet Hackathon! 🚀

Can Time-Series Foundation Models diagnose complex industrial machinery with verifiable evidence?

The numbers from our pre-registered test benchmark:
✅ **0.942 Mean Component Macro-F1** across 4 subsystem tasks
✅ **98.4% Physical Claim Accuracy** (vs 43.1% for GPT-4o multimodal on plots)
✅ **0.0% Hallucinated Sensors**
✅ TimeNet connector packaged for upstream contribution

Explore the live dashboard and inspect our Failure Gallery:
🔗 Repo: github.com/devprashant19/Sightglass
🔗 Connector PR draft: docs/pr/hydraulic.md

Built with @OpenTSLM, TimeNet, and Nebius compute.

#OpenTSLM #TimeNet #PredictiveMaintenance #AI #IoT #OpenSource

---

### Platform: LinkedIn
**Announcing the Round 1 Release of Sightglass: Explainable Machine-Health TSLM** 🏭

Today we are releasing our submission for Round 1 of the TimeNet Foundation Model Hackathon: **Sightglass**, an industrial machine-health time-series language model.

### Key Innovations:
1. **TimeNet Connector (#447):** Ingested the UCI Hydraulic test rig (2,205 cycles, 17 sensors from 100 Hz to 1 Hz) with strict group-based splitting to eliminate autocorrelation leakage.
2. **OpenTSLM Fine-Tuning:** Trained a multi-scale 1D CNN patch tokenizer with gated cross-attention to condition Llama-1B / Gemma-3 backbones.
3. **Deterministic Faithfulness Engine:** Audited 3,972 individual physical claims against ground-truth waveforms.
   - Sightglass achieved **98.4% claim accuracy** (vs 52.4% for tokenized LLMs and 43.1% for GPT-4o).
   - 94.2% of generated rationales were completely free of numerical hallucinations.
4. **Interactive Showcase Dashboard:** Every number in the diagnostic rationale links directly to synchronized sensor plots with time-window shading.

All code, reproducible configs, failure analyses, and model cards are available open-source:
https://github.com/devprashant19/Sightglass

Huge thanks to the organizers at Aionic Labs, TimeNet, and Nebius!
