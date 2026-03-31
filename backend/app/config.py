from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "Document Intelligence Hub"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doc_intelligence"

    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "documents"

    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.1:8b"
    ollama_embed_model: str = "nomic-embed-text"

    upload_dir: Path = Path("uploads")
    max_file_size_mb: int = 50

    chunk_size: int = 512
    chunk_overlap: int = 64
    retriever_top_k: int = 6
    bm25_weight: float = 0.3
    dense_weight: float = 0.7

    class Config:
        env_file = ".env"

settings = Settings()
