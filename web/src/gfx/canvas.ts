import { useEffect, useRef } from 'react';

export const reducedMotion = () => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Canvas sized to its CSS box (DPR capped at 1.5), with a draw loop that only runs while
 * the canvas is on screen. `draw(ctx, w, h, t)` gets device pixels and ms since start.
 * If `animate` is false it draws once per resize.
 */
export function useCanvas(draw: (ctx: CanvasRenderingContext2D, w: number, h: number, t: number) => void, animate = true, deps: unknown[] = []) {
  const ref = useRef<HTMLCanvasElement>(null);
  const drawRef = useRef(draw);
  drawRef.current = draw;
  useEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    const ctx = cv.getContext('2d');
    if (!ctx) return;
    const dpr = Math.min(1.5, window.devicePixelRatio || 1);
    let raf = 0;
    let visible = false;
    const t0 = performance.now();
    const fit = () => {
      const w = Math.max(1, Math.round(cv.clientWidth * dpr));
      const h = Math.max(1, Math.round(cv.clientHeight * dpr));
      if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    };
    const frame = (now: number) => {
      fit();
      drawRef.current(ctx, cv.width, cv.height, now - t0);
      if (animate && visible && !reducedMotion()) raf = requestAnimationFrame(frame);
    };
    const io = new IntersectionObserver(([e]) => {
      const was = visible;
      visible = e.isIntersecting;
      if (visible && !was) { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }
    }, { rootMargin: '120px' });
    io.observe(cv);
    const ro = new ResizeObserver(() => { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); });
    ro.observe(cv);
    return () => { cancelAnimationFrame(raf); io.disconnect(); ro.disconnect(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [animate, ...deps]);
  return ref;
}

export const BAYER8 = [
  0, 32, 8, 40, 2, 34, 10, 42, 48, 16, 56, 24, 50, 18, 58, 26, 12, 44, 4, 36, 14, 46, 6, 38, 60, 28, 52, 20, 62, 30, 54, 22,
  3, 35, 11, 43, 1, 33, 9, 41, 51, 19, 59, 27, 49, 17, 57, 25, 15, 47, 7, 39, 13, 45, 5, 37, 63, 31, 55, 23, 61, 29, 53, 21,
].map((v) => (v + 0.5) / 64);

export type ArtKind = 'glass' | 'pump' | 'valve' | 'gauge' | 'cooler' | 'split' | 'stack' | 'wave';

