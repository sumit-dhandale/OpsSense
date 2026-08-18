#!/usr/bin/env python3
"""Ping Qdrant and create collection incident_memory (cosine, 384-d)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qdrant_store import collection_info, ensure_collection, get_client


def main() -> None:
    client = get_client()
    client.get_collections()
    ensure_collection(client)
    info = collection_info(client)
    print("Qdrant reachable")
    print(f"collection: {info.config.params.vectors}")
    print(f"points: {info.points_count}")


if __name__ == "__main__":
    main()
