from src.deps import get_embedder
from src.embeddings.embedder import Embedder
from src.qdrant_store import get_client
from src.retrieval.filters import normalize_filters, payload_filter
from src.settings import get_settings


def _hit_from_payload(score: float, payload: dict) -> dict:
    return {
        "score": score,
        "incident_id": payload.get("incident_id"),
        "title": payload.get("title"),
        "date": payload.get("date"),
        "service": payload.get("service"),
        "severity": payload.get("severity"),
        "section": payload.get("section"),
        "chunk_index": payload.get("chunk_index"),
        "chunk_id": payload.get("chunk_id"),
        "text": payload.get("text"),
        "parent_text": payload.get("parent_text", ""),
    }


def search(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
    embedder: Embedder | None = None,
    collection: str | None = None,
    score_threshold: float | None = None,
) -> list[dict]:
    settings = get_settings()
    embedder = embedder or get_embedder()
    client = get_client()
    cleaned = normalize_filters(filters)
    response = client.query_points(
        collection_name=collection or settings.qdrant_collection,
        query=embedder.embed(query),
        limit=top_k,
        query_filter=payload_filter(cleaned),
        score_threshold=score_threshold,
        with_payload=True,
    )
    return [
        _hit_from_payload(float(hit.score), hit.payload or {})
        for hit in response.points
    ]
