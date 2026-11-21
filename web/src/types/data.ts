export interface ManifestData {
  schema_version: number;
  mock: boolean;
  generated_at: string;
  git_sha: string;
  datasets: string[];
  models: string[];
}

export interface CycleIndexItem {
  id: string;
  cycle_index: number;
  stable_flag: number;
  true_labels: Record<string, number>;
  predicted_labels: Record<string, number>;
  verified_claims: number;
  total_claims: number;
  is_faithful: boolean;
}

export interface DatasetIndex {
  schema_version: number;
  mock: boolean;
  cycles: CycleIndexItem[];
}

export interface ClaimStated {
  value: number;
  unit: string;
  direction?: 'above' | 'below' | 'within';
  pct?: number;
}

export interface ClaimTrue {
  value: number;
  pct: number;
}

export interface ClaimData {
  span: [number, number];
  component: string;
  sensor: string;
  feature?: string;
  stated: ClaimStated;
  true: ClaimTrue;
  status: 'verified' | 'wrong_value' | 'wrong_direction' | 'unknown_sensor' | 'unknown_quantity' | 'unit_mismatch';
  window?: [number, number];
}

export interface SignalData {
  unit: string;
  rate_hz: number;
  source: string;
  values: number[];
}

export interface ComponentLabel {
  value: number;
  name: string;
}

export interface CycleData {
  schema_version: number;
  mock: boolean;
  id: string;
  dataset: string;
  meta: {
    cycle_index: number;
    stable_flag: number;
  };
  true_labels: Record<string, ComponentLabel>;
  signals: Record<string, SignalData>;
  reference?: Record<string, { mean: number; std: number }>;
  prediction?: {
    model: string;
    labels: Record<string, ComponentLabel>;
    rationale: string;
    claims: ClaimData[];
  };
  baseline_b4?: {
    model: string;
    labels: Record<string, ComponentLabel>;
    rationale: string;
    claims: ClaimData[];
  };
  features?: Record<string, { value: number; unit: string; z: number; pct: number }>;
}

export interface SummaryData {
  headline: {
    mean_macro_f1: number;
    claim_accuracy: number;
    gpt4o_claim_accuracy: number;
    datasets_onboarded: number;
  };
  evaluations: Record<string, any>;
}

export interface WhatIfStep {
  delta_pct: number;
  features: Record<string, number>;
  labels: Record<string, number>;
  rationale: string;
}

export interface WhatIfData {
  schema_version: number;
  mock: boolean;
  cycle_id: string;
  perturbations: Record<string, WhatIfStep[]>;
}
