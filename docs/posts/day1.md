# Day 1 Launch Post: Introducing Sightglass

*Draft, not published. Written at the start, it describes the plan: the OpenTSLM fine-tune it mentions has not been trained. Edit it to match the README before posting.*

## Platform: X (Twitter)
Industrial machines don't fail quietly—they scream through thousands of sensor readings every second. 📈

For the @AionicLabs TimeNet Hackathon, we're building **Sightglass**: an explainable Time-Series Language Model (TSLM) that diagnoses industrial machine faults from raw waveforms and audits every explanation directly against physical signals.

No hallucinated numbers. No black boxes.

Building on @OpenTSLM and TimeNet. Follow along as we train and open-source the pipeline:
github.com/devprashant19/Sightglass

#AI #TimeSeries #OpenTSLM #PredictiveMaintenance #MachineLearning

---

## Platform: LinkedIn
Excited to announce our project for the TimeNet Foundation Model Hackathon: **Sightglass** ⚙️

Most machine learning models in predictive maintenance act as black boxes: an alarm sounds, an amber indicator flashes, but technicians are left guessing whether a pump is leaking or a valve is lagging. Worse, standard generative AI tools hallucinate plausible-sounding explanations that fall apart under engineering review.

With **Sightglass**, we are building a closed-loop system:
1. Ingesting multi-rate raw signals (100 Hz pressure, 10 Hz flow, 1 Hz temperature) via TimeNet.
2. Fine-tuning OpenTSLM Flamingo to generate diagnoses with structured evidence clauses.
3. Pre-registering a deterministic faithfulness engine that recalculates stated values against signal ground truth.

Follow our open-source progress on GitHub: https://github.com/devprashant19/Sightglass
