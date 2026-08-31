"""Backward-compatible shim; prefer src.settings."""

from src.settings import get_settings

_settings = get_settings()

ROOT = _settings.root
DATA_DIR = _settings.data_dir
QDRANT_URL = _settings.qdrant_url
COLLECTION = _settings.qdrant_collection
EMBEDDING_MODEL = _settings.embedding_model
CHUNK_SIZE = _settings.chunk_size
CHUNK_OVERLAP = _settings.chunk_overlap
HYBRID_ALPHA = _settings.hybrid_alpha
LLM_PROVIDER = _settings.llm_provider
OLLAMA_URL = _settings.ollama_url
OLLAMA_MODEL = _settings.ollama_model
OPENAI_API_KEY = _settings.openai_api_key
OPENAI_MODEL = _settings.openai_model
GEMINI_API_KEY = _settings.gemini_api_key
GEMINI_MODEL = _settings.gemini_model
RERANK_ENABLED = _settings.rerank_enabled
RERANK_MODEL = _settings.rerank_model
RETRIEVAL_MIN_SCORE = _settings.retrieval_min_score
RRF_K = _settings.rrf_k


def _vector_size() -> int:
    from src.deps import get_embedder

    return get_embedder().dim


# Lazy property-like access for tests that import VECTOR_SIZE at module level.
class _VectorSize:
    def __int__(self) -> int:
        return _vector_size()

    def __repr__(self) -> str:
        return str(int(self))


VECTOR_SIZE = _VectorSize()  # type: ignore[assignment]
