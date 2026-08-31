#!/usr/bin/env python3
"""Experiment 1: MiniLM-L6 vs MiniLM-L12 (both 384-d). Slow: downloads a second model."""
import json

from src.embeddings.embedder import Embedder
from src.eval.metrics import mean_recall, unique_incident_ids
from src.ingestion.chunker import chunk_documents
from src.ingestion.indexer import index_chunks
from src.ingestion.loader import load_documents
from src.retrieval.vector_search import search
from src.settings import get_settings

EVAL_PATH = get_settings().root / "tests" / "eval" / "queries.json"
MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-MiniLM-L12-v2",
]


def main() -> None:
    queries = json.loads(EVAL_PATH.read_text())
    docs = load_documents()
    chunks = chunk_documents(docs, chunk_size=500, overlap=100)
    for model in MODELS:
        embedder = Embedder(model)
        coll = "incident_memory_" + model.split("/")[-1].replace("-", "_")
        index_chunks(chunks, embedder=embedder, collection=coll, recreate=True)
        pairs = []
        for q in queries:
            hits = search(q["query"], top_k=10, embedder=embedder, collection=coll)
            pairs.append((unique_incident_ids(hits), set(q["relevant"])))
        print(f"{model}: R@3={mean_recall(pairs, 3):.3f} R@5={mean_recall(pairs, 5):.3f}")


if __name__ == "__main__":
    main()
