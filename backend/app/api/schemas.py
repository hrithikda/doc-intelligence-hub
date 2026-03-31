from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentOut(BaseModel):
    id: int
    original_name: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionRequest(BaseModel):
    question: str
    document_id: Optional[int] = None

class SourceRef(BaseModel):
    chunk_index: int
    page: int
    section: str
    filename: str

class QAResponse(BaseModel):
    answer: str
    sources: list[SourceRef]
    document_id: Optional[int]

class EntityOut(BaseModel):
    entity_type: str
    value: str
    context: Optional[str]

class SummaryOut(BaseModel):
    document_id: int
    filename: str
    purpose: Optional[str]
    parties: Optional[str]
    key_dates: Optional[str]
    obligations: Optional[str]
    risks: Optional[str]

class ComparisonRequest(BaseModel):
    document_id_a: int
    document_id_b: int

class ComparisonRow(BaseModel):
    topic: str
    doc_a: str
    doc_b: str
    verdict: str

class ComparisonOut(BaseModel):
    filename_a: str
    filename_b: str
    comparisons: list[ComparisonRow]

class IngestResponse(BaseModel):
    document_id: int
    original_name: str
    chunk_count: int
    entity_count: int
    status: str
