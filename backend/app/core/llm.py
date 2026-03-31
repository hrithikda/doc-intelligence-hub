import ollama
import asyncio
import json
from app.config import settings
from app.core.retriever import RetrievedChunk

def _format_chunks(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        location = f"page {c.page}" if c.page and c.page > 0 else (c.section or "unknown location")
        parts.append(f"[Source {i} | {c.source_filename} | {location}]\n{c.text}")
    return "\n\n".join(parts)

def _extract_json(text: str) -> str:
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1:
            return text[start:end+1]
    return text.strip()

async def answer_question(question: str, chunks: list[RetrievedChunk]) -> dict:
    context = _format_chunks(chunks)
    prompt = f"""You are a precise document analyst. Answer the question using ONLY the provided source chunks.
For every claim, cite the source number in brackets like [Source 1].
If the answer is not in the sources, say "This information is not found in the provided document."

Context:
{context}

Question: {question}

Answer:"""
    response = await asyncio.to_thread(
        ollama.chat,
        model=settings.ollama_llm_model,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response["message"]["content"]
    sources = [{"chunk_index": c.chunk_index, "page": c.page, "section": c.section, "filename": c.source_filename} for c in chunks]
    return {"answer": answer, "sources": sources}

async def generate_summary(chunks: list[RetrievedChunk], filename: str) -> dict:
    context = _format_chunks(chunks[:12])
    prompt = f"""You are a contract and document analyst. Analyze the document and extract structured information.
Return ONLY valid JSON with exactly these keys: purpose, parties, key_dates, obligations, risks.
Each value should be a concise string. Do not include markdown, backticks, or explanation.

Document: {filename}
Content:
{context}

JSON:"""
    response = await asyncio.to_thread(
        ollama.chat,
        model=settings.ollama_llm_model,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = _extract_json(response["message"]["content"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"purpose": raw, "parties": "", "key_dates": "", "obligations": "", "risks": ""}

async def compare_documents(chunks_a: list[RetrievedChunk], chunks_b: list[RetrievedChunk], filename_a: str, filename_b: str) -> dict:
    context_a = _format_chunks(chunks_a[:8])
    context_b = _format_chunks(chunks_b[:8])
    prompt = f"""Compare these two documents. Return ONLY a JSON object like this exact format, no explanation:
{{"comparisons": [{{"topic": "Purpose", "doc_a": "...", "doc_b": "...", "verdict": "differs"}}]}}

Verdict must be one of: similar, differs, only_in_a, only_in_b.
Cover: purpose, parties, obligations, dates, terms, risks, scope.

Document A ({filename_a}):
{context_a}

Document B ({filename_b}):
{context_b}

JSON:"""
    response = await asyncio.to_thread(
        ollama.chat,
        model=settings.ollama_llm_model,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = _extract_json(response["message"]["content"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"comparisons": [{"topic": "Parse error", "doc_a": "Could not parse comparison", "doc_b": "Try again", "verdict": "differs"}]}
