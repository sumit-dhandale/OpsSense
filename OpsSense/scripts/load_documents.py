#!/usr/bin/env python3
"""Print one parsed incident to verify the loader."""
import json

from src.ingestion.loader import load_documents


def main() -> None:
    docs = load_documents()
    if not docs:
        raise SystemExit("no markdown files in data/incidents/")
    print(f"loaded {len(docs)} documents\n")
    sample = docs[0]
    print(
        json.dumps(
            {k: sample[k] for k in ("incident_id", "title", "date", "service", "severity")},
            indent=2,
        )
    )
    print("\n--- content (first 400 chars) ---\n")
    print(sample["content"][:400])


if __name__ == "__main__":
    main()
