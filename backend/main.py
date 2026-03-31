from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.models import init_db
from app.api import documents, qa, analysis, compare
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(documents.router)
app.include_router(qa.router)
app.include_router(analysis.router)
app.include_router(compare.router)

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
