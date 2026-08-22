import uuid

from qdrant_client.models import PointStruct

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION
from src.embeddings.embedder import Embedder
from src.ingestion.chunker import chunk_documents
from src.ingestion.loader import load_documents
from src.qdrant_store import ensure_collection, get_client


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def index_chunks(
    chunks: list[dict],
    embedder: Embedder | None = None,
    collection: str | None = None,
    recreate: bool = True,
) -> int:
    if not chunks:
        return 0
    embedder = embedder or Embedder()
    name = collection or COLLECTION
    client = get_client()
    vectors = embedder.embed_batch([c["text"] for c in chunks])
    ensure_collection(
        client,
        collection=name,
        vector_size=len(vectors[0]),
        recreate=recreate,
    )
    points = [
        PointStruct(
            id=_point_id(chunk["chunk_id"]),
            vector=vector,
            payload={
                "chunk_id": chunk["chunk_id"],
                "incident_id": chunk["incident_id"],
                "title": chunk["title"],
                "service": chunk["service"],
                "severity": chunk["severity"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=name, points=points)
    return len(points)


def index_documents(
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    collection: str | None = None,
    embedder: Embedder | None = None,
    recreate: bool = True,
) -> int:
    docs = load_documents()
    chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)
    return index_chunks(
        chunks, embedder=embedder, collection=collection, recreate=recreate
    )
