import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  Trash2,
  Send,
  Loader2,
  Sparkles,
  Layers,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  FileCheck,
} from 'lucide-react';
import { api } from '../services/api';

export default function DocumentStudio({ refreshStats }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  // Q&A State
  const [query, setQuery] = useState('');
  const [querying, setQuerying] = useState(false);
  const [currentResponse, setCurrentResponse] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setUploadMessage(null);
      const res = await api.uploadDocument(file);
      setUploadMessage({ type: 'success', text: res.message });
      await loadDocuments();
      refreshStats?.();
    } catch (err) {
      setUploadMessage({ type: 'error', text: err.message });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Delete this indexed document and its chunks?')) return;
    try {
      await api.deleteDocument(docId);
      await loadDocuments();
      refreshStats?.();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleQuery = async (queryText = query) => {
    if (!queryText.trim()) return;

    try {
      setQuerying(true);
      const res = await api.queryDocuments(queryText);
      setCurrentResponse(res);
      setQueryHistory((prev) => [res, ...prev]);
    } catch (err) {
      alert(`Query failed: ${err.message}`);
    } finally {
      setQuerying(false);
    }
  };

  const sampleQuestions = [
    'What are the mandatory MFA and IAM access requirements?',
    'What WAF rate-limiting rules are enforced on auth endpoints?',
    'What criteria trigger a P0 Security Incident in the cloud architecture?',
    'How does zero-trust micro-segmentation mitigate AiTM phishing attacks?',
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-white/10">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-[11px] font-semibold text-purple-400 mb-2">
            <FileText className="w-3.5 h-3.5" />
            Requirement 1 — Document Intelligence & RAG
          </div>
          <h1 className="text-2xl font-extrabold text-white">Document Research & Q&A Studio</h1>
          <p className="text-xs text-slate-300 mt-1">
            Ingest PDFs, DOCX, and TXT specifications into vector chunks with grounded source citations.
          </p>
        </div>

        {/* Upload Trigger Button */}
        <div>
          <label className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-glow cursor-pointer transition-all">
            <Upload className="w-4 h-4" />
            <span>{uploading ? 'Processing File...' : 'Upload Document'}</span>
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {uploadMessage && (
        <div
          className={`p-4 rounded-2xl text-xs flex items-center gap-2 border ${
            uploadMessage.type === 'success'
              ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-950/20 border-rose-500/30 text-rose-300'
          }`}
        >
          {uploadMessage.type === 'success' ? (
            <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span>{uploadMessage.text}</span>
        </div>
      )}

      {/* Main Grid: Document Library & Q&A Console */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Indexed Document Library */}
        <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Indexed Library ({documents.length})
              </h3>
            </div>
          </div>

          <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
            {documents.length > 0 ? (
              documents.map((doc) => (
                <div
                  key={doc.doc_id}
                  className="p-3.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2.5 min-w-0">
                      <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 mt-0.5 shrink-0">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-xs font-semibold text-slate-200 truncate">{doc.filename}</h4>
                        <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                          <span className="font-mono uppercase px-1.5 py-0.2 rounded bg-white/5 text-purple-300">
                            {doc.file_type}
                          </span>
                          <span>•</span>
                          <span>{doc.chunk_count} chunks</span>
                          <span>•</span>
                          <span>{Math.round(doc.size_bytes / 1024)} KB</span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(doc.doc_id)}
                      className="text-slate-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all p-1"
                      title="Delete document"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs italic">
                No documents uploaded yet. Upload a PDF or TXT to enable RAG.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Q&A Console */}
        <div className="lg:col-span-2 space-y-6">
          {/* Query Input Box */}
          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Ask Document Corpus
            </h3>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ask questions grounded in the uploaded security specifications..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
                className="flex-1 px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-colors"
              />
              <button
                onClick={() => handleQuery()}
                disabled={querying || !query.trim()}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-glow transition-all"
              >
                {querying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                <span>Ask</span>
              </button>
            </div>

            {/* Quick Presets */}
            <div className="space-y-1.5">
              <span className="text-[11px] text-slate-400 font-medium">Sample Questions:</span>
              <div className="flex flex-wrap gap-2">
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setQuery(q);
                      handleQuery(q);
                    }}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white transition-colors text-left"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Current AI Answer Card */}
          {currentResponse && (
            <div className="glass-panel p-6 rounded-2xl border border-purple-500/30 shadow-glow space-y-4 animate-fadeIn">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <FileCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-white">AI Grounded Response</span>
                </div>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-md font-semibold ${
                    currentResponse.context_found
                      ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                      : 'bg-rose-500/15 text-rose-300 border border-rose-500/30'
                  }`}
                >
                  {currentResponse.context_found
                    ? `${currentResponse.chunks_retrieved} Chunks Correlated`
                    : 'Context Not Found'}
                </span>
              </div>

              {/* Formatted Answer */}
              <div className="text-xs sm:text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                {currentResponse.answer}
              </div>

              {/* Grounded Citations Box */}
              {currentResponse.citations && currentResponse.citations.length > 0 && (
                <div className="pt-4 border-t border-white/10 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-purple-400" />
                    Verified Document Citations & Passages
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {currentResponse.citations.map((cite, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-black/40 border border-white/5 hover:border-purple-500/30 transition-all text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-semibold text-purple-300 truncate">
                            {cite.doc_name} (Page {cite.page})
                          </span>
                          <span className="font-mono text-cyan-400 text-[10px]">
                            Score: {Math.round(cite.similarity_score * 100)}%
                          </span>
                        </div>
                        <p className="text-slate-400 text-[11px] italic line-clamp-3 leading-relaxed">
                          "{cite.snippet}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
