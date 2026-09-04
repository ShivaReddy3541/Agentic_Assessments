"""
Unit and integration tests for Document Research Agent (Requirement 1)
Covering TXT and real binary PDF ingestion, dense vector embeddings, chunking, and grounded Q&A.
"""

import os
import pytest
import pytest_asyncio
from backend.agents.document_agent import document_agent
from backend.models.schemas import DocumentQueryRequest
from backend.rag.vector_store import vector_store, SemanticEmbeddingEngine


def test_dense_semantic_embedding_generation():
    """Verify that real 128-dimensional L2-normalized float embedding vectors are generated."""
    engine = SemanticEmbeddingEngine(dimension=128)
    vec1 = engine.embed_text("Kubernetes network policies with default deny ingress and mutual TLS")
    vec2 = engine.embed_text("Container network security and mTLS cryptographic verification")
    vec3 = engine.embed_text("Chocolate chip cookie recipe with brown sugar and vanilla")

    assert len(vec1) == 128
    assert len(vec2) == 128
    assert len(vec3) == 128
    # All elements must be floats
    assert all(isinstance(x, float) for x in vec1)

    # Compute cosine similarities
    sim_related = engine.cosine_similarity(vec1, vec2)
    sim_unrelated = engine.cosine_similarity(vec1, vec3)

    assert sim_related > sim_unrelated
    assert sim_related > 0.15


@pytest.mark.asyncio
async def test_real_pdf_ingestion_and_retrieval():
    """Verify that a real binary PDF document is ingested, chunked, embedded, and queried with citations."""
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "sample_data",
        "documents",
        "enterprise_cloud_security_controls.pdf",
    )
    assert os.path.exists(pdf_path), "Sample PDF file must exist"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    res = await document_agent.ingest_document(pdf_bytes, "enterprise_cloud_security_controls.pdf")
    assert res.success is True
    assert res.doc_id.startswith("doc_")
    assert res.chunks_indexed >= 1
    assert "enterprise_cloud_security_controls.pdf" in res.filename

    # Query the ingested PDF
    query_req = DocumentQueryRequest(
        query="What policy is enforced on Kubernetes network ingress and what certificate rotation is required?",
        doc_ids=[res.doc_id],
        top_k=3,
    )
    query_res = await document_agent.query(query_req)

    assert query_res.context_found is True
    assert len(query_res.citations) > 0
    assert "enterprise_cloud_security_controls.pdf" in query_res.citations[0].doc_name
    assert "Kubernetes" in query_res.answer or "mTLS" in query_res.answer or "TLS" in query_res.answer


@pytest.mark.asyncio
async def test_document_query_unrelated_content_not_found():
    """Verify that when querying unrelated topics, the agent explicitly states the answer cannot be found."""
    query_req = DocumentQueryRequest(
        query="How to play acoustic guitar chords for beginners?",
        top_k=2,
    )
    query_res = await document_agent.query(query_req)
    assert (
        "cannot find" in query_res.answer.lower()
        or "not found" in query_res.answer.lower()
        or "do not contain" in query_res.answer.lower()
    )
