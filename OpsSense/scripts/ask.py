#!/usr/bin/env python3
"""RAG: retrieve then ask the configured LLM (default Ollama)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag.generator import ask


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--vector-only", action="store_true")
    p.add_argument("--alpha", type=float, default=None)
    p.add_argument("--provider", default=None, help="ollama | openai | gemini")
    args = p.parse_args()
    result = ask(
        args.query,
        top_k=args.top_k,
        use_hybrid=not args.vector_only,
        alpha=args.alpha,
        provider=args.provider,
    )
    print("=== sources ===")
    for i, hit in enumerate(result["sources"], 1):
        print(f"{i}. {hit['incident_id']} — {hit['title']}  score={hit['score']:.3f}")
    print("\n=== answer ===\n")
    print(result["answer"])


if __name__ == "__main__":
    main()
