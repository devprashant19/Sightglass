import { Button, Eyebrow } from '../ui/Button';
import { Chars, Fade, Reveal, T } from '../motion/Reveal';
import { Odometer } from '../motion/Odometer';
import { ScrubChars } from '../motion/Scrub';
import { Grid, Rails } from '../motion/Ambient';
import { DitherArt } from '../gfx/Art';
import { REPO, int } from '../lib/data';
import { useStore } from '../lib/store';
import { goDiagnose } from './Top';

/** Section heading block: eyebrow, accent rule, split heading. */
export function Head({ eyebrow, title, center = false, sub, size = 't-h2', id }: { eyebrow: string; title: string; center?: boolean; sub?: string; size?: string; id?: string }) {
  return (
    <Reveal className={`head ${center ? 'center' : ''}`} id={id}>
      {!center && <span className="rule" style={{ top: 0, bottom: 0 }} />}
      <Fade d={0} dur={0.5}><Eyebrow>{eyebrow}</Eyebrow></Fade>
      <h2 className={size}><Chars text={title} d={0.1} /></h2>
      {sub && <Fade as="p" className="t-p head-sub" d={T.para}>{sub}</Fade>}
    </Reveal>
  );
}

const RINGS = [
  { r: 95, dir: 1, items: [{ a: 20, label: 'COOLER', c: 'var(--coral)' }, { a: 110, label: 'VALVE', c: 'var(--coral)' }, { a: 200, label: 'PUMP', c: 'var(--coral)' }, { a: 290, label: 'ACCUMULATOR', c: 'var(--coral)' }] },
  { r: 175, dir: -1, items: [{ a: 120, label: 'PRESSURE', c: 'var(--violet-2)' }, { a: 240, label: 'FLOW', c: 'var(--violet-2)' }, { a: 0, label: 'MOTOR POWER', c: 'var(--violet-2)' }, { a: 60, c: 'var(--violet-2)' }] },
  { r: 255, dir: 1, items: [{ a: 75, label: 'TEMPERATURE', c: '#efedf0' }, { a: 200, label: 'VIBRATION', c: '#efedf0' }, { a: 300, label: 'VIRTUAL', c: '#efedf0' }, { a: 140, c: '#efedf0' }, { a: 340, c: '#efedf0' }] },
];

/** Orbit: the four machine parts and the sensor groups circling the diagnose() core. Rings turn at 12°/s, alternating. */
export function Checks() {
  return (
    <section className="sec" aria-labelledby="checks-h">
      <div className="container"><div className="inner pad checks">
        <Head id="checks-h" eyebrow="One cycle, every sensor" title="What Sightglass watches" center />
        <div className="orbit" aria-hidden="true">
          <svg viewBox="0 0 600 600">
            <defs>
              <radialGradient id="core-glow"><stop offset="0" stopColor="#ea5d56" stopOpacity=".35" /><stop offset="1" stopColor="#ea5d56" stopOpacity="0" /></radialGradient>
            </defs>
            {RINGS.map((ring, k) => (
              <g key={k} className={`ring ${ring.dir < 0 ? 'ccw' : ''}`} style={{ animationDuration: '30s' }}>
                <circle cx="300" cy="300" r={ring.r} fill="none" stroke="var(--line)" />
                {ring.items.map((it, j) => {
                  const x = 300 + ring.r * Math.cos((it.a * Math.PI) / 180);
                  const y = 300 + ring.r * Math.sin((it.a * Math.PI) / 180);
                  return (
                    <g key={j}>
                      <rect x={x - 4} y={y - 4} width="8" height="8" fill={it.c} />
                      {it.label && (
                        <g className={`upright ${ring.dir < 0 ? 'ccw' : ''}`}>
                          <rect x={x + 12} y={y - 11} width={it.label.length * 8.4 + 16} height="22" fill="var(--bg)" stroke="var(--line-2)" />
                          <text x={x + 20} y={y + 4} className="orbit-label">{it.label}</text>
                        </g>
                      )}
                    </g>
                  );
                })}
              </g>
            ))}
            <circle cx="300" cy="300" r="70" fill="url(#core-glow)" className="core-glow" />
            <circle cx="300" cy="300" r="13" fill="none" stroke="var(--coral)" strokeWidth="2" />
            <text x="300" y="336" textAnchor="middle" className="orbit-label core">DIAGNOSE()</text>
          </svg>
        </div>
        <Reveal className="center-row"><Fade d={0.1}><Button label="Read the extractor (hydraulic.py)" variant="ghost" href={`${REPO}/blob/main/src/sightglass/physics/hydraulic.py`} /></Fade></Reveal>
      </div></div>
    </section>
  );
}

export function Stats() {
  const { summary } = useStore();
  const d = summary?.dataset;
  const stats = [
    { v: d ? int(d.cycles) : '0', k: 'Load cycles', p: 'Sixty-second cycles from the UCI test rig, each labelled with the true state of four parts.' },
    { v: d ? int(d.sensors) : '0', k: 'Sensors', p: 'Pressure and motor power at the fastest rate, flow in between, temperature and vibration once a second.' },
    { v: d ? int(d.samples_per_cycle) : '0', k: 'Samples per cycle', p: 'Every signal kept at its native rate. Nothing is resampled before the evidence is computed.' },
    { v: summary ? int(summary.engine.total_claims ?? 0) : '0', k: 'Claims checked', p: 'Numeric claims in the held-out test explanations, each recomputed from its own cycle.' },
  ];
  return (
    <section className="sec" aria-labelledby="impact-h">
      <div className="container"><div className="inner">
        <div className="pad impact">
          <Head id="impact-h" eyebrow="Impact" title="When a diagnosis shows its working." sub="An alarm says something is wrong. Sightglass says which sensor showed it, by how much, compared with a healthy cycle, and lets you check." />
          <div className="impact-art"><Grid seed={5} dots={4} /><DitherArt kind="glass" className="impact-dither" /></div>
        </div>
        <div className="stats">
          {stats.map((s, i) => (
            <Reveal className="stat" key={s.k} amount={0.2}>
              <div className="t-stat"><Odometer key={s.v} value={s.v} delay={i * 0.12} play={summary ? undefined : false} /></div>
              <div>
                <Fade d={0.9 + i * 0.08}><h3 className="stat-k">{s.k}</h3></Fade>
                <Fade as="p" className="t-small" d={1 + i * 0.08}>{s.p}</Fade>
              </div>
            </Reveal>
          ))}
        </div>
      </div></div>
    </section>
  );
}

export function Intro() {
  const { run } = useStore();
  return (
    <section className="sec" aria-label="Why Sightglass">
      <div className="container"><div className="inner">
        <Rails seed={8} rails={3} />
        <div className="midcta">
          <Grid seed={21} dots={6} />
          <Reveal className="midcta-row"><Fade d={0}>
            <Button label="Run a diagnosis" onClick={() => goDiagnose(run)} />
          </Fade></Reveal>
        </div>
        <div className="pad intro">
          <Reveal><Fade d={0}><Eyebrow>No analyst on site</Eyebrow></Fade></Reveal>
          <ScrubChars className="intro-p" as="p"
            text="Most plants get an alarm that says fault and nothing else. Sightglass reads the same sensors, names the worn part, and writes down its evidence: which sensor, what value, how far from a healthy cycle. Then it recomputes every one of those numbers from the signal before you see them." />
        </div>
      </div></div>
    </section>
  );
}
