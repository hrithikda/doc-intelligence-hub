from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import get_db, Document
from app.core.retriever import retrieve
from app.core.llm import compare_documents
from app.api.schemas import ComparisonRequest, ComparisonOut, ComparisonRow

router = APIRouter(prefix="/compare", tags=["compare"])
COMPARISON_QUERY = "purpose parties obligations dates terms risks scope termination payment"

@router.post("/", response_model=ComparisonOut)
async def compare(request: ComparisonRequest, db: AsyncSession = Depends(get_db)):
    doc_a = await db.get(Document, request.document_id_a)
    doc_b = await db.get(Document, request.document_id_b)
    if not doc_a or not doc_b:
        raise HTTPException(status_code=404, detail="One or both documents not found")
    if doc_a.status != "ready" or doc_b.status != "ready":
        raise HTTPException(status_code=400, detail="Both documents must be fully processed")

    chunks_a = await retrieve(query=COMPARISON_QUERY, document_id=request.document_id_a, top_k=10)
    chunks_b = await retrieve(query=COMPARISON_QUERY, document_id=request.document_id_b, top_k=10)
    result = await compare_documents(chunks_a, chunks_b, doc_a.original_name, doc_b.original_name)
    rows = [ComparisonRow(**row) for row in result.get("comparisons", [])]
    return ComparisonOut(filename_a=doc_a.original_name, filename_b=doc_b.original_name, comparisons=rows)
