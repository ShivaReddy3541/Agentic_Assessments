import React from 'react';
import { Loader2, CheckCircle2, XCircle, Clock, SkipForward } from 'lucide-react';

export default function AgentStatusBadge({ status }) {
  const st = (status || 'PENDING').toUpperCase();

  const config = {
    PENDING: {
      bg: 'bg-slate-800/60 border-slate-700/50 text-slate-400',
      icon: Clock,
      label: 'Pending',
    },
    RUNNING: {
      bg: 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300 shadow-glow',
      icon: Loader2,
      spin: true,
      label: 'Running',
    },
    COMPLETED: {
      bg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400 shadow-glow-emerald',
      icon: CheckCircle2,
      label: 'Completed',
    },
    FAILED: {
      bg: 'bg-rose-500/15 border-rose-500/30 text-rose-400 shadow-glow-rose',
      icon: XCircle,
      label: 'Failed',
    },
    SKIPPED: {
      bg: 'bg-zinc-800 border-zinc-700 text-zinc-500',
      icon: SkipForward,
      label: 'Skipped',
    },
  };

  const current = config[st] || config.PENDING;
  const Icon = current.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${current.bg}`}
    >
      <Icon className={`w-3.5 h-3.5 ${current.spin ? 'animate-spin' : ''}`} />
      {current.label}
    </span>
  );
}
