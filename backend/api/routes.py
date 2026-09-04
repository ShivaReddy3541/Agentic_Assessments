"""
FastAPI REST API routes for Document RAG, Research Agent, Security Analyst,
Multi-Agent Orchestrator, and Reports.
"""

from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from backend.models.schemas import (
    DocumentMetadata,
    DocumentUploadResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    ResearchRequest,
    ResearchReport,
    SecurityAnalysisRequest,
    SecurityAnalysisResult,
    SecurityPreset,
    WorkflowRequest,
    WorkflowState,
    MasterReport,
    ReportSummary,
    SystemStats,
)
from backend.agents.document_agent import document_agent
from backend.agents.research_agent import research_agent
from backend.agents.security_agent import security_agent
from backend.agents.orchestrator import orchestrator
from backend.services.storage_service import storage_service
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/api")


# ==============================================================================
# Health & Stats
# ==============================================================================

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Agentic AI Research & Security Analysis Platform",
        "version": "1.0.0",
        "llm_provider": llm_service.provider,
        "llm_configured": llm_service.is_configured,
    }


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    counts = storage_service.get_counts()
    return SystemStats(
        document_count=counts["document_count"],
        chunk_count=counts["chunk_count"],
        research_count=counts["research_count"],
        security_analysis_count=counts["security_analysis_count"],
        workflow_count=counts["workflow_count"],
        report_count=counts["report_count"],
        llm_provider=llm_service.provider,
        llm_model=llm_service.model,
        llm_configured=llm_service.is_configured,
    )


# ==============================================================================
# Requirement 1: Document & RAG Endpoints
# ==============================================================================

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    allowed_exts = ("pdf", "docx", "doc", "txt", "md", "json")
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(allowed_exts)}",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > 25 * 1024 * 1024:  # 25 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 25 MB limit.")

    result = await document_agent.ingest_document(file_bytes, file.filename)
    return result


@router.get("/documents", response_model=List[DocumentMetadata])
async def list_documents():
    return document_agent.list_documents()


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    deleted = document_agent.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"success": True, "message": f"Document {doc_id} deleted successfully."}


@router.post("/documents/query", response_model=DocumentQueryResponse)
async def query_documents(req: DocumentQueryRequest):
    return await document_agent.query(req)


# ==============================================================================
# Requirement 2: Research Agent Endpoints
# ==============================================================================

@router.post("/research", response_model=ResearchReport)
async def conduct_research(req: ResearchRequest):
    return await research_agent.conduct_research(req)


@router.get("/research/history")
async def get_research_history():
    return research_agent.list_research_history()


# ==============================================================================
# Requirement 3: Security Analyst Agent Endpoints
# ==============================================================================

@router.post("/security/analyze", response_model=SecurityAnalysisResult)
async def analyze_security_logs(req: SecurityAnalysisRequest):
    return await security_agent.analyze_logs(req)


@router.get("/security/presets", response_model=List[SecurityPreset])
async def get_security_presets():
    return security_agent.get_presets()


@router.get("/security/history")
async def get_security_history():
    return security_agent.list_history()


# ==============================================================================
# Requirement 4: Multi-Agent Orchestrator Endpoints
# ==============================================================================

@router.post("/agent/workflow", response_model=WorkflowState)
async def run_multi_agent_workflow(req: WorkflowRequest):
    return await orchestrator.execute_workflow(req)


@router.get("/agent/workflow/{workflow_id}", response_model=WorkflowState)
async def get_workflow_status(workflow_id: str):
    state = orchestrator.get_workflow_state(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return state


@router.get("/agent/workflows")
async def list_workflows():
    return orchestrator.list_workflows()


# ==============================================================================
# Reports Endpoints
# ==============================================================================

@router.get("/reports", response_model=List[ReportSummary])
async def list_reports():
    return storage_service.list_reports()


@router.get("/reports/{report_id}", response_model=MasterReport)
async def get_report(report_id: str):
    rep = storage_service.get_report(report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found.")
    return rep
