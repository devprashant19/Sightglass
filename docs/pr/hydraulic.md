# Upstream TimeNet Pull Request: UCI Hydraulic System (#447)

**Title:** `Add UCI hydraulic system condition monitoring dataset connector`

## Summary
This pull request adds a TimeNet dataset connector for the **UCI Hydraulic System Condition Monitoring** dataset (#447). The dataset captures 2,205 60-second machine load cycles monitoring four critical hydraulic subsystems (cooler, directional valve, high-pressure pump, and nitrogen accumulator).

## Dataset Metadata
- **Source:** [UCI Machine Learning Repository #447](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems)
- **License:** CC BY 4.0 (Creative Commons Attribution 4.0 International)
- **Citation:** Helwig, N., Pignanelli, E., & Schütze, A. (2015). Condition monitoring of a complex hydraulic system using multivariate statistics. In *2015 IEEE International Instrumentation and Measurement Technology Conference (I2MTC)* (pp. 210-215). IEEE.

## Sensors & Time Axes
The connector maps all 17 sensors to native multi-rate regular time axes without artificial resampling:
- 7 channels at 100 Hz (6,000 samples): PS1–PS6 (bar), EPS1 (W)
- 2 channels at 10 Hz (600 samples): FS1–FS2 (l/min)
- 8 channels at 1 Hz (60 samples): TS1–TS4 (°C), VS1 (mm/s), CE (%), CP (kW), SE (%)

## Tasks & Leak-Free Splits
- **Tasks Defined:**
  - `cooler_condition` (3 classes)
  - `valve_condition` (4 classes)
  - `pump_leakage` (3 classes)
  - `accumulator_pressure` (4 classes)
  - `joint_condition` (Multi-label joint diagnosis)
- **Split Strategy:** Grouped stratified split by 4-label tuple `(cooler, valve, pump, accumulator)`. Sequestering entire condition blocks prevents autocorrelation leakage between consecutive load cycles. All classes are fully represented in train.

## Verification & Testing
- `download()` fetches the UCI zip and verifies SHA-256 `24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2`.
- `convert()` validates every shape (2,205 × 6,000 / 600 / 60), rejects non-finite values and unexpected label values, and is deterministic (tested on a fixture).
- Grouped split on real data: 1,543 / 333 / 329 cycles; every class of every component in train.
- **Not done yet:** porting to TimeNet's connector base class and running TimeNet's own make targets (check, test, test-connectors, license-check) on a fork. The PR has not been opened.
