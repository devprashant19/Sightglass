# Sightglass Architectural Decisions

## ADR 01: Project Name & Scope
- **Decision:** The project is named **Sightglass** across all code, packages, configs, URLs, and documentation.
- **Rationale:** A sightglass is the industrial inspection window allowing operators to view fluid and mechanical condition directly. Sightglass provides verifiable visibility into TSLM diagnoses.

## ADR 02: Verification-First Physics Extractors
- **Decision:** Physics feature extraction logic in `src/sightglass/physics/` is the single source of truth for:
  1. Generating training rationales.
  2. Evaluating model faithfulness at test time.
  3. Validating live inferences in the API.
- **Rationale:** Prevents drift between synthetic rationale generation and evaluation checks. All extractors are pure, deterministic functions.

## ADR 03: Grouped Stratified Splits
- **Decision:** Data is split strictly by operational group (never by random window). In hydraulic data, split is grouped by condition combinations; in bearings, by recording / operating condition; in wind, by turbine / event.
- **Rationale:** Random window splits suffer from autocorrelation leakage between adjacent cycles, severely inflating performance metrics.
