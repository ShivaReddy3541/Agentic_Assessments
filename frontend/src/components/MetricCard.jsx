import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, color = 'indigo', badge }) {
  const colorMap = {
    indigo: {
      border: 'border-indigo-500/20',
      iconBg: 'bg-indigo-500/10 text-indigo-400',
      glow: 'hover:border-indigo-500/40',
    },
    cyan: {
      border: 'border-cyan-500/20',
      iconBg: 'bg-cyan-500/10 text-cyan-400',
      glow: 'hover:border-cyan-500/40',
    },
    emerald: {
      border: 'border-emerald-500/20',
      iconBg: 'bg-emerald-500/10 text-emerald-400',
      glow: 'hover:border-emerald-500/40',
    },
    amber: {
      border: 'border-amber-500/20',
      iconBg: 'bg-amber-500/10 text-amber-400',
      glow: 'hover:border-amber-500/40',
    },
    rose: {
      border: 'border-rose-500/20',
      iconBg: 'bg-rose-500/10 text-rose-400',
      glow: 'hover:border-rose-500/40',
    },
    purple: {
      border: 'border-purple-500/20',
      iconBg: 'bg-purple-500/10 text-purple-400',
      glow: 'hover:border-purple-500/40',
    },
  };

  const style = colorMap[color] || colorMap.indigo;

  return (
    <div className={`glass-panel p-5 rounded-2xl border ${style.border} ${style.glow} transition-all duration-200 group`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-xl ${style.iconBg} transition-transform group-hover:scale-110`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-3xl font-bold tracking-tight text-white">{value}</span>
        {badge && (
          <span className="text-xs px-2 py-0.5 rounded-md bg-white/5 text-slate-300 border border-white/10">
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
}
