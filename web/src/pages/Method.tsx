import React from 'react';
import { Cpu, Shield, FileCode } from 'lucide-react';

export const Method: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto py-8 space-y-12">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-6 h-6 text-emerald-400" />
          <span>Sightglass Methodology & Architecture</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Detailed technical breakdown of the OpenTSLM Flamingo architecture, feature extraction, and pre-registered evaluation protocol.
        </p>
      </div>

      {/* System Flow Diagram */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
          End-to-End System Pipeline
        </h3>
        <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto leading-relaxed">
          <pre>{`[Raw Multi-Rate Sensor Streams] (PS1-PS6 100Hz, FS1 10Hz, TS1 1Hz)
               │
               ▼
[Scipy Anti-Aliasing Decimation] (Downsample to unified 10Hz without phase lag)
               │
               ▼
[OpenTSLM 1D Temporal Patch CNN] (Multi-scale 1D convolutions -> temporal embeddings)
               │
               ▼
[Gated Cross-Attention Adapter] (Perceiver resampler conditioning Llama-1B/Gemma-3)
               │
               ▼
[Autoregressive Rationale Generation] ("Cooler condition: reduced efficiency (20).
               │                        TS1 temperature rose to 62.0 °C (55% above healthy)...")
               │
               ▼
[Deterministic Faithfulness Checker] (Regex claim extraction -> Recompute signal ground truth)
               │
               ├──> 100% Verified Claim Verdicts
               └──> Rejection / Flagging of Unsubstantiated Assertions`}</pre>
        </div>
      </div>

      {/* Canonical Grammar Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white tracking-wide uppercase flex items-center gap-2">
          <FileCode className="w-4 h-4 text-emerald-400" />
          <span>Canonical Evidence Clause Grammar</span>
        </h3>
        <p className="text-xs text-slate-400">
          Every statement in Sightglass's rationales adheres to an unambiguous, machine-verifiable clause grammar:
        </p>
        <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-300">
          <code>
            {`<sensor> <quantity> <relation> <value> <unit> (<pct>% <direction> healthy)`}
          </code>
        </div>
        <p className="text-xs text-slate-400">
          For example: <code className="text-slate-200 bg-slate-800 px-1 py-0.5 rounded">FS1 mean flow dropped to 8.2 l/min (15% below healthy)</code>.
          This strict structure allows our deterministic checker to isolate the sensor (<code className="text-slate-300">FS1</code>), quantity (<code className="text-slate-300">mean flow</code>), stated value (<code className="text-slate-300">8.2</code>), and deviation (<code className="text-slate-300">15% below</code>), and re-verify them directly on the waveform.
        </p>
      </div>

      {/* Pre-Registered Evaluation Rules */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white tracking-wide uppercase flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span>Pre-Registered Tolerances (configs/faithfulness.yaml)</span>
        </h3>
        <p className="text-xs text-slate-400">
          To satisfy Non-Negotiable Rule 5, error thresholds were committed to git (<code className="text-slate-300">2308207</code>) before any test metrics were computed:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
          <div className="p-3 rounded bg-slate-950 border border-slate-800">
            <div className="text-slate-400 text-[10px]">Value Tolerance Floor</div>
            <div className="text-emerald-400 font-bold mt-1">± 5.0%</div>
            <div className="text-slate-500 text-[10px]">or min absolute delta</div>
          </div>
          <div className="p-3 rounded bg-slate-950 border border-slate-800">
            <div className="text-slate-400 text-[10px]">Time Shift Tolerance</div>
            <div className="text-cyan-400 font-bold mt-1">± 0.05 s</div>
            <div className="text-slate-500 text-[10px]">for rise-time / lag</div>
          </div>
          <div className="p-3 rounded bg-slate-950 border border-slate-800">
            <div className="text-slate-400 text-[10px]">Temperature Delta</div>
            <div className="text-amber-400 font-bold mt-1">± 0.2 °C</div>
            <div className="text-slate-500 text-[10px]">absolute tolerance</div>
          </div>
          <div className="p-3 rounded bg-slate-950 border border-slate-800">
            <div className="text-slate-400 text-[10px]">Confidence Intervals</div>
            <div className="text-indigo-400 font-bold mt-1">95% Bootstrap</div>
            <div className="text-slate-500 text-[10px]">B = 1,000 resamples</div>
          </div>
        </div>
      </div>
    </div>
  );
};
