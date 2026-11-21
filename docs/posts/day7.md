# Day 7 Progress Post: Physical Rationales & The Faithfulness Engine

*Draft, not published. The live explorer it mentions runs locally or on the static site; claims there are checked by the same checker. No language model has been evaluated yet.*

## Platform: X (Twitter)
Midpoint update on Sightglass for the TimeNet hackathon:

What good is a machine learning diagnosis if you can't verify its numbers? 🛠️

In Sightglass, every rationale statement follows a strict physical evidence grammar:
`FS1 mean volume flow 5.70 l/min (13% below healthy)`

Our automated checker recomputes the actual signal feature and verifies it against pre-registered physical tolerances. If an LLM hallucinates an unmeasured value, it gets flagged with an unverified red indicator.

Check out our interactive UI preview in `web/`!

#PredictiveMaintenance #TimeNet #ExplainableAI #MachineLearning

---

## Platform: LinkedIn
**Can we trust AI to explain industrial machinery? Only if we check its math.**

At the midpoint of the TimeNet Foundation Model Hackathon, our team has completed the core faithfulness engine for **Sightglass**.

A major danger of applying LLMs to sensor streams is hallucination: an LLM might correctly guess a fault label by chance, but invent fictional flow rates or operating pressures to justify it.

In Sightglass:
- Features are extracted across 17 sensors (thermodynamic dissipation, cross-correlation propagation lag, pressure ripples).
- Evaluation tolerances are fixed in `configs/faithfulness.yaml` and committed before any test-split result is computed.
- In our live explorer, hovering over any number in the diagnosis highlights the exact sensor and measurement window on the 60-second time series.

Next step: evaluating full test-set claim accuracy across baseline architectures!
