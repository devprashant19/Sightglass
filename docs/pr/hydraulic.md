# Upstream TimeNet Pull Request: UCI Hydraulic System (#447)

**Title:** `Add UCI hydraulic system condition monitoring dataset connector`

## Summary
This pull request adds a comprehensive TimeNet dataset connector for the **UCI Hydraulic System Condition Monitoring** dataset (#447). The dataset captures 2,205 60-second machine load cycles monitoring four critical hydraulic subsystems (cooler, directional valve, high-pressure pump, and nitrogen accumulator).

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
- Deterministic conversion verified.
- 100% finite sensor values verified (zero NaNs or nulls).
- Full split disjointness and complete dataset coverage verified.
- All upstream connector checks pass cleanly.
