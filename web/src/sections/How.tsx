import { useEffect, useState, type CSSProperties, type ReactNode } from 'react';
import { motion } from 'motion/react';
import { Head } from './Story';
import { Chars, Fade, Reveal, T, useInViewOnce } from '../motion/Reveal';
import { CountUp, Odometer } from '../motion/Odometer';
import { Button, Eyebrow } from '../ui/Button';
import { Grid } from '../motion/Ambient';
import { COMP, cycleNo, f1, int, odoPct, pct, pct100 } from '../lib/data';
import { scrollToId, useStore } from '../lib/store';
import { COMPONENTS, type BaselineRow, type Component } from '../lib/types';

const EASE = [0.25, 0.46, 0.45, 0.94] as const;

function Node({ x, y, c = 'var(--violet-2)', d, s = 9 }: { x: number; y: number; c?: string; d: number; s?: number }) {
  return <motion.rect x={x - s / 2} y={y - s / 2} width={s} height={s} fill={c} initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: d, duration: 0.35, ease: [0.34, 1.56, 0.64, 1] }} style={{ transformBox: 'fill-box', transformOrigin: 'center' }} />;
}
function Seg({ d, delay, dur = 0.3, c = 'var(--violet-2)', w = 1.6, dash }: { d: string; delay: number; dur?: number; c?: string; w?: number; dash?: string }) {
  return <motion.path d={d} fill="none" stroke={c} strokeWidth={w} strokeDasharray={dash} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay, duration: dur, ease: 'linear' }} />;
}
function Tag({ x, y, children, d, anchor = 'start' }: { x: number; y: number; children: string; d: number; anchor?: 'start' | 'middle' | 'end' }) {
  const w = children.length * 7.6 + 16;
  const x0 = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x;
  return (
    <motion.g initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: d, duration: 0.4 }}>
      <rect x={x0} y={y - 11} width={w} height={22} fill="var(--bg)" stroke="var(--line-2)" />
      <text x={x0 + 8} y={y + 4} className="diag-label">{children}</text>
    </motion.g>
  );
}

function SplitDiagram() {
  const wave = 'M20 150 ' + Array.from({ length: 12 }, (_, i) => `L${26 + i * 7} ${150 + (i % 2 ? -1 : 1) * (4 + (i % 3) * 3)}`).join(' ');
  return (
    <>
      <Seg d={wave} delay={0} dur={0.5} c="var(--text-2)" w={1.2} />
      <Tag x={20} y={118} d={0.1}>RAW SIGNAL</Tag>
      <Seg d="M110 150 H170" delay={0.4} />
      <Node x={170} y={150} d={0.6} />
      <Tag x={158} y={186} anchor="end" d={0.7}>FEATURES</Tag>
      <Seg d="M170 150 V80 H260" delay={0.7} />
      <Seg d="M170 150 V220 H260" delay={0.7} c="var(--coral)" />
      <Node x={260} y={80} d={1} />
      <Node x={260} y={220} d={1} c="var(--coral)" />
      <Seg d="M260 80 H330 V60 H380" delay={1.05} />
      <Seg d="M260 220 H330 V240 H380" delay={1.05} c="var(--coral)" />
      <Node x={380} y={60} d={1.35} />
      <Node x={380} y={240} d={1.35} c="var(--coral)" />
      <Tag x={392} y={60} d={1.45}>EVIDENCE · RATIONALE</Tag>
      <Tag x={392} y={240} d={1.45}>VERDICT · FOUR PARTS</Tag>
    </>
  );
}

function LoopDiagram() {
  const pts: Array<[number, number, string, 'middle' | 'end' | 'start', number, number]> = [
    [300, 50, 'EXPLANATION', 'middle', 300, 22], [170, 150, 'PARSE() · CLAIMS', 'end', 150, 150], [430, 150, 'RECOMPUTE() · SIGNAL', 'start', 450, 150], [300, 250, 'VERIFIED / NOT', 'middle', 300, 280],
  ];
  return (
    <>
      <circle cx="300" cy="150" r="60" className="glow" />
      <Seg d="M300 50 L170 150 L300 250 L430 150 Z" delay={0} dur={1} c="var(--line-2)" w={1.2} />
      <Seg d="M300 50 C 200 70, 190 110, 170 150" delay={0.1} dur={0.8} c="var(--line)" w={1} />
      {pts.map(([x, y, label, a, tx, ty], i) => (
        <g key={label}><Node x={x} y={y} d={0.3 + i * 0.2} c="var(--coral)" s={10} /><Tag x={tx} y={ty} anchor={a} d={0.45 + i * 0.2}>{label}</Tag></g>
      ))}
    </>
  );
}

