# AI-Powered Document Intelligence Hub

A fully local, privacy-first document intelligence application. Upload business documents (PDFs, contracts, reports) and interact with them through natural language Q&A, structured summaries, entity extraction, and side-by-side document comparison.

**Zero external API calls. All processing runs on your machine.**

## Features

- **PDF/DOCX/TXT Upload** — drag and drop document ingestion with automatic chunking
- **RAG Q&A** — ask natural language questions, get cited answers grounded in source chunks
- **Hybrid Retrieval** — dense vector search (ChromaDB) + BM25 keyword search fused with Reciprocal Rank Fusion
- **Entity Extraction** — spaCy NER + LLM fallback for contract-specific entities (parties, dates, clauses, monetary values)
- **Structured Summary** — LLM-generated purpose, parties, key dates, obligations, and risks
- **Document Comparison** — side-by-side diff table across two documents with verdict badges

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Ollama (Llama 3.1 8B) |
| Embeddings | nomic-embed-text via Ollama |
| Vector Store | ChromaDB |
| Retrieval | Hybrid dense + BM25 with RRF |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Frontend | React, Vite, Zustand, Axios |
| Parsing | PyMuPDF, python-docx |
| NER | spaCy + LLM fallback |

## Architecture
```
React Frontend (Vite)
    ↓
FastAPI Backend
    ├── Document Parser (PyMuPDF / python-docx)
    ├── Embedding Engine (nomic-embed-text via Ollama)
    ├── Hybrid Retriever (ChromaDB dense + BM25 + RRF)
    ├── LLM (Llama 3.1 8B via Ollama)
    └── Entity Extractor (spaCy + LLM)
        ↓
PostgreSQL (metadata) + ChromaDB (vectors)
```

## Setup

### Prerequisites
- Python 3.11
- Node.js 18+
- Docker
- Ollama

### 1. Install Ollama and pull models
```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### 2. Start Docker services
```bash
docker compose up -d
```

### 3. Backend
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install --only-binary=pymupdf -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8000
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents/upload` | Upload and process a document |
| GET | `/documents/` | List all documents |
| DELETE | `/documents/{id}` | Delete a document |
| POST | `/qa/ask` | Ask a question over documents |
| GET | `/analysis/summary/{id}` | Get structured summary |
| GET | `/analysis/entities/{id}` | Get extracted entities |
| POST | `/compare/` | Compare two documents |
