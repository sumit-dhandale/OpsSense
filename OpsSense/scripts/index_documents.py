#!/usr/bin/env python3
"""Chunk + embed + upsert incident markdown into Qdrant."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import COLLECTION
from src.ingestion.indexer import index_documents
from src.qdrant_store import collection_info, get_client


def main() -> None:
    n = index_documents()
    info = collection_info(get_client(), COLLECTION)
    print(f"upserted {n} points into {COLLECTION}")
    print(f"points_count={info.points_count}")
    recs, _ = get_client().scroll(COLLECTION, limit=1, with_payload=True, with_vectors=False)
    if recs:
        print("sample payload keys:", sorted((recs[0].payload or {}).keys()))


if __name__ == "__main__":
    main()
