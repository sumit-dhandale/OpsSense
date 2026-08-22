#!/usr/bin/env python3
"""Vector search: python scripts/search.py 'Aerospike timeout during fraud evaluation'"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.retrieval.vector_search import search


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--top-k", type=int, default=5)
    args = p.parse_args()
    hits = search(args.query, top_k=args.top_k)
    for i, hit in enumerate(hits, 1):
        print(
            f"{i}. {hit['incident_id']} — {hit['title']}  "
            f"score={hit['score']:.3f}  {hit.get('service')} {hit.get('severity')}"
        )
        snippet = (hit.get("text") or "").replace("\n", " ")[:180]
        print(f"   {snippet}...\n")
    print(json.dumps([{"score": h["score"], "incident_id": h["incident_id"], "title": h["title"]} for h in hits], indent=2))


if __name__ == "__main__":
    main()
