"""
Agent 1: Document Research Agent (Requirement 1)
Responsibilities:
- Ingest documents (PDF, DOCX, TXT)
- Extract text, chunk, and index with dense embeddings
- Retrieve relevant context for questions
- Synthesize answers grounded strictly in retrieved context
- Format source citations with document names and page numbers
- Explicitly state when the answer cannot be found in uploaded documents
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from backend.models.schemas import (
    DocumentMetadata,
    DocumentUploadResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    DocumentQueryCitation,
)
from backend.rag.parsers import DocumentParser
from backend.rag.chunker import TextChunker
from backend.rag.vector_store import vector_store
from backend.services.storage_service import storage_service
from backend.services.llm_service import llm_service


class DocumentAgent:
    def __init__(self):
        self.chunker = TextChunker(chunk_size=650, chunk_overlap=120)
        # Ensure existing chunks are loaded
        vector_store.load_from_storage()

    async def ingest_document(self, file_bytes: bytes, filename: str) -> DocumentUploadResponse:
        """Parse, chunk, index, and store a newly uploaded document."""
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        pages = DocumentParser.parse_file(file_bytes, filename)
        
        full_text = "\n\n".join([p[1] for p in pages])
        chunks = self.chunker.split_pages(doc_id, filename, pages)

        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        meta = DocumentMetadata(
            doc_id=doc_id,
            filename=filename,
            file_type=ext,
            size_bytes=len(file_bytes),
            chunk_count=len(chunks),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        # Save to database & index in vector store
        storage_service.save_document(meta, raw_text=full_text)
        storage_service.save_chunks(chunks)
        vector_store.add_chunks(chunks)

        return DocumentUploadResponse(
            success=True,
            doc_id=doc_id,
            filename=filename,
            chunks_indexed=len(chunks),
            message=f"Document '{filename}' successfully processed and indexed into {len(chunks)} chunks.",
        )

    async def query(self, req: DocumentQueryRequest) -> DocumentQueryResponse:
        """Retrieve relevant chunks and generate a grounded answer."""
        retrieved_chunks = vector_store.search(
            query=req.query,
            top_k=req.top_k,
            doc_ids=req.doc_ids,
        )

        # Relevance threshold check: if top chunk score is below 0.25, declare not found
        if not retrieved_chunks or (retrieved_chunks and retrieved_chunks[0].score < 0.25):
            return DocumentQueryResponse(
                query=req.query,
                answer=(
                    "I cannot find the answer to this question in the uploaded documents. "
                    "The indexed documentation does not contain sufficient relevant context regarding this query."
                ),
                citations=[],
                chunks_retrieved=len(retrieved_chunks),
                context_found=False,
            )

        # Build citations
        citations = [
            DocumentQueryCitation(
                doc_id=c.doc_id,
                doc_name=c.doc_name,
                chunk_index=c.index,
                page=c.page or 1,
                snippet=c.text[:220] + ("..." if len(c.text) > 220 else ""),
                similarity_score=c.score,
            )
            for c in retrieved_chunks
        ]

        # Construct prompt for LLM
        context_blocks = []
        for i, c in enumerate(retrieved_chunks):
            context_blocks.append(
                f"[Source {i+1}: {c.doc_name}, Page {c.page}, Chunk {c.index}]\n{c.text}"
            )
        formatted_context = "\n\n".join(context_blocks)

        system_prompt = (
            "You are an expert Document Intelligence and RAG Agent. "
            "Your task is to answer the user's question using ONLY the retrieved document excerpts provided below. "
            "Rules:\n"
            "1. Ground every claim directly in the provided context.\n"
            "2. Cite your sources using [DocName, Page X] notation.\n"
            "3. If the context does not contain enough information to answer, explicitly state: "
            "'The uploaded documents do not contain enough information to answer this question.'\n"
            "4. Do not make up facts or extrapolate beyond the provided text."
        )

        user_prompt = (
            f"Retrieved Document Context:\n"
            f"----------------------------------------\n"
            f"{formatted_context}\n"
            f"----------------------------------------\n\n"
            f"User Question: {req.query}\n\n"
            f"Provide a clear, comprehensive, and well-structured answer with citations:"
        )

        answer = await llm_service.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.15,
        )

        return DocumentQueryResponse(
            query=req.query,
            answer=answer,
            citations=citations,
            chunks_retrieved=len(retrieved_chunks),
            context_found=True,
        )

    def list_documents(self) -> List[DocumentMetadata]:
        return storage_service.list_documents()

    def delete_document(self, doc_id: str) -> bool:
        vector_store.remove_document(doc_id)
        return storage_service.delete_document(doc_id)


# Global singleton instance
document_agent = DocumentAgent()
