from src.ingestion.chunker import chunk_document, chunk_text
from src.ingestion.loader import load_documents


def test_chunk_size_and_overlap():
    tokens = [f"w{i}" for i in range(120)]
    chunks = chunk_text(" ".join(tokens), chunk_size=50, overlap=10)
    assert len(chunks[0].split()) == 50
    assert chunks[1].split()[0] == "w40"


def test_chunk_preserves_metadata():
    doc = {
        "incident_id": "INC-2841",
        "title": "Aerospike Timeout",
        "service": "fraud",
        "severity": "SEV1",
        "content": " ".join(["token"] * 20),
    }
    chunks = chunk_document(doc, chunk_size=8, overlap=2)
    assert chunks[0]["incident_id"] == "INC-2841"
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_id"] == "INC-2841:1"
    assert chunks[0]["service"] == "fraud"
    assert chunks[0]["severity"] == "SEV1"


def test_real_docs_fit_default_window():
    docs = load_documents()
    from src.ingestion.chunker import chunk_documents

    chunks = chunk_documents(docs)
    assert chunks
    for c in chunks:
        assert len(c["text"].split()) <= 500
        assert c["incident_id"] and c["text"]
