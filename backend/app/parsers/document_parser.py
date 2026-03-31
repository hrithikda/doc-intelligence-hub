import fitz
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from docx import Document as DocxDocument
from app.config import settings

@dataclass
class TextChunk:
    text: str
    page: Optional[int]
    section: Optional[str]
    chunk_index: int
    document_id: int
    source_filename: str

def _clean(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def _split_into_chunks(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += size - overlap
    return chunks

def parse_pdf(file_path: Path) -> list[dict]:
    doc = fitz.open(str(file_path))
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = _clean(page.get_text())
        if text:
            pages.append({"text": text, "page": page_num})
    doc.close()
    return pages

def parse_docx(file_path: Path) -> list[dict]:
    doc = DocxDocument(str(file_path))
    pages = []
    current_section = None
    buffer = []
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            if buffer:
                pages.append({"text": _clean(" ".join(buffer)), "page": None, "section": current_section})
                buffer = []
            current_section = para.text.strip()
        elif para.text.strip():
            buffer.append(para.text.strip())
    if buffer:
        pages.append({"text": _clean(" ".join(buffer)), "page": None, "section": current_section})
    return pages

def parse_txt(file_path: Path) -> list[dict]:
    text = _clean(file_path.read_text(encoding="utf-8", errors="ignore"))
    return [{"text": text, "page": None}]

def parse_document(file_path: Path, document_id: int, original_name: str) -> list[TextChunk]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        raw_pages = parse_pdf(file_path)
    elif suffix in (".docx", ".doc"):
        raw_pages = parse_docx(file_path)
    elif suffix == ".txt":
        raw_pages = parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    chunks = []
    idx = 0
    for page_data in raw_pages:
        sub_chunks = _split_into_chunks(page_data["text"], settings.chunk_size, settings.chunk_overlap)
        for chunk_text in sub_chunks:
            chunks.append(TextChunk(
                text=chunk_text,
                page=page_data.get("page"),
                section=page_data.get("section"),
                chunk_index=idx,
                document_id=document_id,
                source_filename=original_name
            ))
            idx += 1
    return chunks
