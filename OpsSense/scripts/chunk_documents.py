#!/usr/bin/env python3
"""Show how one incident splits into overlapping chunks."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import CHUNK_OVERLAP, CHUNK_SIZE
from src.ingestion.chunker import chunk_document
from src.ingestion.loader import load_documents


def main() -> None:
    docs = load_documents()
    doc = next(d for d in docs if d["incident_id"] == "INC-2841")
    # Tiny windows so you can see overlap on a short postmortem.
    chunks = chunk_document(doc, chunk_size=40, overlap=8)
    print(f"INC-2841 words={len(doc['content'].split())} default={CHUNK_SIZE}/{CHUNK_OVERLAP}")
    print(f"demo chunks with size=40 overlap=8 -> {len(chunks)} chunks\n")
    for c in chunks:
        words = c["text"].split()
        print(f"{c['chunk_id']} service={c['service']} n_words={len(words)}")
        print(f"  first: {words[0]}  last: {words[-1]}")
    print("\nfirst chunk payload:")
    print(json.dumps({k: chunks[0][k] for k in ("chunk_id", "incident_id", "service", "severity", "chunk_index")}, indent=2))


if __name__ == "__main__":
    main()
