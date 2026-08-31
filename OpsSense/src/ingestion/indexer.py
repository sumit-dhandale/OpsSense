import uuid

from qdrant_client.models import PointStruct

from src.deps import get_embedder, invalidate_keyword_index
from src.ingestion.chunker import chunk_documents
from src.ingestion.loader import load_documents
from src.qdrant_store import ensure_collection, get_client
from src.settings import get_settings


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def _payload(chunk: dict) -> dict:
    return {
        "chunk_id": chunk["chunk_id"],
        "incident_id": chunk["incident_id"],
        "title": chunk["title"],
        "date": chunk.get("date", ""),
        "service": chunk["service"],
        "severity": chunk["severity"],
        "section": chunk.get("section", ""),
        "chunk_index": chunk["chunk_index"],
        "text": chunk["text"],
        "parent_text": chunk.get("parent_text", ""),
    }


def index_chunks(
    chunks: list[dict],
    embedder=None,
    collection: str | None = None,
    recreate: bool = False,
) -> int:
    if not chunks:
        return 0
    settings = get_settings()
    embedder = embedder or get_embedder()
    name = collection or settings.qdrant_collection
    client = get_client()
    vectors = embedder.embed_batch([c["text"] for c in chunks])
    ensure_collection(
        client,
        collection=name,
        vector_size=embedder.dim,
        recreate=recreate,
    )
    points = [
        PointStruct(
            id=_point_id(chunk["chunk_id"]),
            vector=vector,
            payload=_payload(chunk),
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=name, points=points)
    if name == settings.qdrant_collection:
        invalidate_keyword_index()
    return len(points)


def index_documents(
    chunk_size: int | None = None,
    overlap: int | None = None,
    collection: str | None = None,
    embedder=None,
    recreate: bool = False,
) -> int:
    docs = load_documents()
    chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)
    return index_chunks(
        chunks, embedder=embedder, collection=collection, recreate=recreate
    )
