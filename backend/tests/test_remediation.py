"""
Comprehensive Strict Verification and Remediation Test Suite for AegisMind AI.
Validates:
- Requirement 1: Document Ingestion, Hybrid Vector RAG Retrieval, Citation Formatting, LLM Pipeline & Fallback
- Requirement 2: Live Web Search, DuckDuckGo Parsing, Source-Page Crawling, Multi-Domain Research, No Static Cyber Leakage
- Requirement 3 & 4: Document -> Security Orchestration Dependency, Causal Policy Violation Evaluation
- Requirement 4: End-to-End Multi-Agent Workflow Execution, Blackboard State Passing, Master Report Generation
"""

import os
import pytest
import pytest_asyncio
from backend.agents.document_agent import document_agent
from backend.agents.research_agent import research_agent
from backend.agents.security_agent import security_agent
from backend.agents.orchestrator import orchestrator
from backend.services.search_service import search_service
from backend.services.llm_service import llm_service
from backend.models.schemas import (
    DocumentQueryRequest,
    ResearchRequest,
    SecurityAnalysisRequest,
    WorkflowRequest,
    SeverityLevel,
    StepStatus,
    AgentType,
)


# ==============================================================================
# Requirement 1: Document / RAG Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_r1_pdf_rag_ingestion_and_grounded_answer():
    """Verify end-to-end PDF ingestion, chunking, retrieval, and grounded citation generation."""
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "sample_data",
        "documents",
        "enterprise_cloud_security_controls.pdf",
    )
    assert os.path.exists(pdf_path), f"PDF file not found at {pdf_path}"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    upload_res = await document_agent.ingest_document(pdf_bytes, "enterprise_cloud_security_controls.pdf")
    assert upload_res.success is True
    assert upload_res.chunks_indexed >= 1
    doc_id = upload_res.doc_id

    # In-domain query grounded in the PDF
    query_req = DocumentQueryRequest(
        query="What policy is enforced on Kubernetes network ingress and what certificate rotation is required?",
        doc_ids=[doc_id],
        top_k=3,
    )
    query_res = await document_agent.query(query_req)

    assert query_res.context_found is True
    assert query_res.chunks_retrieved >= 1
    assert len(query_res.citations) >= 1
    # Check citation metadata
    first_cit = query_res.citations[0]
    assert first_cit.doc_name == "enterprise_cloud_security_controls.pdf"
    assert first_cit.similarity_score > 0.0
    assert len(first_cit.snippet) > 20
    assert len(query_res.answer) > 30


@pytest.mark.asyncio
async def test_r1_out_of_domain_query_rejected():
    """Verify that queries with no relevant context are explicitly declared not found."""
    query_req = DocumentQueryRequest(
        query="What are the best soil fertilization techniques for growing sweet corn in autumn?",
        top_k=3,
    )
    query_res = await document_agent.query(query_req)
    assert query_res.context_found is False
    assert (
        "cannot find" in query_res.answer.lower()
        or "not found" in query_res.answer.lower()
        or "do not contain" in query_res.answer.lower()
    )


# ==============================================================================
# Requirement 2: Web Research & Source-Page Crawling Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_r2_source_page_crawler():
    """Verify that source-page crawler performs a real outbound HTTP request and extracts clean text."""
    test_url = "https://en.wikipedia.org/wiki/Zero_trust_security_model"
    crawled_text = await search_service.fetch_source_page(test_url, timeout=10.0)

    assert isinstance(crawled_text, str)
    assert len(crawled_text) > 100
    assert "<script" not in crawled_text.lower()
    assert "<style" not in crawled_text.lower()
    assert "zero trust" in crawled_text.lower() or "security" in crawled_text.lower()


@pytest.mark.asyncio
async def test_r2_multi_domain_research_no_static_leakage():
    """Verify live search, crawling, and synthesis across distinct domains without cybersecurity leakage."""
    test_domains = [
        {
            "query": "Tomato gardening planting and soil care tips",
            "forbidden_keywords": ["zero trust", "c2 beaconing", "shadow copy", "mitre att&ck"],
            "expected_keywords": ["tomato", "plant", "soil", "garden", "fruit", "water"],
        },
        {
            "query": "Python async programming event loop best practices",
            "forbidden_keywords": ["vssadmin", "ransomware", "aitm phishing", "sqlmap"],
            "expected_keywords": ["python", "async", "loop", "concurrency", "await", "task"],
        },
    ]

    for item in test_domains:
        req = ResearchRequest(query=item["query"], depth="comprehensive", max_sources=3)
        report = await research_agent.conduct_research(req)

        assert report.research_id.startswith("res_")
        assert len(report.sources) >= 1
        assert len(report.key_findings) >= 1
        assert len(report.strategic_takeaways) >= 1
        assert len(report.conclusion) > 30

        # Verify sources have valid URLs and domains
        for s in report.sources:
            assert s.url.startswith("http")
            assert len(s.domain) > 0
            assert s.credibility_score > 0.0

        # Verify dynamic conclusion and takeaways do not leak inappropriate cyber terms
        summary_and_conclusion = (report.executive_summary + " " + report.conclusion + " " + " ".join(report.strategic_takeaways)).lower()
        for forbidden in item["forbidden_keywords"]:
            assert forbidden not in summary_and_conclusion, f"Found leaked keyword '{forbidden}' in report for topic '{item['query']}'"

        # Verify topic relevance
        assert any(exp in summary_and_conclusion for exp in item["expected_keywords"]), f"Report did not contain expected keywords for '{item['query']}'"


