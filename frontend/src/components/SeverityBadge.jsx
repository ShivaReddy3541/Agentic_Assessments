import React from 'react';
import { AlertTriangle, AlertCircle, Info, ShieldAlert } from 'lucide-react';

export default function SeverityBadge({ severity }) {
  const sev = (severity || 'MEDIUM').toUpperCase();

  const config = {
    CRITICAL: {
      bg: 'bg-rose-500/15 border-rose-500/30 text-rose-400',
      icon: ShieldAlert,
      glow: 'shadow-glow-rose',
    },
    HIGH: {
      bg: 'bg-orange-500/15 border-orange-500/30 text-orange-400',
      icon: AlertTriangle,
      glow: '',
    },
    MEDIUM: {
      bg: 'bg-amber-500/15 border-amber-500/30 text-amber-400',
      icon: AlertCircle,
      glow: '',
    },
    LOW: {
      bg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',
      icon: Info,
      glow: 'shadow-glow-emerald',
    },
  };

  const current = config[sev] || config.MEDIUM;
  const Icon = current.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border ${current.bg} ${current.glow}`}
    >
      <Icon className="w-3.5 h-3.5" />
      {sev}
    </span>
  );
}