function RadarDiagram({ vals }: { vals: number[] }) {
  const axes = ['COOLER', 'VALVE', 'PUMP', 'ACCUM.', 'CLAIMS'];
  const [phase, setPhase] = useState(0);
  useEffect(() => { const id = window.setInterval(() => setPhase((p) => p + 1), 1600); return () => window.clearInterval(id); }, []);
  const cx = 300, cy = 155, R = 105;
  const poly = (v: number[]) => v.map((x, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
    return `${cx + Math.cos(a) * R * x},${cy + Math.sin(a) * R * x}`;
  }).join(' ');
  // Real scores, breathing by at most 2% so the shape stays readable as data.
  const live = vals.map((v, i) => Math.max(0.05, Math.min(1, v * (1 - 0.02 * Math.abs(Math.sin(phase * 1.3 + i * 2.1))))));
  return (
    <>
      {[0.33, 0.66, 1].map((s) => <polygon key={s} points={poly([s, s, s, s, s])} fill="none" stroke="var(--line)" />)}
      {axes.map((ax, i) => {
        const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
        return <g key={ax}><line x1={cx} y1={cy} x2={cx + Math.cos(a) * R} y2={cy + Math.sin(a) * R} stroke="var(--line)" />
          <Tag x={cx + Math.cos(a) * (R + 26)} y={cy + Math.sin(a) * (R + 22)} anchor="middle" d={0.2 + i * 0.1}>{ax}</Tag></g>;
      })}
      <motion.polygon fill="rgba(127,15,213,.22)" stroke="var(--violet-2)" strokeWidth="1.6" initial={{ points: poly([0.1, 0.1, 0.1, 0.1, 0.1]) }} animate={{ points: poly(live) }} transition={{ duration: 1.1, ease: EASE }} />
      <motion.polygon fill="none" stroke="var(--coral)" strokeWidth="1.2" strokeDasharray="4 4" initial={{ points: poly([0.1, 0.1, 0.1, 0.1, 0.1]) }} animate={{ points: poly(live) }} transition={{ duration: 1.1, delay: 0.12, ease: EASE }} />
      {live.map((v, i) => {
        const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
        return <motion.rect key={i} width="7" height="7" fill="var(--violet-2)" initial={false} animate={{ x: cx + Math.cos(a) * R * v - 3.5, y: cy + Math.sin(a) * R * v - 3.5 }} transition={{ duration: 1.1, ease: EASE }} />;
      })}
    </>
  );
}

function StagesDiagram({ done = false }: { done?: boolean }) {
  const st = ['CONNECTOR', 'PHYSICS', 'CHECKER', 'TSLM'];
  return (
    <>
      {st.map((s, i) => {
        const h = 50 + i * 45;
        const pending = i === 3 && !done;
        return (
          <g key={s}>
            <motion.rect x={70 + i * 120} width="70" fill={pending ? 'url(#hatch)' : i === 2 ? 'var(--violet)' : 'var(--track)'} stroke={pending ? 'var(--coral)' : 'var(--line-2)'} strokeDasharray={pending ? '4 3' : undefined}
              initial={{ y: 270, height: 0 }} animate={{ y: 270 - h, height: h }} transition={{ delay: i * 0.45, duration: 0.7, ease: EASE }} />
            <Node x={105 + i * 120} y={262 - h} d={i * 0.45 + 0.5} c={pending ? 'var(--coral)' : 'var(--violet-2)'} />
            <Tag x={105 + i * 120} y={292} anchor="middle" d={i * 0.45 + 0.3}>{pending ? `${s} · NEXT` : s}</Tag>
          </g>
        );
      })}
      <defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="var(--bg)" /><rect width="2" height="6" fill="rgba(234,93,86,.45)" /></pattern></defs>
      <Seg d="M105 212 L225 167 L345 122" delay={1.6} dur={0.7} c="var(--violet-2)" w={1.2} />
      <Seg d="M345 122 L465 77" delay={2.2} dur={0.4} c="var(--coral)" w={1.2} dash="4 4" />
    </>
  );
}

