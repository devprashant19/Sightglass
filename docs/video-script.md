# Sightglass Video Demo Script (2 Minutes 30 Seconds)

**Format:** 1080p, 60fps screen recording with burned-in subtitles.  
**Tone:** Engineering-first, calm, precise, no AI hype words.

---

### [0:00 – 0:20] The Problem
**Visual:** High-pressure industrial hydraulic valve and accumulator schematic. Red warning flag flashes on a factory HMI display.  
**Narration:**
> "In an industrial hydraulic plant, an alarm triggers: 'Subsystem anomaly.' But which component failed? Is the valve sticking, is the cooler fouled, or is the main pump leaking internally?
> Standard anomaly alarms tell you *that* something is wrong, but never *why*. And general-purpose LLMs hallucinate plausible-sounding explanations that don't match the sensor waveforms."

---

### [0:20 – 0:40] Introducing Sightglass
**Visual:** Sightglass logo and architecture pipeline diagram (Sensor waveforms -> Anti-aliasing Decimation -> OpenTSLM Flamingo -> Faithful Evidence Generator).  
**Narration:**
> "This is Sightglass: an explainable Time-Series Language Model built for the TimeNet hackathon.
> Sightglass diagnoses multi-component industrial machinery from raw, multi-rate sensor signals—and justifies every diagnosis with physical evidence clauses verified directly against the underlying time series."

---

### [0:40 – 1:40] Live Explorer Demo (The Hero Moment)
**Visual:** Sightglass Explorer UI (`#/explore/hydraulic-00001`).  
**Narration:**
> "Let's inspect test cycle number 1.
> On the left, we select our cycle. In the center, our 17 sensors are rendered across synchronized time axes: high-frequency 100 Hz pressure transients, 10 Hz volume flows, and 1 Hz thermodynamic temperatures.
> On the right, Sightglass generates individual component condition ratings and an evidence rationale."

*(Action on screen: Mouse hovers over claim `[FS1 mean flow dropped to 8.2 l/min]`)*  
**Narration:**
> "Watch what happens when I hover over this claim: the volume flow sensor chart instantly scrolls into view, the sensor trace thickens, and the exact 60-second measurement window is shaded.
> Our pre-registered faithfulness checker computed the true signal mean at 8.18 l/min—confirming the model's assertion within our 5% physical tolerance. Notice the green verified tick."

*(Action on screen: Click to cycle `hydraulic-00048` or failure gallery)*  
**Narration:**
> "And here is our transparent audit: on cycle 48, the model predicted slightly reduced accumulator pressure instead of severely reduced. Because our faithfulness engine checks every assertion against raw signals, subtle calibration limits are immediately flagged for human review."

---

### [1:40 – 2:10] Verified Results
**Visual:** Results page (`#/results`) with baselines comparison table and faithfulness bar chart.  
**Narration:**
> "We pre-registered our evaluation protocol and error tolerances in Git commit 2308207 before computing any test-split metrics.
> On the held-out test split, Sightglass achieves 0.942 mean component macro-F1.
> More importantly: while GPT-4o hallucinates sensors and scores only 43.1% claim accuracy, Sightglass achieves 98.4% claim accuracy, with 94.2% of rationales completely free of unverified numbers."

---

### [2:10 – 2:30] Roadmap & Open-Source
**Visual:** Team and dataset page (`#/dataset`, `#/team`). GitHub repo with PR draft.  
**Narration:**
> "Our UCI Hydraulic connector is packaged for upstream contribution to TimeNet. In upcoming rounds, we are extending Sightglass to high-frequency bearing vibration orders and offshore wind farm telemetry.
> Explore the live dashboard, inspect the failure gallery, and reproduce our runs at github.com/devprashant19/Sightglass."
