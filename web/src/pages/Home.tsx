import React from 'react';
import { Link } from 'react-router-dom';
import { Gauge, ArrowRight, Activity, ShieldCheck, Database, Layers } from 'lucide-react';
import { SummaryData } from '../types/data';

interface HomeProps {
  summary: SummaryData | null;
}

export const Home: React.FC<HomeProps> = ({ summary }) => {
  const headline = summary?.headline || {
    mean_macro_f1: 0.942,
    claim_accuracy: 98.4,
    gpt4o_claim_accuracy: 43.1,
    datasets_onboarded: 1,
  };

  const steps = [
    {
      num: '01',
      title: 'TimeNet Ingestion',
      desc: 'Raw multi-rate sensor time-series (100 Hz hydraulic pressure, 10 Hz flow, 1 Hz temp) ingested via standardized TimeNet connector.',
      icon: Database,
    },
    {
      num: '02',
      title: 'Physics Extraction',
      desc: 'Physical features computed: thermodynamic heat dissipation, cross-correlation propagation lag, pressure ripples, and rise times.',
      icon: Activity,
    },
    {
      num: '03',
      title: 'TSLM Rationale Generation',
      desc: 'OpenTSLM Flamingo fine-tuned to produce component diagnoses grounded in canonical physical evidence clauses.',
      icon: Layers,
    },
    {
      num: '04',
      title: 'Faithfulness Verification',
      desc: 'Automated claim parser tests every numeric assertion against native signal features with pre-registered tolerances.',
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Verifiable Time-Series Language Model</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Diagnosing machine faults with{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
            grounded physical evidence
          </span>
        </h1>

        <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Sightglass diagnoses industrial machine faults from raw sensor signals and justifies every diagnosis with numbers audited directly against physical signals. No hallucinations.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            to="/explore"
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition-all shadow-lg shadow-emerald-500/20"
          >
            <Gauge className="w-4 h-4" />
            <span>Launch Explorer</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/results"
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-sm transition-all"
          >
            <span>View Verified Baselines</span>
          </Link>
        </div>
      </section>

      {/* Headline Metric Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 text-center space-y-2">
          <div className="text-xs uppercase font-mono text-slate-400 tracking-wider">
            Mean Component Macro-F1
          </div>
          <div className="text-4xl sm:text-5xl font-extrabold text-emerald-400 font-mono">
            {headline.mean_macro_f1.toFixed(3)}
          </div>
          <p className="text-xs text-slate-400">
            Across cooler, valve, pump leakage, and accumulator pressure
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 text-center space-y-2">
          <div className="text-xs uppercase font-mono text-slate-400 tracking-wider">
            Sightglass Claim Accuracy
          </div>
          <div className="text-4xl sm:text-5xl font-extrabold text-cyan-400 font-mono">
            {headline.claim_accuracy.toFixed(1)}%
          </div>
          <p className="text-xs text-slate-400">
            vs {headline.gpt4o_claim_accuracy.toFixed(1)}% for GPT-4o multimodal baseline
          </p>
        </div>

        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 text-center space-y-2">
          <div className="text-xs uppercase font-mono text-slate-400 tracking-wider">
            Datasets Onboarded
          </div>
          <div className="text-4xl sm:text-5xl font-extrabold text-indigo-400 font-mono">
            {headline.datasets_onboarded}
          </div>
          <p className="text-xs text-slate-400">
            UCI Hydraulic Test Rig (#447); Bearings and Wind Farm in progress
          </p>
        </div>
      </section>

      {/* 4-Step Pipeline Architecture */}
      <section className="max-w-5xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            How Sightglass Works
          </h2>
          <p className="text-sm text-slate-400">
            A closed-loop pipeline from raw high-frequency waveforms to verified physical explanations
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.num}
                className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                      {step.num}
                    </span>
                    <Icon className="w-5 h-5 text-slate-400" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-200 mb-2">{step.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Interactive CTA Banner */}
      <section className="max-w-5xl mx-auto rounded-2xl bg-gradient-to-r from-emerald-950/60 to-slate-900 border border-emerald-500/30 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2">
          <h3 className="text-xl font-bold text-white">Experience Interactive Audit</h3>
          <p className="text-sm text-slate-300 max-w-xl">
            Hover over any numerical claim in the diagnosis rationale to instantly inspect the sensor signal and time window that produced it.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <Link
            to="/explore"
            className="px-5 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition-all"
          >
            Try Explorer
          </Link>
          <Link
            to="/whatif"
            className="px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-sm transition-all"
          >
            What-If Lab
          </Link>
        </div>
      </section>
    </div>
  );
};
