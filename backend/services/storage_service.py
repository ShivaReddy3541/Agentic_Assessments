"""
Thread-safe SQLite storage service for documents, chunks, research tasks,
security analyses, multi-agent workflows, and generated reports.
"""

import os
import sqlite3
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from backend.models.schemas import (
    DocumentMetadata,
    ResearchReport,
    SecurityAnalysisResult,
    WorkflowState,
    MasterReport,
    ReportSummary,
    SeverityLevel,
)


class StorageService:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "platform.db")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    raw_text TEXT
                )
            """)

            # Document chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    doc_name TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    page INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    FOREIGN KEY (doc_id) REFERENCES documents (doc_id) ON DELETE CASCADE
                )
            """)

            # Research history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_tasks (
                    research_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Security analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_analyses (
                    analysis_id TEXT PRIMARY KEY,
                    threat TEXT NOT NULL,
                    attack_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Workflow states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_states (
                    workflow_id TEXT PRIMARY KEY,
                    task_prompt TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    title TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    severity TEXT,
                    markdown_content TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    # ==========================================================================
    # Document operations
    # ==========================================================================

    def save_document(self, meta: DocumentMetadata, raw_text: str = ""):
        with self._get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT OR REPLACE INTO documents (doc_id, filename, file_type, size_bytes, chunk_count, created_at, raw_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (meta.doc_id, meta.filename, meta.file_type, meta.size_bytes, meta.chunk_count, meta.created_at, raw_text),
            )
            conn.commit()

    def list_documents(self) -> List[DocumentMetadata]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT doc_id, filename, file_type, size_bytes, chunk_count, created_at FROM documents ORDER BY created_at DESC").fetchall()
            return [
                DocumentMetadata(
                    doc_id=r["doc_id"],
                    filename=r["filename"],
                    file_type=r["file_type"],
                    size_bytes=r["size_bytes"],
                    chunk_count=r["chunk_count"],
                    created_at=r["created_at"],
                )
                for r in rows
            ]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            r = conn.cursor().execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()
            if r:
                return dict(r)
            return None

    def delete_document(self, doc_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    def save_chunks(self, chunks: List[Dict[str, Any]]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for c in chunks:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO document_chunks (chunk_id, doc_id, doc_name, chunk_index, page, text)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (c["chunk_id"], c["doc_id"], c["doc_name"], c.get("index", c.get("chunk_index", 0)), c.get("page", 1), c["text"]),
                )
            conn.commit()

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM document_chunks ORDER BY doc_id, chunk_index").fetchall()
            return [dict(r) for r in rows]

    # ==========================================================================
    # Research operations
    # ==========================================================================

    def save_research_report(self, report: ResearchReport):
        with self._get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT OR REPLACE INTO research_tasks (research_id, query, data_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (report.research_id, report.query, report.model_dump_json(), report.timestamp),
            )
            conn.commit()

    def list_research_reports(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT research_id, query, created_at, data_json FROM research_tasks ORDER BY created_at DESC").fetchall()
            return [json.loads(r["data_json"]) for r in rows]

    # ==========================================================================
    # Security operations
    # ==========================================================================

    def save_security_analysis(self, analysis: SecurityAnalysisResult):
        with self._get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT OR REPLACE INTO security_analyses (analysis_id, threat, attack_type, severity, confidence, data_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis.analysis_id,
                    analysis.threat,
                    analysis.attack_type,
                    analysis.severity.value,
                    analysis.confidence,
                    analysis.model_dump_json(),
                    analysis.timestamp,
                ),
            )
            conn.commit()

    def list_security_analyses(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT data_json FROM security_analyses ORDER BY created_at DESC").fetchall()
            return [json.loads(r["data_json"]) for r in rows]

    # ==========================================================================
    # Workflow operations
    # ==========================================================================

    def save_workflow_state(self, state: WorkflowState):
        with self._get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT OR REPLACE INTO workflow_states (workflow_id, task_prompt, status, data_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (state.workflow_id, state.task_prompt, state.status.value, state.model_dump_json(), state.started_at),
            )
            conn.commit()

    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        with self._get_connection() as conn:
            r = conn.cursor().execute("SELECT data_json FROM workflow_states WHERE workflow_id = ?", (workflow_id,)).fetchone()
            if r:
                return WorkflowState.model_validate_json(r["data_json"])
            return None

    def list_workflows(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT data_json FROM workflow_states ORDER BY created_at DESC").fetchall()
            return [json.loads(r["data_json"]) for r in rows]

    # ==========================================================================
    # Report operations
    # ==========================================================================

    def save_report(self, report: MasterReport, report_type: str = "MULTI_AGENT"):
        with self._get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT OR REPLACE INTO reports (report_id, workflow_id, title, report_type, severity, markdown_content, data_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.report_id,
                    report.workflow_id,
                    report.title,
                    report_type,
                    report.severity_assessment.value if report.severity_assessment else None,
                    report.markdown_content,
                    report.model_dump_json(),
                    report.generated_at,
                ),
            )
            conn.commit()

    def get_report(self, report_id: str) -> Optional[MasterReport]:
        with self._get_connection() as conn:
            r = conn.cursor().execute("SELECT data_json FROM reports WHERE report_id = ?", (report_id,)).fetchone()
            if r:
                return MasterReport.model_validate_json(r["data_json"])
            return None

    def list_reports(self) -> List[ReportSummary]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute(
                "SELECT report_id, workflow_id, title, report_type, severity, markdown_content, created_at FROM reports ORDER BY created_at DESC"
            ).fetchall()
            summaries = []
            for r in rows:
                word_count = len(r["markdown_content"].split())
                sev = SeverityLevel(r["severity"]) if r["severity"] else None
                summaries.append(
                    ReportSummary(
                        report_id=r["report_id"],
                        workflow_id=r["workflow_id"],
                        title=r["title"],
                        generated_at=r["created_at"],
                        report_type=r["report_type"],
                        severity=sev,
                        word_count=word_count,
                    )
                )
            return summaries

    # ==========================================================================
    # System stats
    # ==========================================================================

    def get_counts(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            c = conn.cursor()
            docs = c.execute("SELECT COUNT(*) as cnt FROM documents").fetchone()["cnt"]
            chunks = c.execute("SELECT COUNT(*) as cnt FROM document_chunks").fetchone()["cnt"]
            res = c.execute("SELECT COUNT(*) as cnt FROM research_tasks").fetchone()["cnt"]
            sec = c.execute("SELECT COUNT(*) as cnt FROM security_analyses").fetchone()["cnt"]
            wf = c.execute("SELECT COUNT(*) as cnt FROM workflow_states").fetchone()["cnt"]
            rep = c.execute("SELECT COUNT(*) as cnt FROM reports").fetchone()["cnt"]
            return {
                "document_count": docs,
                "chunk_count": chunks,
                "research_count": res,
                "security_analysis_count": sec,
                "workflow_count": wf,
                "report_count": rep,
            }


# Global singleton instance
storage_service = StorageService()
