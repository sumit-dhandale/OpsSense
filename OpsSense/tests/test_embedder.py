import numpy as np

from src.embeddings.embedder import Embedder


def cosine(a, b) -> float:
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def test_semantic_vs_keyword():
    embedder = Embedder()
    a, b, c = embedder.embed_batch(
        [
            "database connection timeout",
            "DB connection pool exhausted",
            "football match tonight",
        ]
    )
    assert len(a) == 384
    assert cosine(a, b) > cosine(a, c)
    assert cosine(a, b) > cosine(b, c)
