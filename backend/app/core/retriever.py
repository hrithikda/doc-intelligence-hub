from rank_bm25 import BM25Okapi
from dataclasses import dataclass
from app.config import settings
from app.core.embedder import embed_text
from app.db.chroma_client import query_collection

@dataclass
class RetrievedChunk:
    text: str
    document_id: int
    chunk_index: int
    page: int
    section: str
    source_filename: str
    score: float

def _reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return scores

async def retrieve(query: str, document_id: int | None = None, top_k: int | None = None) -> list[RetrievedChunk]:
    k = top_k or settings.retriever_top_k
    where = {"document_id": document_id} if document_id else None

    query_embedding = await embed_text(query)
    dense_results = await query_collection(query_embedding, n_results=k * 2, where=where)

    dense_docs = dense_results["documents"][0]
    dense_metas = dense_results["metadatas"][0]
    dense_ids = [f"doc{m['document_id']}_chunk{m['chunk_index']}" for m in dense_metas]

    tokenized = [doc.lower().split() for doc in dense_docs]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_ranking = [dense_ids[i] for i in sorted(range(len(bm25_scores)), key=lambda x: bm25_scores[x], reverse=True)]

    fused_scores = _reciprocal_rank_fusion([dense_ids, bm25_ranking])
    id_to_meta = {dense_ids[i]: (dense_docs[i], dense_metas[i]) for i in range(len(dense_ids))}
    top_ids = sorted(fused_scores, key=fused_scores.get, reverse=True)[:k]

    results = []
    for chunk_id in top_ids:
        if chunk_id not in id_to_meta:
            continue
        text, meta = id_to_meta[chunk_id]
        results.append(RetrievedChunk(
            text=text,
            document_id=meta["document_id"],
            chunk_index=meta["chunk_index"],
            page=meta["page"],
            section=meta["section"],
            source_filename=meta["source_filename"],
            score=fused_scores[chunk_id]
        ))
    return results
