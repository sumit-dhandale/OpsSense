"""Split document text into overlapping windows. Metadata is copied onto every chunk."""

from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")
    tokens = text.split()
    if not tokens:
        return []
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(" ".join(tokens[start:end]))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return chunks


def chunk_document(
    doc: dict, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[dict]:
    parts = chunk_text(doc["content"], chunk_size=chunk_size, overlap=overlap)
    return [
        {
            "chunk_id": f"{doc['incident_id']}:{i}",
            "incident_id": doc["incident_id"],
            "title": doc.get("title", ""),
            "service": doc.get("service", ""),
            "severity": doc.get("severity", ""),
            "chunk_index": i,
            "text": text,
        }
        for i, text in enumerate(parts)
    ]


def chunk_documents(
    docs: list[dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[dict]:
    chunks: list[dict] = []
    for doc in docs:
        chunks.extend(chunk_document(doc, chunk_size=chunk_size, overlap=overlap))
    return chunks
