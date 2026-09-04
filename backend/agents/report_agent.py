"""
Report Generator Agent
Synthesizes inputs from Document Agent, Research Agent, and Security Analyst Agent
into a unified 11-section executive master report.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.models.schemas import (
    MasterReport,
    SecurityMitigationStep,
    SeverityLevel,
)
from backend.services.storage_service import storage_service
from backend.services.llm_service import llm_service


class ReportAgent:
    async def generate_master_report(
        self,
        workflow_id: str,
        task_prompt: str,
        document_context: Optional[str] = None,
        research_context: Optional[Dict[str, Any]] = None,
        security_context: Optional[Dict[str, Any]] = None,
    ) -> MasterReport:
        """Generate structured 11-section master report dynamically from agent results."""
        report_id = f"rep_{uuid.uuid4().hex[:8]}"

        # Extract structured items
        doc_text = document_context or "No internal documentation was queried for this assessment."

        res_text = "No external web intelligence was queried for this assessment."
        references = []
        if research_context:
            res_text = research_context.get("executive_summary", "")
            for s in research_context.get("sources", []):
                references.append(f"[{s.get('title', 'External Reference')}]({s.get('url', '#')}) — {s.get('domain', 'Web Source')}")

        threats = []
        severity = SeverityLevel.MEDIUM
        evidence = []
        mitigations = []
        sec_text = "No live security logs were analyzed for this assessment."

        if security_context:
            threats.append(security_context.get("threat", "Identified Security Threat"))
            sec_sev = security_context.get("severity", "MEDIUM")
            if isinstance(sec_sev, SeverityLevel):
                severity = sec_sev
            elif str(sec_sev).upper() in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
                severity = SeverityLevel(str(sec_sev).upper())

            sec_text = security_context.get("explanation", "")
            evidence = security_context.get("evidence", [])
            indicators = security_context.get("indicators", [])
            for ind in indicators:
                evidence.append(f"IOC Indicator: {ind}")

            for m in security_context.get("mitigations", []):
                if isinstance(m, dict):
                    mitigations.append(
                        SecurityMitigationStep(
                            priority=m.get("priority", "IMMEDIATE"),
                            action=m.get("action", "Mitigate Threat"),
                            description=m.get("description", "Execute remediation."),
                            command_or_rule=m.get("command_or_rule"),
                        )
                    )
                elif isinstance(m, SecurityMitigationStep):
                    mitigations.append(m)

        if not references:
            references = [
                "[NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) — csrc.nist.gov",
                "[MITRE ATT&CK Enterprise Framework](https://attack.mitre.org/) — attack.mitre.org",
                "[CISA Cyber Defense Directives](https://www.cisa.gov/) — cisa.gov",
            ]

        # Executive summary generation via LLM
        exec_summary_prompt = (
            f"User Objective: {task_prompt}\n\n"
            f"Document Insights: {doc_text[:400]}\n\n"
            f"External Research: {res_text[:400]}\n\n"
            f"Security Analysis Findings: {sec_text[:400]}\n\n"
            f"Write a concise, high-impact 2-paragraph Executive Summary for this comprehensive security assessment:"
        )

        system_prompt = "You are a Chief Information Security Officer (CISO) and Principal AI Architect."
        executive_summary = await llm_service.generate_text(
            prompt=exec_summary_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

        conclusion_prompt = (
            f"Provide a strategic conclusion and organizational outlook based on findings: {task_prompt} and severity: {severity.value}."
        )
        conclusion = await llm_service.generate_text(
            prompt=conclusion_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

        title = f"Multi-Agent Security & Intelligence Report: {task_prompt[:50]}..."

        # Assemble full markdown content
        markdown_lines = [
            f"# {title}",
            f"**Report ID**: `{report_id}` | **Workflow ID**: `{workflow_id}` | **Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Overall Threat Severity**: `{severity.value}`",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            executive_summary,
            "",
            "## 2. Research Question / Objective",
            f"**Primary Objective**: {task_prompt}",
            "",
            "## 3. Internal Document Findings (RAG)",
            doc_text,
            "",
            "## 4. External Intelligence & Research Findings",
            res_text,
            "",
            "## 5. Security Telemetry & Log Analysis",
            sec_text,
            "",
            "## 6. Identified Threats",
        ]

        if threats:
            for t in threats:
                markdown_lines.append(f"- **{t}**")
        else:
            markdown_lines.append("- No immediate critical threat identified.")

        markdown_lines.extend([
            "",
            "## 7. Severity Assessment",
            f"- **Assigned Severity Rating**: `{severity.value}`",
            f"- **Confidence Rating**: {int(security_context.get('confidence', 0.9) * 100) if security_context else 90}%",
            "",
            "## 8. Correlated Evidence & Indicators of Compromise (IOCs)",
        ])

        if evidence:
            for ev in evidence:
                markdown_lines.append(f"- `{ev}`")
        else:
            markdown_lines.append("- Telemetry baseline within normal thresholds.")

        markdown_lines.extend([
            "",
            "## 9. Actionable Mitigations & Playbook",
        ])

        if mitigations:
            for idx, m in enumerate(mitigations, 1):
                cmd_block = f"\n  ```bash\n  {m.command_or_rule}\n  ```" if m.command_or_rule else ""
                markdown_lines.append(
                    f"{idx}. **[{m.priority}] {m.action}**\n   {m.description}{cmd_block}"
                )
        else:
            markdown_lines.append("1. Maintain standard security monitoring and continuous auditing.")

        markdown_lines.extend([
            "",
            "## 10. References & Source Intelligence",
        ])

        for ref in references:
            markdown_lines.append(f"- {ref}")

        markdown_lines.extend([
            "",
            "## 11. Strategic Conclusion & Recommendations",
            conclusion,
        ])

        full_markdown = "\n".join(markdown_lines)

        report = MasterReport(
            report_id=report_id,
            workflow_id=workflow_id,
            title=title,
            generated_at=datetime.now(timezone.utc).isoformat(),
            executive_summary=executive_summary,
            objective=task_prompt,
            document_findings=doc_text,
            research_findings=res_text,
            security_analysis=sec_text,
            threats_identified=threats,
            severity_assessment=severity,
            evidence=evidence,
            recommended_mitigations=mitigations,
            references=references,
            conclusion=conclusion,
            markdown_content=full_markdown,
        )

        # Persist report
        storage_service.save_report(report, report_type="MULTI_AGENT")
        return report


# Global singleton instance
report_agent = ReportAgent()
