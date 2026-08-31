"""In-process BM25 over chunk texts (from Qdrant scroll or a passed list)."""

from rank_bm25 import BM25Okapi

from src.qdrant_store import get_client
from src.retrieval.filters import matches_filters, normalize_filters
from src.settings import get_settings


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def load_chunks_from_qdrant(collection: str | None = None) -> list[dict]:
    settings = get_settings()
    client = get_client()
    name = collection or settings.qdrant_collection
    chunks = []
    offset = None
    while True:
        records, offset = client.scroll(
            collection_name=name,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for rec in records:
            payload = rec.payload or {}
            chunks.append(
                {
                    "chunk_id": payload.get("chunk_id"),
                    "incident_id": payload.get("incident_id"),
                    "title": payload.get("title"),
                    "date": payload.get("date"),
                    "service": payload.get("service"),
                    "severity": payload.get("severity"),
                    "section": payload.get("section"),
                    "chunk_index": payload.get("chunk_index"),
                    "text": payload.get("text", ""),
                    "parent_text": payload.get("parent_text", ""),
                }
            )
        if offset is None:
            break
    return chunks


class KeywordIndex:
    def __init__(self, chunks: list[dict] | None = None, collection: str | None = None):
        self.chunks = (
            chunks if chunks is not None else load_chunks_from_qdrant(collection)
        )
        self._bm25 = (
            BM25Okapi([_tokenize(c["text"]) for c in self.chunks])
            if self.chunks
            else None
        )

    def search(
        self, query: str, top_k: int = 5, filters: dict | None = None
    ) -> list[dict]:
        if not self.chunks or self._bm25 is None:
            return []
        cleaned = normalize_filters(filters)
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = []
        for chunk, score in zip(self.chunks, scores):
            if not matches_filters(chunk, cleaned):
                continue
            ranked.append({**chunk, "score": float(score)})
        ranked.sort(key=lambda r: r["score"], reverse=True)
        return ranked[:top_k]


def keyword_search(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
    chunks: list[dict] | None = None,
    collection: str | None = None,
) -> list[dict]:
    return KeywordIndex(chunks=chunks, collection=collection).search(
        query, top_k=top_k, filters=filters
    )
