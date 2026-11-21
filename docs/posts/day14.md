# Day 14 results post — draft (numbers from results/summary.json, 2026-11-22)

Do not post until the TSLM run exists or the post says plainly that it does not.

## X
Sightglass, round 1 of the TimeNet hackathon: machine-fault diagnosis where every number in the explanation is checked against the signal.

On the real UCI hydraulic rig (329 held-out cycles, grouped split):
- Diagnosis: 0.959 mean macro-F1 (physics features + LightGBM)
- Checker: catches 1,000 of 1,000 deliberately corrupted numbers
- TSLM fine-tune: next, needs GPU time

Dashboard · repo: github.com/devprashant19/Sightglass

## LinkedIn
We built Sightglass for round 1 of the TimeNet hackathon. It diagnoses four components of an industrial hydraulic test rig from 17 sensors and writes the evidence for each diagnosis as numbers you can check.

What is real today:
1. The UCI #447 dataset (2,205 cycles), downloaded and checksummed by our connector, split by operating condition so test conditions are never seen in training.
2. A diagnosis engine: LightGBM on physics features reaches 0.959 mean macro-F1 on the held-out split (cooler 1.000, valve 0.997, pump 0.969, accumulator 0.870).
3. A faithfulness checker that recomputes every stated number from the raw signal. On 2,205 reference explanations it verifies all 17,883 claims and catches every ±20% corruption and every flipped direction we planted.
4. An honest weak spot: in only 64% of component paragraphs does the cited evidence clearly support the label, lowest for the accumulator (40%).

Next: fine-tune OpenTSLM on GPU and put its explanations through the same checker.
