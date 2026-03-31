import asyncio
import json
import ollama
from app.config import settings

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

SPACY_LABEL_MAP = {
    "PERSON": "person",
    "ORG": "organization",
    "GPE": "location",
    "DATE": "date",
    "TIME": "date",
    "MONEY": "monetary_value",
    "LAW": "clause",
    "PRODUCT": "product",
    "EVENT": "event"
}

def extract_with_spacy(text: str) -> list[dict]:
    if not nlp:
        return []
    doc = nlp(text[:50000])
    seen = set()
    entities = []
    for ent in doc.ents:
        key = (ent.label_, ent.text.strip())
        if key in seen or not ent.text.strip():
            continue
        seen.add(key)
        mapped = SPACY_LABEL_MAP.get(ent.label_)
        if mapped:
            start = max(0, ent.start_char - 60)
            end = min(len(text), ent.end_char + 60)
            entities.append({
                "entity_type": mapped,
                "value": ent.text.strip(),
                "context": text[start:end].strip()
            })
    return entities

async def extract_with_llm(text: str) -> list[dict]:
    sample = text[:4000]
    prompt = f"""Extract key entities from this document. Return ONLY valid JSON with an "entities" array.
Each item must have: entity_type (one of: person, organization, date, monetary_value, clause, obligation), value, context (short surrounding phrase).
Focus on contract-specific entities: parties, effective dates, payment terms, termination clauses.

Document excerpt:
{sample}

JSON:"""
    response = await asyncio.to_thread(
        ollama.chat,
        model=settings.ollama_llm_model,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response["message"]["content"].strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(raw)
        return parsed.get("entities", [])
    except json.JSONDecodeError:
        return []

async def extract_entities(full_text: str) -> list[dict]:
    spacy_entities = extract_with_spacy(full_text)
    llm_entities = await extract_with_llm(full_text)
    seen = {(e["entity_type"], e["value"].lower()) for e in spacy_entities}
    merged = list(spacy_entities)
    for e in llm_entities:
        key = (e.get("entity_type", ""), e.get("value", "").lower())
        if key not in seen and e.get("value"):
            seen.add(key)
            merged.append(e)
    return merged
