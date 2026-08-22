from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL, VECTOR_SIZE


class Embedder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name)

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return [v.tolist() for v in vectors]

    @property
    def dim(self) -> int:
        return VECTOR_SIZE
