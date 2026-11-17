# Rationale Spotcheck (50 Representative Cycles)

Round-trip claim verification rate: **100.0%** across all 26460 generated claims.

### Cycle `hydraulic-00000`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.99 °C/min (2316711% above healthy); CE cooling efficiency 4.15 % (96% below healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 289.9 W·min/l (within 1% of healthy); FS1 mean volume flow 8.24 l/min (within 1% of healthy); SE system efficiency factor 64.8 % (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00001`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.11 °C/min (1910637% above healthy); CE cooling efficiency 20.6 % (78% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: SE system efficiency factor 65.0 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.3 W·min/l (within 1% of healthy); FS1 mean volume flow 8.18 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00002`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 96.9 % (within 2% of healthy); TS1-TS2 cooler temperature difference 4.98 °C (within 1% of healthy); TS1 temperature slope 0.015 °C/min (6944% above healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: SE system efficiency factor 64.4 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 294.5 W·min/l (within 1% of healthy); FS1 mean volume flow 8.15 l/min (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00003`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.92 °C/min (2284034% above healthy); CE cooling efficiency 4.22 % (96% below healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.25 s (260% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: SE system efficiency factor 65.1 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.8 W·min/l (within 1% of healthy); FS1 mean volume flow 8.17 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00004`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 3.98 °C/min (1846904% above healthy); CE cooling efficiency 18.1 % (81% below healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: SE system efficiency factor 65.2 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 291.8 W·min/l (within 1% of healthy); FS1 mean volume flow 8.19 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00005`
```
Cooler: full efficiency. Evidence: TS1 mean temperature 40.0 °C (within 1% of healthy); TS1-TS2 cooler temperature difference 5.01 °C (within 1% of healthy); CE cooling efficiency 95.5 % (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: SE system efficiency factor 64.9 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.0 W·min/l (within 1% of healthy); FS1 mean volume flow 8.19 l/min (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00006`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.6 °C (67% above healthy); TS1 temperature slope 4.89 °C/min (2270386% above healthy); CE cooling efficiency 2.94 % (97% below healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). A small switching delay appears during the main pressure transient, reflecting early valve degradation.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 295.1 W·min/l (within 1% of healthy); SE system efficiency factor 64.5 % (within 1% of healthy); FS1 mean volume flow 8.19 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.6 bar (3% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00007`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.05 °C/min (1882680% above healthy); CE cooling efficiency 18.1 % (81% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 296.7 W·min/l (within 1% of healthy); FS1 mean volume flow 8.09 l/min (within 1% of healthy); SE system efficiency factor 64.3 % (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00008`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 95.7 % (within 1% of healthy); TS1-TS2 cooler temperature difference 5.00 °C (within 1% of healthy); TS1 mean temperature 40.0 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: no leakage. Evidence: SE system efficiency factor 65.2 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.1 W·min/l (within 1% of healthy); FS1 mean volume flow 8.18 l/min (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.4 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00009`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.89 °C/min (2273336% above healthy); CE cooling efficiency 3.54 % (96% below healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 295.9 W·min/l (within 1% of healthy); FS1 mean volume flow 8.11 l/min (within 1% of healthy); SE system efficiency factor 64.7 % (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00010`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.14 °C/min (1924055% above healthy); CE cooling efficiency 20.3 % (79% below healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.14 l/min (within 1% of healthy); SE system efficiency factor 65.0 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.4 W·min/l (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.6 bar (3% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00011`
```
Cooler: full efficiency. Evidence: TS1-TS2 cooler temperature difference 5.02 °C (within 1% of healthy); TS1 mean temperature 40.0 °C (within 1% of healthy); TS1 temperature slope 0.03 °C/min (13833% above healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.26 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 291.6 W·min/l (within 1% of healthy); SE system efficiency factor 65.1 % (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00012`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.93 °C/min (2291767% above healthy); CE cooling efficiency 2.95 % (97% below healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 377.1 W·min/l (29% above healthy); FS1 mean volume flow 6.35 l/min (22% below healthy); SE system efficiency factor 57.8 % (11% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00013`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.06 °C/min (1886440% above healthy); CE cooling efficiency 17.8 % (81% below healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 374.4 W·min/l (28% above healthy); FS1 mean volume flow 6.38 l/min (22% below healthy); SE system efficiency factor 56.5 % (13% below healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00014`
```
Cooler: full efficiency. Evidence: TS1 mean temperature 40.0 °C (within 1% of healthy); TS1-TS2 cooler temperature difference 5.02 °C (within 1% of healthy); TS1 temperature slope -0.029 °C/min (13618% below healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 368.3 W·min/l (26% above healthy); FS1 mean volume flow 6.46 l/min (21% below healthy); SE system efficiency factor 56.4 % (13% below healthy). Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.6 bar (3% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00015`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.91 °C/min (2279242% above healthy); CE cooling efficiency 2.20 % (98% below healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 383.9 W·min/l (31% above healthy); FS1 mean volume flow 6.28 l/min (23% below healthy); SE system efficiency factor 56.5 % (13% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.4 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00016`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.01 °C/min (1862314% above healthy); CE cooling efficiency 18.1 % (81% below healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 371.3 W·min/l (27% above healthy); FS1 mean volume flow 6.42 l/min (22% below healthy); SE system efficiency factor 56.9 % (12% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00017`
```
Cooler: full efficiency. Evidence: TS1 mean temperature 40.0 °C (within 1% of healthy); TS1 temperature slope -0.048 °C/min (22224% below healthy); TS1-TS2 cooler temperature difference 5.01 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 382.2 W·min/l (30% above healthy); FS1 mean volume flow 6.31 l/min (23% below healthy); SE system efficiency factor 57.1 % (12% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.4 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00018`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.97 °C/min (2309106% above healthy); CE cooling efficiency 1.82 % (98% below healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). A small switching delay appears during the main pressure transient, reflecting early valve degradation.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 376.4 W·min/l (29% above healthy); FS1 mean volume flow 6.42 l/min (22% below healthy); SE system efficiency factor 57.4 % (11% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00019`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.08 °C/min (1893713% above healthy); CE cooling efficiency 19.7 % (79% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 377.4 W·min/l (29% above healthy); FS1 mean volume flow 6.37 l/min (22% below healthy); SE system efficiency factor 57.5 % (11% below healthy). Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00020`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 96.2 % (within 1% of healthy); TS1-TS2 cooler temperature difference 5.01 °C (within 1% of healthy); TS1 mean temperature 40.0 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 368.8 W·min/l (26% above healthy); FS1 mean volume flow 6.48 l/min (21% below healthy); SE system efficiency factor 57.3 % (12% below healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.7 bar (3% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00021`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.91 °C/min (2281087% above healthy); CE cooling efficiency 3.62 % (96% below healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 378.2 W·min/l (29% above healthy); FS1 mean volume flow 6.35 l/min (22% below healthy); SE system efficiency factor 57.2 % (12% below healthy). Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00022`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.03 °C/min (1872665% above healthy); CE cooling efficiency 19.4 % (80% below healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 375.3 W·min/l (28% above healthy); FS1 mean volume flow 6.40 l/min (22% below healthy); SE system efficiency factor 55.6 % (14% below healthy). Minor drop in delivered flow relative to motor power indicates early internal pump leakage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00023`
```
Cooler: full efficiency. Evidence: TS1 mean temperature 40.0 °C (within 1% of healthy); CE cooling efficiency 94.5 % (within 1% of healthy); TS1 temperature slope 0.018 °C/min (8172% above healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 377.7 W·min/l (29% above healthy); FS1 mean volume flow 6.37 l/min (22% below healthy); SE system efficiency factor 57.0 % (12% below healthy). Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00024`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.94 °C/min (2293937% above healthy); CE cooling efficiency 3.19 % (97% below healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.45 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 536.1 W·min/l (83% above healthy); FS1 mean volume flow 4.49 l/min (45% below healthy); SE system efficiency factor 49.0 % (24% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00025`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.08 °C/min (1894009% above healthy); CE cooling efficiency 19.2 % (80% below healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 523.0 W·min/l (79% above healthy); FS1 mean volume flow 4.61 l/min (44% below healthy); SE system efficiency factor 48.5 % (25% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00026`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 94.5 % (within 1% of healthy); TS1 temperature slope -0.03 °C/min (13803% below healthy); TS1 mean temperature 40.0 °C (within 1% of healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.45 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 526.6 W·min/l (80% above healthy); FS1 mean volume flow 4.55 l/min (44% below healthy); SE system efficiency factor 49.0 % (24% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.2 bar (14% above healthy); PS3 pressure ripple 12.2 bar (14% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00027`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.91 °C/min (2278613% above healthy); CE cooling efficiency 3.17 % (97% below healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 534.0 W·min/l (82% above healthy); FS1 mean volume flow 4.48 l/min (45% below healthy); SE system efficiency factor 49.1 % (24% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00028`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.03 °C/min (1873113% above healthy); CE cooling efficiency 20.1 % (79% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 530.3 W·min/l (81% above healthy); FS1 mean volume flow 4.55 l/min (44% below healthy); SE system efficiency factor 48.7 % (25% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.1 bar (12% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00029`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 96.0 % (within 1% of healthy); TS1 mean temperature 40.0 °C (within 1% of healthy); TS1 temperature slope -0.002 °C/min (941% below healthy). Heat exchanger maintains expected fluid cooling delta without thermal drift.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 517.8 W·min/l (77% above healthy); FS1 mean volume flow 4.65 l/min (43% below healthy); SE system efficiency factor 48.9 % (25% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 12.1 bar (12% above healthy); PS3 pressure ripple 12.0 bar (12% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00030`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.98 °C/min (2313824% above healthy); CE cooling efficiency 2.91 % (97% below healthy). Thermal equilibrium is compromised, causing fluid temperature to rise well above nominal operating limits.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 534.2 W·min/l (82% above healthy); FS1 mean volume flow 4.51 l/min (45% below healthy); SE system efficiency factor 49.6 % (24% below healthy). Significant reduction in delivered volume flow at nominal electrical power indicates severe internal pump slippage.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00031`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.13 °C/min (1918527% above healthy); CE cooling efficiency 18.5 % (81% below healthy). Thermal dissipation is sub-optimal, allowing gradual temperature elevation during continuous load cycles.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 513.5 W·min/l (75% above healthy); FS1 mean volume flow 4.67 l/min (43% below healthy); SE system efficiency factor 50.0 % (23% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00032`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 94.0 % (within 1% of healthy); TS1 temperature slope -0.01 °C/min (4786% below healthy); TS1 mean temperature 40.0 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 506.9 W·min/l (73% above healthy); FS1 mean volume flow 4.71 l/min (42% below healthy); SE system efficiency factor 48.9 % (25% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00033`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.97 °C/min (2309987% above healthy); CE cooling efficiency 3.28 % (97% below healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 528.6 W·min/l (81% above healthy); FS1 mean volume flow 4.56 l/min (44% below healthy); SE system efficiency factor 48.3 % (25% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.6 bar (2% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00034`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.01 °C/min (1863293% above healthy); CE cooling efficiency 18.1 % (81% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 512.1 W·min/l (75% above healthy); FS1 mean volume flow 4.67 l/min (43% below healthy); SE system efficiency factor 48.8 % (25% below healthy). High power-to-flow ratio demonstrates extensive internal leakage across the pump chambers.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.5 bar (2% above healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00035`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 92.4 % (3% below healthy); TS1 temperature slope 0.04 °C/min (18542% above healthy); TS1 mean temperature 40.0 °C (within 1% of healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: optimal. Evidence: PS1 pressure rise time 5.65 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: severe leakage. Evidence: EPS1/FS1 power-to-flow ratio 523.1 W·min/l (79% above healthy); FS1 mean volume flow 4.59 l/min (44% below healthy); SE system efficiency factor 49.8 % (23% below healthy). Motor draws full electrical power while circuit flow drops substantially, confirming internal fluid bypassing.
Accumulator: close to total failure. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 196.7 bar (3% above healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00036`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.93 °C/min (2290790% above healthy); CE cooling efficiency 2.83 % (97% below healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: SE system efficiency factor 64.4 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 292.5 W·min/l (within 1% of healthy); FS1 mean volume flow 8.18 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 12.0 bar (12% above healthy); PS3 pressure ripple 12.0 bar (12% above healthy); PS1 peak pressure 195.5 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00037`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.17 °C/min (1938272% above healthy); CE cooling efficiency 17.6 % (81% below healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.24 l/min (within 1% of healthy); SE system efficiency factor 64.5 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 291.8 W·min/l (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 12.0 bar (12% above healthy); PS3 pressure ripple 12.0 bar (12% above healthy); PS1 peak pressure 195.3 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00038`
```
Cooler: full efficiency. Evidence: TS1-TS2 cooler temperature difference 4.96 °C (within 1% of healthy); TS1 mean temperature 40.0 °C (within 1% of healthy); CE cooling efficiency 96.0 % (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 294.4 W·min/l (within 1% of healthy); FS1 mean volume flow 8.15 l/min (within 1% of healthy); SE system efficiency factor 64.9 % (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 12.0 bar (12% above healthy); PS3 pressure ripple 12.0 bar (12% above healthy); PS1 peak pressure 195.4 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00039`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.95 °C/min (2299544% above healthy); CE cooling efficiency 2.77 % (97% below healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.25 s (260% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.04 l/min (within 2% of healthy); EPS1/FS1 power-to-flow ratio 296.3 W·min/l (within 1% of healthy); SE system efficiency factor 65.1 % (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 195.3 bar (within 2% of healthy). Pressure buffering is largely ineffective due to compromised pre-charge pressure in the accumulator.
```

### Cycle `hydraulic-00040`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.07 °C/min (1891569% above healthy); CE cooling efficiency 16.9 % (82% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Transient response is severely sluggish, preventing timely transition of working pressure.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 291.1 W·min/l (within 1% of healthy); FS1 mean volume flow 8.22 l/min (within 1% of healthy); SE system efficiency factor 64.7 % (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 195.3 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00041`
```
Cooler: full efficiency. Evidence: CE cooling efficiency 95.9 % (within 1% of healthy); TS1-TS2 cooler temperature difference 5.01 °C (within 1% of healthy); TS1 temperature slope -0.021 °C/min (9881% below healthy). Thermal characteristics align with nominal continuous cooling performance.
Valve: severe lag. Evidence: PS2 mean pressure 136.3 bar (within 1% of healthy); PS1 pressure rise time 6.24 s (259% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Substantial delay in circuit pressurization confirms delayed spool actuation in the main valve.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.26 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 291.7 W·min/l (within 1% of healthy); SE system efficiency factor 64.8 % (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.8 bar (10% above healthy); PS3 pressure ripple 11.8 bar (10% above healthy); PS1 peak pressure 195.5 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00042`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.88 °C/min (2266958% above healthy); CE cooling efficiency 5.31 % (94% below healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.03 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Minor delay in pressure rise and slight inter-sensor switching lag indicate beginning valve actuation lag.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 295.6 W·min/l (within 1% of healthy); SE system efficiency factor 65.1 % (within 1% of healthy); FS1 mean volume flow 8.18 l/min (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 195.3 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00043`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.19 °C/min (1945776% above healthy); CE cooling efficiency 19.5 % (80% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.02 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: no leakage. Evidence: SE system efficiency factor 65.5 % (within 1% of healthy); FS1 mean volume flow 8.21 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.5 W·min/l (within 1% of healthy). No internal bypassing detected; volumetric efficiency is optimal.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 195.3 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00044`
```
Cooler: full efficiency. Evidence: TS1-TS2 cooler temperature difference 4.98 °C (within 1% of healthy); CE cooling efficiency 94.6 % (within 1% of healthy); TS1 mean temperature 40.0 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: small lag. Evidence: PS2 mean pressure 136.5 bar (within 1% of healthy); PS1 pressure rise time 6.02 s (247% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Hydraulic valve exhibits slight transient lag while maintaining target pressure.
Pump leakage: no leakage. Evidence: SE system efficiency factor 63.9 % (within 1% of healthy); EPS1/FS1 power-to-flow ratio 293.1 W·min/l (within 1% of healthy); FS1 mean volume flow 8.19 l/min (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.5 bar (7% above healthy); PS3 pressure ripple 11.5 bar (7% above healthy); PS1 peak pressure 195.4 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00045`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.7 °C (67% above healthy); TS1 temperature slope 4.92 °C/min (2285867% above healthy); CE cooling efficiency 2.25 % (98% below healthy). Rapid temperature accumulation with minimal inlet-outlet drop indicates loss of cooling circulation.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Directional valve actuates cleanly with no discernible switching hesitation.
Pump leakage: no leakage. Evidence: SE system efficiency factor 65.9 % (within 2% of healthy); EPS1/FS1 power-to-flow ratio 292.2 W·min/l (within 1% of healthy); FS1 mean volume flow 8.20 l/min (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.2 bar (5% above healthy); PS3 pressure ripple 11.2 bar (5% above healthy); PS1 peak pressure 195.5 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00046`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.04 °C/min (1878638% above healthy); CE cooling efficiency 18.9 % (80% below healthy). Heat exchanger effectiveness has dropped below optimal threshold, producing elevated mean temperatures.
Valve: optimal. Evidence: PS1 pressure rise time 5.64 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Valve switching latency remains tightly within normal healthy tolerances.
Pump leakage: no leakage. Evidence: FS1 mean volume flow 8.13 l/min (within 1% of healthy); EPS1/FS1 power-to-flow ratio 294.5 W·min/l (within 1% of healthy); SE system efficiency factor 64.6 % (within 1% of healthy). Flow delivery and motor electrical consumption match expected volumetric efficiency without leakage.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.2 bar (5% above healthy); PS3 pressure ripple 11.2 bar (5% above healthy); PS1 peak pressure 195.3 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00047`
```
Cooler: full efficiency. Evidence: TS1 mean temperature 40.0 °C (within 1% of healthy); TS1 temperature slope 0.035 °C/min (16197% above healthy); TS1-TS2 cooler temperature difference 4.98 °C (within 1% of healthy). Operating temperatures and thermal gradient remain within optimal baseline specifications.
Valve: optimal. Evidence: PS1 pressure rise time 5.65 s (225% above healthy); PS2 mean pressure 136.7 bar (within 1% of healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Sharp pressure transient and immediate switching between sensors indicate optimal valve response.
Pump leakage: no leakage. Evidence: EPS1/FS1 power-to-flow ratio 295.3 W·min/l (within 1% of healthy); SE system efficiency factor 64.4 % (within 1% of healthy); FS1 mean volume flow 8.20 l/min (within 1% of healthy). Pump delivers nominal flow rate at baseline electrical input power.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 11.2 bar (5% above healthy); PS3 pressure ripple 11.2 bar (5% above healthy); PS1 peak pressure 195.4 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

### Cycle `hydraulic-00048`
```
Cooler: close to total failure. Evidence: TS1 mean temperature 66.6 °C (67% above healthy); TS1 temperature slope 4.95 °C/min (2299105% above healthy); CE cooling efficiency 3.04 % (97% below healthy). Elevated hydraulic oil temperature and reduced heat dissipation across the exchanger indicate severe cooler malfunction.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.45 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 375.3 W·min/l (28% above healthy); FS1 mean volume flow 6.38 l/min (22% below healthy); SE system efficiency factor 56.8 % (12% below healthy). Volumetric delivery is slightly compromised due to minor internal bypass flow.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 12.0 bar (12% above healthy); PS3 pressure ripple 12.0 bar (12% above healthy); PS1 peak pressure 195.6 bar (within 2% of healthy). Dampening capacity is substantially impaired, producing high-frequency pressure oscillations across the circuit.
```

### Cycle `hydraulic-00049`
```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 62.0 °C (55% above healthy); TS1 temperature slope 4.11 °C/min (1906983% above healthy); CE cooling efficiency 19.1 % (80% below healthy). Moderate fluid temperature rise and diminished heat exchange indicate degraded cooler efficiency.
Valve: close to total failure. Evidence: PS2 mean pressure 136.1 bar (within 1% of healthy); PS1 pressure rise time 6.44 s (271% above healthy); PS1/PS2 valve switching lag 0.0 s (within 1% of healthy). Prolonged pressure rise time and marked switching lag between pressure lines point to severe directional valve response lag.
Pump leakage: weak leakage. Evidence: EPS1/FS1 power-to-flow ratio 376.8 W·min/l (29% above healthy); FS1 mean volume flow 6.40 l/min (22% below healthy); SE system efficiency factor 57.0 % (12% below healthy). Slight elevation in power-to-flow ratio reflects incipient volumetric efficiency loss.
Accumulator: severely reduced. Evidence: PS1 pressure ripple 12.0 bar (12% above healthy); PS3 pressure ripple 12.0 bar (12% above healthy); PS1 peak pressure 195.4 bar (within 2% of healthy). Marked pressure ripple and reduced peak pressure indicate severe loss of hydraulic accumulator gas pre-charge.
```

