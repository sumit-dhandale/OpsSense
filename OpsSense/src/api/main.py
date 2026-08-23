from pydantic import BaseModel, Field

from src.ingestion.indexer import index_documents
from src.rag.generator import ask as rag_ask
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.vector_search import search as vector_search

from fastapi import FastAPI

app = FastAPI(title="Incident Memory")


class SearchBody(BaseModel):
    query: str
    top_k: int = 5
    filters: dict | None = None
    mode: str = Field(default="vector", description="vector | hybrid")
    alpha: float | None = None
    score_threshold: float | None = None


class AskBody(BaseModel):
    query: str
    top_k: int = 5
    filters: dict | None = None
    use_hybrid: bool = True
    alpha: float | None = None


@app.post("/index")
def index_all():
    n = index_documents()
    return {"indexed_chunks": n}


@app.post("/search")
def search(body: SearchBody):
    if body.mode == "hybrid":
        hits = hybrid_search(
            body.query, top_k=body.top_k, alpha=body.alpha, filters=body.filters
        )
    else:
        hits = vector_search(
            body.query,
            top_k=body.top_k,
            filters=body.filters,
            score_threshold=body.score_threshold,
        )
    return {"results": hits}


@app.post("/ask")
def ask(body: AskBody):
    return rag_ask(
        body.query,
        top_k=body.top_k,
        use_hybrid=body.use_hybrid,
        alpha=body.alpha,
        filters=body.filters,
    )
