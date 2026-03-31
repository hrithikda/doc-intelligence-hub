import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.models import get_db, Document, ExtractedEntity, DocumentSummary
from app.db.chroma_client import upsert_chunks, delete_document_chunks
from app.parsers.document_parser import parse_document
from app.core.embedder import embed_chunks
from app.core.llm import generate_summary
from app.core.retriever import retrieve
from app.extractors.entity_extractor import extract_entities
from app.api.schemas import DocumentOut, IngestResponse

router = APIRouter(prefix="/documents", tags=["documents"])
ALLOWED_TYPES = {".pdf", ".docx", ".doc", ".txt"}

@router.post("/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {suffix} not supported.")

    size = 0
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    save_path = settings.upload_dir / safe_name
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(save_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_file_size_mb * 1024 * 1024:
                save_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_file_size_mb}MB limit.")
            await f.write(chunk)

    doc_record = Document(
        filename=safe_name,
        original_name=file.filename,
        file_path=str(save_path),
        file_type=suffix.lstrip("."),
        file_size_bytes=size,
        status="processing"
    )
    db.add(doc_record)
    await db.flush()
    document_id = doc_record.id

    chunks = parse_document(save_path, document_id, file.filename)
    ids, embeddings, texts, metadatas = await embed_chunks(chunks)
    await upsert_chunks(ids, embeddings, texts, metadatas)
    doc_record.chunk_count = len(chunks)

    full_text = " ".join(c.text for c in chunks)
    entities = await extract_entities(full_text)
    for e in entities:
        db.add(ExtractedEntity(
            document_id=document_id,
            entity_type=e.get("entity_type", "unknown"),
            value=e.get("value", ""),
            context=e.get("context")
        ))

    top_chunks = await retrieve(query="document overview purpose parties obligations", document_id=document_id, top_k=12)
    summary_data = await generate_summary(top_chunks, file.filename)
    db.add(DocumentSummary(
        document_id=document_id,
        purpose=summary_data.get("purpose"),
        parties=summary_data.get("parties"),
        key_dates=summary_data.get("key_dates"),
        obligations=summary_data.get("obligations"),
        risks=summary_data.get("risks"),
        raw_summary=str(summary_data)
    ))

    doc_record.status = "ready"
    return IngestResponse(
        document_id=document_id,
        original_name=file.filename,
        chunk_count=len(chunks),
        entity_count=len(entities),
        status="ready"
    )

@router.get("/", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await delete_document_chunks(document_id)
    Path(doc.file_path).unlink(missing_ok=True)
    await db.delete(doc)
    return {"status": "deleted", "document_id": document_id}
