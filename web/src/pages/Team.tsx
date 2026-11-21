import React from 'react';
import { Users, Code, GitPullRequest, Box, ExternalLink } from 'lucide-react';

export const Team: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-8 space-y-12">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Users className="w-6 h-6 text-emerald-400" />
          <span>Team Sightglass & Project Links</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Built for the TimeNet hackathon: advancing explainable foundation models for physical time-series.
        </p>
      </div>

      {/* Team Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold font-mono">
              DP
            </div>
            <div>
              <div className="font-bold text-white">Prashant Dev</div>
              <div className="text-xs text-slate-400">Lead AI & Systems Engineer</div>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            TimeNet connector architecture, physics feature engineering, OpenTSLM Flamingo training pipeline, faithfulness verification engine, and dashboard export.
          </p>
          <a
            href="https://github.com/devprashant19"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-mono transition-colors"
          >
            <Code className="w-3.5 h-3.5" />
            <span>@devprashant19</span>
          </a>
        </div>

        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-bold font-mono">
              SG
            </div>
            <div>
              <div className="font-bold text-white">Sightglass Core Team</div>
              <div className="text-xs text-slate-400">TimeNet Hackathon Team</div>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Evaluation protocol pre-registration, failure analysis, UI design system, counterfactual simulator, and upstream contributions.
          </p>
          <div className="text-xs text-slate-400 font-mono">
            Open-source under MIT Licence
          </div>
        </div>
      </div>

      {/* Project Links & Resources */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
          Key Repositories & Artifacts
        </h3>

        <div className="divide-y divide-slate-800">
          <div className="py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Code className="w-4 h-4 text-slate-400" />
              <div>
                <div className="text-xs font-semibold text-white">Sightglass Source Code</div>
                <div className="text-[11px] text-slate-400">Complete end-to-end repository with reproduction configs</div>
              </div>
            </div>
            <a
              href="https://github.com/devprashant19/Sightglass"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-mono text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <GitPullRequest className="w-4 h-4 text-slate-400" />
              <div>
                <div className="text-xs font-semibold text-white">TimeNet Connector PR Draft</div>
                <div className="text-[11px] text-slate-400">Upstream dataset connector ready for OpenTSLM/TimeNet</div>
              </div>
            </div>
            <span className="text-xs font-mono text-slate-400">
              docs/pr/hydraulic.md
            </span>
          </div>

          <div className="py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Box className="w-4 h-4 text-slate-400" />
              <div>
                <div className="text-xs font-semibold text-white">Model Card & Specifications</div>
                <div className="text-[11px] text-slate-400">Detailed architecture, data governance, and ethical notes</div>
              </div>
            </div>
            <span className="text-xs font-mono text-slate-400">
              MODEL_CARD.md
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
