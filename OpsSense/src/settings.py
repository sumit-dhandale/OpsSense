from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    root: Path = Path(__file__).resolve().parents[1]
    data_dir: Path | None = None

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "incident_memory"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    chunk_size: int = 500
    chunk_overlap: int = 100
    hybrid_alpha: float = 0.7
    rrf_k: int = 60

    rerank_enabled: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    retrieval_min_score: float = 0.35

    llm_provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    @field_validator("chunk_size")
    @classmethod
    def chunk_size_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("chunk_size must be > 0")
        return v

    @field_validator("hybrid_alpha")
    @classmethod
    def hybrid_alpha_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("hybrid_alpha must be between 0 and 1")
        return v

    @model_validator(mode="after")
    def validate_overlap(self) -> "Settings":
        if self.chunk_overlap < 0 or self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and < chunk_size")
        if self.data_dir is None:
            self.data_dir = self.root / "data" / "incidents"
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings() -> None:
    get_settings.cache_clear()
