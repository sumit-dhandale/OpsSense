#!/usr/bin/env python3
"""Experiments 3–6 on the existing incident_memory index (run index_documents.py first)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ROOT
from src.eval.metrics import mean_recall, unique_incident_ids
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.keyword_search import keyword_search
from src.retrieval.vector_search import search

EVAL_PATH = ROOT / "tests" / "eval" / "queries.json"


def _pairs(search_fn, queries, k=10, **kwargs):
    out = []
    for q in queries:
        hits = search_fn(q["query"], top_k=k, **kwargs)
        out.append((unique_incident_ids(hits), set(q["relevant"])))
    return out


def main() -> None:
    queries = json.loads(EVAL_PATH.read_text())

    print("=== Experiment 3: top-k (vector, incident-id recall) ===")
    pairs = _pairs(search, queries, k=10)
    for k in (1, 3, 5, 10):
        print(f"  Recall@{k}: {mean_recall(pairs, k):.3f}")

    print("\n=== Experiment 4: score threshold (vector, top 10) ===")
    for thr in (None, 0.3, 0.5, 0.7):
        pairs_t = []
        for q in queries:
            hits = search(q["query"], top_k=10, score_threshold=thr)
            pairs_t.append((unique_incident_ids(hits), set(q["relevant"])))
        n = sum(len(ids) for ids, _ in pairs_t) / len(pairs_t)
        print(
            f"  threshold={thr}: mean unique ids={n:.2f}  "
            f"Recall@5={mean_recall(pairs_t, 5):.3f}"
        )

    print("\n=== Experiment 5: keyword vs vector vs hybrid ===")
    for name, fn, extra in (
        ("keyword", keyword_search, {}),
        ("vector", search, {}),
        ("hybrid a=0.7", hybrid_search, {"alpha": 0.7}),
        ("hybrid a=0.5", hybrid_search, {"alpha": 0.5}),
    ):
        p = _pairs(fn, queries, k=10, **extra)
        print(f"  {name:16} R@3={mean_recall(p, 3):.3f}  R@5={mean_recall(p, 5):.3f}")

    print("\n=== Experiment 6: metadata filter service=fraud ===")
    fraud_q = [
        q
        for q in queries
        if "INC-2841" in q["relevant"] or "INC-1923" in q["relevant"]
    ]
    p_off = _pairs(search, fraud_q, k=5)
    p_on = _pairs(search, fraud_q, k=5, filters={"service": "fraud"})
    print(f"  unfiltered R@5={mean_recall(p_off, 5):.3f}")
    print(f"  service=fraud R@5={mean_recall(p_on, 5):.3f}")

    demo = "Aerospike timeout"
    print(f"\n=== demo query: {demo!r} ===")
    print("vector:  ", [h["incident_id"] for h in search(demo, top_k=5)])
    print("keyword: ", [h["incident_id"] for h in keyword_search(demo, top_k=5)])
    print("hybrid:  ", [h["incident_id"] for h in hybrid_search(demo, top_k=5)])
    print(
        "filter fraud+SEV1:",
        [
            h["incident_id"]
            for h in search(
                demo, top_k=5, filters={"service": "fraud", "severity": "SEV1"}
            )
        ],
    )


if __name__ == "__main__":
    main()
