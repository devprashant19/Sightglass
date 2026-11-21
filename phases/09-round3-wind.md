# Phase 9 — Round 3: CARE wind turbines

| | |
|---|---|
| **Goal** | Early warning of wind-turbine faults from SCADA data, with explanations based on deviation from expected normal behaviour, and a reported warning lead time. |
| **Owner** | Both (Aman: licence, connector, physics, eval; Teammate: training, export, wind-farm page) |
| **When** | Round 3 |
| **Depends on** | Round 1 pipeline; windowing from Phase 8 |
| **Unblocks** | Phase 10 pooled model |

---

## 1. Licence first (day 1)

- **CARE dataset** (CC BY-SA 4.0): SCADA data from real wind farms with labelled fault events and normal periods **(verify contents and size)**.
- [ ] ShareAlike requires derivatives to carry the same licence. Ask in the TimeNet Discord whether a CC BY-SA connector is acceptable, and whether the build counts as a derivative. Write the answer in `docs/competition-notes.md`.
- [ ] If it isn't accepted: ship a user-built connector (the user downloads the data and the connector converts it locally, with nothing redistributed), or switch to OPS-SAT spacecraft telemetry for this round.

## 2. Connector (`timenet_connectors/datasets/<org>/care_wind/`)

| TimeF concept | Wind mapping |
|---|---|
| Record | One turbine's time series over one dataset period (or one labelled event period plus its lead-up) **(decide from the data layout)** |
| Source | SCADA groups: power and wind, temperatures (gearbox, generator, bearings, nacelle, ambient), rotor and pitch, grid |
| Signal | Each SCADA channel at its native rate (often 10-minute averages) |
| Annotations | Fault events (start, end, component, description), normal periods, turbine id, farm id |

- [ ] **Splits by turbine and by event**, never by window. Test turbines or test events are held out completely.
- [ ] Tasks: `early_warning` (binary per window: is a fault event coming within the horizon?), `fault_component` (which component, for windows before an event), `diagnosis_qa`.

## 3. Windows and labels

- [ ] Sliding windows, for example 3 days of history, stepped every 6 hours **(tune on train)**.
- [ ] A window is positive if a labelled fault starts within the warning horizon (for example 14 days) after the window ends; negative if it's inside a normal period with no event in the horizon; windows during an event are excluded.
- [ ] Record horizon and window length in `configs/data/wind.yaml` before test. <!-- check-docs: ignore -->

## 4. Physics module (`src/sightglass/physics/wind.py`) — normal-behaviour models

The core idea: a gearbox bearing at 70 °C is fine at full power on a hot day and alarming at low power on a cold day. So we compare each temperature with what's *expected* for the current conditions.

- [ ] For each monitored component temperature, fit a normal-behaviour model on **normal periods of train turbines only**: expected temperature from power, wind speed, ambient temperature, rotor speed (start with gradient boosting or ridge on lagged inputs).
- [ ] Residual = measured − expected. Features per window:

| Feature | Definition | Unit |
|---|---|---|
| `<comp>.residual_mean` | Mean residual over the window | °C |
| `<comp>.residual_trend` | Slope of the residual over the window | °C/day |
| `<comp>.residual_max` | Max residual | °C |
| `<comp>.days_above` | Days with residual above the healthy 95th percentile | days |
| `power_curve.deficit` | Power below the turbine's normal power curve at the same wind speed | % |

- [ ] Healthy reference: residual distribution per component on normal periods of train turbines.

### Rationale example

> Early warning: gearbox. Evidence: gearbox bearing temperature residual 4.1 °C (above healthy) averaged over 5 days; residual trend 0.6 °C/day. The bearing runs hotter than expected for its power and ambient temperature, and the gap is growing.

## 5. Training and evaluation

- [ ] Phase 4 setup, with the window's channels as series and the residual features as text.
- [ ] Baselines: threshold on residual (the classic SCADA approach), LightGBM on features, a simple autoencoder anomaly score, tokenized-text LLM.
- [ ] Metrics (decide the exact definitions before test, in the eval protocol):

| Metric | Definition |
|---|---|
| Event detection rate | % of test fault events with at least one warning inside the horizon before the event |
| **Warning lead time** | Time from the first correct warning to the event start; median and IQR across events |
| False alarms | Warnings on normal periods, per turbine-month |
| Window-level F1 | Secondary |
| Faithfulness | As in Phase 5, on residual claims |

- [ ] An operating-point chart: detection rate vs false alarms per turbine-month as the warning threshold varies.

## 6. Dashboard: wind-farm view (`#/wind`)

- [ ] Farm overview: turbines as a grid or map (positions if the dataset has them; otherwise a grid), coloured by current warning state at a chosen date.
- [ ] Turbine timeline: residuals over time, warning markers, labelled fault events shaded.
- [ ] Lead-time chart: one bar per test event, showing how early the first warning came.
- [ ] Hovering a claim highlights the residual series and the window it refers to.

## Exit criteria

- [ ] Licence question answered and recorded.
- [ ] CARE connector PR merged (or open and passing), or the fallback chosen.
- [ ] Warning lead time, detection rate and false-alarm rate reported, with faithfulness.
- [ ] Wind-farm page live.

## Risks in this phase

| Risk | What to do |
|---|---|
| ShareAlike blocks TimeNet hosting | User-built connector or OPS-SAT |
| Few fault events | Report per-event results, not just averages; give CIs |
| Normal-behaviour model learns the fault | Fit only on normal periods of train turbines; check residuals on held-out normal periods are near zero |
| Data gaps and curtailment | Mask curtailed and missing periods; record the rules in the dataset card |
