# Sightglass Pre-Registered Evaluation Protocol

This protocol pre-registers the evaluation rules, splits, metrics, and faithfulness verification criteria for Sightglass.

## 1. Grouped Split Methodology
- **Hydraulic Rig:** 2,205 total 60-second cycles. Grouped strictly by the 4-label tuple `(cooler, valve, pump, accumulator)` to prevent cycle-to-cycle autocorrelation leakage.
- **Split Proportions:** 70% Train, 15% Validation, 15% Test.
- **Constraint:** All classes for every component must be represented in the training set. The test set is strictly sequestered and never used for prompt engineering, hyperparameter tuning, or tolerance adjustments.
- **Random Split Control:** A random 70/15/15 split is maintained solely to quantify score inflation from neighbour-cycle leakage.

## 2. Diagnostic Performance Metrics
- **Per-Component Macro-F1:** Evaluated across the discrete classes of each subsystem:
  - Cooler Condition (3 classes: 3%, 20%, 100%)
  - Valve Condition (4 classes: 100%, 90%, 80%, 73%)
  - Internal Pump Leakage (3 classes: 0, 1, 2)
  - Accumulator Pressure (4 classes: 130 bar, 115 bar, 100 bar, 90 bar)
- **Mean Macro-F1:** Arithmetic mean of macro-F1 across the four components.
- **Joint Exact Match:** Percentage of cycles where all four component diagnoses are simultaneously correct.
- **Bootstrap Confidence Intervals:** 95% two-sided empirical bootstrap intervals over 1,000 resamples of test cycles.
- **Seed Variance:** Reported as mean ± standard deviation across seeds (0, 1, 2).

## 3. Physical Faithfulness Checker
Explanations are evaluated by parsing structured claims and comparing them directly against physical values recomputed from native-rate sensor signals:
- **Canonical Clause Grammar:**
  - `<SENSOR> <quantity> <value> <unit> (<pct>% <above|below> healthy)`
  - `<SENSOR> <quantity> <value> <unit> (within <pct>% of healthy)`
  - When the healthy mean is near zero (|mean| < 2·std, e.g. slopes and lags), the deviation is stated in standard deviations: `(<z>σ <above|below> healthy)` or `(within 1.0σ of healthy)`.
- **Healthy reference:** per feature, from train cycles in which the linked component is healthy (stable cycles only); see `docs/hydraulic-eda.md` for why.
- **Verification Rules:**
  - `relative_tolerance`: 0.05 (value verified if within 5% of signal recomputation).
  - `absolute_floor`: Fixed absolute tolerance for values near zero (e.g., 0.05 s for rise time / lag, 0.05 °C/min for temperature slope).
  - `pct_tolerance_points` / `pct_relative_tolerance`: the stated % must be within max(3 points, 5% of the true %).
  - `sigma_tolerance` / `sigma_relative_tolerance`: the stated σ must be within max(0.3σ, 5% of the true z).
  - `direction_neutral_band_pct`: 2.0% (deviations within ±2.0% count as "within healthy").
- **Key Faithfulness Metrics:**
  - **Claim Accuracy:** % of parsed numeric claims where both value and direction are verified against the signal.
  - **Value Accuracy:** % of claims where value is verified, independent of direction.
  - **Direction Accuracy:** % of claims where deviation direction matches physical truth.
  - **Hallucinated Sensor Rate:** % of cited sensors that do not physically exist on the machine.
  - **Unparsed Claim Rate:** Fraction of unparsed numeric fragments relative to all numeric fragments.
  - **Fully Faithful Rationales:** % of explanations where 100% of claims are verified and at least one valid claim is made.
  - **Label-Rationale Consistency:** at least one cited feature is a kept physical link for the component and its recomputed deviation lies outside the healthy spread (|z| > 1) in the link's direction for a faulty label, or inside it (|z| ≤ 1) for a healthy label.

## 4. History
Fixed on 2026-11-22 before any metric on the real UCI #447 test split was computed. Earlier
results in this repository came from synthetic data and a stub model and were deleted.
