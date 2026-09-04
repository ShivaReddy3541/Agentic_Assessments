import React, { useState, useEffect } from 'react';
import {
  GitMerge,
  Play,
  Loader2,
  Sparkles,
  Database,
  Layers,
  FileCheck2,
  CheckCircle2,
  Download,
  Eye,
  RefreshCw,
  Clock,
  Zap,
} from 'lucide-react';
import PipelineVisualizer from '../components/PipelineVisualizer';
import SeverityBadge from '../components/SeverityBadge';
import { api } from '../services/api';

export default function WorkflowStudio({ refreshStats, setActiveTab }) {
  const [taskPrompt, setTaskPrompt] = useState(
    'Research recent AiTM phishing and SSH brute-force attack trends, retrieve internal perimeter architecture controls from our documentation, analyze the server authentication logs for indicators of compromise, and generate a comprehensive security assessment report.'
  );
  const [loading, setLoading] = useState(false);
  const [workflowState, setWorkflowState] = useState(null);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [selectedBlackboardTab, setSelectedBlackboardTab] = useState('external_research');

  const presetWorkflows = [
    {
      title: 'Full Threat & Architecture Investigation',
      prompt:
        'Research recent AiTM phishing and SSH brute-force attack trends, retrieve internal perimeter architecture controls from our documentation, analyze the server authentication logs for indicators of compromise, and generate a comprehensive security assessment report.',
    },
    {
      title: 'SQL Injection & Web Application Assessment',
      prompt:
        'Investigate OWASP SQL injection exploitation patterns, cross-reference our database parameterization and WAF specification documents, analyze web server access telemetry for automated sqlmap queries, and compile an incident response plan.',
    },
    {
      title: 'Ransomware C2 Beaconing & Lateral Movement',
      prompt:
        'Research ransomware command-and-control beaconing intervals and shadow copy deletion signatures, verify enterprise zero-trust micro-segmentation policies, analyze endpoint and firewall telemetry for C2 communication, and synthesize executive playbooks.',
    },
  ];

  const handleLaunchWorkflow = async (customPrompt = taskPrompt) => {
    if (!customPrompt.trim()) return;

    try {
      setLoading(true);
      setWorkflowState(null);
      const state = await api.runWorkflow(customPrompt);
      setWorkflowState(state);
      refreshStats?.();
    } catch (err) {
      alert(`Workflow execution failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!workflowState?.final_report?.markdown_content) return;
    const blob = new Blob([workflowState.final_report.markdown_content], {
      type: 'text/markdown;charset=utf-8;',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Security_Report_${workflowState.workflow_id}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-indigo-500/30 shadow-glow flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-[11px] font-semibold text-indigo-300 mb-2">
            <GitMerge className="w-3.5 h-3.5" />
            Requirement 4 — Multi-Agent Collaboration Engine
          </div>
          <h1 className="text-2xl font-extrabold text-white">Multi-Agent Orchestration Studio</h1>
          <p className="text-xs text-slate-300 mt-1">
            Dynamic orchestration where Document, Research, and Security Analyst agents collaborate automatically via shared blackboard memory.
          </p>
        </div>

        <button
          onClick={() => handleLaunchWorkflow()}
          disabled={loading || !taskPrompt.trim()}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-500 hover:opacity-90 disabled:opacity-50 text-white text-xs font-semibold shadow-glow transition-all self-start sm:self-auto"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          <span>{loading ? 'Orchestrating Agents...' : 'Execute Multi-Agent Workflow'}</span>
        </button>
      </div>

      {/* Task Prompt Input & Presets */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          Autonomous Multi-Agent Task Prompt
        </h3>

        <textarea
          rows={3}
          value={taskPrompt}
          onChange={(e) => setTaskPrompt(e.target.value)}
          placeholder="Describe the multi-agent task (e.g. research external threats, correlate internal architecture documents, analyze security logs, and generate a master report)..."
          className="w-full p-4 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed"
        />

        {/* Workflow Presets */}
        <div className="space-y-1.5">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-400" />
            Preset Multi-Agent Scenarios:
          </span>
          <div className="flex flex-wrap gap-2">
            {presetWorkflows.map((pw, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setTaskPrompt(pw.prompt);
                  handleLaunchWorkflow(pw.prompt);
                }}
                className="text-[11px] px-3.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white transition-colors text-left"
              >
                {pw.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Live Workflow Pipeline Graph */}
      {workflowState && (
        <div className="space-y-6 animate-fadeIn">
          {/* Pipeline Stepper Component */}
          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <GitMerge className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Live Multi-Agent Collaboration Graph</h3>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                <span>Workflow ID: <span className="text-cyan-400">{workflowState.workflow_id}</span></span>
                <span>•</span>
                <span>Total Duration: <span className="text-emerald-400">{workflowState.total_duration_ms} ms</span></span>
              </div>
            </div>

            <PipelineVisualizer
              steps={workflowState.steps}
              activeStepIndex={activeStepIndex}
              onSelectStep={(idx) => setActiveStepIndex(idx)}
            />
          </div>

          {/* Shared Blackboard Memory Inspector */}
          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Inter-Agent Shared Blackboard State</h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                Cross-Agent Context Sharing
              </span>
            </div>

            {/* Blackboard Sub-tabs */}
            <div className="flex gap-2">
              {[
                { id: 'external_research', label: '1. Research Agent Output', color: 'cyan' },
                { id: 'document_findings', label: '2. Document Agent Context', color: 'purple' },
                { id: 'security_analysis', label: '3. Security Analyst Output', color: 'rose' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSelectedBlackboardTab(tab.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    selectedBlackboardTab === tab.id
                      ? 'bg-white/15 text-white border border-white/20'
                      : 'bg-white/5 text-slate-400 hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Blackboard Content View */}
            <div className="p-4 rounded-xl bg-[#06090F] border border-white/5 max-h-60 overflow-y-auto">
              {workflowState.shared_blackboard[selectedBlackboardTab] ? (
                <pre className="font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {JSON.stringify(workflowState.shared_blackboard[selectedBlackboardTab], null, 2)}
                </pre>
              ) : (
                <div className="text-center py-6 text-slate-600 text-xs italic">
                  No data populated in this channel yet
                </div>
              )}
            </div>
          </div>

          {/* Final Synthesized Master Report */}
          {workflowState.final_report && (
            <div className="glass-panel p-6 rounded-2xl border border-emerald-500/30 shadow-glow-emerald space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    <FileCheck2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">
                      Synthesized 11-Section Master Security Assessment
                    </h3>
                    <p className="text-xs text-slate-400">
                      Report ID: {workflowState.final_report.report_id}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <SeverityBadge severity={workflowState.final_report.severity_assessment} />
                  <button
                    onClick={handleDownloadReport}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/10 text-xs font-semibold text-white transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download Markdown
                  </button>
                </div>
              </div>

              {/* Rendered Markdown Preview */}
              <div className="p-6 rounded-2xl bg-[#06090F] border border-white/5 space-y-6 text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
                {/* 1. Executive Summary */}
                <div className="space-y-2">
                  <h4 className="text-sm font-bold text-emerald-400">1. Executive Summary</h4>
                  <p className="text-slate-300 leading-relaxed">
                    {workflowState.final_report.executive_summary}
                  </p>
                </div>

                {/* 2. Research Objective */}
                <div className="space-y-2 pt-4 border-t border-white/5">
                  <h4 className="text-sm font-bold text-cyan-400">2. Research Objective</h4>
                  <p className="text-slate-300">{workflowState.final_report.objective}</p>
                </div>

                {/* 3. Document Findings */}
                <div className="space-y-2 pt-4 border-t border-white/5">
                  <h4 className="text-sm font-bold text-purple-400">3. Internal Document Findings (RAG)</h4>
                  <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {workflowState.final_report.document_findings}
                  </p>
                </div>

                {/* 4. External Intelligence */}
                <div className="space-y-2 pt-4 border-t border-white/5">
                  <h4 className="text-sm font-bold text-blue-400">4. External Intelligence & Web Findings</h4>
                  <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {workflowState.final_report.research_findings}
                  </p>
                </div>

                {/* 5. Security Analysis & Threats */}
                <div className="space-y-2 pt-4 border-t border-white/5">
                  <h4 className="text-sm font-bold text-rose-400">5. Security Telemetry & Threats Identified</h4>
                  <p className="text-slate-300 leading-relaxed">
                    {workflowState.final_report.security_analysis}
                  </p>
                  <ul className="list-disc pl-5 space-y-1 text-slate-300">
                    {workflowState.final_report.threats_identified?.map((t, i) => (
                      <li key={i} className="font-semibold text-rose-300">{t}</li>
                    ))}
                  </ul>
                </div>

                {/* 6. Correlated Evidence */}
                {workflowState.final_report.evidence && workflowState.final_report.evidence.length > 0 && (
                  <div className="space-y-2 pt-4 border-t border-white/5">
                    <h4 className="text-sm font-bold text-amber-400">6. Correlated Evidence & IOCs</h4>
                    <div className="flex flex-wrap gap-2">
                      {workflowState.final_report.evidence.map((ev, i) => (
                        <span key={i} className="px-2.5 py-1 rounded bg-white/5 border border-white/10 font-mono text-[11px] text-slate-300">
                          {ev}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 7. Actionable Mitigations */}
                {workflowState.final_report.recommended_mitigations && (
                  <div className="space-y-3 pt-4 border-t border-white/5">
                    <h4 className="text-sm font-bold text-emerald-400">7. Actionable Mitigations & Playbook</h4>
                    <div className="space-y-2">
                      {workflowState.final_report.recommended_mitigations.map((m, i) => (
                        <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/5 text-xs space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-[10px] px-2 py-0.2 rounded bg-indigo-500/20 text-indigo-300">
                              {m.priority}
                            </span>
                            <span className="font-semibold text-white">{m.action}</span>
                          </div>
                          <p className="text-slate-400 text-[11px]">{m.description}</p>
                          {m.command_or_rule && (
                            <pre className="p-2 rounded bg-black/50 font-mono text-[10px] text-emerald-300 mt-1">
                              {m.command_or_rule}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 8. References & Sources */}
                {workflowState.final_report.references && (
                  <div className="space-y-2 pt-4 border-t border-white/5">
                    <h4 className="text-sm font-bold text-slate-300">8. References & Verified Sources</h4>
                    <ul className="list-disc pl-5 space-y-1 text-slate-400 text-xs">
                      {workflowState.final_report.references.map((ref, i) => (
                        <li key={i}>{ref}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 9. Conclusion */}
                <div className="space-y-2 pt-4 border-t border-white/5">
                  <h4 className="text-sm font-bold text-cyan-400">9. Strategic Conclusion</h4>
                  <p className="text-slate-300 leading-relaxed">
                    {workflowState.final_report.conclusion}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
