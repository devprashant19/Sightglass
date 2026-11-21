import React, { useMemo } from 'react';
import { SignalData, ClaimData } from '../types/data';

interface SensorChartProps {
  title: string;
  signals: Record<string, SignalData>;
  activeClaim: ClaimData | null;
  cursorTime: number | null;
  onCursorMove: (time: number | null) => void;
  reference?: Record<string, { mean: number; std: number }>;
}

const COLOR_PALETTE: Record<string, string> = {
  PS1: '#38bdf8', // sky-400
  PS2: '#818cf8', // indigo-400
  PS3: '#c084fc', // purple-400
  PS4: '#f472b6', // pink-400
  PS5: '#fb7185', // rose-400
  PS6: '#fdba74', // orange-300
  FS1: '#34d399', // emerald-400
  FS2: '#a7f3d0', // emerald-200
  TS1: '#f87171', // red-400
  TS2: '#fb923c', // orange-400
  TS3: '#facc15', // yellow-400
  TS4: '#a3e635', // lime-400
  EPS1: '#e879f9', // fuchsia-400
  VS1: '#2dd4bf', // teal-400
  CE: '#60a5fa', // blue-400
  CP: '#93c5fd', // blue-300
  SE: '#4ade80', // green-400
};

export const SensorChart: React.FC<SensorChartProps> = ({
  title,
  signals,
  activeClaim,
  cursorTime,
  onCursorMove,
  reference,
}) => {
  const signalKeys = Object.keys(signals);
  if (signalKeys.length === 0) return null;

  // Compute global min/max across all signals in this group for scaling
  const { minY, maxY, durationSec } = useMemo(() => {
    let min = Infinity;
    let max = -Infinity;
    let dur = 60;

    for (const key of signalKeys) {
      const sig = signals[key];
      if (!sig || !sig.values || sig.values.length === 0) continue;
      dur = Math.max(dur, (sig.values.length - 1) / sig.rate_hz);
      for (let i = 0; i < sig.values.length; i++) {
        const v = sig.values[i];
        if (v < min) min = v;
        if (v > max) max = v;
      }
    }
    const pad = (max - min) * 0.08 || 1.0;
    return { minY: min - pad, maxY: max + pad, durationSec: dur || 60 };
  }, [signals, signalKeys]);

  const width = 640;
  const height = 140;
  const padding = { top: 10, bottom: 20, left: 45, right: 15 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const toX = (sec: number) => padding.left + (sec / durationSec) * plotWidth;
  const toY = (val: number) => padding.top + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;

  // Check if active claim matches one of the signals in this group
  const highlightedSensor = activeClaim?.sensor;
  const highlightWindow = activeClaim?.window;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 relative group">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-semibold text-slate-300 tracking-wide uppercase">{title}</h4>
        <div className="flex items-center gap-3">
          {signalKeys.map((key) => {
            const isHigh = highlightedSensor === key;
            return (
              <div
                key={key}
                className={`flex items-center gap-1.5 text-[11px] font-mono transition-opacity ${
                  isHigh ? 'opacity-100 font-bold scale-105' : 'opacity-70 group-hover:opacity-100'
                }`}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full inline-block"
                  style={{ backgroundColor: COLOR_PALETTE[key] || '#94a3b8' }}
                />
                <span className={isHigh ? 'text-emerald-300 underline' : 'text-slate-300'}>
                  {key} ({signals[key].unit})
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto overflow-visible select-none cursor-crosshair"
        onMouseMove={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          const relX = e.clientX - rect.left;
          const ratio = Math.max(0, Math.min(1, (relX - padding.left) / plotWidth));
          onCursorMove(ratio * durationSec);
        }}
        onMouseLeave={() => onCursorMove(null)}
      >
        {/* Grid lines */}
        {[0, 15, 30, 45, 60].map((sec) => (
          <line
            key={`grid-${sec}`}
            x1={toX(sec)}
            y1={padding.top}
            x2={toX(sec)}
            y2={padding.top + plotHeight}
            stroke="#1e293b"
            strokeDasharray="2,2"
          />
        ))}

        {/* Highlighted claim time-window shading */}
        {highlightWindow && signalKeys.includes(highlightedSensor || '') && (
          <rect
            x={toX(highlightWindow[0])}
            y={padding.top}
            width={Math.max(4, toX(highlightWindow[1]) - toX(highlightWindow[0]))}
            height={plotHeight}
            fill="#10b981"
            fillOpacity="0.15"
            stroke="#10b981"
            strokeWidth="1"
            strokeDasharray="3,3"
          />
        )}

        {/* Healthy Reference Bands if available */}
        {reference &&
          signalKeys.map((key) => {
            const ref = reference[`${key}.mean`];
            if (!ref) return null;
            const topY = toY(ref.mean + ref.std);
            const botY = toY(ref.mean - ref.std);
            return (
              <rect
                key={`ref-${key}`}
                x={padding.left}
                y={Math.min(topY, botY)}
                width={plotWidth}
                height={Math.abs(botY - topY) || 2}
                fill="#38bdf8"
                fillOpacity="0.05"
              />
            );
          })}

        {/* Signal Paths */}
        {signalKeys.map((key) => {
          const sig = signals[key];
          if (!sig || !sig.values || sig.values.length === 0) return null;
          const n = sig.values.length;
          const dt = 1.0 / sig.rate_hz;
          const isHighlighted = highlightedSensor === key;
          const strokeColor = COLOR_PALETTE[key] || '#94a3b8';

          let d = '';
          for (let i = 0; i < n; i++) {
            const x = toX(i * dt);
            const y = toY(sig.values[i]);
            d += `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)} `;
          }

          return (
            <path
              key={`path-${key}`}
              d={d}
              fill="none"
              stroke={strokeColor}
              strokeWidth={isHighlighted ? 2.5 : 1.2}
              strokeOpacity={highlightedSensor && !isHighlighted ? 0.35 : 0.9}
              className="transition-all duration-150"
            />
          );
        })}

        {/* Cursor line */}
        {cursorTime !== null && cursorTime >= 0 && cursorTime <= durationSec && (
          <g>
            <line
              x1={toX(cursorTime)}
              y1={padding.top}
              x2={toX(cursorTime)}
              y2={padding.top + plotHeight}
              stroke="#fbbf24"
              strokeWidth="1.5"
            />
            <text
              x={toX(cursorTime)}
              y={padding.top - 2}
              fill="#fbbf24"
              fontSize="9"
              textAnchor="middle"
              className="font-mono font-bold"
            >
              {cursorTime.toFixed(1)}s
            </text>
          </g>
        )}

        {/* X Axis labels */}
        {[0, 15, 30, 45, 60].map((sec) => (
          <text
            key={`label-${sec}`}
            x={toX(sec)}
            y={height - 5}
            fill="#64748b"
            fontSize="9"
            textAnchor="middle"
            className="font-mono"
          >
            {sec}s
          </text>
        ))}

        {/* Y Axis min/max labels */}
        <text x={padding.left - 5} y={padding.top + 8} fill="#64748b" fontSize="8" textAnchor="end" className="font-mono">
          {maxY.toFixed(1)}
        </text>
        <text x={padding.left - 5} y={padding.top + plotHeight} fill="#64748b" fontSize="8" textAnchor="end" className="font-mono">
          {minY.toFixed(1)}
        </text>
      </svg>
    </div>
  );
};
