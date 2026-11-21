import type { ArtKind } from '../gfx/canvas';
import type { Component } from './types';

export const REPO = 'https://github.com/devprashant19/Sightglass';
export const UCI_URL = 'https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems';

/** Healthy (full-condition) value per component, as defined in the dataset's documentation. */
export const HEALTHY: Record<Component, number> = { cooler_condition: 100, valve_condition: 100, pump_leakage: 0, accumulator_pressure: 130 };

export const COMP: Record<Component, { short: string; title: string; text: string; art: ArtKind; unit: string }> = {
  cooler_condition: {
    short: 'Cooler', title: 'Cooler efficiency', art: 'cooler', unit: '%',
    text: 'A failing cooler lets the oil run hot. Sightglass looks for higher temperatures, a steeper rise across the cycle and a smaller drop across the heat exchanger.',
  },
  valve_condition: {
    short: 'Valve', title: 'Valve switching', art: 'valve', unit: '%',
    text: 'A lagging valve switches late. The evidence is in the pressure lines: a slower rise in PS1 and a longer delay before PS2 follows.',
  },
  pump_leakage: {
    short: 'Pump', title: 'Internal pump leakage', art: 'pump', unit: '',
    text: 'A leaking pump draws the same motor power but delivers less flow. The power-to-flow ratio climbs while FS1 drops.',
  },
  accumulator_pressure: {
    short: 'Accumulator', title: 'Accumulator pressure', art: 'gauge', unit: 'bar',
    text: 'A weak accumulator buffers less. Pressure ripple grows and the peaks it should absorb get through.',
  },
};

export const SOURCE_ORDER = ['pressure', 'power', 'flow', 'temperature', 'vibration', 'virtual'];
export const SOURCE_LABEL: Record<string, string> = {
  pressure: 'Pressure', power: 'Motor power', flow: 'Volume flow', temperature: 'Temperature', vibration: 'Vibration', virtual: 'Virtual',
};

export const STATUS_TEXT: Record<string, string> = {
  verified: 'Verified against the signal',
  wrong_value: 'Number does not match the signal',
  wrong_direction: 'Direction does not match the signal',
  unknown_sensor: 'Cites a sensor that does not exist',
  unknown_quantity: 'Cites a quantity the checker cannot compute',
  unit_mismatch: 'Wrong unit for this sensor',
};

export const isHealthy = (comp: Component, v: number) => HEALTHY[comp] === v;

/** "hydraulic-01423" → "1423" */
export const cycleNo = (id: string) => String(Number(id.split('-').pop() ?? id));

export function pct(v: number | null | undefined, digits = 1) {
  if (v == null || Number.isNaN(v)) return '–';
  const x = v <= 1.0000001 && v >= 0 ? v * 100 : v;
  return `${x.toFixed(digits)}%`;
}
/** Values already in 0..100. */
export const pct100 = (v: number | null | undefined, digits = 1) => (v == null || Number.isNaN(v) ? '–' : `${v.toFixed(digits)}%`);
export const f1 = (v: number | null | undefined) => (v == null || Number.isNaN(v) ? '–' : v.toFixed(3));
export const int = (v: number | null | undefined) => (v == null ? '–' : Math.round(v).toLocaleString('en-US'));

/** Odometer text for a 0..1 fraction shown as a percentage with one decimal, e.g. 0.9734 → "97.3". */
export const odoPct = (v: number | null | undefined) => (v == null ? '0' : ((v <= 1.0000001 ? v * 100 : v)).toFixed(1));
