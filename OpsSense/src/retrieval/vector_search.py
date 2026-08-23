from qdrant_client.models import FieldCondition, Filter, MatchValue

from src.config import COLLECTION
from src.embeddings.embedder import Embedder
from src.qdrant_store import get_client


def payload_filter(filters: dict | None) -> Filter | None:
    """Exact match on payload fields (metadata), not on embedding space."""
    if not filters:
        return None
    must = [
        FieldCondition(key=key, match=MatchValue(value=value))
        for key, value in filters.items()
        if value not in (None, "")
    ]
    return Filter(must=must) if must else None


def search(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
    embedder: Embedder | None = None,
    collection: str | None = None,
    score_threshold: float | None = None,
) -> list[dict]:
    embedder = embedder or Embedder()
    client = get_client()
    response = client.query_points(
        collection_name=collection or COLLECTION,
        query=embedder.embed(query),
        limit=top_k,
        query_filter=payload_filter(filters),
        score_threshold=score_threshold,
        with_payload=True,
    )
    results = []
    for hit in response.points:
        payload = hit.payload or {}
        results.append(
            {
                "score": float(hit.score),
                "incident_id": payload.get("incident_id"),
                "title": payload.get("title"),
                "service": payload.get("service"),
                "severity": payload.get("severity"),
                "chunk_index": payload.get("chunk_index"),
                "chunk_id": payload.get("chunk_id"),
                "text": payload.get("text"),
            }
        )
    return results
