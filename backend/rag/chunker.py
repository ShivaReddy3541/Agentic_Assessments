"""
Text chunking module with recursive character splitting and metadata tracking.
"""

import uuid
from typing import List, Dict, Any, Tuple


class TextChunker:
    def __init__(self, chunk_size: int = 650, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_pages(
        self, doc_id: str, doc_name: str, pages: List[Tuple[int, str]]
    ) -> List[Dict[str, Any]]:
        """
        Takes list of (page_num, page_text) and splits into overlapping chunks.
        """
        chunks = []
        chunk_idx = 0

        for page_num, page_text in pages:
            if not page_text.strip():
                continue

            page_chunks = self._recursive_split(page_text)
            for text_chunk in page_chunks:
                text_clean = text_chunk.strip()
                if len(text_clean) < 15:
                    continue

                chunk_id = f"{doc_id}_c{chunk_idx}_{uuid.uuid4().hex[:6]}"
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "doc_name": doc_name,
                        "index": chunk_idx,
                        "page": page_num,
                        "text": text_clean,
                    }
                )
                chunk_idx += 1

        return chunks

    def _recursive_split(self, text: str) -> List[str]:
        """Splits text recursively using paragraphs, sentences, and words."""
        if len(text) <= self.chunk_size:
            return [text]

        separators = ["\n\n", "\n", ". ", "; ", ", ", " "]
        return self._split_text_with_separators(text, separators)

    def _split_text_with_separators(self, text: str, separators: List[str]) -> List[str]:
        if not separators:
            # Fallback: slice by chunk_size
            return [
                text[i : i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
            ]

        sep = separators[0]
        splits = text.split(sep)
        chunks = []
        current_chunk = []
        current_len = 0

        for s in splits:
            s_len = len(s) + len(sep)
            if current_len + s_len > self.chunk_size and current_chunk:
                merged = sep.join(current_chunk).strip()
                if merged:
                    chunks.append(merged)
                # Keep overlap items from the end
                overlap_chars = 0
                overlap_chunk = []
                for item in reversed(current_chunk):
                    if overlap_chars + len(item) <= self.chunk_overlap:
                        overlap_chunk.insert(0, item)
                        overlap_chars += len(item)
                    else:
                        break
                current_chunk = overlap_chunk
                current_len = sum(len(x) + len(sep) for x in current_chunk)

            current_chunk.append(s)
            current_len += s_len

        if current_chunk:
            merged = sep.join(current_chunk).strip()
            if merged:
                chunks.append(merged)

        # If any chunk is still larger than chunk_size, recurse with next separator
        final_chunks = []
        for c in chunks:
            if len(c) > self.chunk_size * 1.5 and len(separators) > 1:
                final_chunks.extend(
                    self._split_text_with_separators(c, separators[1:])
                )
            else:
                final_chunks.append(c)

        return final_chunks