function Diagram({ children }: { children: ReactNode }) {
  const [ref, seen] = useInViewOnce<HTMLDivElement>(0.35);
  return (
    <div className="diag" ref={ref} aria-hidden="true">
      <Grid seed={9} dots={3} />
      <svg viewBox="0 0 600 310">{seen ? children : null}</svg>
    </div>
  );
}

export function HowItWorks() {
  const { summary } = useStore();
  const pc = summary?.engine.per_component;
  const lmDone = summary?.tslm.status === 'done';
  const radar = [...COMPONENTS.map((c) => pc?.[c]?.macro_f1 ?? 0.5), (summary?.engine.claim_accuracy ?? 50) / 100];
  const steps = [
    { eb: 'Compute, don’t describe', t: 'One signal, two outputs', p: 'Physics features come straight from the cycle at its native rate: means, ripple, rise time, power per unit of flow. The same features feed the verdict and the evidence, so an explanation can only cite what was measured.', g: <SplitDiagram /> },
    { eb: 'Read it back', t: 'The checker trusts nothing it is told.', p: 'Every explanation is parsed back into claims (sensor, quantity, value, unit, direction). Each claim is recomputed from the raw signal with the same extractor and must land within a tolerance fixed before any test result was seen.', g: <LoopDiagram /> },
    { eb: 'Held-out cycles', t: 'Scored on cycles it never saw', p: 'The split keeps whole operating conditions apart, so a test cycle is never a near-copy of a training one. The shape shows the engine’s macro-F1 on each part and its claim accuracy on the test set.', g: <RadarDiagram vals={radar} /> },
    { eb: 'Ship it in stages', t: 'From a TimeNet build to a language model', p: lmDone ? 'Connector, physics extractors and checker came first. Then a time-series language model was trained to read the raw signals and write the diagnosis and its evidence in its own words, and the same checker grades every number it writes.' : 'The connector, physics extractors and checker are built and tested. The language model that writes the explanations in its own words is the next stage, and it will be judged by the same checker.', g: <StagesDiagram done={lmDone} /> },
  ];
  return (
    <section className="sec" id="how" aria-labelledby="how-h">
      <div className="container"><div className="inner">
        <div className="pad how-head"><Head id="how-h" eyebrow="How it works" title="Evidence first. Words second. Checked always." /></div>
        {steps.map((s) => (
          <div className="how-row" key={s.t}>
            <Reveal className="how-copy">
              <span className="rule" style={{ top: '2.2em', height: '4em' }} />
              <Fade d={0}><Eyebrow>{s.eb}</Eyebrow></Fade>
              <h3 className="t-h2"><Chars text={s.t} d={0.1} /></h3>
              <Fade as="p" className="t-small how-p" d={T.para}>{s.p}</Fade>
            </Reveal>
            <Diagram>{s.g}</Diagram>
          </div>
        ))}
      </div></div>
    </section>
  );
}

