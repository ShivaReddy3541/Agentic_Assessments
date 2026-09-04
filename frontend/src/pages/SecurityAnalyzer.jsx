import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  Play,
  Loader2,
  Terminal,
  ShieldCheck,
  Zap,
  CheckCircle2,
  Copy,
  Check,
  Layers,
  FileCode,
  Sparkles,
} from 'lucide-react';
import SeverityBadge from '../components/SeverityBadge';
import LogViewer from '../components/LogViewer';
import { api } from '../services/api';

export default function SecurityAnalyzer({ refreshStats }) {
  const [logs, setLogs] = useState('');
  const [presets, setPresets] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  useEffect(() => {
    loadPresets();
  }, []);

  const loadPresets = async () => {
    try {
      const data = await api.getSecurityPresets();
      setPresets(data);
      if (data.length > 0) {
        // Auto-select first preset for instant demo
        selectPreset(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const selectPreset = (preset) => {
    setSelectedPreset(preset.id);
    setLogs(preset.sample_data);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!logs.trim()) return;

    try {
      setLoading(true);
      const res = await api.analyzeSecurityLogs(logs, 'auth', selectedPreset);
      setResult(res);
      refreshStats?.();
    } catch (err) {
      alert(`Security analysis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCommand = (cmd, idx) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-[11px] font-semibold text-rose-400 mb-2">
            <AlertTriangle className="w-3.5 h-3.5" />
            Requirement 3 — Security Analyst Agent
          </div>
          <h1 className="text-2xl font-extrabold text-white">Security Telemetry & Threat Analyzer</h1>
          <p className="text-xs text-slate-300 mt-1">
            Detect attack vectors, classify severity, extract indicators of compromise (IOCs), and generate actionable playbooks.
          </p>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading || !logs.trim()}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 disabled:opacity-50 text-white text-xs font-semibold shadow-glow-rose transition-all self-start sm:self-auto"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          <span>{loading ? 'Analyzing Threat Telemetry...' : 'Execute Threat Analysis'}</span>
        </button>
      </div>

      {/* Preset Selector Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-white/10 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            Built-in Realistic Security Attack Presets (7 Scenarios)
          </span>
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          {presets.map((p) => {
            const isSelected = selectedPreset === p.id;
            return (
              <button
                key={p.id}
                onClick={() => selectPreset(p)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                  isSelected
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-glow-rose'
                    : 'bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white'
                }`}
              >
                {p.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Log Editor & Analysis Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Raw Log Input */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <Terminal className="w-4 h-4 text-rose-400" />
                Raw Security Telemetry Logs
              </span>
              <span className="text-[10px] font-mono text-slate-500">
                {logs.split('\n').filter((l) => l.trim()).length} lines
              </span>
            </div>

            <textarea
              rows={16}
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              placeholder="Paste raw syslog, auth.log, Apache/Nginx access logs, Windows security events, or JSON alerts..."
              className="w-full p-3 rounded-xl bg-[#06090F] border border-white/10 font-mono text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-rose-500 resize-none leading-relaxed"
            />
          </div>
        </div>

        {/* Right Column: AI Analysis Result */}
        <div className="lg:col-span-7 space-y-6">
          {result ? (
            <div className="space-y-6 animate-fadeIn">
              {/* Threat Banner */}
              <div className="glass-panel p-6 rounded-2xl border border-rose-500/30 shadow-glow-rose space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={result.severity} />
                    <span className="text-xs font-mono text-slate-400">
                      Confidence: {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-white/5 text-cyan-300 border border-white/10">
                    {result.attack_type}
                  </span>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white">{result.threat}</h3>
                  <p className="text-xs sm:text-sm text-slate-300 mt-2 leading-relaxed">
                    {result.explanation}
                  </p>
                </div>

                {/* Indicators of Compromise (IOCs) */}
                {result.indicators && result.indicators.length > 0 && (
                  <div className="pt-3 border-t border-white/10 space-y-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Extracted Indicators of Compromise (IOCs)
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {result.indicators.map((ioc, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-lg bg-black/50 border border-rose-500/30 font-mono text-[11px] text-rose-300"
                        >
                          {ioc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Actionable Mitigations */}
              <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-white/10">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    Actionable Remediation & Mitigation Playbook ({result.mitigations?.length || 0})
                  </span>
                </div>

                <div className="space-y-3">
                  {result.mitigations?.map((m, idx) => {
                    const isImmediate = m.priority === 'IMMEDIATE';
                    return (
                      <div
                        key={idx}
                        className={`p-4 rounded-xl border text-xs space-y-2 ${
                          isImmediate
                            ? 'bg-rose-950/15 border-rose-500/30'
                            : 'bg-white/5 border-white/5'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                              isImmediate
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : 'bg-white/10 text-slate-300'
                            }`}
                          >
                            {m.priority}
                          </span>
                          <span className="text-xs font-bold text-slate-100">{m.action}</span>
                        </div>

                        <p className="text-slate-300 text-[11px] leading-relaxed">{m.description}</p>

                        {m.command_or_rule && (
                          <div className="relative mt-2">
                            <pre className="p-2.5 rounded-lg bg-[#06090F] border border-white/10 font-mono text-[11px] text-emerald-400 overflow-x-auto">
                              {m.command_or_rule}
                            </pre>
                            <button
                              onClick={() => handleCopyCommand(m.command_or_rule, idx)}
                              className="absolute right-2 top-2 p-1.5 rounded-md bg-white/10 hover:bg-white/20 text-slate-300 transition-colors"
                              title="Copy Command"
                            >
                              {copiedIndex === idx ? (
                                <Check className="w-3 h-3 text-emerald-400" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-12 rounded-2xl border border-white/10 text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto text-slate-500">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-300">Awaiting Log Telemetry Execution</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Select one of the 7 attack scenarios above or paste your custom security logs, then click{' '}
                <strong>Execute Threat Analysis</strong>.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
