# Rationale spot-check (50 random train cycles, real UCI #447 data)

Checker round trip: 17883/17883 claims verified (100.0%). Read each one against the physics; note any number or interpretation that looks wrong.

### `hydraulic-00021` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 44.7 °C (44% above healthy); TS1 mean temperature 48.3 °C (34% above healthy); TS3 mean temperature 49.6 °C (28% above healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.86 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.64 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 368 W·min/l (4% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 46.4 bar (within 1% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-00039` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 46.6 °C (50% above healthy); TS1 mean temperature 50.8 °C (41% above healthy); TS3 mean temperature 52.3 °C (35% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.89 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.63 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 365 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 46.1 bar (within 1% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-00063` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 47.3 °C (53% above healthy); TS1 mean temperature 52.0 °C (44% above healthy); TS3 mean temperature 53.5 °C (38% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS1/PS2 valve switching lag 9.79 s (within 1% of healthy); PS2 pressure rise time 9.40 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.62 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 364 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 46.0 bar (within 1% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-00087` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 48.2 °C (55% above healthy); TS1 mean temperature 52.9 °C (47% above healthy); TS3 mean temperature 54.5 °C (40% above healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.76 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.61 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 365 W·min/l (5% below healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.9 bar (within 2% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-00098` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 48.7 °C (57% above healthy); TS1 mean temperature 53.2 °C (48% above healthy); TS3 mean temperature 54.7 °C (41% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.76 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.61 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 365 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.9 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00114` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.0 °C (58% above healthy); TS1 mean temperature 53.6 °C (49% above healthy); TS3 mean temperature 55.1 °C (42% above healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: optimal. Evidence: PS2 pressure rise time 9.40 s (within 1% of healthy); PS1/PS2 valve switching lag 9.75 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.60 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 364 W·min/l (5% below healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00131` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.2 °C (59% above healthy); TS1 mean temperature 53.8 °C (49% above healthy); TS3 mean temperature 55.3 °C (42% above healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.75 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.60 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 364 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00136` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.2 °C (59% above healthy); TS1 mean temperature 53.8 °C (49% above healthy); TS3 mean temperature 55.4 °C (42% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.75 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.61 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 363 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00151` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.3 °C (59% above healthy); TS1 mean temperature 53.9 °C (50% above healthy); TS3 mean temperature 55.5 °C (43% above healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.74 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.60 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 363 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00153` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.2 °C (59% above healthy); TS1 mean temperature 53.9 °C (50% above healthy); TS3 mean temperature 55.5 °C (43% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.74 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.61 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 363 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-00191` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.5 °C (59% above healthy); TS1 mean temperature 54.2 °C (51% above healthy); TS3 mean temperature 55.7 °C (43% above healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.74 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.60 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 363 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-00205` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.6 °C (60% above healthy); TS1 mean temperature 54.3 °C (51% above healthy); TS3 mean temperature 55.8 °C (44% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.74 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.60 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 364 W·min/l (5% below healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00206` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.6 °C (60% above healthy); TS1 mean temperature 54.3 °C (51% above healthy); TS3 mean temperature 55.8 °C (44% above healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS2 pressure rise time 9.40 s (within 1% of healthy); PS1/PS2 valve switching lag 9.75 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.59 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 364 W·min/l (5% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Circuit pressure ripple is minimal and peak buffering operates at optimal baseline.
```

### `hydraulic-00274` · labels {'cooler_condition': 3, 'valve_condition': 90, 'pump_leakage': 1, 'accumulator_pressure': 130}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 49.6 °C (60% above healthy); TS1 mean temperature 54.4 °C (51% above healthy); TS3 mean temperature 55.9 °C (44% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.77 s (within 1% of healthy); PS2 pressure rise time 9.47 s (2% above healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.37 l/min (3% below healthy); EPS1/FS1 power-to-flow ratio 377 W·min/l (within 2% of healthy); SE system efficiency factor 58.0 % (within 1% of healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: optimal. Evidence: PS2 pressure ripple 45.8 bar (within 2% of healthy). Hydraulic accumulator effectively dampens load transients with normal pre-charge.
```