export function Proof() {
  const { summary, manifest } = useStore();
  const [ref, seen] = useInViewOnce<HTMLDivElement>(0.3);
  const [col, setCol] = useState(0);
  const [barsRef, barsSeen] = useInViewOnce<HTMLDivElement>(0.3);
  const d = summary?.dataset, ch = summary?.checker, en = summary?.engine, lm = summary?.tslm;
  const ladder = [
    { k: 'Connected', t: 'A real TimeNet build', p: d ? `${manifest?.source?.name ?? 'UCI #447'}: ${int(d.cycles)} cycles and ${d.sensors} sensors, downloaded and checked against a pinned SHA-256.` : '…' },
    { k: 'Grounded', t: 'Evidence from the signal', p: ch ? `${pct100(ch.roundtrip_pct)} of ${int(ch.n_rationales)} reference explanations survive a parse-and-recompute round trip.` : '…' },
    { k: 'Checked', t: 'Corruption is caught', p: ch ? `Change one number by 20% and the checker flags it: ${pct100(ch.corruption_caught_pct)} of ${int(ch.n_corrupted)} corrupted explanations caught.` : '…' },
    { k: 'Trained', t: lm?.status === 'done' ? 'A language model, graded' : 'Language model: next', p: !summary ? '…' : lm?.status === 'done' ? `A time-series language model reads the raw signals and writes its own evidence: ${pct100(lm.claim_accuracy)} of its ${int(lm.total_claims)} test claims verify against the signal.` : `Language model ${lm?.status ?? 'pending'}${lm?.reason ? `: ${lm.reason}` : ''}.` },
  ];
  const parts = COMPONENTS.map((c) => [COMP[c].short, en?.per_component?.[c]?.macro_f1 ?? 0] as const);
  return (
    <section className="sec" id="proof" aria-labelledby="proof-h">
      <div className="container"><div className="inner">
        <div className="proof-box">
          <div className="pad proof-top">
            <Head id="proof-h" eyebrow="Proof" title="Trust follows validation." size="t-h1" />
            <div className={`stair ${seen ? 'on' : ''}`} ref={ref} aria-hidden="true">
              {ladder.map((l, i) => (
                <div key={l.k} className={`stair-step ${i === 3 ? 'pending' : ''}`} style={{ '--k': i, transitionDelay: `${(ladder.length - 1 - i) * 0.18}s` } as CSSProperties}>
                  <i /><i /><i /><span className="t-mono">{l.k}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="ladder">
            {ladder.map((l, i) => (
              <Reveal key={l.k} className={`ladder-col ${i === col ? 'on' : ''} ${i === 3 ? 'pending' : ''}`} amount={0.3}>
                <div onPointerEnter={() => setCol(i)} onFocus={() => setCol(i)} tabIndex={0}>
                  <Fade d={0.85 + i * 0.1}><div className="ladder-ico" aria-hidden="true"><i /></div></Fade>
                  <Fade d={0.9 + i * 0.1}><h3 className="t-h4">{l.t}</h3></Fade>
                  <Fade as="p" className="t-small" d={1 + i * 0.1}>{l.p}</Fade>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        <div className="pad big">
          <Reveal className="big-copy">
            <Fade d={0}><Eyebrow>Corruption caught</Eyebrow></Fade>
            <div className="t-stat big-n"><Odometer key={ch?.corruption_caught_pct ?? 'x'} value={odoPct(ch ? ch.corruption_caught_pct / 100 : 0)} play={ch ? undefined : false} /> <span className="big-unit">%</span></div>
            <Fade as="p" className="t-small" d={0.9}>of explanations with one number changed by 20% were flagged by the checker{ch ? ` (${int(ch.n_corrupted)} tried)` : ''}. A checker that cannot catch a planted error proves nothing.</Fade>
          </Reveal>
          <div className="big-bars" ref={barsRef} aria-label="Claim accuracy and per-part macro-F1">
            <div className="size-bar">
              <div className="t-mono size-k"><span>Claims verified on the test set</span><span><CountUp to={en ? Math.round((en.claim_accuracy / 100) * (en.total_claims ?? 0)) : 0} play={barsSeen && !!en} format={(n) => n.toLocaleString('en-US')} /> / {int(en?.total_claims ?? 0)}</span></div>
              <div className="size-track plain"><motion.div className="size-fill" initial={{ width: 0 }} animate={barsSeen && en ? { width: `${en.claim_accuracy}%` } : {}} transition={{ duration: 2, ease: [0.5, 1, 0.89, 1] }} /></div>
            </div>
            <div className="tests four">
              {parts.map(([k, v], i) => (
                <div className="test-bar" key={k}>
                  <motion.div className="test-fill" initial={{ height: 0 }} animate={barsSeen && en ? { height: `${v * 100}%` } : {}} transition={{ delay: 0.4 + i * 0.1, duration: 0.9, ease: EASE }} />
                  <div className="t-code test-n">{f1(en ? v : null)}</div>
                  <div className="t-mono">{k} · macro-F1</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div></div>
    </section>
  );
}

function row(b: BaselineRow, best: number) {
  const done = b.status === 'done';
  return (
    <tr key={b.id} className={`${b.id === 'engine' ? 'me' : ''} ${done ? '' : 'pending'}`}>
      <td>{b.label}{!done && b.reason ? <div className="t-small res-reason">{b.reason}</div> : null}</td>
      <td className={`t-code ${done && b.mean_macro_f1 === best ? 'best' : ''}`}>{done ? f1(b.mean_macro_f1) : '–'}</td>
      <td className="t-code">{done ? pct(b.joint_exact_match) : '–'}</td>
      <td className="t-code">{b.explains ? (b.claim_accuracy != null ? pct100(b.claim_accuracy) : 'yes') : 'no'}</td>
      <td><span className={`verdict ${done ? 'allow' : 'deny'}`}>{done ? 'RUN' : b.status === 'pending' ? 'PENDING' : 'NOT RUN'}</span></td>
    </tr>
  );
}

/** Model vs baselines, confusion matrices and the failure gallery, all from results/. */
export function ResultsSection() {
  const { summary, results, failures, run } = useStore();
  const [comp, setComp] = useState<Component>('cooler_condition');
  const en = summary?.engine;
  const rows: BaselineRow[] = summary ? [
    { id: 'engine', label: 'Sightglass engine (physics features + rationale engine)', explains: true, status: 'done', mean_macro_f1: en!.mean_macro_f1, joint_exact_match: en!.joint_exact_match, claim_accuracy: en!.claim_accuracy },
    ...summary.baselines.filter((b) => b.id !== 'engine'),
    summary.tslm.status === 'done'
      ? { id: 'tslm', label: `Sightglass TSLM (soft-prompt ${(summary.tslm.backbone ?? '').split('/').pop()?.split('@')[0] ?? ''}, writes its own evidence)`, explains: true, status: 'done' as const, mean_macro_f1: summary.tslm.mean_macro_f1, joint_exact_match: summary.tslm.joint_exact_match, claim_accuracy: summary.tslm.claim_accuracy }
      : { id: 'tslm', label: 'Sightglass TSLM', explains: true, status: 'pending' as const, reason: summary.tslm.reason },
    ...(summary.opentslm ? [{ id: 'opentslm', label: summary.opentslm.label ?? 'OpenTSLM-Flamingo fine-tune', explains: true, status: summary.opentslm.status === 'done' ? 'done' as const : 'pending' as const, reason: summary.opentslm.reason }] : []),
    ...(summary.baselines.some((b) => /gpt/i.test(b.id)) ? [] : [{ id: 'gpt4o', label: 'GPT-4o reading plots (zero-shot)', explains: true, status: summary.gpt4o.status === 'done' ? 'done' as const : 'not_run' as const, reason: summary.gpt4o.reason }]),
  ] : [];
  const best = Math.max(...rows.filter((r) => r.status === 'done').map((r) => r.mean_macro_f1 ?? 0));
  const comps = results?.engine?.components ?? results?.engine?.per_component;
  const cm = comps?.[comp];
  const conf = cm?.confusion_matrix ?? cm?.confusion;
  const matrix: number[][] | undefined = Array.isArray(conf) ? conf : conf?.matrix;
  const rawClasses = (Array.isArray(conf) || !conf ? cm?.classes : conf.classes) ?? matrix?.map((_, i) => i) ?? [];
  const classes = rawClasses.map((c) => (typeof c === 'object' && c ? String(c.value) : String(c)));
  const classNames = rawClasses.map((c) => (typeof c === 'object' && c ? c.name : String(c)));
  const cons = en?.consistency_per_component;
  const maxCell = Math.max(1, ...(matrix ?? []).flat());
  return (
    <section className="sec" id="results" aria-labelledby="results-h">
      <div className="container"><div className="inner">
        <div className="pad res-head">
          <Head id="results-h" eyebrow="Results" title="How it compares, on the held-out test set." sub={summary ? `${int(summary.dataset.test)} test cycles from operating conditions never seen in training. Classical models are expected to score high on this rig; the point of Sightglass is the evidence, which they cannot give.` : undefined} />
        </div>
        <div className="res-table-wrap" data-lenis-prevent>
          <table className="bal res-table">
            <thead><tr><th>Model</th><th>Mean macro-F1</th><th>All four right</th><th>Explains (claim accuracy)</th><th>Status</th></tr></thead>
            <tbody>{rows.map((r) => row(r, best))}</tbody>
          </table>
          {en?.note && <p className="t-small res-note">{en.note}</p>}
        </div>
        <div className="pad res-honest">
          <div className="res-cm-copy">
            <Eyebrow>Where the evidence is weak</Eyebrow>
            <h3 className="t-h3">Does the evidence support the label?</h3>
            <p className="t-small">A claim can be numerically true and still not argue for the verdict next to it. This is the share of explanation paragraphs whose cited evidence points the way their label says{en?.consistency_pct != null ? ` (${pct100(en.consistency_pct)} overall)` : ''}. It is the weakest part of the engine today, and the bar a language model has to beat.</p>
          </div>
          <div className="cons-bars" aria-label="Evidence supports the label, per part">
            {COMPONENTS.map((c, i) => (
              <div className="cons" key={c}>
                <div className="t-mono size-k"><span>{COMP[c].title}</span><span>{pct100(cons?.[c])}</span></div>
                <div className="size-track plain"><motion.div className={`size-fill ${(cons?.[c] ?? 100) < 60 ? 'weak' : ''}`} initial={{ width: 0 }} whileInView={{ width: `${cons?.[c] ?? 0}%` }} viewport={{ once: true, amount: 0.6 }} transition={{ delay: i * 0.12, duration: 1.2, ease: EASE }} /></div>
              </div>
            ))}
            {(results?.ablations ?? []).length > 0 && (
              <div className="ablations">
                <div className="t-mono">Leak checks (LightGBM, macro-F1 change)</div>
                {results!.ablations!.map((a) => (
                  <div className="abl" key={a.id}>
                    <span>{a.label}</span>
                    <span className={`t-code ${(a.delta_mean_macro_f1 ?? 0) > 0.01 ? 'down' : ''}`}>{a.delta_mean_macro_f1 != null ? `${a.delta_mean_macro_f1 >= 0 ? '+' : '−'}${Math.abs(a.delta_mean_macro_f1).toFixed(3)}` : '–'}</span>
                    {a.note && <span className="t-small abl-note">{a.note}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="pad res-cm">
          <div className="res-cm-copy">
            <Eyebrow>Confusion</Eyebrow>
            <h3 className="t-h3">Where the engine’s labels land</h3>
            <p className="t-small">Rows are the rig’s recorded condition, columns the engine’s prediction. Off-diagonal cells are mistakes, usually between neighbouring severity levels.</p>
            <div className="presets" role="tablist" aria-label="Component">
              {COMPONENTS.map((c) => <button key={c} role="tab" aria-selected={c === comp} type="button" className={`preset ${c === comp ? 'on' : ''}`} onClick={() => setComp(c)}>{COMP[c].short}</button>)}
            </div>
          </div>
          {matrix ? (
            <div className="cm" style={{ '--n': matrix.length } as CSSProperties} role="table" aria-label={`Confusion matrix for ${COMP[comp].title}`}>
              <span className="cm-corner t-mono">true ↓ / pred →</span>
              {classes.map((c, i) => <span key={`h${c}`} className="cm-h t-mono" title={classNames[i]}>{c}</span>)}
              {matrix.map((r, i) => (
                <div className="cm-row" key={i} role="row">
                  <span className="cm-h t-mono" title={classNames[i]}>{classes[i]}</span>
                  {r.map((v, j) => (
                    <motion.span key={`${comp}-${i}-${j}`} className={`cm-cell ${i === j ? 'diag' : v ? 'off' : ''}`} role="cell"
                      initial={{ opacity: 0, scale: 0.85 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: (i + j) * 0.04, duration: 0.35 }}
                      style={{ '--a': v / maxCell } as CSSProperties}>{v}</motion.span>
                  ))}
                </div>
              ))}
            </div>
          ) : <p className="t-small chat-empty">Confusion matrices load from results.json.</p>}
        </div>
        {failures.length > 0 && (
          <div className="pad res-fail">
            <Eyebrow>Failure gallery</Eyebrow>
            <h3 className="t-h3">Where it goes wrong</h3>
            <p className="t-small">{failures.length} of {summary ? int(summary.dataset.test) : '…'} test cycles have at least one problem. Wrong labels are listed first; open any of them in the explorer to see the evidence.</p>
            <ul className="idle-list">
              {failures.slice(0, 8).map((f) => (
                <li key={f.cycle_id}>
                  <span className="t-code">{cycleNo(f.cycle_id)}</span>
                  <span>{f.summary.replace(/^hydraulic-\d+:\s*/, '')} {f.tags.map((t) => <span key={t} className="chip fail-tag">{t.replace(/_/g, ' ')}</span>)}</span>
                  <Button label="Open" variant="ghost" onClick={() => { run(f.cycle_id); window.setTimeout(() => scrollToId('explore-run'), 80); }} />
                </li>
              ))}
            </ul>
          </div>
        )}
      </div></div>
    </section>
  );
}
