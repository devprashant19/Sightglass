// Shapes of the static export written by scripts/export_site_data.py (schema_version 2)
// and of the live API (api/main.py). Every number the page shows comes from one of these.

export type Component = 'cooler_condition' | 'valve_condition' | 'pump_leakage' | 'accumulator_pressure';
export const COMPONENTS: Component[] = ['cooler_condition', 'valve_condition', 'pump_leakage', 'accumulator_pressure'];

export type ClaimStatus = 'verified' | 'wrong_value' | 'wrong_direction' | 'unknown_sensor' | 'unknown_quantity' | 'unit_mismatch';

export interface Source { name: string; url: string; sha256?: string; licence: string; citation?: string }

export interface Manifest {
  schema_version: number;
  mock: boolean;
  synthetic?: boolean;
  generated_at: string;
  git_sha: string;
  source?: Source;
  models?: string[];
}

export interface NotRun { status: 'pending' | 'not_run' | 'done'; reason?: string; label?: string }

export interface BaselineRow {
  id: string;
  label: string;
  explains: boolean;
  status: 'done' | 'not_run' | 'pending';
  reason?: string;
  mean_macro_f1?: number | null;
  joint_exact_match?: number | null;
  per_component?: Partial<Record<Component, number>>;
  claim_accuracy?: number | null;
}

/** The trained soft-prompt TSLM on the test split (results/tslm_test.json via evaluate.py). */
export interface TslmResult {
  model: string;
  backbone: string;
  n_test_cycles: number;
  mean_macro_f1: number;
  joint_exact_match: number;
  per_component: Partial<Record<Component, { macro_f1: number; accuracy: number }>>;
  format_ok_pct: number;
  claim_accuracy: number;
  value_accuracy: number;
  direction_accuracy: number;
  fully_faithful_pct: number;
  consistency_pct: number;
  claims_per_rationale: number;
  total_claims: number;
  verified_claims: number;
  status_counts: Partial<Record<ClaimStatus, number>>;
}

export interface Summary {
  dataset: {
    cycles: number; sensors: number; samples_per_cycle: number; components: number;
    unique_conditions?: number; train: number; val: number; test: number; healthy_all_four?: number; healthy_reference_n?: number | Record<string, number>;
  };
  engine: {
    model: string;
    mean_macro_f1: number;
    mean_macro_f1_ci95?: [number, number];
    joint_exact_match: number;
    per_component: Partial<Record<Component, { macro_f1: number; accuracy: number }>>;
    claim_accuracy: number;
    value_accuracy?: number;
    direction_accuracy?: number;
    fully_faithful_pct: number;
    consistency_pct?: number;
    claims_per_rationale?: number;
    total_claims?: number;
    verified_claims?: number;
    consistency_per_component?: Partial<Record<Component, number>>;
    note?: string;
  };
  checker: { roundtrip_pct: number; n_rationales: number; corruption_caught_pct: number; n_corrupted: number; tolerance_rel?: number };
  tslm: NotRun & Partial<TslmResult>;
  opentslm?: NotRun;
  gpt4o: NotRun;
  baselines: BaselineRow[];
}

export interface IndexItem {
  id: string;
  cycle_index: number;
  stable_flag: number;
  true_labels: Record<Component, number>;
  predicted_labels: Record<Component, number>;
  correct: number;
  total_claims: number;
  verified_claims: number;
  is_faithful: boolean;
  healthy: boolean;
  tslm_correct?: number;
  tslm_total_claims?: number;
  tslm_verified_claims?: number;
}
export interface DatasetIndex { schema_version: number; mock: boolean; cycles: IndexItem[] }

export interface Label { value: number; name: string }

export interface Claim {
  span: [number, number];
  component: Component;
  sensor: string;
  feature?: string;
  quantity?: string;
  stated: { value: number; unit: string; direction?: 'above' | 'below' | 'within' | null; pct?: number | null; sigma?: number | null };
  true: { value: number | null; pct?: number | null; z?: number | null };
  status: ClaimStatus;
  window?: [number, number] | null;
}

export interface Paragraph { component: Component; label_value: number; label_name: string; text: string; span: [number, number] }

export interface Prediction {
  model: string;
  labels: Record<Component, Label>;
  rationale: string;
  paragraphs?: Paragraph[];
  claims: Claim[];
  consistency?: Partial<Record<Component, boolean>>;
  latency_ms?: number;
}

export interface Signal { unit: string; rate_hz: number; source: string; values: number[] }

export interface Cycle {
  schema_version: number;
  mock: boolean;
  id: string;
  dataset: string;
  meta: { cycle_index: number; stable_flag: number };
  true_labels: Record<Component, Label>;
  prediction: Prediction;
  /** The language model's own rationale for this cycle, re-checked by the engine's checker. Labels may be null when a line names no level. */
  tslm_prediction?: Prediction;
  signals: Record<string, Signal>;
  features?: Record<string, { value: number; unit: string; z?: number | null; pct?: number | null }>;
  reference?: Record<string, { mean: number; std: number }>;
}

export interface Link { feature: string; sensor: string; quantity: string; unit: string; direction: 'up' | 'down'; effect: number; p_value?: number | null; kept: boolean; virtual?: boolean }
export type Links = Partial<Record<Component, Link[]>>;

export interface SensorInfo { name: string; source: string; unit: string; rate_hz: number; n_samples: number; description: string }
export interface DatasetInfo {
  sensors: SensorInfo[];
  labels: Partial<Record<Component, Record<string, string>>>;
  split: { method: string; reason?: string; train: number; val: number; test: number };
  source?: Source;
  load_snippet?: string;
}

export interface Confusion { classes: Array<number | string>; matrix: number[][] }
export interface ComponentResult { macro_f1: number; accuracy: number; confusion_matrix?: number[][]; confusion?: Confusion | number[][]; classes?: Array<number | string | Label> }
export interface Ablation { id: string; label: string; mean_macro_f1?: number; delta_mean_macro_f1?: number; note?: string }
export interface Results {
  engine?: { components?: Partial<Record<Component, ComponentResult>>; per_component?: Partial<Record<Component, ComponentResult>> };
  baselines?: BaselineRow[];
  ablations?: Ablation[];
}

export interface WhatIfPoint { type: 'flow' | 'temperature' | 'ripple' | 'baseline' | string; amount: number; label: string; prediction: Pick<Prediction, 'labels' | 'rationale' | 'claims'> }
export interface WhatIf { cycle_id: string; mock: boolean; grid: WhatIfPoint[] }

export interface Failure { cycle_id: string; tags: string[]; components?: string[]; inconsistent_components?: string[]; true_labels: Record<string, number>; pred_labels: Record<string, number>; summary: string }

export interface Health { model: string; version?: string; data_source?: string; git_sha?: string; cycles?: number }
