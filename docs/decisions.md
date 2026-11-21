# Decisions

Decisions beyond the four in the [README](../README.md#design-decisions-worth-explaining). Each gives the reason, the alternative and what it costs.

## 1. The name

The project is called **Sightglass** in all code, packages, configs, URLs and documents. A sightglass is the small window on a pump, gearbox or tank that lets an operator look at the fluid inside. The project does the same for a diagnosis: you can see the evidence and check it.

## 2. One extractor serves training, explanation and checking

`src/sightglass/physics/` is the only place a feature is computed. The features the classifier learns from, the numbers the explainer states and the values the checker recomputes all come from the same pure, deterministic functions, and the live API uses them too.

The alternative, a separate implementation in the checker, would look more independent. It would also drift, and a checker that disagrees with the explainer about how "PS2 rise time" is defined reports errors that are not errors. The cost is that a bug in a feature is invisible to the checker: both sides make it. The synthetic-signal tests in `tests/test_physics.py`, which compare features with known answers, are the guard against that.

## 3. Splits are grouped, never random

Data is split by operating group, never by random cycle or window. On the hydraulic rig the group is the four-label condition tuple. The bearing and wind code is written for the same rule (by operating condition, and by turbine), though both run only on synthetic stand-ins.

Neighbouring cycles are strongly correlated, so a random split leaks near-copies of test cycles into training. Measured on B1, it overstates mean macro-F1 by about 0.04 (`results/ablations.json`). The cost: the grouped test set has only 29 condition combinations, so a result is a statement about those conditions, and the bootstrap intervals in `results/eval_engine.json` are over cycles, not conditions.

## 4. The healthy reference is fitted per component

Each feature's healthy mean and spread come from the train cycles in which the component it is linked to is healthy, ignoring the other three. Only 21 cycles have all four parts healthy, and they form one condition that the grouped split put in test, so "fit on fully healthy train cycles" would have meant fitting on nothing.

The alternative, moving those 21 cycles to train, would break the rule that a condition belongs to one split. The cost is a reference that mixes in other parts' faults: a temperature reference for the cooler includes cycles with a lagging valve. `HealthyReference.fit_per_component` records which basis each feature used, and `results/engine_training.json` lists them with their sample sizes.

## 5. The site is static, and the API optional

Every test cycle is diagnosed ahead of time and exported, and the page calls the API only on a local host or with `?api`. The reasons and the cost are in the [README](../README.md#architecture). One more cost: the export, about 18 MB, is committed, so each re-export adds that much to the repository.

## 6. Code that cannot run raises

The GPT-4o baseline, the tokenized-LLM baseline and the full TSLM training mode raise with a reason, and that reason is written into `results/baselines.json` and the README table. The alternative, a stub that returns plausible output so the pipeline completes, is exactly how invented numbers get into a results table. The cost is a table with three empty rows, which is the honest state of the project.

## 7. 100 Hz sensors are decimated for the TSLM, never for checking

The TSLM prompt (`src/sightglass/tslm/prompt.py`) feeds the 100 Hz sensors at 10 Hz, to keep its input small. The checker always recomputes from the native-rate signal, so downsampling can change what a model sees, never what counts as correct. [downsampling.md](downsampling.md) measured the drift this causes, about 1% on means, and recommends bin-averaging over `scipy.signal.decimate` before the TSLM is trained. That change has not been made.
