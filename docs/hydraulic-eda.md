# UCI Hydraulic System (#447) — Exploratory Data Analysis & Split Decision

## 1. Dataset Dimensions & Sensor Channels
The dataset comprises 2,205 continuous 60-second load cycles from a primary hydraulic circuit paired with a secondary cooling-filtration circuit.

| Sensor | Physical Quantity | Native Rate | Points / Cycle | Engineering Unit | Subsystem |
|---|---|---|---|---|---|
| PS1 | Working pressure | 100 Hz | 6,000 | bar | Primary circuit |
| PS2 | Return pressure | 100 Hz | 6,000 | bar | Main directional valve |
| PS3 | Feed pressure | 100 Hz | 6,000 | bar | High-pressure pump |
| PS4 | Filter pressure | 100 Hz | 6,000 | bar | Filtration circuit |
| PS5 | Accumulator pressure | 100 Hz | 6,000 | bar | Nitrogen accumulator |
| PS6 | Cooler pressure | 100 Hz | 6,000 | bar | Heat exchanger inlet |
| EPS1 | Motor power | 100 Hz | 6,000 | W | Electric drive motor |
| FS1 | Volume flow | 10 Hz | 600 | l/min | Main flow rate |
| FS2 | Volume flow | 10 Hz | 600 | l/min | Cooling circuit flow |
| TS1 | Fluid temperature | 1 Hz | 60 | °C | Cooler inlet |
| TS2 | Fluid temperature | 1 Hz | 60 | °C | Cooler outlet |
| TS3 | Fluid temperature | 1 Hz | 60 | °C | Reservoir tank |
| TS4 | Fluid temperature | 1 Hz | 60 | °C | Pump body |
| VS1 | Mechanical vibration | 1 Hz | 60 | mm/s | Main pump casing |
| CE | Cooling efficiency | 1 Hz | 60 | % | Virtual calculated |
| CP | Cooling power | 1 Hz | 60 | kW | Virtual calculated |
| SE | Efficiency factor | 1 Hz | 60 | % | Virtual calculated |

## 2. Ground Truth Health Labels (`profile.txt`)
Five distinct columns track machine degradation states:
1. **Cooler Condition:** 3% (close to total failure), 20% (reduced efficiency), 100% (full efficiency).
2. **Valve Condition:** 100% (optimal switching), 90% (small switching lag), 80% (severe lag), 73% (close to total failure).
3. **Internal Pump Leakage:** 0 (no leakage), 1 (weak leakage), 2 (severe leakage).
4. **Hydraulic Accumulator:** 130 bar (optimal), 115 bar (slightly reduced pre-charge), 100 bar (severely reduced), 90 bar (close to total failure).
5. **Stable Flag:** 0 = condition was stable; 1 = conditions might not have reached thermal/mechanical equilibrium yet.

## 3. Label Sequence & Autocorrelation Analysis
- Condition combinations change in sequential experimental blocks on the test bench.
- High autocorrelation exists between adjacent cycles ($i$ and $i+1$). A random train/val/test split causes severe data leakage where nearly identical sensor trajectories exist in both train and test splits, artificially inflating classical ML and LLM scores.
- **Split Decision:** We implement a **Grouped Stratified Split** partitioned on the 4-label tuple `(cooler, valve, pump, accumulator)`. Entire condition blocks are held out together.
- Class Representation: Training set receives 70% of cycles and is guaranteed to contain every severity level of all four subsystems. Validation and test sets receive 15% each.
- **Random Split Baseline:** Retained strictly as an ablation control to demonstrate the magnitude of neighbor-leakage score inflation.

## 4. Virtual Sensor Leakage Risk
Sensors `CE`, `CP`, and `SE` are computed from primary physical channels (`TS1`, `TS2`, `FS1`, `EPS1`). In particular, `CE` strongly correlates directly with the cooler target label. Sightglass implements a specific ablation (`no_virtual`) dropping these channels to verify that physical reasoning holds when relying purely on direct physical sensors.
