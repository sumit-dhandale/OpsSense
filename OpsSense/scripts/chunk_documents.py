#!/usr/bin/env python3
"""Show how one incident splits into overlapping chunks."""
import json

from src.ingestion.chunker import chunk_document
from src.ingestion.loader import load_documents
from src.settings import get_settings


def main() -> None:
    settings = get_settings()
    docs = load_documents()
    doc = next(d for d in docs if d["incident_id"] == "INC-2841")
    chunks = chunk_document(doc, chunk_size=40, overlap=8)
    print(
        f"INC-2841 words={len(doc['content'].split())} "
        f"default={settings.chunk_size}/{settings.chunk_overlap}"
    )
    print(f"demo chunks with size=40 overlap=8 -> {len(chunks)} chunks\n")
    for c in chunks:
        words = c["text"].split()
        print(f"{c['chunk_id']} section={c.get('section')} n_words={len(words)}")
        print(f"  first: {words[0]}  last: {words[-1]}")
    keys = ("chunk_id", "incident_id", "section", "service", "severity", "chunk_index")
    print("\nfirst chunk payload:")
    print(json.dumps({k: chunks[0][k] for k in keys}, indent=2))


if __name__ == "__main__":
    main()
