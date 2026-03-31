from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import get_db, Document, DocumentSummary, ExtractedEntity
from app.api.schemas import SummaryOut, EntityOut

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/summary/{document_id}", response_model=SummaryOut)
async def get_summary(document_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    result = await db.execute(
        select(DocumentSummary).where(DocumentSummary.document_id == document_id).order_by(DocumentSummary.created_at.desc())
    )
    summary = result.scalar_one_or_none()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not yet generated")
    return SummaryOut(
        document_id=document_id,
        filename=doc.original_name,
        purpose=summary.purpose,
        parties=summary.parties,
        key_dates=summary.key_dates,
        obligations=summary.obligations,
        risks=summary.risks
    )

@router.get("/entities/{document_id}", response_model=list[EntityOut])
async def get_entities(document_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    result = await db.execute(
        select(ExtractedEntity).where(ExtractedEntity.document_id == document_id)
    )
    return result.scalars().all()
