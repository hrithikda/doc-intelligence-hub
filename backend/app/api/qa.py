from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import get_db, QASession, Document
from app.core.retriever import retrieve
from app.core.llm import answer_question
from app.api.schemas import QuestionRequest, QAResponse, SourceRef

router = APIRouter(prefix="/qa", tags=["qa"])

@router.post("/ask", response_model=QAResponse)
async def ask(request: QuestionRequest, db: AsyncSession = Depends(get_db)):
    if request.document_id:
        doc = await db.get(Document, request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.status != "ready":
            raise HTTPException(status_code=400, detail="Document is still processing")

    chunks = await retrieve(query=request.question, document_id=request.document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant content found")

    result = await answer_question(request.question, chunks)

    if request.document_id:
        db.add(QASession(
            document_id=request.document_id,
            question=request.question,
            answer=result["answer"],
            source_chunks=str(result["sources"])
        ))

    return QAResponse(
        answer=result["answer"],
        sources=[SourceRef(**s) for s in result["sources"]],
        document_id=request.document_id
    )
