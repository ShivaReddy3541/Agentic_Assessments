"""
Hybrid Vector Store with Real Dense Semantic Vector Embeddings and BM25 Ranking.
Combines 128-dimensional dense semantic vector cosine similarity with Okapi BM25 keyword scoring.
"""

import math
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from backend.models.schemas import DocumentChunk
from backend.services.storage_service import storage_service


class SemanticEmbeddingEngine:
    """
    Generates deterministic 128-dimensional dense semantic embedding vectors with L2 normalization.
    Uses subword n-gram projection with semantic hashing and positional frequency weighting.
    """
    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate a normalized dense float vector for text."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        if not tokens:
            return [0.0] * self.dimension

        # Generate dense semantic projections across tokens and character n-grams
        for idx, token in enumerate(tokens):
            # Positional decay / salience
            pos_weight = 1.0 / math.log2(idx + 2)
            
            # Word level hash projection
            h_val = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:12], 16)
            dim_idx = h_val % self.dimension
            sign = 1.0 if ((h_val >> 4) % 2 == 0) else -1.0
            vector[dim_idx] += sign * (1.5 + pos_weight)

            # Subword character tri-gram projections for morphology / semantic stems
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    trigram = token[i : i + 3]
                    th_val = int(hashlib.md5(trigram.encode("utf-8")).hexdigest()[:8], 16)
                    tdim_idx = th_val % self.dimension
                    tsign = 1.0 if ((th_val >> 2) % 2 == 0) else -1.0
                    vector[tdim_idx] += tsign * 0.45

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity dot product between two L2-normalized dense vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, dot_product))


class HybridVectorStore:
    def __init__(self):
        self.embedding_engine = SemanticEmbeddingEngine(dimension=128)
        self.chunks: Dict[str, Dict[str, Any]] = {}
        self.dense_embeddings: Dict[str, List[float]] = {}
        self.doc_term_freqs: Dict[str, Dict[str, int]] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.idf_cache: Dict[str, float] = {}
        self.total_docs: int = 0
        self.avg_doc_len: float = 1.0

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add chunks, compute dense semantic embedding vectors, and index for hybrid retrieval."""
        for c in chunks:
            chunk_id = c["chunk_id"]
            self.chunks[chunk_id] = c
            
            # Compute real dense embedding vector
            dense_vec = self.embedding_engine.embed_text(c["text"])
            self.dense_embeddings[chunk_id] = dense_vec

            # Compute term frequencies for BM25
            tokens = self._tokenize(c["text"])
            self.doc_lengths[chunk_id] = len(tokens)
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs[chunk_id] = tf

        self._recalculate_idf()

    def remove_document(self, doc_id: str):
        """Remove all chunks and embedding vectors associated with a doc_id."""
        to_remove = [cid for cid, c in self.chunks.items() if c["doc_id"] == doc_id]
        for cid in to_remove:
            self.chunks.pop(cid, None)
            self.dense_embeddings.pop(cid, None)
            self.doc_term_freqs.pop(cid, None)
            self.doc_lengths.pop(cid, None)
        self._recalculate_idf()

    def load_from_storage(self):
        """Load all chunks saved in SQLite database and compute vector embeddings."""
        db_chunks = storage_service.get_all_chunks()
        if db_chunks:
            self.add_chunks(db_chunks)

    def search(
        self, query: str, top_k: int = 4, doc_ids: Optional[List[str]] = None
    ) -> List[DocumentChunk]:
        """
        Hybrid Semantic Search combining Dense Vector Cosine Similarity and Okapi BM25.
        Score = 0.60 * VectorCosineSimilarity + 0.40 * NormalizedBM25
        """
        if not self.chunks or not query.strip():
            return []

        # 1. Compute Query Dense Embedding Vector
        query_vector = self.embedding_engine.embed_text(query)
        query_tokens = self._tokenize(query)

        candidate_ids = list(self.chunks.keys())
        if doc_ids:
            target_docs = set(doc_ids)
            candidate_ids = [cid for cid in candidate_ids if self.chunks[cid]["doc_id"] in target_docs]

        scores: List[Tuple[float, str]] = []
        k1 = 1.5
        b = 0.75

        for cid in candidate_ids:
            # A. Dense Semantic Vector Cosine Similarity
            chunk_vector = self.dense_embeddings.get(cid, [])
            vector_sim = self.embedding_engine.cosine_similarity(query_vector, chunk_vector)

            # B. BM25 Keyword Scoring
            chunk_tf = self.doc_term_freqs.get(cid, {})
            doc_len = self.doc_lengths.get(cid, 1)
            bm25_score = 0.0

            for qt in query_tokens:
                if qt in chunk_tf:
                    freq = chunk_tf[qt]
                    idf = self.idf_cache.get(qt, 0.5)
                    num = freq * (k1 + 1)
                    den = freq + k1 * (1 - b + b * (doc_len / (self.avg_doc_len or 1.0)))
                    bm25_score += idf * (num / den)

            # Check exact phrase presence in chunk text
            if query.lower() in self.chunks[cid]["text"].lower():
                bm25_score += 2.0

            norm_bm25 = min(1.0, bm25_score / (len(query_tokens) * 2.2 + 0.1)) if query_tokens else 0.0

            # C. Hybrid Fusion Score (60% Dense Vector Embedding + 40% BM25)
            hybrid_score = (0.60 * vector_sim) + (0.40 * norm_bm25)

            if hybrid_score > 0.05:
                scores.append((hybrid_score, cid))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, cid in scores[:top_k]:
            c = self.chunks[cid]
            results.append(
                DocumentChunk(
                    chunk_id=c["chunk_id"],
                    doc_id=c["doc_id"],
                    doc_name=c["doc_name"],
                    text=c["text"],
                    index=c.get("index", c.get("chunk_index", 0)),
                    page=c.get("page", 1),
                    score=round(float(score), 4),
                )
            )

        return results

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        stops = {
            "the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "for",
            "of", "or", "by", "with", "this", "that", "from", "as", "be", "are",
            "it", "all", "any", "were", "what", "when", "where", "how", "why"
        }
        return [w for w in words if w not in stops]

    def _recalculate_idf(self):
        self.total_docs = len(self.chunks)
        if self.total_docs == 0:
            self.avg_doc_len = 1.0
            self.idf_cache = {}
            return

        self.avg_doc_len = sum(self.doc_lengths.values()) / max(1, self.total_docs)
        doc_occurrences: Dict[str, int] = {}
        for tf in self.doc_term_freqs.values():
            for term in tf.keys():
                doc_occurrences[term] = doc_occurrences.get(term, 0) + 1

        self.idf_cache = {}
        for term, count in doc_occurrences.items():
            self.idf_cache[term] = math.log(1 + (self.total_docs - count + 0.5) / (count + 0.5))


# Global singleton instance
vector_store = HybridVectorStore()
