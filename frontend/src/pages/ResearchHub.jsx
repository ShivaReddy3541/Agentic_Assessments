import React, { useState, useEffect } from 'react';
import {
  Search,
  Globe,
  ExternalLink,
  BookOpen,
  Loader2,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Share2,
  Clock,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';

export default function ResearchHub({ refreshStats }) {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('comprehensive');
  const [loading, setLoading] = useState(false);
  const [currentReport, setCurrentReport] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await api.getResearchHistory();
      setHistory(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleResearch = async (researchQuery = query) => {
    if (!researchQuery.trim()) return;

    try {
      setLoading(true);
      const report = await api.conductResearch(researchQuery, depth, 5);
      setCurrentReport(report);
      await loadHistory();
      refreshStats?.();
    } catch (err) {
      alert(`Research failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sampleTopics = [
    'Current challenges in Zero Trust Architecture and AiTM phishing defenses',
    'Adversary-in-the-Middle reverse proxy tools and FIDO2 WebAuthn mitigation',
    'Autonomous Multi-Agent AI architectures in cybersecurity threat triage',
    'Ransomware command and control beaconing detection techniques',
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-[11px] font-semibold text-cyan-400 mb-2">
            <Search className="w-3.5 h-3.5" />
            Requirement 2 — Autonomous Research Agent
          </div>
          <h1 className="text-2xl font-extrabold text-white">Autonomous Web Research Hub</h1>
          <p className="text-xs text-slate-300 mt-1">
            Formulate multi-source web intelligence, evaluate source credibility, and synthesize structured research reports.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-white/5 p-1 rounded-xl border border-white/10 self-start sm:self-auto">
          <button
            onClick={() => setDepth('brief')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              depth === 'brief'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Brief
          </button>
          <button
            onClick={() => setDepth('comprehensive')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              depth === 'comprehensive'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Comprehensive
          </button>
        </div>
      </div>

      {/* Query Search Panel */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          Conduct New Cyber & Technology Investigation
        </h3>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-4 top-3.5" />
            <input
              type="text"
              placeholder="Enter research question or cyber intelligence topic..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleResearch()}
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
          <button
            onClick={() => handleResearch()}
            disabled={loading || !query.trim()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white text-xs font-semibold shadow-glow-cyan transition-all"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            <span>{loading ? 'Researching...' : 'Investigate'}</span>
          </button>
        </div>

        {/* Preset Topics */}
        <div className="space-y-1.5">
          <span className="text-[11px] text-slate-400 font-medium">Suggested Topics:</span>
          <div className="flex flex-wrap gap-2">
            {sampleTopics.map((topic, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(topic);
                  handleResearch(topic);
                }}
                className="text-[11px] px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white transition-colors text-left"
              >
                {topic}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Research Output View */}
      {currentReport && (
        <div className="space-y-6 animate-fadeIn">
          {/* Executive Summary Card */}
          <div className="glass-panel p-6 rounded-2xl border border-cyan-500/30 shadow-glow-cyan space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Synthesized Research Report</h3>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                {currentReport.sources?.length || 0} Sources Verified
              </span>
            </div>

            <div className="text-xs sm:text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
              {currentReport.executive_summary}
            </div>

            {/* Strategic Takeaways */}
            {currentReport.strategic_takeaways && (
              <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Strategic Recommendations & Takeaways
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {currentReport.strategic_takeaways.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-black/40 border border-white/5 flex items-start gap-2 text-xs text-slate-300"
                    >
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sources and Key Findings Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Findings */}
            <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-white/10">
                <Layers className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Extracted Key Findings ({currentReport.key_findings?.length || 0})
                </h3>
              </div>

              <div className="space-y-3">
                {currentReport.key_findings?.map((finding, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                        {finding.category}
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-100">{finding.finding}</h4>
                    <p className="text-[11px] text-slate-400 leading-relaxed italic">
                      "{finding.evidence}"
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Collected Sources & Credibility */}
            <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-white/10">
                <Globe className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Verified External Sources ({currentReport.sources?.length || 0})
                </h3>
              </div>

              <div className="space-y-3">
                {currentReport.sources?.map((src, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all text-xs space-y-1.5 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-cyan-300 truncate">{src.title}</span>
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-slate-400 hover:text-cyan-300 p-1"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                    <div className="flex items-center gap-3 text-[10px] text-slate-400">
                      <span className="font-mono">{src.domain}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-emerald-400">
                        <ShieldCheck className="w-3 h-3" />
                        Credibility: {Math.round(src.credibility_score * 100)}%
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px] line-clamp-2 leading-relaxed">
                      {src.snippet}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
