import { useMemo, useState } from 'react';
import { Button, SightglassMark } from '../ui/Button';
import { Chars, Fade, Reveal, T } from '../motion/Reveal';
import { Grid, Rails, rng } from '../motion/Ambient';
import { REPO, cycleNo, int, isHealthy } from '../lib/data';
import { scrollToId, useStore } from '../lib/store';
import { COMPONENTS, type IndexItem } from '../lib/types';

const LINKS: Array<[string, string]> = [['Explorer', 'explore'], ['Evidence', 'evidence'], ['How it works', 'how'], ['Results', 'results']];

export function goDiagnose(run: (id?: string) => void, id?: string) {
  run(id);
  window.setTimeout(() => scrollToId('explore-run'), 80);
}

export function Nav() {
  const { run, status } = useStore();
  const [open, setOpen] = useState(false);
  const go = (id: string) => { setOpen(false); scrollToId(id); };
  return (
    <header className="nav">
      <div className="container nav-row">
        <nav className="nav-links" aria-label="Sections">
          {LINKS.map(([label, id]) => (
            <a key={id} href={`#${id}`} onClick={(e) => { e.preventDefault(); go(id); }}>{label}</a>
          ))}
          <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
        </nav>
        <a className="nav-logo" href="#top" onClick={(e) => { e.preventDefault(); go('top'); }} aria-label="Sightglass, back to top">
          <SightglassMark /> <span>Sightglass</span>
        </a>
        <div className="nav-cta">
          <Button label={status === 'running' ? 'Diagnosing…' : 'Run a diagnosis'} busy={status === 'running'} onClick={() => { setOpen(false); goDiagnose(run); }} />
          <button className="nav-burger" aria-expanded={open} aria-controls="nav-sheet" onClick={() => setOpen((o) => !o)}>
            <span className="sr">Menu</span><i /><i />
          </button>
        </div>
      </div>
      <div id="nav-sheet" className={`nav-sheet ${open ? 'open' : ''}`} hidden={!open}>
        {LINKS.map(([label, id]) => <a key={id} href={`#${id}`} onClick={(e) => { e.preventDefault(); go(id); }}>{label}</a>)}
        <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
      </div>
    </header>
  );
}

function HealthPill() {
  const { health, healthState, manifest, summary, loadError, mock } = useStore();
  const n = summary?.dataset.cycles;
  const text = loadError
    ? `Data unavailable: ${loadError}`
    : healthState === 'checking' ? 'Checking the inference service…'
    : healthState === 'live' ? `Live engine ready · ${int(health?.cycles ?? n ?? null)} test cycles`
    : mock ? 'Mock export · not real results'
    : manifest ? `Precomputed export · ${manifest.source?.name.split(' ').slice(0, 2).join(' ') ?? 'UCI'} · ${n != null ? int(n) : ''} cycles`
    : 'Loading the export…';
  const dot = loadError ? 'bad' : healthState === 'live' ? 'ok' : mock ? 'warn' : manifest ? 'ok' : '';
  return (
    <span className="pill" role="status">
      <span className={`dot ${dot}`} />
      {text}
    </span>
  );
}

export function Hero() {
  const { run } = useStore();
  return (
    <section className="hero" id="top">
      <div className="container">
        <div className="inner hero-inner">
          <Grid seed={11} dots={12} />
          <Reveal mode="load" delay={0.2} className="hero-copy">
            <h1 className="t-hero"><Chars text="Machine faults," st={0.03} /><br /><Chars text="explained with evidence." d={0.5} st={0.03} /></h1>
            <Fade as="p" className="t-p hero-p" d={T.para + 0.2}>
              Sightglass reads every sensor on a hydraulic test rig, names the part that is wearing out, and backs each claim with a number recomputed from the signal and checked.
            </Fade>
            <Fade d={T.button + 0.2} dur={0.6} className="hero-actions">
              <Button label="Run a diagnosis" onClick={() => goDiagnose(run)} />
              <Button label="Read the code" variant="ghost" href={REPO} />
            </Fade>
            <Fade d={T.button + 0.45} dur={0.6} className="hero-health"><HealthPill /></Fade>
          </Reveal>
        </div>
      </div>
      <Stream />
      <div className="container"><div className="inner"><Rails seed={3} /></div></div>
    </section>
  );
}

interface Bar { o: number; c: number; hi: number; lo: number; good: boolean; item?: IndexItem }

