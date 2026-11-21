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
**Visual:** Sightglass explorer (pick a test cycle id from `web/public/data/hydraulic/index.json`).  
**Narration:**
> "Let's inspect test cycle number 1.
> On the left, we select our cycle. In the center, our 17 sensors are rendered across synchronized time axes: high-frequency 100 Hz pressure transients, 10 Hz volume flows, and 1 Hz thermodynamic temperatures.
> On the right, Sightglass generates individual component condition ratings and an evidence rationale."

*(Action on screen: Mouse hovers over claim `[FS1 mean flow dropped to 8.2 l/min]`)*  
**Narration:**
> "Watch what happens when I hover over this claim: the volume flow sensor chart instantly scrolls into view, the sensor trace thickens, and the exact 60-second measurement window is shaded.
> The checker recomputed that number from the raw signal and it agrees within the pre-registered 5% tolerance, so it gets a verified tick."

*(Action on screen: Click to cycle `hydraulic-00048` or failure gallery)*  
**Narration:**
> "And here is a failure from the gallery (pick a real one from `web/public/data/hydraulic/failures.json` when recording): a wrong accumulator level, shown with the evidence that misled it."

---

### [1:40 – 2:10] Verified Results
**Visual:** Results section of the dashboard (numbers load from `web/public/data/summary.json`).
**Narration:**
> "On 329 held-out cycles from operating conditions the model never saw, the engine reaches 0.959 mean macro-F1. The accumulator is the hard part at 0.870.
> The checker itself is tested: we planted 1,000 wrong numbers and flipped 529 directions in reference explanations, and it caught all of them.
> And we show where it falls short: the cited evidence supports the label in 64% of component paragraphs. The language model fine-tune is next."

---

### [2:10 – 2:30] Roadmap & Open-Source
**Visual:** Team and dataset page (`#/dataset`, `#/team`). GitHub repo with PR draft.  
**Narration:**
> "Our UCI Hydraulic connector is packaged for upstream contribution to TimeNet. In upcoming rounds, we are extending Sightglass to high-frequency bearing vibration orders and offshore wind farm telemetry.
> Explore the live dashboard, inspect the failure gallery, and reproduce our runs at github.com/devprashant19/Sightglass."
