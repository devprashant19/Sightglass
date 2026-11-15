# TimeNet Hackathon — Competition Notes

## 1. Challenge & Submission Requirements
- **Challenge:** TimeNet Online Hackathon (https://challenge.timenet.ai/)
- **Objective:** Build a Temporal AI application, onboard a new domain dataset into TimeNet TimeF format, and fine-tune or train an open temporal foundation model (such as OpenTSLM).
- **Submission Package Requirements:**
  1. Link to opened or merged Pull Request on `OpenTSLM/TimeNet` adding the dataset connector.
  2. Public GitHub repository (`sightglass`) with complete codebase, reproduction instructions, and clear licensing.
  3. Deployed public dashboard showcasing interactive model diagnoses and evidence.
  4. 2–3 minute video demonstration (captions burned-in, clear narrative).
  5. Comprehensive `MODEL_CARD.md` detailing architecture, training data, evaluation metrics, and ethical limitations.
  6. Public X and LinkedIn social posts documenting the project launch, progress, and results.
  7. Official submission form submission (e.g., tally.so/r/J1qbyK).

## 2. Judging Criteria & Weighting
- **Technical Excellence & Rigor:** Correct time-series handling, leak-free grouped evaluation, reproducible runs.
- **Novelty & Differentiation:** Explanation faithfulness—verifying model-claimed numbers against physical ground truth signals rather than ungrounded hallucinated rationales.
- **Usability & Presentation:** Interactive dashboard, clear visualizations with synchronous cursors, responsive design.
- **Open-Source Contribution:** High-quality, clean dataset connector meeting all TimeNet standards and passing CI checks.

## 3. Dataset Status & Claims
- **Round 1 (UCI Hydraulic Test Rig - #447):** Confirmed free and unclaimed in open/closed PRs. Full CC BY 4.0 license.
- **Round 2 (HUST Bearings):** Mendeley Data, CC BY 4.0 license. Pre-checked.
- **Round 3 (CARE Wind Turbines):** CC BY-SA 4.0. Note: ShareAlike compatibility checked; fallback paths prepared (local user build or OPS-SAT).
