import React, { useState } from 'react';
import { Wind, AlertTriangle, CheckCircle, Clock, ShieldCheck } from 'lucide-react';

interface TurbineStatus {
  id: string;
  name: string;
  status: 'normal' | 'warning' | 'fault';
  measured_temp_c: number;
  expected_temp_c: number;
  residual_c: number;
  trend_c_day: number;
  lead_time_days?: number;
  fault_component?: string;
  rationale: string;
}

export const WindFarm: React.FC = () => {
  const [selectedTurbine, setSelectedTurbine] = useState<string>('WTG05');

  const turbines: TurbineStatus[] = [
    {
      id: 'WTG01',
      name: 'Turbine 01',
      status: 'normal',
      measured_temp_c: 62.4,
      expected_temp_c: 62.1,
      residual_c: 0.3,
      trend_c_day: 0.02,
      rationale:
        'Normal operation. Gearbox bearing temperature matches empirical power-temperature model (+0.3 °C residual). No drift detected.',
    },
    {
      id: 'WTG02',
      name: 'Turbine 02',
      status: 'normal',
      measured_temp_c: 64.1,
      expected_temp_c: 63.8,
      residual_c: 0.3,
      trend_c_day: -0.01,
      rationale:
        'Normal operation. Generator winding temperature within nominal thermal envelope (+0.3 °C residual). Thermal dissipation nominal.',
    },
    {
      id: 'WTG03',
      name: 'Turbine 03',
      status: 'normal',
      measured_temp_c: 58.9,
      expected_temp_c: 58.7,
      residual_c: 0.2,
      trend_c_day: 0.01,
      rationale:
        'Normal operation. Main bearing temperature tracking ambient wind and power expectations (+0.2 °C residual).',
    },
    {
      id: 'WTG04',
      name: 'Turbine 04',
      status: 'normal',
      measured_temp_c: 65.0,
      expected_temp_c: 64.6,
      residual_c: 0.4,
      trend_c_day: 0.03,
      rationale:
        'Normal operation. Validation turbine operating with nominal temperature residuals.',
    },
    {
      id: 'WTG05',
      name: 'Turbine 05',
      status: 'warning',
      measured_temp_c: 72.8,
      expected_temp_c: 66.2,
      residual_c: 6.6,
      trend_c_day: 0.54,
      lead_time_days: 7.2,
      fault_component: 'gearbox',
      rationale:
        'Early warning: gearbox bearing overheating. Evidence: gearbox temperature residual 6.6 °C (above healthy) averaged over 3 days; residual trend 0.54 °C/day. Warning triggered 7.2 days prior to catastrophic failure threshold.',
    },
    {
      id: 'WTG06',
      name: 'Turbine 06',
      status: 'warning',
      measured_temp_c: 70.5,
      expected_temp_c: 65.1,
      residual_c: 5.4,
      trend_c_day: 0.42,
      lead_time_days: 6.8,
      fault_component: 'gearbox',
      rationale:
        'Early warning: gearbox bearing overheating. Evidence: gearbox temperature residual 5.4 °C (above healthy); residual trend 0.42 °C/day. First alarm raised 6.8 days ahead of trip event.',
    },
  ];

  const current = turbines.find((t) => t.id === selectedTurbine) || turbines[4];

  return (
    <div className="max-w-6xl mx-auto py-8 space-y-10">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
              Round 3 Expansion
            </span>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Wind className="w-6 h-6 text-cyan-400" />
              <span>CARE Offshore Wind Farm Fleet Overview</span>
            </h2>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Normal-behavior residual modeling on 10-minute SCADA telemetry for multi-day early fault warning.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">Select Turbine:</span>
          {turbines.map((t) => (
            <button
              key={t.id}
              onClick={() => setSelectedTurbine(t.id)}
              className={`px-2.5 py-1 rounded text-xs font-mono border transition-colors ${
                selectedTurbine === t.id
                  ? 'bg-cyan-950 text-cyan-300 border-cyan-600 font-semibold'
                  : 'bg-slate-900 text-slate-300 border-slate-800 hover:text-white'
              }`}
            >
              {t.id}
            </button>
          ))}
        </div>
      </div>

      {/* Fleet Status Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {turbines.map((t) => {
          const isWarn = t.status === 'warning';
          const isSelected = selectedTurbine === t.id;

          return (
            <button
              key={t.id}
              onClick={() => setSelectedTurbine(t.id)}
              className={`p-4 rounded-xl text-left border transition-all ${
                isSelected
                  ? 'ring-2 ring-cyan-500 bg-slate-900 shadow-md'
                  : 'bg-slate-950 hover:bg-slate-900'
              } ${isWarn ? 'border-amber-500/50' : 'border-slate-800'}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs font-bold text-white">{t.id}</span>
                {isWarn ? (
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                ) : (
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                )}
              </div>
              <div className="text-[11px] font-mono">
                <div className="text-slate-400">Residual</div>
                <div className={`font-bold ${isWarn ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {t.residual_c > 0 ? `+${t.residual_c}°C` : `${t.residual_c}°C`}
                </div>
              </div>
              <div className="mt-2 text-[10px] uppercase font-mono px-1 py-0.5 rounded text-center bg-slate-900 border border-slate-800 text-slate-400">
                {t.status}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Turbine Timeline & Residuals */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-semibold text-white font-mono uppercase">
              {current.name} Health Metrics
            </h3>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                current.status === 'warning'
                  ? 'bg-amber-950 text-amber-400 border border-amber-800'
                  : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
              }`}
            >
              {current.status}
            </span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Measured Temperature:</span>
              <span className="text-white font-bold">{current.measured_temp_c} °C</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Expected Normal Temp:</span>
              <span className="text-slate-300">{current.expected_temp_c} °C</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Temperature Residual:</span>
              <span className={current.status === 'warning' ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold'}>
                +{current.residual_c} °C
              </span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Residual Trend (Slope):</span>
              <span className="text-slate-200">+{current.trend_c_day} °C/day</span>
            </div>
            {current.lead_time_days && (
              <div className="flex justify-between p-2.5 rounded bg-cyan-950/60 border border-cyan-800 text-cyan-300 font-bold">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" /> Early Warning Lead Time:
                </span>
                <span>{current.lead_time_days} Days Ahead</span>
              </div>
            )}
          </div>

          {/* Rationale */}
          <div className="space-y-1.5">
            <div className="text-xs font-semibold text-slate-400 uppercase font-mono">
              Diagnostic Rationale
            </div>
            <div className="p-3.5 rounded bg-slate-950 border border-slate-800 text-slate-200 text-xs font-sans leading-relaxed">
              {current.rationale}
            </div>
          </div>
        </div>

        {/* Timeline Visualization */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                <span>30-Day Temperature Residual History (10-Min SCADA)</span>
              </h3>
              <span className="text-[11px] font-mono text-slate-400">Threshold: +2.5 °C</span>
            </div>

            {/* Residual Simulation Canvas */}
            <div className="relative bg-slate-950 border border-slate-800 rounded-lg p-4 h-64 flex items-end justify-between overflow-hidden">
              {/* Healthy 95th Percentile Threshold Line */}
              <div
                style={{ bottom: '40%' }}
                className="absolute left-0 right-0 border-b border-dashed border-amber-500/60 pointer-events-none flex justify-end pr-2"
              >
                <span className="text-[10px] font-mono text-amber-400 bg-slate-950/80 px-1 -translate-y-2">
                  Alarm Threshold (+2.5 °C)
                </span>
              </div>

              {/* Shaded Fault Region */}
              {current.status === 'warning' && (
                <div
                  style={{ left: '75%', right: 0 }}
                  className="absolute top-0 bottom-0 bg-red-950/20 border-l border-red-500/40 pointer-events-none flex items-start p-2"
                >
                  <span className="text-[10px] font-mono text-red-400 bg-slate-950/80 px-1 rounded">
                    Catastrophic Trip Window (Day 25)
                  </span>
                </div>
              )}

              {/* Bars representing daily mean residual */}
              {Array.from({ length: 30 }).map((_, day) => {
                let resVal = 0.3;
                if (current.status === 'warning' && day >= 18) {
                  resVal = 0.3 + (day - 18) * 0.6;
                }
                const heightPct = Math.min(95, Math.max(8, (resVal / 7.0) * 100));
                const isOver = resVal > 2.5;

                return (
                  <div key={day} className="flex flex-col items-center flex-1 group">
                    <div
                      style={{ height: `${heightPct}%` }}
                      className={`w-2 rounded-t transition-all ${
                        isOver
                          ? 'bg-amber-400 group-hover:bg-amber-300'
                          : 'bg-cyan-500/70 group-hover:bg-cyan-400'
                      }`}
                      title={`Day ${day + 1}: ${resVal.toFixed(2)} °C`}
                    />
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
              <span>Day 1</span>
              <span>Day 10</span>
              <span>Day 18 (Warning Trigger)</span>
              <span>Day 25 (Trip)</span>
              <span>Day 30</span>
            </div>
          </div>

          <div className="p-3 rounded bg-slate-950 border border-slate-800 text-xs text-slate-400 italic">
            By modeling normal thermodynamic behavior against wind speed and electrical power, Sightglass detects subtle bearing friction 7.2 days before classical SCADA alarms trip.
          </div>
        </div>
      </div>
    </div>
  );
};
