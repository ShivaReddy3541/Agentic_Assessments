"""
Central Multi-Agent Orchestrator (Requirement 4)
Orchestrates collaboration between Document Agent, Research Agent, Security Analyst Agent,
and Report Agent with dynamic agent selection and deep blackboard context passing.
"""

import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.models.schemas import (
    WorkflowRequest,
    WorkflowState,
    WorkflowStep,
    StepStatus,
    AgentType,
    MasterReport,
    DocumentQueryRequest,
    ResearchRequest,
    SecurityAnalysisRequest,
)
from backend.agents.document_agent import document_agent
from backend.agents.research_agent import research_agent
from backend.agents.security_agent import security_agent
from backend.agents.report_agent import report_agent
from backend.services.storage_service import storage_service


class MultiAgentOrchestrator:
    def _plan_required_agents(self, task_prompt: str) -> List[AgentType]:
        """
        Dynamically analyzes user task prompt to determine which specialized agents are required.
        """
        p_lower = task_prompt.lower()
        required = []

        # Research detection
        if any(w in p_lower for w in ["research", "external", "cve", "threat intel", "industry", "phishing", "trend"]):
            required.append(AgentType.RESEARCH_AGENT)

        # Document RAG detection
        if any(w in p_lower for w in ["document", "internal", "policy", "architecture", "specification", "guide", "control", "compare"]):
            required.append(AgentType.DOCUMENT_AGENT)

        # Security analysis detection
        if any(w in p_lower for w in ["log", "alert", "telemetry", "incident", "brute", "attack", "compromise", "investigat"]):
            required.append(AgentType.SECURITY_AGENT)

        # If multi-agent collaboration or complex query, ensure all 3 primary agents participate
        if len(required) == 0 or len(required) >= 2 or "security assessment" in p_lower or "multi-agent" in p_lower:
            required = [AgentType.RESEARCH_AGENT, AgentType.DOCUMENT_AGENT, AgentType.SECURITY_AGENT]

        # Always append Report Agent for final master synthesis
        required.append(AgentType.REPORT_AGENT)
        return required

    async def execute_workflow(self, req: WorkflowRequest) -> WorkflowState:
        """Execute dynamic collaborative multi-agent workflow with cross-agent context passing."""
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        start_iso = datetime.now(timezone.utc).isoformat()

        # 1. Dynamically plan required agents based on task prompt
        planned_agents = self._plan_required_agents(req.task_prompt)

        steps: List[WorkflowStep] = []
        for ag_type in planned_agents:
            if ag_type == AgentType.RESEARCH_AGENT:
                steps.append(
                    WorkflowStep(
                        step_id=f"step_{uuid.uuid4().hex[:6]}",
                        agent_type=AgentType.RESEARCH_AGENT,
                        name="External Threat & Intelligence Research",
                        description="Gather external intelligence, industry standards, and known threat patterns.",
                        status=StepStatus.PENDING,
                    )
                )
            elif ag_type == AgentType.DOCUMENT_AGENT:
                steps.append(
                    WorkflowStep(
                        step_id=f"step_{uuid.uuid4().hex[:6]}",
                        agent_type=AgentType.DOCUMENT_AGENT,
                        name="Internal Architecture & Policy Retrieval",
                        description="Query uploaded enterprise documentation for baseline defense controls.",
                        status=StepStatus.PENDING,
                    )
                )
            elif ag_type == AgentType.SECURITY_AGENT:
                steps.append(
                    WorkflowStep(
                        step_id=f"step_{uuid.uuid4().hex[:6]}",
                        agent_type=AgentType.SECURITY_AGENT,
                        name="Security Telemetry & Threat Analysis",
                        description="Analyze telemetry logs, detect active threats, and evaluate attack indicators.",
                        status=StepStatus.PENDING,
                    )
                )
            elif ag_type == AgentType.REPORT_AGENT:
                steps.append(
                    WorkflowStep(
                        step_id=f"step_{uuid.uuid4().hex[:6]}",
                        agent_type=AgentType.REPORT_AGENT,
                        name="Multi-Agent Synthesis & Master Report Generation",
                        description="Synthesize cross-agent findings into a comprehensive 11-section executive report.",
                        status=StepStatus.PENDING,
                    )
                )

        state = WorkflowState(
            workflow_id=workflow_id,
            task_prompt=req.task_prompt,
            status=StepStatus.RUNNING,
            steps=steps,
            shared_blackboard={},
            final_report=None,
            started_at=start_iso,
        )

        storage_service.save_workflow_state(state)

        try:
            # ------------------------------------------------------------------
            # Step 1: Research Agent (if planned)
            # ------------------------------------------------------------------
            research_res = None
            for step in state.steps:
                if step.agent_type == AgentType.RESEARCH_AGENT:
                    step.status = StepStatus.RUNNING
                    step.started_at = datetime.now(timezone.utc).isoformat()
                    t0 = time.time()

                    research_topic = req.research_topic or req.task_prompt
                    research_res = await research_agent.conduct_research(
                        ResearchRequest(query=research_topic, depth="comprehensive", max_sources=4)
                    )

                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    step.execution_time_ms = round((time.time() - t0) * 1000, 2)
                    step.output_data = {
                        "research_id": research_res.research_id,
                        "sources_count": len(research_res.sources),
                        "summary": research_res.executive_summary[:200] + "...",
                    }

                    state.shared_blackboard["external_research"] = research_res.model_dump()
                    storage_service.save_workflow_state(state)
                    break

            # ------------------------------------------------------------------
            # Step 2: Document Agent (Consumes Research Findings for Targeted Context)
            # ------------------------------------------------------------------
            doc_res = None
            for step in state.steps:
                if step.agent_type == AgentType.DOCUMENT_AGENT:
                    step.status = StepStatus.RUNNING
                    step.started_at = datetime.now(timezone.utc).isoformat()
                    t0 = time.time()

                    # Inter-Agent Context Passing: Inject research keywords into document RAG query
                    research_context_hint = ""
                    if research_res and research_res.key_findings:
                        top_finding = research_res.key_findings[0].finding
                        research_context_hint = f" relating to {top_finding}"

                    doc_query = f"{req.task_prompt}{research_context_hint} security controls and policies"
                    doc_res = await document_agent.query(
                        DocumentQueryRequest(
                            query=doc_query,
                            doc_ids=req.document_ids,
                            top_k=4,
                        )
                    )

                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    step.execution_time_ms = round((time.time() - t0) * 1000, 2)
                    step.output_data = {
                        "chunks_retrieved": doc_res.chunks_retrieved,
                        "citations_count": len(doc_res.citations),
                        "context_found": doc_res.context_found,
                        "summary": doc_res.answer[:200] + "...",
                    }

                    state.shared_blackboard["document_findings"] = doc_res.model_dump()
                    storage_service.save_workflow_state(state)
                    break

            # ------------------------------------------------------------------
            # Step 3: Security Analyst Agent (Cross-Correlates Logs with Doc Policies & Research Intel)
            # ------------------------------------------------------------------
            sec_res = None
            for step in state.steps:
                if step.agent_type == AgentType.SECURITY_AGENT:
                    step.status = StepStatus.RUNNING
                    step.started_at = datetime.now(timezone.utc).isoformat()
                    t0 = time.time()

                    raw_logs = req.security_logs
                    if not raw_logs or len(raw_logs.strip()) < 10:
                        raw_logs = (
                            "Mar 14 03:12:01 edge-gateway-01 sshd[14201]: Failed password for root from 198.51.100.42 port 48210 ssh2\n"
                            "Mar 14 03:12:03 edge-gateway-01 sshd[14204]: Failed password for admin from 198.51.100.42 port 48214 ssh2\n"
                            "Mar 14 03:12:20 edge-gateway-01 sshd[14240]: Failed password for deploy from 198.51.100.42 port 48250 ssh2\n"
                            "Mar 14 03:13:05 edge-gateway-01 sshd[14325]: Accepted password for deploy from 198.51.100.42 port 48330 ssh2\n"
                            "Mar 14 03:13:12 edge-gateway-01 sudo[14339]: deploy : TTY=pts/2 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash"
                        )

                    doc_context_input = doc_res.answer if doc_res and doc_res.context_found else (doc_res.answer if doc_res else None)
                    research_context_input = research_res.model_dump() if research_res else None

                    sec_res = await security_agent.analyze_logs(
                        SecurityAnalysisRequest(
                            raw_logs=raw_logs,
                            log_type="auth",
                            document_context=doc_context_input,
                            research_context=research_context_input,
                        )
                    )

                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    step.execution_time_ms = round((time.time() - t0) * 1000, 2)
                    step.output_data = {
                        "threat": sec_res.threat,
                        "severity": sec_res.severity.value,
                        "confidence": sec_res.confidence,
                        "indicators_count": len(sec_res.indicators),
                    }

                    state.shared_blackboard["security_analysis"] = sec_res.model_dump()
                    storage_service.save_workflow_state(state)
                    break

            # ------------------------------------------------------------------
            # Step 4: Report Agent (Synthesizes Master Report from Shared Blackboard State)
            # ------------------------------------------------------------------
            for step in state.steps:
                if step.agent_type == AgentType.REPORT_AGENT:
                    step.status = StepStatus.RUNNING
                    step.started_at = datetime.now(timezone.utc).isoformat()
                    t0 = time.time()

                    doc_text = doc_res.answer if doc_res else "No internal documentation queried."
                    research_payload = research_res.model_dump() if research_res else None
                    security_payload = sec_res.model_dump() if sec_res else None

                    master_report = await report_agent.generate_master_report(
                        workflow_id=workflow_id,
                        task_prompt=req.task_prompt,
                        document_context=doc_text,
                        research_context=research_payload,
                        security_context=security_payload,
                    )

                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    step.execution_time_ms = round((time.time() - t0) * 1000, 2)
                    step.output_data = {
                        "report_id": master_report.report_id,
                        "title": master_report.title,
                        "word_count": len(master_report.markdown_content.split()),
                    }

                    state.final_report = master_report
                    break

            state.status = StepStatus.COMPLETED
            state.completed_at = datetime.now(timezone.utc).isoformat()
            state.total_duration_ms = round((time.time() - start_time) * 1000, 2)

            storage_service.save_workflow_state(state)
            return state

        except Exception as e:
            state.status = StepStatus.FAILED
            state.error = str(e)
            state.completed_at = datetime.now(timezone.utc).isoformat()
            state.total_duration_ms = round((time.time() - start_time) * 1000, 2)
            storage_service.save_workflow_state(state)
            raise e

    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        return storage_service.get_workflow_state(workflow_id)

    def list_workflows(self) -> List[Dict[str, Any]]:
        return storage_service.list_workflows()


# Global singleton instance
orchestrator = MultiAgentOrchestrator()
