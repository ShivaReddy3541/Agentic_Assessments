"""
Unit and integration tests for Multi-Agent Orchestrator (Requirement 4).
Tests dynamic agent planning, inter-agent context passing, blackboard memory, and master report generation.
"""

import pytest
import pytest_asyncio
from backend.agents.orchestrator import orchestrator
from backend.models.schemas import WorkflowRequest, StepStatus, AgentType


def test_dynamic_agent_planning():
    """Verify that orchestrator dynamically plans agents based on task prompt."""
    # 1. Prompt focusing on external research & document comparison
    plan1 = orchestrator._plan_required_agents(
        "Research zero-trust industry standards and compare with our internal architecture policies."
    )
    assert AgentType.RESEARCH_AGENT in plan1
    assert AgentType.DOCUMENT_AGENT in plan1
    assert AgentType.REPORT_AGENT in plan1

    # 2. Comprehensive multi-agent investigation prompt
    plan2 = orchestrator._plan_required_agents(
        "Investigate recent brute-force incident, retrieve internal security policies, analyze firewall telemetry logs, and compile a security assessment."
    )
    assert AgentType.RESEARCH_AGENT in plan2
    assert AgentType.DOCUMENT_AGENT in plan2
    assert AgentType.SECURITY_AGENT in plan2
    assert AgentType.REPORT_AGENT in plan2


@pytest.mark.asyncio
async def test_multi_agent_collaboration_and_context_passing():
    """Verify that downstream agents consume upstream blackboard context and synthesize master report."""
    req = WorkflowRequest(
        task_prompt="Research AiTM phishing attacks, verify internal authentication policies, and analyze authentication logs for credential abuse.",
        research_topic="Adversary-in-the-Middle AiTM phishing defenses",
        security_logs="Mar 14 03:12:01 sshd: Failed password for root from 198.51.100.42\nMar 14 03:13:05 sshd: Accepted password for deploy from 198.51.100.42",
    )

    state = await orchestrator.execute_workflow(req)

    assert state.workflow_id.startswith("wf_")
    assert state.status == StepStatus.COMPLETED
    assert len(state.steps) >= 3

    # Verify all planned steps completed successfully
    for step in state.steps:
        assert step.status == StepStatus.COMPLETED
        assert step.execution_time_ms is not None
        assert step.execution_time_ms >= 0

    # Verify shared blackboard contains cross-agent context channels
    assert "external_research" in state.shared_blackboard
    assert "document_findings" in state.shared_blackboard
    assert "security_analysis" in state.shared_blackboard

    # Verify that the final master report integrates all intermediate outputs
    assert state.final_report is not None
    assert len(state.final_report.markdown_content) > 200
    assert "Executive Summary" in state.final_report.markdown_content
    assert "Threats" in state.final_report.markdown_content
    assert len(state.final_report.recommended_mitigations) > 0


@pytest.mark.asyncio
async def test_orchestrator_state_retrieval():
    req = WorkflowRequest(
        task_prompt="Evaluate infrastructure posture against ransomware C2 beaconing.",
    )
    state = await orchestrator.execute_workflow(req)

    retrieved = orchestrator.get_workflow_state(state.workflow_id)
    assert retrieved is not None
    assert retrieved.workflow_id == state.workflow_id
    assert retrieved.status == StepStatus.COMPLETED
