import { render, screen, fireEvent } from '@testing-library/react';
import { ParaText, claimsIn, paragraphsOf } from '../sections/Rationale';
import { pickDefault } from '../lib/store';
import type { Claim, IndexItem, Prediction } from '../lib/types';

const text = [
  'Cooler: reduced efficiency. Evidence: TS1 mean temperature 51.4 °C (12% above healthy). The oil runs hot.',
  'Valve: optimal. Evidence: PS1 pressure rise time 0.52 s (within 1% of healthy).',
].join('\n');

const claim = (clause: string, sensor: string, status: Claim['status']): Claim => {
  const s = text.indexOf(clause);
  return {
    span: [s, s + clause.length], component: sensor === 'TS1' ? 'cooler_condition' : 'valve_condition', sensor,
    stated: { value: 1, unit: 'x' }, true: { value: 1 }, status,
  };
};

const p: Prediction = {
  model: 'test',
  labels: {
    cooler_condition: { value: 20, name: 'reduced efficiency' }, valve_condition: { value: 100, name: 'optimal' },
    pump_leakage: { value: 0, name: 'no leakage' }, accumulator_pressure: { value: 130, name: 'optimal' },
  },
  rationale: text,
  claims: [
    claim('TS1 mean temperature 51.4 °C (12% above healthy)', 'TS1', 'verified'),
    claim('PS1 pressure rise time 0.52 s (within 1% of healthy)', 'PS1', 'wrong_value'),
  ],
};

describe('rationale rendering', () => {
  it('splits the rationale into one paragraph per component with correct offsets', () => {
    const paras = paragraphsOf(p);
    expect(paras.map((q) => q.component)).toEqual(['cooler_condition', 'valve_condition']);
    expect(text.slice(paras[1].start, paras[1].end)).toMatch(/^Valve: optimal\./);
    expect(claimsIn(p, paras[0]).map((c) => c.claim.sensor)).toEqual(['TS1']);
  });

  it('renders each claim as a chip with its verdict, and the label line in bold', () => {
    const paras = paragraphsOf(p);
    const hot: Array<number | null> = [];
    render(<>{paras.map((q) => <ParaText key={q.start} p={p} para={q} hot={null} setHot={(k) => hot.push(k)} />)}</>);
    expect(screen.getByRole('button', { name: /TS1: Verified against the signal/ })).toHaveTextContent('TS1 mean temperature 51.4 °C');
    expect(screen.getByRole('button', { name: /PS1: Number does not match the signal/ })).toHaveClass('bad');
    expect(screen.getByText('Cooler: reduced efficiency.').tagName).toBe('B');
    fireEvent.pointerEnter(screen.getByRole('button', { name: /TS1/ }));
    expect(hot).toEqual([0]);
  });
});

describe('default cycle', () => {
  const item = (id: string, correct: number, faithful: boolean, labels: [number, number, number, number]): IndexItem => ({
    id, cycle_index: Number(id.slice(-3)), stable_flag: 0, correct, total_claims: 9, verified_claims: faithful ? 9 : 8, is_faithful: faithful, healthy: false,
    true_labels: { cooler_condition: labels[0], valve_condition: labels[1], pump_leakage: labels[2], accumulator_pressure: labels[3] },
    predicted_labels: { cooler_condition: labels[0], valve_condition: labels[1], pump_leakage: labels[2], accumulator_pressure: labels[3] },
  });
  it('prefers a fully correct, fully verified cycle with the most faults', () => {
    expect(pickDefault([
      item('hydraulic-001', 3, true, [3, 73, 2, 90]),
      item('hydraulic-002', 4, true, [100, 100, 0, 130]),
      item('hydraulic-003', 4, true, [20, 100, 1, 130]),
      item('hydraulic-004', 4, false, [3, 73, 2, 90]),
    ])).toBe('hydraulic-003');
  });
});
