import ollama
import asyncio
from app.config import settings
from app.parsers.document_parser import TextChunk

async def embed_text(text: str) -> list[float]:
    response = await asyncio.to_thread(
        ollama.embeddings,
        model=settings.ollama_embed_model,
        prompt=text
    )
    return response["embedding"]

async def embed_batch(texts: list[str], batch_size: int = 16) -> list[list[float]]:
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = await asyncio.gather(*[embed_text(t) for t in batch])
        embeddings.extend(batch_embeddings)
    return embeddings

async def embed_chunks(chunks: list[TextChunk]):
    texts = [c.text for c in chunks]
    embeddings = await embed_batch(texts)
    ids = [f"doc{c.document_id}_chunk{c.chunk_index}" for c in chunks]
    metadatas = [
        {
            "document_id": c.document_id,
            "chunk_index": c.chunk_index,
            "page": c.page or -1,
            "section": c.section or "",
            "source_filename": c.source_filename
        }
        for c in chunks
    ]
    return ids, embeddings, texts, metadatas
