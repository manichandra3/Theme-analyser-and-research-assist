from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional

import google.generativeai as genai


class Embedder(ABC):
    """Interface for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        ...

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class GeminiEmbedder(Embedder):
    """Google Gemini embedding provider with response caching."""

    def __init__(self, api_key: str, model: str = "embedding-001"):
        genai.configure(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> List[float]:
        return list(self._cached_embed(self.model, text))

    @staticmethod
    @lru_cache(maxsize=8192)
    def _cached_embed(model: str, text: str) -> tuple:
        result = genai.embed_content(model=model, content=text, task_type="retrieval_query")
        return tuple(result["embedding"])

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        try:
            result = genai.embed_content(model=self.model, content=texts, task_type="retrieval_document")
            return [list(e) for e in result["embedding"]]
        except Exception:
            return [list(self.embed(t)) for t in texts]


def get_embedder(api_key: str, model: str = "embedding-001") -> Embedder:
    return GeminiEmbedder(api_key, model)