# ==============================================================================
# Requirement 3 & 4: Document -> Security Orchestration Causal Dependency
# ==============================================================================

@pytest.mark.asyncio
async def test_r3_r4_document_to_security_causal_dependency():
    """
    Strict Causal Test:
    Test A: Security Agent receives Document findings enforcing strict SSH key authentication & password ban.
            -> Downstream analysis MUST flag a policy violation and mandate compliance with the document policy.
    Test B: Security Agent receives same logs WITHOUT document context.
            -> Downstream analysis does NOT flag the document policy violation.
    """
    ssh_logs = (
        "Mar 14 03:12:01 edge-gateway-01 sshd[14201]: Failed password for root from 198.51.100.42 port 48210 ssh2\n"
        "Mar 14 03:12:03 edge-gateway-01 sshd[14204]: Failed password for admin from 198.51.100.42 port 48214 ssh2\n"
        "Mar 14 03:12:06 edge-gateway-01 sshd[14209]: Failed password for deploy from 198.51.100.42 port 48220 ssh2\n"
        "Mar 14 03:13:05 edge-gateway-01 sshd[14325]: Accepted password for deploy from 198.51.100.42 port 48330 ssh2\n"
        "Mar 14 03:13:12 edge-gateway-01 sudo[14339]: deploy : TTY=pts/2 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash"
    )

    doc_context_a = (
        "Internal Architecture Document (doc_sec_baseline.pdf, Page 1):\n"
        "All edge servers mandate hardware SSH keys and FIDO2 MFA. PasswordAuthentication is strictly disabled."
    )

    # Execution A: With Document Findings
    req_a = SecurityAnalysisRequest(
        raw_logs=ssh_logs,
        log_type="auth",
        document_context=doc_context_a,
    )
    res_a = await security_agent.analyze_logs(req_a)

    # Execution B: Without Document Findings
    req_b = SecurityAnalysisRequest(
        raw_logs=ssh_logs,
        log_type="auth",
        document_context=None,
    )
    res_b = await security_agent.analyze_logs(req_b)

    # Causal Verification
    has_policy_violation_a = any("[Policy Violation]" in ev for ev in res_a.evidence)
    has_policy_violation_b = any("[Policy Violation]" in ev for ev in res_b.evidence)

    assert has_policy_violation_a is True, "Test A must detect policy violation when document context is present"
    assert has_policy_violation_b is False, "Test B must NOT detect policy violation when document context is absent"

    # Verify mitigation in Test A recommends enforcing internal documented baseline
    has_doc_mitigation_a = any("Documented" in m.action for m in res_a.mitigations)
    assert has_doc_mitigation_a is True, "Test A must generate a mitigation referencing internal documented policy"

    # Both must identify the core technical threat accurately
    assert res_a.severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL)
    assert res_b.severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL)


# ==============================================================================
# Requirement 4: Multi-Agent Workflow & Master Report
# ==============================================================================

@pytest.mark.asyncio
async def test_r4_full_orchestration_workflow_and_master_report():
    """Verify end-to-end multi-agent orchestration, shared blackboard state passing, and 11-section master report."""
    req = WorkflowRequest(
        task_prompt="Investigate SSH brute force security incident, verify internal cloud security controls, research AiTM phishing patterns, and compile comprehensive assessment.",
        research_topic="Adversary-in-the-Middle phishing and credential attacks",
        security_logs=(
            "Mar 14 03:12:01 sshd: Failed password for root from 198.51.100.42\n"
            "Mar 14 03:12:05 sshd: Failed password for admin from 198.51.100.42\n"
            "Mar 14 03:13:05 sshd: Accepted password for deploy from 198.51.100.42\n"
            "Mar 14 03:13:12 sudo: deploy : USER=root ; COMMAND=/bin/bash"
        ),
    )

    state = await orchestrator.execute_workflow(req)

    assert state.workflow_id.startswith("wf_")
    assert state.status == StepStatus.COMPLETED
    assert len(state.steps) == 4

    # Verify each agent executed and recorded timing
    agent_types_executed = [step.agent_type for step in state.steps]
    assert AgentType.RESEARCH_AGENT in agent_types_executed
    assert AgentType.DOCUMENT_AGENT in agent_types_executed
    assert AgentType.SECURITY_AGENT in agent_types_executed
    assert AgentType.REPORT_AGENT in agent_types_executed

    for step in state.steps:
        assert step.status == StepStatus.COMPLETED
        assert step.execution_time_ms is not None

    # Verify shared blackboard contains all intermediate agent outputs
    assert "external_research" in state.shared_blackboard
    assert "document_findings" in state.shared_blackboard
    assert "security_analysis" in state.shared_blackboard

    # Verify Master Report
    report = state.final_report
    assert report is not None
    assert report.report_id.startswith("rep_")
    assert report.severity_assessment in (SeverityLevel.HIGH, SeverityLevel.CRITICAL)
    assert len(report.threats_identified) >= 1
    assert len(report.recommended_mitigations) >= 1
    assert len(report.references) >= 1
    assert "1. Executive Summary" in report.markdown_content
    assert "3. Internal Document Findings" in report.markdown_content
    assert "4. External Intelligence & Research Findings" in report.markdown_content
    assert "5. Security Telemetry & Log Analysis" in report.markdown_content
    assert "9. Actionable Mitigations & Playbook" in report.markdown_content
    assert "11. Strategic Conclusion" in report.markdown_content
