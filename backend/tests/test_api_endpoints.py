"""
Integration tests for FastAPI REST API endpoints.
"""

import pytest
import pytest_asyncio
import httpx
from backend.main import app


@pytest.mark.asyncio
async def test_health_and_stats_endpoints():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Health check
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

        # Stats check
        resp = await client.get("/api/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert "document_count" in stats
        assert "workflow_count" in stats


@pytest.mark.asyncio
async def test_security_presets_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/security/presets")
        assert resp.status_code == 200
        presets = resp.json()
        assert len(presets) >= 7


@pytest.mark.asyncio
async def test_document_upload_and_query_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload
        files = {"file": ("api_test_doc.txt", b"Zero trust enforces mutual TLS on all Kubernetes service mesh traffic.", "text/plain")}
        upload_resp = await client.post("/api/documents/upload", files=files)
        assert upload_resp.status_code == 200
        upload_data = upload_resp.json()
        assert upload_data["success"] is True
        doc_id = upload_data["doc_id"]

        # Query
        query_payload = {"query": "What protocol does zero trust enforce on Kubernetes service mesh?", "top_k": 3}
        query_resp = await client.post("/api/documents/query", json=query_payload)
        assert query_resp.status_code == 200
        query_data = query_resp.json()
        assert query_data["context_found"] is True
        assert len(query_data["citations"]) > 0


@pytest.mark.asyncio
async def test_research_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"query": "Micro-segmentation in cloud architecture", "depth": "brief", "max_sources": 3}
        resp = await client.post("/api/research", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "research_id" in data
        assert len(data["sources"]) > 0


@pytest.mark.asyncio
async def test_security_analyze_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "raw_logs": "192.0.2.145 - - [14/Mar/2026] 'GET /products?id=1%20UNION%20SELECT%20username,password_hash%20FROM%20users-- HTTP/1.1' 200",
            "log_type": "web",
        }
        resp = await client.post("/api/security/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "severity" in data
        assert "threat" in data
        assert len(data["mitigations"]) > 0


@pytest.mark.asyncio
async def test_workflow_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "task_prompt": "Analyze cloud infrastructure security and assess potential credential stuffing risks.",
        }
        resp = await client.post("/api/agent/workflow", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert len(data["steps"]) == 4
        assert data["final_report"] is not None

        # Fetch workflow by ID
        wf_id = data["workflow_id"]
        get_resp = await client.get(f"/api/agent/workflow/{wf_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["workflow_id"] == wf_id