/** Luminance field (0..1) for each generated artwork, in unit coordinates (x,y ∈ 0..1, aspect a = w/h). */
function field(kind: ArtKind, x: number, y: number, a: number): number {
  const cx = (x - 0.5) * a, cy = y - 0.5;
  const r = Math.hypot(cx, cy);
  const ang = Math.atan2(cy, cx);
  switch (kind) {
    case 'glass': { // round sight glass: bolted rim, fluid below a wavy meniscus, a glint
      const rim = Math.max(0, 1 - Math.abs(r - 0.34) / 0.045);
      const bolts = Math.abs(r - 0.405) < 0.022 && Math.abs(Math.sin(ang * 4)) > 0.96 ? 1 : 0;
      const level = 0.04 + Math.sin(cx * 18) * 0.012;
      const fluid = r < 0.3 && cy > level ? 0.55 + 0.35 * (cy - level) / 0.3 : 0;
      const glint = r < 0.3 && Math.abs(cx + cy * 0.6 + 0.12) < 0.025 && cy < level ? 0.8 : 0;
      return Math.min(1, rim + bolts + fluid + glint + 0.12 * (1 - y));
    }
    case 'pump': { // impeller: hub, curved vanes, volute casing
      const hub = Math.max(0, 1 - r / 0.08);
      const vane = r > 0.08 && r < 0.3 ? Math.pow(Math.abs(Math.cos(ang * 3 + r * 9)), 22) * 0.95 : 0;
      const casing = Math.max(0, 1 - Math.abs(r - (0.33 + ang * 0.012)) / 0.035);
      return Math.min(1, hub + vane + casing + 0.14 * (1 - r));
    }
    case 'valve': { // gate valve: pipe, bow-tie body, stem and handwheel
      const pipe = Math.abs(cy - 0.12) < 0.07 && Math.abs(cx) > 0.16 ? 0.7 : 0;
      const body = Math.abs(cy - 0.12) < Math.abs(cx) * 0.9 + 0.02 && Math.abs(cx) < 0.18 && Math.abs(cy - 0.12) < 0.16 ? 0.9 : 0;
      const stem = Math.abs(cx) < 0.02 && cy < 0 && cy > -0.24 ? 1 : 0;
      const wheel = Math.max(0, 1 - Math.abs(Math.hypot(cx, (cy + 0.28) * 2.6) - 0.15) / 0.03);
      return Math.min(1, pipe + body + stem + wheel + 0.1);
    }
    case 'gauge': { // pressure gauge: dial, ticks, needle
      const dial = Math.max(0, 1 - Math.abs(r - 0.33) / 0.04);
      const ticks = r > 0.24 && r < 0.3 && ang > -Math.PI * 0.95 && ang < Math.PI * 0.05 - 0.2 && Math.abs(Math.sin(ang * 9)) > 0.93 ? 1 : 0;
      const na = -0.65;
      const along = cx * Math.cos(na) + cy * Math.sin(na);
      const perp = Math.abs(-cx * Math.sin(na) + cy * Math.cos(na));
      const needle = along > -0.03 && along < 0.26 && perp < 0.018 ? 1 : 0;
      return Math.min(1, dial + ticks + needle + Math.max(0, 1 - r / 0.05) + 0.1 * (1 - y));
    }
    case 'cooler': { // finned heat exchanger with heat haze above
      const fins = Math.abs(cy - 0.1) < 0.2 && Math.abs(cx) < 0.32 && Math.abs(((cx + 0.32) * 14) % 1 - 0.5) < 0.22 ? 0.85 : 0;
      const frame = Math.abs(cy - 0.1) < 0.22 && Math.abs(cx) < 0.34 && !(Math.abs(cy - 0.1) < 0.2 && Math.abs(cx) < 0.32) ? 1 : 0;
      const haze = cy < -0.14 ? Math.max(0, 1 - Math.abs(cx - Math.sin(cy * 26) * 0.04) / 0.3) * (0.42 + cy) : 0;
      return Math.min(1, fins + frame + haze + 0.08);
    }
    case 'split': { // one signal splitting into evidence and verdict
      const stem = x < 0.42 ? Math.max(0, 1 - Math.abs(cy - Math.sin(x * 40) * 0.03) / 0.06) : 0;
      const up = x >= 0.42 ? Math.max(0, 1 - Math.abs(cy + (x - 0.42) * 0.7) / 0.05) : 0;
      const dn = x >= 0.42 ? Math.max(0, 1 - Math.abs(cy - (x - 0.42) * 0.7) / 0.05) : 0;
      return Math.min(1, stem + up + dn + 0.12 * (1 - r));
    }
    case 'stack': { // stacked load cycles
      const row = Math.floor(y * 6);
      const off = ((row * 37) % 5) / 10;
      const inBlock = Math.abs(((x + off) * 4) % 1 - 0.5) < 0.38 && Math.abs((y * 6) % 1 - 0.5) < 0.36;
      return inBlock ? 0.35 + 0.6 * ((row + 1) / 6) : 0.06;
    }
    default: { // sensor waveform band
      const w = Math.sin(x * 9 + y * 3) * 0.08 + Math.sin(x * 31) * 0.02;
      return Math.max(0, 1 - Math.abs(cy - w) / 0.18) * 0.9 + 0.1;
    }
  }
}

/** Render a two-colour ordered (Bayer 8×8) dither of an artwork into a canvas. cell = device px per dither cell. */
export function renderDither(kind: ArtKind, w: number, h: number, cell: number, colors: [string, string] = ['#7f0fd5', '#e66157']): HTMLCanvasElement {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  const ctx = cv.getContext('2d')!;
  const cols = Math.ceil(w / cell), rows = Math.ceil(h / cell);
  const a = w / h;
  ctx.fillStyle = colors[0];
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = colors[1];
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const v = field(kind, (i + 0.5) / cols, (j + 0.5) / rows, a);
      if (v > BAYER8[(j % 8) * 8 + (i % 8)]) ctx.fillRect(i * cell, j * cell, cell, cell);
    }
  }
  return cv;
}
