# Hydraulic EDA — real UCI #447 data

All numbers below were computed on the real dataset (downloaded 2026-11-22, SHA-256
`24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2`) by the connector build in
`data/build/hydraulic/`. An earlier version of this file described synthetic data; it was replaced.

## Shapes

- 2,205 cycles of 60 s; 17 sensor files; 43,680 samples per cycle
  (7 × 6,000 at 100 Hz, 2 × 600 at 10 Hz, 8 × 60 at 1 Hz). No missing values.
- `profile.txt`: 5 integer columns per cycle.

## Labels (counts match `documentation.txt`)

| Component | Classes (count) |
|---|---|
| Cooler (%) | 3: 732 · 20: 732 · 100: 741 |
| Valve (%) | 73: 360 · 80: 360 · 90: 360 · 100: 1,125 |
| Pump leakage | 0: 1,221 · 1: 492 · 2: 492 |
| Accumulator (bar) | 90: 808 · 100: 399 · 115: 399 · 130: 599 |
| Stable flag | 0 = conditions were stable: 1,449 · 1 = static conditions might not have been reached yet: 756 |

## Label sequence

- 144 unique four-label combinations (every combination of the 3 × 4 × 3 × 4 levels occurs),
  10 to 230 cycles each.
- The four-label tuple changes 193 times along the run (194 runs of constant conditions; median
  run 10 cycles, longest 210). Cooler changes only twice (long blocks); valve changes 144 times.
- Neighbouring cycles are strongly correlated (lag-1 correlation of mean PS1 = 0.72), so a
  random split would put near-copies of test cycles in train.
- 26% of condition changes start with a cycle flagged "not yet stable".

## Split decision

Conditions repeat throughout the run, so the split is **grouped by the four-label tuple**: each
combination goes entirely to train, val or test, and the first combination seen for any class
goes to train so every class of every component is in train.

| Split | Cycles | Combinations |
|---|---|---|
| train | 1,543 | 104 |
| val | 333 | 11 |
| test | 329 | 29 |

A random 70/15/15 split (seed 0) is kept only for the leakage ablation.

## Healthy cycles

Only **21 cycles** have all four components healthy (cooler 100 %, valve 100 %, pump 0,
accumulator 130 bar). They form one combination, which the grouped split put in **test**, so
train has none. The healthy reference is therefore fitted **per component**: a feature linked to
component X uses the train cycles where X is healthy (stable cycles only); unlinked features use
cycles with at least three of the four components healthy. See `HealthyReference.fit_per_component`.

## Virtual-sensor leakage

A one-feature logistic regression on mean CE (virtual cooling efficiency) alone reaches a cooler
macro-F1 of 1.0 on the test split. CE is computed from other sensors, so the cooler label is
close to directly readable from it. The no-virtual ablation in `results/ablations.json` measures
what B1 loses without CE, CP and SE.
