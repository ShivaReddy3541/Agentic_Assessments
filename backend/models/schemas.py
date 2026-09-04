"""
Pydantic schemas and data models for the Agentic AI Research & Security Analysis Platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# Enums
# ==============================================================================

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class AgentType(str, Enum):
    ORCHESTRATOR = "ORCHESTRATOR"
    DOCUMENT_AGENT = "DOCUMENT_AGENT"
    RESEARCH_AGENT = "RESEARCH_AGENT"
    SECURITY_AGENT = "SECURITY_AGENT"
    REPORT_AGENT = "REPORT_AGENT"


# ==============================================================================
# Document & RAG Models (Requirement 1)
# ==============================================================================

class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    size_bytes: int
    chunk_count: int
    created_at: str


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_name: str
    text: str
    index: int
    page: Optional[int] = 1
    score: Optional[float] = 0.0


class DocumentUploadResponse(BaseModel):
    success: bool
    doc_id: str
    filename: str
    chunks_indexed: int
    message: str


class DocumentQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Question to answer using document context")
    doc_ids: Optional[List[str]] = Field(default=None, description="Optional filter by specific document IDs")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of relevant chunks to retrieve")


class DocumentQueryCitation(BaseModel):
    doc_id: str
    doc_name: str
    chunk_index: int
    page: Optional[int] = 1
    snippet: str
    similarity_score: float


class DocumentQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[DocumentQueryCitation] = []
    chunks_retrieved: int
    context_found: bool


# ==============================================================================
# Research Agent Models (Requirement 2)
# ==============================================================================

class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Topic or query to research")
    depth: str = Field(default="comprehensive", description="'brief' or 'comprehensive'")
    max_sources: int = Field(default=5, ge=1, le=10)


class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str
    domain: str
    credibility_score: float = 0.85
    published_date: Optional[str] = None


class ResearchFinding(BaseModel):
    category: str
    finding: str
    evidence: str
    source_url: str


class ResearchReport(BaseModel):
    research_id: str
    query: str
    executive_summary: str
    key_findings: List[ResearchFinding] = []
    sources: List[SourceItem] = []
    strategic_takeaways: List[str] = []
    conclusion: str
    timestamp: str


# ==============================================================================
# Security Analyst Agent Models (Requirement 3)
# ==============================================================================

class SecurityMitigationStep(BaseModel):
    priority: str = Field(..., description="IMMEDIATE, INVESTIGATION, LONG_TERM, DETECTION_RULE")
    action: str
    description: str
    command_or_rule: Optional[str] = None


class SecurityAnalysisRequest(BaseModel):
    raw_logs: str = Field(..., min_length=10, description="Raw log text or structured alerts to analyze")
    log_type: Optional[str] = Field(default="generic", description="syslog, auth, web, windows, ids, firewall, json, generic")
    preset_id: Optional[str] = None
    document_context: Optional[str] = Field(default=None, description="Internal architectural policies/controls from Document RAG")
    research_context: Optional[Dict[str, Any]] = Field(default=None, description="External threat intelligence from Research Agent")


class SecurityAnalysisResult(BaseModel):
    analysis_id: str
    threat: str
    attack_type: str
    severity: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    indicators: List[str] = []  # Extracted IOCs (IPs, accounts, paths, commands)
    evidence: List[str] = []    # Specific suspicious log lines/signals
    explanation: str
    mitigations: List[SecurityMitigationStep] = []
    log_count: int = 0
    raw_log_summary: str
    timestamp: str


class SecurityPreset(BaseModel):
    id: str
    name: str
    description: str
    category: str
    log_type: str
    sample_data: str


# ==============================================================================
# Multi-Agent Orchestration & Workflow Models (Requirement 4)
# ==============================================================================

class WorkflowStep(BaseModel):
    step_id: str
    agent_type: AgentType
    name: str
    description: str
    status: StepStatus = StepStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class WorkflowRequest(BaseModel):
    task_prompt: str = Field(..., min_length=5, description="High level multi-agent task prompt")
    document_ids: Optional[List[str]] = None
    security_logs: Optional[str] = None
    research_topic: Optional[str] = None


class MasterReport(BaseModel):
    report_id: str
    workflow_id: str
    title: str
    generated_at: str
    executive_summary: str
    objective: str
    document_findings: str
    research_findings: str
    security_analysis: str
    threats_identified: List[str] = []
    severity_assessment: SeverityLevel
    evidence: List[str] = []
    recommended_mitigations: List[SecurityMitigationStep] = []
    references: List[str] = []
    conclusion: str
    markdown_content: str


class WorkflowState(BaseModel):
    workflow_id: str
    task_prompt: str
    status: StepStatus = StepStatus.PENDING
    steps: List[WorkflowStep] = []
    shared_blackboard: Dict[str, Any] = {}
    final_report: Optional[MasterReport] = None
    started_at: str
    completed_at: Optional[str] = None
    total_duration_ms: Optional[float] = None
    error: Optional[str] = None


class ReportSummary(BaseModel):
    report_id: str
    workflow_id: Optional[str] = None
    title: str
    generated_at: str
    report_type: str
    severity: Optional[SeverityLevel] = None
    word_count: int


# ==============================================================================
# System Stats & Health
# ==============================================================================

class SystemStats(BaseModel):
    document_count: int
    chunk_count: int
    research_count: int
    security_analysis_count: int
    workflow_count: int
    report_count: int
    llm_provider: str
    llm_model: str
    llm_configured: bool
