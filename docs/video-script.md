# Demo video script (about 2 minutes 30 seconds)

**Status: not recorded.** Record it against the built site with no API running, so every result on screen says Precomputed, or with `make api` running to show Live. Every number spoken below is from `results/summary.json`; check it again before recording.

**Format:** 1080p screen recording with burned-in subtitles.
**Tone:** engineering-first, calm, precise.

---

## [0:00 – 0:20] The problem

**Visual:** a hydraulic rig schematic with its four parts marked: cooler, valve, pump, accumulator.
**Narration:**
> "A hydraulic press raises an alarm. Which part is wearing out: the cooler, the valve, the pump or the accumulator? The alarm doesn't say. And if you ask a language model to explain the sensor traces, you get fluent numbers with no way to tell whether they are in the data."

---

## [0:20 – 0:40] What Sightglass is

**Visual:** the site's hero, then the "How it works" section.
**Narration:**
> "Sightglass reads one 60-second cycle of a test rig's 17 sensors, names the condition of each part, and writes the evidence as numbers. Then a separate checker reads that text back and recomputes every number from the signal. Today the diagnosis is a gradient-boosted model on physics features. The language model the checker was built for has not been trained yet."

---

## [0:40 – 1:40] The explorer

**Visual:** open `/?cycle=hydraulic-00253&run`.
**Narration:**
> "This is test cycle 253, from operating conditions the model never saw in training. Cooler and valve: correct. Pump: Sightglass says severe leakage; the rig recorded weak. Three of four right."

*(On screen: point at the pump paragraph and its ticked claims.)*
**Narration:**
> "And yet all nine numbers in the explanation are ticked. Each one was recomputed from this cycle's signal and agrees within the tolerance fixed before testing. A verified number is not a correct diagnosis, and the page shows you both."

*(On screen: scroll to the what-if lab, choose "Raise temperature", move the slider to +2 °C.)*
**Narration:**
> "Here is a healthy cycle. Warm the oil by two degrees, and the accumulator verdict changes. That is a shortcut the model learned from how the rig was tested, and we show it rather than hide it."

---

## [1:40 – 2:10] Results

**Visual:** the Results section.
**Narration:**
> "On 329 held-out cycles, the engine reaches 0.959 mean macro-F1; the accumulator is the hard part at 0.870. The checker is tested too: we planted 1,000 wrong numbers and flipped 529 directions in reference explanations, and it caught all of them. Where it falls short: the cited evidence supports the label in 64% of component paragraphs."

---

## [2:10 – 2:30] What is open

**Visual:** the repository's README, the "Not verified" list.
**Narration:**
> "What has not been done is listed in the README: the language-model fine-tune, the language-model baselines, real bearing and wind data, and the TimeNet pull request. The code, the data connector and every result file are at github.com/devprashant19/Sightglass."
