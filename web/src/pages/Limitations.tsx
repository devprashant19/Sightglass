import React from 'react';
import { HelpCircle, AlertTriangle } from 'lucide-react';

export const Limitations: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto py-8 space-y-12">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <HelpCircle className="w-6 h-6 text-amber-400" />
          <span>Limitations and Research Roadmap</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Honest accounting of the current system boundaries, edge cases, and future dataset expansions.
        </p>
      </div>

      {/* Limitations Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>Single Laboratory Test Rig</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            The UCI Hydraulic dataset was collected on a single physical test bench under controlled laboratory cycles. While real degradation states were induced, the cycle profile is highly repetitive (fixed 60-second cycle length with a programmed valve actuation sequence). Generalizing to variable-speed, continuous-duty hydraulic presses requires un-segmented stream inference.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>Virtual Sensor Information Leakage</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Sensors CE (cooling efficiency) and CP (cooling power) are mathematical formulas derived from TS1–TS4. While our ablation study confirms that removing them causes less than a 0.004 macro-F1 change, raw physical models should rely solely on physical transducers.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>Decimation of Fast Transients</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Decimating 100 Hz signals to 10 Hz preserves mean, plateau, and rise times, but blurs the single highest 10-millisecond pressure overshoot spike (PS1 peak) by ~1.5%, which explains our primary failure cases in the Failure Gallery.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>Test-Split Sample Size</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Our test split comprises 331 full 60-second cycles (15% of the 2,205 total). While all 4 components have non-empty support in every split, rare extreme failure combinations have wide 95% bootstrap confidence intervals.
          </p>
        </div>
      </div>

      {/* Multi-Round Roadmap */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        <h3 className="text-base font-semibold text-white tracking-wide">
          Multi-Round Roadmap
        </h3>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-4">
            <span className="w-7 h-7 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-400 flex items-center justify-center text-xs font-mono font-bold shrink-0">
              R1
            </span>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">Round 1: Hydraulic Rig</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-900/60 text-emerald-300">
                  Completed
                </span>
              </div>
              <p className="text-xs text-slate-400">
                17 sensor channels, 4 multi-class components, 100% faithful ground-truth rationale builder, LightGBM/MiniRocket/CNN baselines, pre-registered evaluation.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-4">
            <span className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center text-xs font-mono font-bold shrink-0">
              R2
            </span>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">Round 2: HUST Bearing Vibration</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                  Phased Next
                </span>
              </div>
              <p className="text-xs text-slate-400">
                High-frequency 51.2 kHz accelerometer recordings. Characteristic bearing fault orders (BPFO, BPFI, BSF, FTF) calculated via Hilbert envelope spectrum.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-4">
            <span className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center text-xs font-mono font-bold shrink-0">
              R3
            </span>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">Round 3: CARE Offshore Wind Farm</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                  Phased Next
                </span>
              </div>
              <p className="text-xs text-slate-400">
                SCADA 10-minute telemetry across multi-megawatt turbines. Early warning prediction days in advance using normal-behavior residual tracking.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
