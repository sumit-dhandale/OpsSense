#!/usr/bin/env python3
"""Chunk + embed + upsert incident markdown into Qdrant."""
import argparse

from src.ingestion.indexer import index_documents
from src.qdrant_store import collection_info, get_client
from src.settings import get_settings


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--recreate",
        action="store_true",
        help="delete and recreate the collection before indexing",
    )
    args = p.parse_args()
    settings = get_settings()
    n = index_documents(recreate=args.recreate)
    info = collection_info(get_client(), settings.qdrant_collection)
    print(f"upserted {n} points into {settings.qdrant_collection}")
    print(f"points_count={info.points_count}")
    recs, _ = get_client().scroll(
        settings.qdrant_collection, limit=1, with_payload=True, with_vectors=False
    )
    if recs:
        print("sample payload keys:", sorted((recs[0].payload or {}).keys()))


if __name__ == "__main__":
    main()
