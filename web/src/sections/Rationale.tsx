import { Fragment, type ReactNode } from 'react';
import { STATUS_TEXT } from '../lib/data';
import { COMPONENTS, type Claim, type Component, type Prediction } from '../lib/types';

const HEADERS: Array<[RegExp, Component]> = [
  [/^\s*cooler/i, 'cooler_condition'],
  [/^\s*valve/i, 'valve_condition'],
  [/^\s*pump/i, 'pump_leakage'],
  [/^\s*accumulator/i, 'accumulator_pressure'],
];

export interface Para { component: Component; start: number; end: number; text: string }

/** Split a rationale into one paragraph per component, keeping offsets into the full text (claim spans use them). */
export function paragraphsOf(p: Prediction): Para[] {
  if (p.paragraphs?.length) {
    return p.paragraphs.map((q) => ({ component: q.component, start: q.span[0], end: q.span[1], text: p.rationale.slice(q.span[0], q.span[1]) }));
  }
  const out: Para[] = [];
  let off = 0;
  p.rationale.split('\n').forEach((line, i) => {
    if (line.trim()) {
      const hit = HEADERS.find(([re]) => re.test(line));
      out.push({ component: hit ? hit[1] : COMPONENTS[Math.min(i, 3)], start: off, end: off + line.length, text: line });
    }
    off += line.length + 1;
  });
  return out;
}

export function claimsIn(p: Prediction, para: Para): Array<{ claim: Claim; k: number }> {
  return p.claims
    .map((claim, k) => ({ claim, k }))
    .filter(({ claim }) => claim.span[0] >= para.start && claim.span[1] <= para.end)
    .sort((a, b) => a.claim.span[0] - b.claim.span[0]);
}

function fmtN(v: number | null | undefined, unit = '') {
  if (v == null || Number.isNaN(v)) return '–';
  const a = Math.abs(v);
  const s = a >= 1000 ? v.toFixed(0) : a >= 100 ? v.toFixed(1) : a >= 1 ? v.toFixed(2) : v.toPrecision(3);
  return `${s}${unit ? ` ${unit}` : ''}`;
}

export function ClaimChip({ claim, children, hot, onHot }: { claim: Claim; children: ReactNode; hot: boolean; onHot: (on: boolean) => void }) {
  const ok = claim.status === 'verified';
  return (
    // An inline span (not <button>) so a long clause wraps with the sentence like text does.
    <span role="button" tabIndex={0} className={`claim ${ok ? 'ok' : 'bad'} ${hot ? 'hot' : ''}`}
      onPointerEnter={() => onHot(true)} onPointerLeave={() => onHot(false)} onFocus={() => onHot(true)} onBlur={() => onHot(false)}
      onClick={() => onHot(!hot)} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onHot(!hot); } }}
      aria-pressed={hot} aria-label={`${claim.sensor}: ${STATUS_TEXT[claim.status] ?? claim.status}`}>
      <span className="claim-ico" aria-hidden="true">{ok ? '✓' : '✕'}</span>
      <span className="claim-txt">{children}</span>
      <span className="claim-tip" role="tooltip">
        <span className="t-mono">{STATUS_TEXT[claim.status] ?? claim.status}</span>
        <span className="claim-cmp">
          <span><i>stated</i> {fmtN(claim.stated.value, claim.stated.unit)}</span>
          <span><i>signal</i> {fmtN(claim.true.value, claim.stated.unit)}</span>
        </span>
        {claim.true.z != null && <span className="claim-z t-code">{claim.true.z >= 0 ? '+' : ''}{claim.true.z.toFixed(1)}σ from healthy</span>}
      </span>
    </span>
  );
}

/** One component's paragraph with each evidence clause rendered as a checkable chip. */
export function ParaText({ p, para, hot, setHot }: { p: Prediction; para: Para; hot: number | null; setHot: (k: number | null) => void }) {
  // The label line ("Cooler: reduced efficiency.") is bold; it never overlaps a claim.
  const head = /^\s*[^.:]+:[^.]*\./.exec(para.text);
  const headEnd = head ? para.start + head[0].length : para.start;
  const text = (a: number, b: number, key: string): ReactNode[] => {
    if (b <= a) return [];
    if (a < headEnd) {
      const m = Math.min(b, headEnd);
      return [<b key={`${key}h`} className="para-head">{p.rationale.slice(a, m)}</b>, ...(m < b ? [<Fragment key={key}>{p.rationale.slice(m, b)}</Fragment>] : [])];
    }
    return [<Fragment key={key}>{p.rationale.slice(a, b)}</Fragment>];
  };
  const parts: ReactNode[] = [];
  let at = para.start;
  for (const { claim, k } of claimsIn(p, para)) {
    parts.push(...text(at, claim.span[0], `t${at}`));
    parts.push(
      <ClaimChip key={`c${k}`} claim={claim} hot={hot === k} onHot={(on) => setHot(on ? k : null)}>
        {p.rationale.slice(claim.span[0], claim.span[1])}
      </ClaimChip>,
    );
    at = Math.max(at, claim.span[1]);
  }
  parts.push(...text(at, para.end, `t${at}`));
  return <p className="para">{parts}</p>;
}
