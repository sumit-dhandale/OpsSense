#!/usr/bin/env python3
"""Recall@3/@5 vs chunk size 200 / 500 / 1000 (overlap 20% of size).

Uses collection incident_memory_eval so it does not wipe your Step 5 index.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ROOT
from src.embeddings.embedder import Embedder
from src.eval.metrics import mean_recall, unique_incident_ids
from src.ingestion.chunker import chunk_documents
from src.ingestion.indexer import index_chunks
from src.ingestion.loader import load_documents
from src.retrieval.vector_search import search

EVAL_PATH = ROOT / "tests" / "eval" / "queries.json"
COLLECTION = "incident_memory_eval"


def run_chunk_eval() -> list[dict]:
    queries = json.loads(EVAL_PATH.read_text())
    docs = load_documents()
    embedder = Embedder()
    rows = []
    for size in (200, 500, 1000):
        overlap = max(1, size // 5)
        chunks = chunk_documents(docs, chunk_size=size, overlap=overlap)
        index_chunks(chunks, embedder=embedder, collection=COLLECTION, recreate=True)
        pairs = []
        for q in queries:
            hits = search(
                q["query"], top_k=10, embedder=embedder, collection=COLLECTION
            )
            pairs.append((unique_incident_ids(hits), set(q["relevant"])))
        rows.append(
            {
                "chunk_size": size,
                "overlap": overlap,
                "chunks": len(chunks),
                "recall@3": round(mean_recall(pairs, 3), 3),
                "recall@5": round(mean_recall(pairs, 5), 3),
            }
        )
    return rows


def main() -> None:
    table = run_chunk_eval()
    print(f"{'chunk':>8} {'overlap':>8} {'n':>6} {'R@3':>8} {'R@5':>8}")
    for r in table:
        print(
            f"{r['chunk_size']:>8} {r['overlap']:>8} {r['chunks']:>6} "
            f"{r['recall@3']:>8.3f} {r['recall@5']:>8.3f}"
        )


if __name__ == "__main__":
    main()