const faultsOf = (c: IndexItem) => COMPONENTS.filter((k) => !isHealthy(k, c.true_labels[k])).length;

/** Cycle stream: one candle per held-out test cycle. Violet: every label and claim right. Coral: something missed. */
function Stream() {
  const { index, cycleId, run, resultFor } = useStore();
  const [hover, setHover] = useState<number | null>(null);
  const bars = useMemo<Bar[]>(() => {
    const items = index ? [...index.cycles].sort((a, b) => a.cycle_index - b.cycle_index) : [];
    const N = 64;
    const pick = items.length > N ? Array.from({ length: N }, (_, k) => items[Math.round((k * (items.length - 1)) / (N - 1))]) : items;
    if (cycleId && pick.length && !pick.some((p) => p.id === cycleId)) {
      const sel = items.find((p) => p.id === cycleId);
      if (sel) pick[pick.length - 1] = sel;
    }
    const r = rng(42);
    const out: Bar[] = [];
    let p = 50;
    const src = pick.length ? pick : Array.from({ length: 58 }, () => undefined);
    for (const item of src) {
      const sev = item ? faultsOf(item) : Math.floor(r() * 4);
      const target = 26 + sev * 14 + (r() - 0.5) * 10;
      const o = p, c = Math.max(10, Math.min(90, target));
      const good = item ? item.correct === 4 && item.is_faithful : r() > 0.3;
      out.push({ o, c, hi: Math.max(o, c) + 2 + r() * 5, lo: Math.min(o, c) - 2 - r() * 5, good, item });
      p = c;
    }
    return out;
  }, [index, cycleId]);
  const W = 1000, H = 220, bw = W / Math.max(1, bars.length);
  const y = (v: number) => H - (v / 100) * H;
  const hb = hover != null ? bars[hover] : null;
  const shown = resultFor ?? cycleId;
  return (
    <div className="stream">
      <div className="container"><div className="inner stream-inner">
        <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="stream-svg" onPointerLeave={() => setHover(null)} role="img"
          aria-label="Test-cycle stream: violet bars were diagnosed correctly with every claim verified, coral bars missed a label or a claim.">
          {bars.map((b, k) => {
            const x = k * bw + bw * 0.22, w = bw * 0.56;
            const top = y(Math.max(b.o, b.c)), bot = y(Math.min(b.o, b.c));
            const col = b.good ? 'var(--violet)' : 'var(--coral)';
            const sel = b.item && b.item.id === shown;
            const dim = hover != null && hover !== k ? 0.45 : sel ? 1 : 0.82;
            return (
              <g key={k} opacity={dim} onPointerEnter={() => setHover(k)} className={`bar ${sel ? 'live' : ''} ${b.item ? 'pick' : ''}`}
                onClick={() => b.item && goDiagnose(run, b.item.id)}>
                <rect x={k * bw} y={0} width={bw} height={H} fill="transparent" />
                <line x1={x + w / 2} x2={x + w / 2} y1={y(b.hi)} y2={y(b.lo)} stroke={col} strokeWidth={1.2} vectorEffect="non-scaling-stroke" />
                <rect x={x} y={top} width={w} height={Math.max(2, bot - top)} fill={col} />
                {sel && b.item && <text x={x + w / 2} y={Math.min(H - 4, bot + 16)} textAnchor="middle" className="bar-n">{cycleNo(b.item.id)}</text>}
              </g>
            );
          })}
        </svg>
        <div className="stream-legend t-mono">
          <span><i className="sw v" /> correct · every claim verified</span>
          <span><i className="sw c" /> a label or claim missed</span>
          <span className="stream-note">{index ? 'One bar per held-out test cycle · height = faulty parts · click to diagnose' : 'Loading test cycles…'}</span>
        </div>
        {hb && (
          <div className="stream-tip" style={{ left: `${Math.min(88, Math.max(12, ((hover! + 0.5) / bars.length) * 100))}%` }}>
            <span className={`verdict ${hb.good ? 'allow' : 'deny'}`}>{hb.good ? 'VERIFIED' : 'MISSED'}</span>
            <span>{hb.item
              ? `Cycle ${cycleNo(hb.item.id)} · ${hb.item.correct}/4 parts right · ${hb.item.verified_claims}/${hb.item.total_claims} claims verified`
              : 'Loading…'}</span>
          </div>
        )}
      </div></div>
    </div>
  );
}