### `hydraulic-00458` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 115}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 51.4 °C (66% above healthy); TS1 mean temperature 56.0 °C (56% above healthy); TS3 mean temperature 57.6 °C (48% above healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.89 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 6.60 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 362 W·min/l (6% below healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: slightly reduced. Evidence: PS2 pressure ripple 45.5 bar (2% below healthy). Elevated pressure ripple across working lines indicates moderate degradation of accumulator pre-charge.
```

### `hydraulic-00513` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 2, 'accumulator_pressure': 100}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 52.8 °C (70% above healthy); TS3 mean temperature 59.1 °C (52% above healthy); TS1 mean temperature 57.5 °C (60% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.40 s (within 1% of healthy); PS1/PS2 valve switching lag 9.63 s (within 2% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 3.28 l/min (50% below healthy); EPS1/FS1 power-to-flow ratio 799 W·min/l (109% above healthy); SE system efficiency factor 30.4 % (48% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 56.6 bar (21% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-00647` · labels {'cooler_condition': 3, 'valve_condition': 100, 'pump_leakage': 2, 'accumulator_pressure': 90}

```
Cooler: close to total failure. Evidence: TS4 mean temperature 52.6 °C (69% above healthy); TS3 mean temperature 58.8 °C (51% above healthy); TS1 mean temperature 57.2 °C (59% above healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS2 pressure rise time 9.40 s (within 1% of healthy); PS1/PS2 valve switching lag 9.59 s (2% below healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 3.26 l/min (50% below healthy); EPS1/FS1 power-to-flow ratio 804 W·min/l (110% above healthy); SE system efficiency factor 30.2 % (49% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 56.6 bar (21% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-00958` · labels {'cooler_condition': 20, 'valve_condition': 80, 'pump_leakage': 2, 'accumulator_pressure': 130}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 41.6 °C (34% above healthy); TS1 mean temperature 45.9 °C (28% above healthy); TS3 mean temperature 48.2 °C (24% above healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: severe lag. Evidence: PS1/PS2 valve switching lag 9.94 s (within 1% of healthy); PS2 pressure rise time 9.57 s (3% above healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.35 l/min (3% below healthy); EPS1/FS1 power-to-flow ratio 390 W·min/l (within 2% of healthy); SE system efficiency factor 56.2 % (4% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: optimal. Evidence: PS2 pressure ripple 46.5 bar (within 1% of healthy). Hydraulic accumulator effectively dampens load transients with normal pre-charge.
```

### `hydraulic-01079` · labels {'cooler_condition': 20, 'valve_condition': 73, 'pump_leakage': 2, 'accumulator_pressure': 115}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 40.7 °C (31% above healthy); TS3 mean temperature 47.4 °C (22% above healthy); TS1 mean temperature 45.1 °C (25% above healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: close to total failure. Evidence: PS1/PS2 valve switching lag 10.0 s (2% above healthy); PS2 pressure rise time 9.70 s (5% above healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.33 l/min (4% below healthy); EPS1/FS1 power-to-flow ratio 393 W·min/l (3% above healthy); SE system efficiency factor 55.2 % (6% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: slightly reduced. Evidence: PS2 pressure ripple 46.8 bar (within 1% of healthy). Hydraulic dampening shows early wear with mildly heightened ripple during load transitions.
```

### `hydraulic-01149` · labels {'cooler_condition': 20, 'valve_condition': 100, 'pump_leakage': 1, 'accumulator_pressure': 115}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 40.1 °C (29% above healthy); TS1 mean temperature 44.6 °C (24% above healthy); TS3 mean temperature 46.8 °C (20% above healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.89 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.47 l/min (within 2% of healthy); EPS1/FS1 power-to-flow ratio 382 W·min/l (within 1% of healthy); SE system efficiency factor 57.7 % (within 2% of healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: slightly reduced. Evidence: PS2 pressure ripple 46.4 bar (within 1% of healthy). Slight increase in pressure oscillations indicates reduced surge dampening capacity.
```

### `hydraulic-01181` · labels {'cooler_condition': 20, 'valve_condition': 90, 'pump_leakage': 0, 'accumulator_pressure': 115}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 40.1 °C (29% above healthy); TS1 mean temperature 44.6 °C (24% above healthy); TS3 mean temperature 46.9 °C (21% above healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.92 s (within 1% of healthy); PS2 pressure rise time 9.46 s (within 2% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 369 W·min/l (4% below healthy); FS1 mean volume flow 6.68 l/min (within 2% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: slightly reduced. Evidence: PS2 pressure ripple 46.6 bar (within 1% of healthy). Elevated pressure ripple across working lines indicates moderate degradation of accumulator pre-charge.
```

### `hydraulic-01213` · labels {'cooler_condition': 20, 'valve_condition': 73, 'pump_leakage': 2, 'accumulator_pressure': 100}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 39.7 °C (28% above healthy); TS1 mean temperature 44.1 °C (23% above healthy); TS3 mean temperature 46.4 °C (19% above healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: close to total failure. Evidence: PS1/PS2 valve switching lag 10.0 s (2% above healthy); PS2 pressure rise time 9.69 s (4% above healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.33 l/min (4% below healthy); EPS1/FS1 power-to-flow ratio 394 W·min/l (3% above healthy); SE system efficiency factor 55.1 % (6% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 46.9 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01252` · labels {'cooler_condition': 20, 'valve_condition': 73, 'pump_leakage': 1, 'accumulator_pressure': 100}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 39.6 °C (28% above healthy); TS1 mean temperature 44.1 °C (23% above healthy); TS3 mean temperature 46.4 °C (19% above healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: close to total failure. Evidence: PS1/PS2 valve switching lag 10.0 s (2% above healthy); PS2 pressure rise time 9.69 s (4% above healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.43 l/min (2% below healthy); EPS1/FS1 power-to-flow ratio 386 W·min/l (within 1% of healthy); SE system efficiency factor 56.6 % (3% below healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.0 bar (within 1% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### `hydraulic-01285` · labels {'cooler_condition': 20, 'valve_condition': 100, 'pump_leakage': 1, 'accumulator_pressure': 100}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 39.7 °C (28% above healthy); TS1 mean temperature 44.1 °C (22% above healthy); TS3 mean temperature 46.3 °C (19% above healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.87 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.47 l/min (within 2% of healthy); EPS1/FS1 power-to-flow ratio 383 W·min/l (within 1% of healthy); SE system efficiency factor 57.6 % (within 2% of healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 46.4 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01286` · labels {'cooler_condition': 20, 'valve_condition': 100, 'pump_leakage': 1, 'accumulator_pressure': 100}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 39.8 °C (28% above healthy); TS1 mean temperature 44.1 °C (22% above healthy); TS3 mean temperature 46.3 °C (19% above healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.88 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.47 l/min (within 2% of healthy); EPS1/FS1 power-to-flow ratio 383 W·min/l (within 1% of healthy); SE system efficiency factor 57.6 % (within 2% of healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 46.4 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01381` · labels {'cooler_condition': 20, 'valve_condition': 100, 'pump_leakage': 2, 'accumulator_pressure': 90}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 39.6 °C (28% above healthy); TS1 mean temperature 44.1 °C (22% above healthy); TS3 mean temperature 46.3 °C (19% above healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.84 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.35 l/min (3% below healthy); EPS1/FS1 power-to-flow ratio 391 W·min/l (within 2% of healthy); SE system efficiency factor 56.5 % (4% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 46.3 bar (within 1% of healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### `hydraulic-01446` · labels {'cooler_condition': 20, 'valve_condition': 90, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: reduced efficiency. Evidence: TS4 mean temperature 40.0 °C (29% above healthy); TS1 mean temperature 44.6 °C (24% above healthy); TS3 mean temperature 46.8 °C (20% above healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.85 s (within 1% of healthy); PS2 pressure rise time 9.46 s (within 2% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 371 W·min/l (3% below healthy); FS1 mean volume flow 6.66 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 46.6 bar (within 1% of healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### `hydraulic-01483` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 mean temperature 36.1 °C (within 1% of healthy); TS2 mean temperature 41.8 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.68 l/min (within 2% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.0 bar (within 1% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### `hydraulic-01498` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.409 °C/min (3% above healthy); TS4 mean temperature 30.6 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: optimal. Evidence: PS2 pressure rise time 9.38 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.69 l/min (within 2% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01561` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 30.6 °C (within 1% of healthy); TS2 mean temperature 41.1 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.70 l/min (within 2% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.2 bar (within 1% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### `hydraulic-01567` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 30.6 °C (within 1% of healthy); TS2 mean temperature 41.2 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: optimal. Evidence: PS2 pressure rise time 9.38 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 381 W·min/l (within 1% of healthy); FS1 mean volume flow 6.69 l/min (within 2% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01583` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.407 °C/min (3% above healthy); TS2 mean temperature 41.2 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 381 W·min/l (within 1% of healthy); FS1 mean volume flow 6.68 l/min (within 2% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.2 bar (within 1% of healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### `hydraulic-01626` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.367 °C/min (7% below healthy); TS4 mean temperature 30.6 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: optimal. Evidence: PS2 pressure rise time 9.38 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 381 W·min/l (within 1% of healthy); FS1 mean volume flow 6.68 l/min (within 2% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### `hydraulic-01648` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.443 °C/min (12% above healthy); TS4 mean temperature 30.5 °C (within 2% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: optimal. Evidence: PS2 pressure rise time 9.38 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.70 l/min (within 2% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01703` · labels {'cooler_condition': 100, 'valve_condition': 90, 'pump_leakage': 2, 'accumulator_pressure': 130}

```
Cooler: full efficiency. Evidence: TS1 mean temperature 35.7 °C (within 1% of healthy); TS3 mean temperature 38.6 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.90 s (within 1% of healthy); PS2 pressure rise time 9.46 s (within 2% of healthy). A small switching delay appears during the main pressure transient, reflecting early valve degradation.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.43 l/min (2% below healthy); EPS1/FS1 power-to-flow ratio 401 W·min/l (5% above healthy); SE system efficiency factor 55.6 % (5% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: optimal. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Hydraulic accumulator effectively dampens load transients with normal pre-charge.
```

### `hydraulic-01711` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 2, 'accumulator_pressure': 130}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.391 °C/min (within 1% of healthy); TS1 mean temperature 35.7 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: optimal. Evidence: PS2 pressure rise time 9.38 s (within 1% of healthy); PS1/PS2 valve switching lag 9.89 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.43 l/min (2% below healthy); EPS1/FS1 power-to-flow ratio 400 W·min/l (4% above healthy); SE system efficiency factor 55.8 % (5% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: optimal. Evidence: PS2 pressure ripple 47.0 bar (within 1% of healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-01762` · labels {'cooler_condition': 100, 'valve_condition': 73, 'pump_leakage': 0, 'accumulator_pressure': 130}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 31.1 °C (within 1% of healthy); TS2 mean temperature 41.7 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: close to total failure. Evidence: PS1/PS2 valve switching lag 10.1 s (3% above healthy); PS2 pressure rise time 9.69 s (4% above healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 381 W·min/l (within 1% of healthy); FS1 mean volume flow 6.66 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: optimal. Evidence: PS2 pressure ripple 47.8 bar (2% above healthy). Pressure stability and surge dampening meet full design specifications.
```

### `hydraulic-01894` · labels {'cooler_condition': 100, 'valve_condition': 73, 'pump_leakage': 0, 'accumulator_pressure': 115}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.401 °C/min (within 1% of healthy); TS4 mean temperature 31.1 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: close to total failure. Evidence: PS1/PS2 valve switching lag 10.0 s (2% above healthy); PS2 pressure rise time 9.69 s (4% above healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 381 W·min/l (within 1% of healthy); FS1 mean volume flow 6.66 l/min (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: slightly reduced. Evidence: PS2 pressure ripple 47.8 bar (2% above healthy). Elevated pressure ripple across working lines indicates moderate degradation of accumulator pre-charge.
```

### `hydraulic-01954` · labels {'cooler_condition': 100, 'valve_condition': 80, 'pump_leakage': 2, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.409 °C/min (3% above healthy); TS2 mean temperature 41.9 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: severe lag. Evidence: PS1/PS2 valve switching lag 9.90 s (within 1% of healthy); PS2 pressure rise time 9.56 s (3% above healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.40 l/min (3% below healthy); EPS1/FS1 power-to-flow ratio 401 W·min/l (5% above healthy); SE system efficiency factor 55.5 % (5% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.3 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01963` · labels {'cooler_condition': 100, 'valve_condition': 90, 'pump_leakage': 2, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.401 °C/min (within 1% of healthy); TS2 mean temperature 41.9 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.87 s (within 1% of healthy); PS2 pressure rise time 9.46 s (within 2% of healthy). A small switching delay appears during the main pressure transient, reflecting early valve degradation.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.41 l/min (2% below healthy); EPS1/FS1 power-to-flow ratio 399 W·min/l (4% above healthy); SE system efficiency factor 55.8 % (5% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.0 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-01964` · labels {'cooler_condition': 100, 'valve_condition': 90, 'pump_leakage': 2, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.383 °C/min (3% below healthy); TS2 mean temperature 41.9 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.86 s (within 1% of healthy); PS2 pressure rise time 9.46 s (within 2% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: severe leakage. Evidence: FS1 mean volume flow 6.42 l/min (2% below healthy); EPS1/FS1 power-to-flow ratio 400 W·min/l (4% above healthy); SE system efficiency factor 55.8 % (5% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-02011` · labels {'cooler_condition': 100, 'valve_condition': 90, 'pump_leakage': 1, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 31.2 °C (within 1% of healthy); TS2 mean temperature 41.9 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: small lag. Evidence: PS1/PS2 valve switching lag 9.87 s (within 1% of healthy); PS2 pressure rise time 9.46 s (within 2% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.51 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 391 W·min/l (2% above healthy); SE system efficiency factor 57.1 % (2% below healthy). Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.2 bar (within 1% of healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### `hydraulic-02028` · labels {'cooler_condition': 100, 'valve_condition': 73, 'pump_leakage': 0, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 31.2 °C (within 1% of healthy); TS1 mean temperature 36.2 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: close to total failure. Evidence: PS1/PS2 valve switching lag 10.0 s (2% above healthy); PS2 pressure rise time 9.69 s (4% above healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 382 W·min/l (within 1% of healthy); FS1 mean volume flow 6.66 l/min (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.7 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### `hydraulic-02033` · labels {'cooler_condition': 100, 'valve_condition': 80, 'pump_leakage': 0, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.394 °C/min (within 1% of healthy); TS4 mean temperature 31.1 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: severe lag. Evidence: PS1/PS2 valve switching lag 9.91 s (within 1% of healthy); PS2 pressure rise time 9.56 s (3% above healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.69 l/min (within 2% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.5 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### `hydraulic-02038` · labels {'cooler_condition': 100, 'valve_condition': 80, 'pump_leakage': 0, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.405 °C/min (2% above healthy); TS4 mean temperature 31.2 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: severe lag. Evidence: PS1/PS2 valve switching lag 9.91 s (within 1% of healthy); PS2 pressure rise time 9.56 s (3% above healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.68 l/min (within 2% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.5 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-02040` · labels {'cooler_condition': 100, 'valve_condition': 80, 'pump_leakage': 0, 'accumulator_pressure': 100}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 31.1 °C (within 1% of healthy); TS1 temperature slope 0.41 °C/min (4% above healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: severe lag. Evidence: PS1/PS2 valve switching lag 9.92 s (within 1% of healthy); PS2 pressure rise time 9.56 s (3% above healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 381 W·min/l (within 1% of healthy); FS1 mean volume flow 6.67 l/min (within 2% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: severely reduced. Evidence: PS2 pressure ripple 47.5 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-02065` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS4 mean temperature 31.0 °C (within 1% of healthy); TS1 mean temperature 36.1 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.82 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 380 W·min/l (within 1% of healthy); FS1 mean volume flow 6.68 l/min (within 2% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-02114` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 1, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.389 °C/min (within 2% of healthy); TS3 mean temperature 38.7 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: optimal. Evidence: PS2 pressure rise time 9.38 s (within 1% of healthy); PS1/PS2 valve switching lag 9.84 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.50 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 392 W·min/l (2% above healthy); SE system efficiency factor 56.9 % (3% below healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.0 bar (within 1% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### `hydraulic-02154` · labels {'cooler_condition': 100, 'valve_condition': 100, 'pump_leakage': 1, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.389 °C/min (within 2% of healthy); TS4 mean temperature 30.6 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: optimal. Evidence: PS2 pressure rise time 9.39 s (within 1% of healthy); PS1/PS2 valve switching lag 9.84 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: weak leakage. Evidence: FS1 mean volume flow 6.51 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 392 W·min/l (2% above healthy); SE system efficiency factor 57.1 % (3% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.1 bar (within 1% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### `hydraulic-02166` · labels {'cooler_condition': 100, 'valve_condition': 80, 'pump_leakage': 0, 'accumulator_pressure': 90}

```
Cooler: full efficiency. Evidence: TS1 temperature slope 0.395 °C/min (within 1% of healthy); TS2 mean temperature 41.2 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: severe lag. Evidence: PS1/PS2 valve switching lag 9.89 s (within 1% of healthy); PS2 pressure rise time 9.56 s (3% above healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 382 W·min/l (within 1% of healthy); FS1 mean volume flow 6.67 l/min (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS2 pressure ripple 47.5 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

