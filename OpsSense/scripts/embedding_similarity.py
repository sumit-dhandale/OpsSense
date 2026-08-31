#!/usr/bin/env python3
"""Semantic similarity vs keyword overlap on three phrases."""
import numpy as np

from src.deps import get_embedder


def cosine(a, b) -> float:
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def main() -> None:
    texts = [
        "database connection timeout",
        "DB connection pool exhausted",
        "football match tonight",
    ]
    embedder = get_embedder()
    vecs = embedder.embed_batch(texts)
    print(f"model={embedder.model_name} dim={len(vecs[0])}\n")
    for i, ti in enumerate(texts):
        for j, tj in enumerate(texts):
            if j <= i:
                continue
            print(f"cosine({ti!r},\n       {tj!r}) = {cosine(vecs[i], vecs[j]):.3f}")
    print("\nCosine is not a probability. Closer to 1 = more similar direction.")
    print("Qdrant is configured for Cosine because MiniLM is trained for that geometry.")


if __name__ == "__main__":
    main()
