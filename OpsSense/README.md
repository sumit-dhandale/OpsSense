# Incident Memory (OpsSense)

RAG system for retrieving similar historical production incidents and generating structured investigation guidance.

## Quickstart

```bash
cd OpsSense
docker compose up -d qdrant
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/setup_qdrant.py
python scripts/index_documents.py --recreate   # first run or after schema changes
pytest -m "not integration" -v
uvicorn src.api.main:app --reload --port 8000
```

```bash
curl -s localhost:8000/health
curl -s -X POST localhost:8000/search -H 'content-type: application/json' \
  -d '{"query":"Aerospike timeout during fraud evaluation","top_k":5,"mode":"hybrid"}'
curl -s -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"query":"Why are fraud feature lookups timing out?"}'
```

CLI:

```bash
python scripts/search.py "Aerospike timeout" --mode hybrid
python scripts/ask.py "Why are fraud feature lookups timing out?"
python scripts/run_experiments.py
```

## Docs

- [Step-by-step tutorial](docs/tutorial.md) — original lab walkthrough (Steps 1–13)
- [Architecture](docs/architecture.md) — module map and data flow

## Key changes (v0.2)

- Cached embedder / Qdrant client / BM25 index (no cold-start per request)
- RRF hybrid search + optional cross-encoder rerank (`RERANK_ENABLED`)
- Section-aware chunking with parent-document context in RAG
- Structured JSON `/ask` response with citation validation and retrieval guardrail
- `GET /health`, input validation, safe default `recreate=false` on `/index`

## Layout

```
src/ingestion/     load, chunk, index
src/retrieval/     vector, BM25, RRF hybrid, reranker
src/rag/           structured generator
src/api/main.py    /health, /index, /search, /ask
tests/eval/        gold queries
```
