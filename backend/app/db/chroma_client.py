import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

_client = None
_collection = None

async def get_client():
    global _client
    if _client is None:
        _client = await chromadb.AsyncHttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    return _client

async def get_collection():
    global _collection
    if _collection is None:
        client = await get_client()
        _collection = await client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

async def upsert_chunks(chunk_ids, embeddings, documents, metadatas):
    collection = await get_collection()
    await collection.upsert(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

async def query_collection(query_embedding, n_results, where=None):
    collection = await get_collection()
    kwargs = {"query_embeddings": [query_embedding], "n_results": n_results, "include": ["documents", "metadatas", "distances"]}
    if where:
        kwargs["where"] = where
    return await collection.query(**kwargs)

async def delete_document_chunks(document_id):
    collection = await get_collection()
    await collection.delete(where={"document_id": document_id})
