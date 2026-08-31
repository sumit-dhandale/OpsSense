#!/usr/bin/env python3
"""RAG: retrieve then ask the configured LLM (default Ollama)."""
import argparse
import json

from src.rag.generator import ask


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--vector-only", action="store_true")
    p.add_argument("--alpha", type=float, default=None)
    p.add_argument("--provider", default=None, help="ollama | openai | gemini")
    p.add_argument("--json", action="store_true", help="print raw JSON response")
    args = p.parse_args()
    result = ask(
        args.query,
        top_k=args.top_k,
        use_hybrid=not args.vector_only,
        alpha=args.alpha,
        provider=args.provider,
    )
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print("=== sources ===")
    for i, hit in enumerate(result["sources"], 1):
        print(f"{i}. {hit['incident_id']} — {hit['title']}  score={hit['score']:.3f}")
    if result.get("insufficient_evidence"):
        print("\n=== insufficient historical evidence ===")
        return
    print("\n=== similar incidents ===")
    for item in result.get("similar_incidents", []):
        print(f"- {item['incident_id']}: {item['similarity']}")
    print("\n=== investigation areas ===")
    for area in result.get("investigation_areas", []):
        print(f"- {area}")
    print("\n=== hypotheses ===")
    for hyp in result.get("hypotheses", []):
        print(f"- {hyp}")


if __name__ == "__main__":
    main()
