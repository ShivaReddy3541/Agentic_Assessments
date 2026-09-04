"""
Unit and integration tests for Research Agent (Requirement 2).
"""

import pytest
import pytest_asyncio
from backend.agents.research_agent import research_agent
from backend.models.schemas import ResearchRequest


@pytest.mark.asyncio
async def test_research_agent_workflow():
    req = ResearchRequest(
        query="Current challenges in Zero Trust Architecture and AiTM phishing defense",
        depth="comprehensive",
        max_sources=4,
    )

    report = await research_agent.conduct_research(req)

    assert report.research_id.startswith("res_")
    assert len(report.sources) > 0
    assert len(report.key_findings) > 0
    assert report.executive_summary is not None
    assert len(report.executive_summary) > 50
    # Verify source citations are preserved
    for source in report.sources:
        assert source.url.startswith("http")
        assert len(source.domain) > 0
        assert source.credibility_score > 0.0


@pytest.mark.asyncio
async def test_research_history_listing():
    history = research_agent.list_research_history()
    assert isinstance(history, list)
    assert len(history) >= 1
