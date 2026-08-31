from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.deps import get_keyword_index, invalidate_keyword_index, warm_dependencies
from src.ingestion.indexer import index_documents
from src.logging_config import setup_logging
from src.qdrant_store import collection_info
from src.rag.generator import ask as rag_ask
from src.retrieval.filters import ALLOWED_FILTER_KEYS, normalize_filters
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.vector_search import search as vector_search
from src.settings import get_settings

setup_logging()


class SearchFilters(BaseModel):
    service: str | None = None
    severity: str | None = None
    incident_id: str | None = None

    def to_dict(self) -> dict | None:
        raw = {
            k: v
            for k, v in self.model_dump().items()
            if k in ALLOWED_FILTER_KEYS and v not in (None, "")
        }
        return raw or None


class IndexBody(BaseModel):
    recreate: bool = False


class SearchBody(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: SearchFilters | None = None
    mode: Literal["vector", "hybrid"] = "vector"
    alpha: float | None = Field(default=None, ge=0.0, le=1.0)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class AskBody(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: SearchFilters | None = None
    use_hybrid: bool = True
    alpha: float | None = Field(default=None, ge=0.0, le=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    warm_dependencies()
    yield


app = FastAPI(title="Incident Memory", lifespan=lifespan)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_request: Request, exc: RuntimeError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health():
    settings = get_settings()
    qdrant_ok = False
    points = 0
    try:
        info = collection_info()
        qdrant_ok = info is not None
        if info:
            points = info.points_count or 0
    except Exception:
        qdrant_ok = False
    return {
        "status": "ok" if qdrant_ok else "degraded",
        "qdrant": qdrant_ok,
        "collection_points": points,
        "embedding_model": settings.embedding_model,
    }


@app.post("/index")
def index_all(body: IndexBody = IndexBody()):
    n = index_documents(recreate=body.recreate)
    invalidate_keyword_index()
    get_keyword_index()
    return {"indexed_chunks": n}


@app.post("/search")
def search(body: SearchBody):
    filters = normalize_filters(body.filters.to_dict() if body.filters else None)
    if body.mode == "hybrid":
        hits = hybrid_search(
            body.query, top_k=body.top_k, alpha=body.alpha, filters=filters
        )
    else:
        hits = vector_search(
            body.query,
            top_k=body.top_k,
            filters=filters,
            score_threshold=body.score_threshold,
        )
    return {"results": hits}


@app.post("/ask")
def ask(body: AskBody):
    filters = normalize_filters(body.filters.to_dict() if body.filters else None)
    return rag_ask(
        body.query,
        top_k=body.top_k,
        use_hybrid=body.use_hybrid,
        alpha=body.alpha,
        filters=filters,
    )
