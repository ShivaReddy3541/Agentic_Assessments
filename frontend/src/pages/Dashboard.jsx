import React, { useState, useEffect } from 'react';
import {
  Shield,
  FileText,
  Search,
  AlertTriangle,
  GitMerge,
  FileSpreadsheet,
  ArrowRight,
  Database,
  Cpu,
  CheckCircle,
  Activity,
  Layers,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import SeverityBadge from '../components/SeverityBadge';
import { api } from '../services/api';

export default function Dashboard({ setActiveTab, stats, refreshStats }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecentReports();
  }, []);

  const loadRecentReports = async () => {
    try {
      setLoading(true);
      const data = await api.listReports();
      setReports(data.slice(0, 5));
    } catch (err) {
      console.error('Failed to load reports', err);
    } finally {
      setLoading(false);
    }
  };

  const agentCards = [
    {
      id: 'documents',
      title: 'Document RAG Agent',
      requirement: 'Requirement 1',
      desc: 'Ingest enterprise PDFs/DOCX, hybrid vector retrieval, and context-grounded Q&A with exact citations.',
      icon: FileText,
      color: 'from-purple-500/20 to-indigo-600/20 border-purple-500/40 text-purple-400',
      action: 'Open RAG Studio',
      tab: 'documents',
    },
    {
      id: 'research',
      title: 'Autonomous Research Agent',
      requirement: 'Requirement 2',
      desc: 'Formulate queries, gather multi-source web intelligence, evaluate credibility, and synthesize reports.',
      icon: Search,
      color: 'from-cyan-500/20 to-blue-600/20 border-cyan-500/40 text-cyan-400',
      action: 'Start Web Research',
      tab: 'research',
    },
    {
      id: 'security',
      title: 'Security Analyst Agent',
      requirement: 'Requirement 3',
      desc: 'Deep security telemetry parsing, threat classification, severity scoring, IOC extraction, and playbooks.',
      icon: AlertTriangle,
      color: 'from-rose-500/20 to-orange-600/20 border-rose-500/40 text-rose-400',
      action: 'Analyze Security Logs',
      tab: 'security',
    },
    {
      id: 'workflow',
      title: 'Multi-Agent Orchestrator',
      requirement: 'Requirement 4 (Core)',
      desc: 'Autonomous collaboration engine connecting all agents with shared blackboard memory and master report synthesis.',
      icon: GitMerge,
      color: 'from-emerald-500/20 to-teal-600/20 border-emerald-500/40 text-emerald-400',
      action: 'Launch Multi-Agent Workflow',
      tab: 'workflow',
      highlight: true,
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl glass-panel p-8 border border-white/10">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-72 h-72 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-cyan-500/20 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400 mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            SHIVAREDDY3541 / LIVE INTELLIGENCE CONSOLE
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            Evidence in. Decisions out.
          </h1>
          <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed">
            Agentic_Assessments brings grounded documents, external signals, security telemetry, and coordinated AI analysis into one operational workspace.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-4">
            <button
              onClick={() => setActiveTab('workflow')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-glow transition-all"
            >
              <GitMerge className="w-4 h-4" />
              Open Mission Control
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                refreshStats();
                loadRecentReports();
              }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-300 transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Sync Workspace
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Documents"
          value={stats?.document_count || 0}
          subtitle="Indexed files"
          icon={FileText}
          color="indigo"
        />
        <MetricCard
          title="Vector Chunks"
          value={stats?.chunk_count || 0}
          subtitle="Indexed snippets"
          icon={Database}
          color="cyan"
        />
        <MetricCard
          title="Research"
          value={stats?.research_count || 0}
          subtitle="Web topics"
          icon={Search}
          color="emerald"
        />
        <MetricCard
          title="Threat Analyses"
          value={stats?.security_analysis_count || 0}
          subtitle="Processed logs"
          icon={AlertTriangle}
          color="rose"
        />
        <MetricCard
          title="Workflows"
          value={stats?.workflow_count || 0}
          subtitle="Multi-agent runs"
          icon={GitMerge}
          color="amber"
          badge="Req 4"
        />
        <MetricCard
          title="Reports"
          value={stats?.report_count || 0}
          subtitle="Master outputs"
          icon={FileSpreadsheet}
          color="purple"
        />
      </div>

      {/* 4 Agent Modules Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">Your intelligence systems</h2>
            <p className="text-xs text-slate-400">
              Pick a focused tool or send the full investigation through Mission Control.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {agentCards.map((agent) => {
            const Icon = agent.icon;
            return (
              <div
                key={agent.id}
                className={`glass-panel p-6 rounded-2xl border transition-all duration-300 flex flex-col justify-between ${
                  agent.highlight
                    ? 'border-indigo-500/50 bg-indigo-950/20 ring-1 ring-indigo-500/30 shadow-glow'
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl border bg-gradient-to-br ${agent.color}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-white/10 text-slate-300 uppercase tracking-wider">
                      {agent.requirement}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white">{agent.title}</h3>
                  <p className="mt-2 text-xs text-slate-300 leading-relaxed">{agent.desc}</p>
                </div>

                <div className="mt-6 pt-4 border-t border-white/5">
                  <button
                    onClick={() => setActiveTab(agent.tab)}
                    className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-200 transition-colors group"
                  >
                    <span>{agent.action}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Activity & Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports Feed */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Recent Multi-Agent Reports</h3>
            </div>
            <button
              onClick={() => setActiveTab('reports')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              View All ({stats?.report_count || 0}) <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {reports.length > 0 ? (
              reports.map((rep) => (
                <div
                  key={rep.report_id}
                  onClick={() => setActiveTab('reports')}
                  className="p-3.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-indigo-500/30 transition-all cursor-pointer flex items-center justify-between gap-4"
                >
                  <div className="min-w-0">
                    <h4 className="text-xs font-semibold text-slate-200 truncate">{rep.title}</h4>
                    <div className="flex items-center gap-3 mt-1 text-[11px] text-slate-400">
                      <span>{new Date(rep.generated_at).toLocaleString()}</span>
                      <span>•</span>
                      <span>{rep.word_count} words</span>
                      <span>•</span>
                      <span className="font-mono text-cyan-400">{rep.report_type}</span>
                    </div>
                  </div>
                  {rep.severity && <SeverityBadge severity={rep.severity} />}
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-500 text-xs italic">
                No reports generated yet. Run a Multi-Agent Workflow to generate your first master report.
              </div>
            )}
          </div>
        </div>

        {/* System Architecture & Status */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Platform Health & Status</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5">
                <span className="text-slate-400">LLM Provider</span>
                <span className="font-semibold text-white capitalize">{stats?.llm_provider || 'Gemini'}</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5">
                <span className="text-slate-400">Model Engine</span>
                <span className="font-mono text-cyan-400 text-[11px]">{stats?.llm_model || 'gemini-3.5-flash-lite'}</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5">
                <span className="text-slate-400">Vector Store</span>
                <span className="text-emerald-400 font-medium">Hybrid TF-IDF / BM25 (Active)</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5">
                <span className="text-slate-400">Blackboard State</span>
                <span className="text-indigo-400 font-medium">SQLite Persistent</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5">
                <span className="text-slate-400">System Status</span>
                <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                  <CheckCircle className="w-3.5 h-3.5" /> 100% Operational
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/5 text-[11px] text-slate-500 text-center">
            Assignment 2 — Fully Self-Contained Project
          </div>
        </div>
      </div>
    </div>
  );
}
