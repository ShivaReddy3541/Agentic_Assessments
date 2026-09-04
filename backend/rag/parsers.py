"""
Document text extraction and cleaning parsers for PDF, DOCX, TXT, and Markdown.
"""

import io
import re
from typing import List, Tuple
from pypdf import PdfReader
import docx


class DocumentParser:
    @staticmethod
    def parse_file(file_bytes: bytes, filename: str) -> List[Tuple[int, str]]:
        """
        Parses binary file bytes and returns list of (page_number, text) tuples.
        """
        ext = filename.lower().split(".")[-1] if "." in filename else "txt"

        if ext == "pdf":
            return DocumentParser._parse_pdf(file_bytes)
        elif ext in ("docx", "doc"):
            return DocumentParser._parse_docx(file_bytes)
        else:
            return DocumentParser._parse_text(file_bytes)

    @staticmethod
    def _parse_pdf(file_bytes: bytes) -> List[Tuple[int, str]]:
        pages = []
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                cleaned = DocumentParser.clean_text(text)
                if cleaned:
                    pages.append((i + 1, cleaned))
        except Exception as e:
            # Fallback to UTF-8 decoding if PDF parsing fails
            raw = DocumentParser.clean_text(file_bytes.decode("utf-8", errors="ignore"))
            if raw:
                pages.append((1, raw))
        return pages if pages else [(1, "Empty document")]

    @staticmethod
    def _parse_docx(file_bytes: bytes) -> List[Tuple[int, str]]:
        pages = []
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            cleaned = DocumentParser.clean_text("\n".join(full_text))
            if cleaned:
                pages.append((1, cleaned))
        except Exception:
            raw = DocumentParser.clean_text(file_bytes.decode("utf-8", errors="ignore"))
            if raw:
                pages.append((1, raw))
        return pages if pages else [(1, "Empty document")]

    @staticmethod
    def _parse_text(file_bytes: bytes) -> List[Tuple[int, str]]:
        text = file_bytes.decode("utf-8", errors="ignore")
        cleaned = DocumentParser.clean_text(text)
        return [(1, cleaned)] if cleaned else [(1, "Empty document")]

    @staticmethod
    def clean_text(text: str) -> str:
        """Sanitize text, remove control characters and normalize whitespaces."""
        if not text:
            return ""
        # Remove null characters
        text = text.replace("\x00", "")
        # Normalize multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Normalize multiple spaces
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
