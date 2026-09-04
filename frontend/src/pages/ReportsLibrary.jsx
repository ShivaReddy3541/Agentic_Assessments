import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  Search,
  Download,
  Printer,
  Eye,
  FileCode,
  Calendar,
  Layers,
  ArrowLeft,
  Share2,
} from 'lucide-react';
import SeverityBadge from '../components/SeverityBadge';
import { api } from '../services/api';

export default function ReportsLibrary() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await api.listReports();
      setReports(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectReport = async (reportId) => {
    try {
      const full = await api.getReport(reportId);
      setSelectedReport(full);
    } catch (err) {
      alert(`Failed to load report details: ${err.message}`);
    }
  };

  const handleDownloadMarkdown = (rep = selectedReport) => {
    if (!rep) return;
    const blob = new Blob([rep.markdown_content], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${rep.report_id}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadJSON = (rep = selectedReport) => {
    if (!rep) return;
    const blob = new Blob([JSON.stringify(rep, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${rep.report_id}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredReports = reports.filter((r) => {
    const matchesSearch =
      r.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      r.report_id.toLowerCase().includes(searchFilter.toLowerCase());
    const matchesSeverity = severityFilter === 'ALL' || r.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[11px] font-semibold text-indigo-400 mb-2">
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Executive Reports Repository
          </div>
          <h1 className="text-2xl font-extrabold text-white">Security & Research Reports Library</h1>
          <p className="text-xs text-slate-300 mt-1">
            Browse, inspect, and export all single-agent and multi-agent synthesized master assessments.
          </p>
        </div>

        {selectedReport && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleDownloadMarkdown()}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Markdown
            </button>
            <button
              onClick={() => handleDownloadJSON()}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-colors"
            >
              <FileCode className="w-3.5 h-3.5" />
              JSON
            </button>
            <button
              onClick={() => window.print()}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              Print
            </button>
          </div>
        )}
      </div>

      {/* Main Layout: List & Detail View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Report Filters & List */}
        <div className="lg:col-span-4 space-y-4">
          <div className="glass-panel p-4 rounded-2xl border border-white/10 space-y-3">
            {/* Search Box */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search reports by title or ID..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Severity Filter */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase transition-all ${
                    severityFilter === sev
                      ? 'bg-indigo-600 text-white shadow-glow'
                      : 'bg-white/5 text-slate-400 hover:text-white'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>

          {/* List of Reports */}
          <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {filteredReports.length > 0 ? (
              filteredReports.map((rep) => {
                const isSelected = selectedReport?.report_id === rep.report_id;
                return (
                  <div
                    key={rep.report_id}
                    onClick={() => handleSelectReport(rep.report_id)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-indigo-950/30 border-indigo-500/50 shadow-glow'
                        : 'glass-panel hover:bg-white/10 border-white/5'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="text-xs font-bold text-slate-200 line-clamp-2 leading-snug">
                        {rep.title}
                      </h4>
                      {rep.severity && <SeverityBadge severity={rep.severity} />}
                    </div>

                    <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-400">
                      <span className="font-mono">{rep.report_id}</span>
                      <span>•</span>
                      <span>{rep.word_count} words</span>
                      <span>•</span>
                      <span>{new Date(rep.generated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="glass-panel p-8 rounded-2xl border border-white/10 text-center text-slate-500 text-xs italic">
                No reports found matching your filter criteria.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Full Report Reader */}
        <div className="lg:col-span-8">
          {selectedReport ? (
            <div className="glass-panel p-8 rounded-2xl border border-white/10 space-y-6 animate-fadeIn">
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-white/10">
                <div>
                  <span className="text-[11px] font-mono text-cyan-400">
                    Report ID: {selectedReport.report_id}
                  </span>
                  <h2 className="text-lg font-bold text-white mt-1">{selectedReport.title}</h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Generated on {new Date(selectedReport.generated_at).toLocaleString()}
                  </p>
                </div>
                {selectedReport.severity_assessment && (
                  <SeverityBadge severity={selectedReport.severity_assessment} />
                )}
              </div>

              {/* Full Markdown Report Body */}
              <div className="prose prose-invert max-w-none text-xs sm:text-sm text-slate-200 leading-relaxed space-y-4">
                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Executive Summary
                  </h3>
                  <p>{selectedReport.executive_summary}</p>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Research Objective
                  </h3>
                  <p className="text-slate-300">{selectedReport.objective}</p>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400">
                    Document Intelligence Findings
                  </h3>
                  <p className="whitespace-pre-wrap text-slate-300">{selectedReport.document_findings}</p>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
                    External Web Research
                  </h3>
                  <p className="whitespace-pre-wrap text-slate-300">{selectedReport.research_findings}</p>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400">
                    Security Analysis & Threat Detections
                  </h3>
                  <p className="text-slate-300">{selectedReport.security_analysis}</p>
                </div>

                {selectedReport.recommended_mitigations && (
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                      Recommended Mitigations
                    </h3>
                    <div className="space-y-2">
                      {selectedReport.recommended_mitigations.map((m, i) => (
                        <div key={i} className="p-3 rounded-xl bg-black/40 border border-white/5 text-xs">
                          <span className="font-bold text-indigo-400">[{m.priority}] {m.action}</span>: {m.description}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                    Strategic Conclusion
                  </h3>
                  <p className="text-slate-300">{selectedReport.conclusion}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-16 rounded-2xl border border-white/10 text-center text-slate-500 text-xs italic">
              Select a report from the list on the left to read its full assessment.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
