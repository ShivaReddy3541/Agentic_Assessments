import React from 'react';
import {
  Search,
  FileText,
  ShieldAlert,
  FileCheck2,
  CheckCircle2,
  Clock,
  Loader2,
  XCircle,
  ArrowRight,
  Database,
  Cpu,
} from 'lucide-react';

export default function PipelineVisualizer({ steps = [], activeStepIndex = 0, onSelectStep }) {
  const agentIcons = {
    RESEARCH_AGENT: Search,
    DOCUMENT_AGENT: FileText,
    SECURITY_AGENT: ShieldAlert,
    REPORT_AGENT: FileCheck2,
  };

  const agentGradients = {
    RESEARCH_AGENT: 'from-cyan-500/20 to-blue-600/20 border-cyan-500/40 text-cyan-400',
    DOCUMENT_AGENT: 'from-purple-500/20 to-indigo-600/20 border-purple-500/40 text-purple-400',
    SECURITY_AGENT: 'from-rose-500/20 to-orange-600/20 border-rose-500/40 text-rose-400',
    REPORT_AGENT: 'from-emerald-500/20 to-teal-600/20 border-emerald-500/40 text-emerald-400',
  };

  return (
    <div className="w-full">
      {/* Visual Workflow Pipeline Stepper */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
        {steps.map((step, idx) => {
          const Icon = agentIcons[step.agent_type] || Cpu;
          const isCurrent = idx === activeStepIndex;
          const isCompleted = step.status === 'COMPLETED';
          const isRunning = step.status === 'RUNNING';
          const isFailed = step.status === 'FAILED';

          return (
            <div
              key={step.step_id || idx}
              onClick={() => onSelectStep && onSelectStep(idx)}
              className={`glass-panel p-4 rounded-2xl border transition-all duration-200 cursor-pointer relative overflow-hidden ${
                isRunning
                  ? 'border-indigo-500/60 shadow-glow ring-1 ring-indigo-500/50 scale-[1.02]'
                  : isCompleted
                  ? 'border-emerald-500/30 bg-emerald-950/10'
                  : isFailed
                  ? 'border-rose-500/40 bg-rose-950/10'
                  : 'border-white/5 opacity-75'
              }`}
            >
              {/* Step indicator header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
                      isCompleted
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        : isRunning
                        ? 'bg-indigo-500/30 text-indigo-300 border border-indigo-500/50 animate-pulse'
                        : 'bg-white/5 text-slate-400 border border-white/10'
                    }`}
                  >
                    0{idx + 1}
                  </div>
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Step {idx + 1}
                  </span>
                </div>

                {/* Status icon */}
                <div>
                  {isRunning && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
                  {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                  {isFailed && <XCircle className="w-4 h-4 text-rose-400" />}
                  {!isRunning && !isCompleted && !isFailed && (
                    <Clock className="w-4 h-4 text-slate-500" />
                  )}
                </div>
              </div>

              {/* Agent card body */}
              <div className="flex items-start gap-3">
                <div
                  className={`p-2.5 rounded-xl border bg-gradient-to-br ${
                    agentGradients[step.agent_type] || 'from-indigo-500/20 to-purple-500/20'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-xs font-bold text-slate-100 truncate">{step.name}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Execution time footer */}
              {step.execution_time_ms !== undefined && step.execution_time_ms !== null && (
                <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[10px] text-slate-400">
                  <span>Execution:</span>
                  <span className="font-mono text-cyan-400">{step.execution_time_ms} ms</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
