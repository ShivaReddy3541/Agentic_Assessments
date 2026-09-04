/**
 * Frontend API client for communicating with the FastAPI backend.
 */

const API_BASE = '/api';

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = 'Network request failed';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || JSON.stringify(errorJson);
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export const api = {
  // System Health & Stats
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  async getStats() {
    const res = await fetch(`${API_BASE}/stats`);
    return handleResponse(res);
  },

  // Document & RAG (Requirement 1)
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async listDocuments() {
    const res = await fetch(`${API_BASE}/documents`);
    return handleResponse(res);
  },

  async deleteDocument(docId) {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  async queryDocuments(query, docIds = null, topK = 4) {
    const res = await fetch(`${API_BASE}/documents/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, doc_ids: docIds, top_k: topK }),
    });
    return handleResponse(res);
  },

  // Research Agent (Requirement 2)
  async conductResearch(query, depth = 'comprehensive', maxSources = 5) {
    const res = await fetch(`${API_BASE}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, depth, max_sources: maxSources }),
    });
    return handleResponse(res);
  },

  async getResearchHistory() {
    const res = await fetch(`${API_BASE}/research/history`);
    return handleResponse(res);
  },

  // Security Analyst Agent (Requirement 3)
  async analyzeSecurityLogs(rawLogs, logType = 'generic', presetId = null) {
    const res = await fetch(`${API_BASE}/security/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_logs: rawLogs, log_type: logType, preset_id: presetId }),
    });
    return handleResponse(res);
  },

  async getSecurityPresets() {
    const res = await fetch(`${API_BASE}/security/presets`);
    return handleResponse(res);
  },

  async getSecurityHistory() {
    const res = await fetch(`${API_BASE}/security/history`);
    return handleResponse(res);
  },

  // Multi-Agent Orchestrator (Requirement 4)
  async runWorkflow(taskPrompt, options = {}) {
    const res = await fetch(`${API_BASE}/agent/workflow`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        task_prompt: taskPrompt,
        document_ids: options.documentIds || null,
        security_logs: options.securityLogs || null,
        research_topic: options.researchTopic || null,
      }),
    });
    return handleResponse(res);
  },

  async getWorkflowState(workflowId) {
    const res = await fetch(`${API_BASE}/agent/workflow/${workflowId}`);
    return handleResponse(res);
  },

  async listWorkflows() {
    const res = await fetch(`${API_BASE}/agent/workflows`);
    return handleResponse(res);
  },

  // Reports
  async listReports() {
    const res = await fetch(`${API_BASE}/reports`);
    return handleResponse(res);
  },

  async getReport(reportId) {
    const res = await fetch(`${API_BASE}/reports/${reportId}`);
    return handleResponse(res);
  },
};
