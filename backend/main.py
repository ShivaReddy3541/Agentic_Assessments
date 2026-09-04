"""
Main FastAPI application entrypoint for Agentic AI Research & Security Analysis Platform.
"""

import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.rag.vector_store import vector_store
from backend.agents.document_agent import document_agent
from backend.services.storage_service import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup initialization: load existing vector chunks and index sample docs if first run."""
    vector_store.load_from_storage()

    # If no documents are loaded, auto-load sample documents for seamless out-of-the-box demo
    existing_docs = storage_service.list_documents()
    if not existing_docs:
        sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "documents")
        if os.path.exists(sample_dir):
            for filename in os.listdir(sample_dir):
                filepath = os.path.join(sample_dir, filename)
                if os.path.isfile(filepath) and filename.endswith((".txt", ".pdf", ".docx")):
                    try:
                        with open(filepath, "rb") as f:
                            content = f.read()
                        await document_agent.ingest_document(content, filename)
                        print(f"[Init] Auto-ingested sample document: {filename}")
                    except Exception as e:
                        print(f"[Init] Failed to ingest {filename}: {e}")

    yield


app = FastAPI(
    title="Agentic AI Research & Security Analysis Platform",
    description="Multi-Agent AI Platform featuring Document RAG, Autonomous Web Research, Security Log Analysis, and Dynamic Multi-Agent Collaboration.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(router)


if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
