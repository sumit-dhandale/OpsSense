# Incident Memory

RAG lab: given a production error snippet, retrieve similar historical incidents.

We build it **one layer at a time**. Current stop: **Step 2 — load documents**.

## Architecture (target)

```mermaid
flowchart TB
  subgraph ingest [Ingestion later]
    MD[Markdown incidents]
    Loader[loader]
    Chunker[chunker]
    Embed[embedder]
    Indexer[indexer]
  end
  subgraph store [Step 1 now]
    Col[Qdrant collection incident_memory]
  end
  MD --> Loader --> Chunker --> Embed --> Indexer --> Col
```

## Step 1 — What a vector database is

Qdrant stores **points**. Each point later will be:

- `id`
- `vector` (a list of floats from an embedding model)
- `payload` (JSON metadata: incident id, service, severity, chunk text)

A **collection** is a named vector space with a fixed size and distance metric. We create `incident_memory` now, empty:

- size **384** — matches `all-MiniLM-L6-v2` in Step 4. Wrong size later = insert errors.
- distance **Cosine** — MiniLM cares about *direction* of meaning, not vector length. Cosine is not a probability.

**ANN / HNSW (high level):** Qdrant does not compare your query to every stored vector once you have many points. It walks a graph of neighbors (HNSW) and returns *approximately* the nearest ones. Fast enough to matter at millions of points; our 20 docs would be fine with brute force. We still use Qdrant so the production shape is visible.

We are **not** embedding or searching yet. Step 1 only proves: Docker Qdrant is up, Python can create the collection.

## Setup and test

Docker must be running (Docker Desktop or similar).

```bash
cd OpsSense   # this repo
docker compose up -d
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup_qdrant.py
pytest tests/test_qdrant_setup.py -v
```

Success looks like: `Qdrant reachable`, collection Cosine size 384, pytest passed.

Dashboard: http://localhost:6333/dashboard

## Step 2 — Document loading

Raw markdown is not a search record. The loader (`src/ingestion/loader.py`) reads `data/incidents/*.md` and returns a **normalized dict**:

```json
{
  "incident_id": "INC-2841",
  "title": "Aerospike Timeout During Peak Traffic",
  "service": "fraud",
  "severity": "SEV1",
  "content": "..."
}
```

**Why preprocess.** Files have headings, blank lines, and human labels (`Fraud Detection` vs `fraud`). Retrieval later needs stable keys for filters and a single `content` string to chunk.

**Why metadata is separate from the body.** `service` and `severity` are exact fields for Qdrant payload filters (Step 7). If you only stuffed them into the embedded text, a query could not reliably say “only SEV1 fraud.” The body still contains those words for semantic search; metadata is the structured copy.

**Why similar incidents.** Several docs mention Aerospike timeouts, payment latency, and pool exhaustion with *different* root causes. That makes retrieval non-trivial later.

Qdrant is unused this step.

```bash
source .venv/bin/activate
python scripts/load_documents.py
pytest tests/test_loader.py -v
```

Expect ~19 documents and parsed `INC-2841` with `service: fraud`.

Stop here. Step 3 is chunking.
