import React, { useState } from 'react';
import { Database, Copy, Check, ExternalLink } from 'lucide-react';

export const Dataset: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const snippet = `from sightglass.data.loader import load_cycles

# Load grouped test cycles with native 100 Hz waveforms
cycles = load_cycles("hydraulic", split="test")
print(f"Loaded {len(cycles)} cycles. Sample sensors: {list(cycles[0].signals.keys())}")
`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-5xl mx-auto py-8 space-y-10">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Database className="w-6 h-6 text-emerald-400" />
          <span>UCI Hydraulic Condition Monitoring Dataset (#447)</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          A physical industrial test rig measuring 17 sensors at 100 Hz, 10 Hz, and 1 Hz across 2,205 repetitive 60-second machine cycles.
        </p>
      </div>

      {/* Dataset Specification Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <div className="text-xs text-slate-400 font-mono">Dataset Size</div>
          <div className="text-2xl font-bold text-white font-mono">2,205 Cycles</div>
          <p className="text-xs text-slate-400">60 seconds per cycle (36.75 hours)</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <div className="text-xs text-slate-400 font-mono">Total Sensor Channels</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">17 Signals</div>
          <p className="text-xs text-slate-400">6 pressure, 2 flow, 4 temp, power, vib, 3 virtual</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <div className="text-xs text-slate-400 font-mono">Licence</div>
          <div className="text-2xl font-bold text-indigo-400 font-mono">CC BY 4.0</div>
          <p className="text-xs text-slate-400">Open access industrial benchmark</p>
        </div>
      </div>

      {/* Sensor Rates & Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
          Physical Channels & Sampling Frequencies
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Subsystem</th>
                <th className="py-2.5 px-3">Channels</th>
                <th className="py-2.5 px-3">Sampling Rate</th>
                <th className="py-2.5 px-3">Points / Cycle</th>
                <th className="py-2.5 px-3">Physical Unit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              <tr>
                <td className="py-2.5 px-3 font-semibold text-white">Pressure</td>
                <td className="py-2.5 px-3">PS1, PS2, PS3, PS4, PS5, PS6</td>
                <td className="py-2.5 px-3 text-cyan-400">100 Hz</td>
                <td className="py-2.5 px-3">6,000</td>
                <td className="py-2.5 px-3">bar</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-white">Motor Power</td>
                <td className="py-2.5 px-3">EPS1</td>
                <td className="py-2.5 px-3 text-cyan-400">100 Hz</td>
                <td className="py-2.5 px-3">6,000</td>
                <td className="py-2.5 px-3">W</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-white">Volume Flow</td>
                <td className="py-2.5 px-3">FS1, FS2</td>
                <td className="py-2.5 px-3 text-emerald-400">10 Hz</td>
                <td className="py-2.5 px-3">600</td>
                <td className="py-2.5 px-3">l/min</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-white">Temperature</td>
                <td className="py-2.5 px-3">TS1, TS2, TS3, TS4</td>
                <td className="py-2.5 px-3 text-amber-400">1 Hz</td>
                <td className="py-2.5 px-3">60</td>
                <td className="py-2.5 px-3">°C</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-white">Vibration</td>
                <td className="py-2.5 px-3">VS1</td>
                <td className="py-2.5 px-3 text-amber-400">1 Hz</td>
                <td className="py-2.5 px-3">60</td>
                <td className="py-2.5 px-3">mm/s</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-white">Virtual / Efficiency</td>
                <td className="py-2.5 px-3">CE, CP, SE</td>
                <td className="py-2.5 px-3 text-purple-400">1 Hz</td>
                <td className="py-2.5 px-3">60</td>
                <td className="py-2.5 px-3">%, kW, %</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Python Quickstart Snippet */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            TimeNet Loading Snippet
          </h3>
          <button
            onClick={copyToClipboard}
            className="flex items-center gap-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy Code'}</span>
          </button>
        </div>

        <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 overflow-x-auto">
          {snippet}
        </pre>
      </div>

      {/* Upstream PR Banner */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
        <div>
          <h4 className="text-sm font-semibold text-white">TimeNet Connector Contribution</h4>
          <p className="text-xs text-slate-400">
            Our dataset connector is packaged for upstream submission into OpenTSLM/TimeNet.
          </p>
        </div>
        <a
          href="https://github.com/OpenTSLM/TimeNet/pull/123"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono transition-colors shrink-0"
        >
          <span>View PR Draft</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
};
