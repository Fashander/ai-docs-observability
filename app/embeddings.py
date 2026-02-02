from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from typing import List, Sequence

try:
    # Chroma uses this protocol for custom embeddings
    from chromadb.api.types import EmbeddingFunction
except Exception:  # pragma: no cover
    EmbeddingFunction = object  # type: ignore


class HashEmbeddingFunction(EmbeddingFunction):
    """Deterministic, dependency-free embedding function.

    This is *not* semantically meaningful like a transformer embedding,
    but it's perfect for a repo/demo where:
    - you want Chroma wired up end-to-end
    - you don't want to download large ML models
    - you want repeatable results

    We create a fixed-length vector by hashing tokens into buckets.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim

    def __call__(self, texts: Sequence[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            vec = [0.0] * self.dim
            for tok in (text or "").lower().split():
                h = hashlib.sha256(tok.encode("utf-8")).digest()
                idx = int.from_bytes(h[:4], "little") % self.dim
                sign = 1.0 if (h[4] % 2 == 0) else -1.0
                vec[idx] += sign
            # L2 normalize
            norm = sum(x * x for x in vec) ** 0.5
            if norm > 0:
                vec = [x / norm for x in vec]
            vectors.append(vec)
        return vectors


class OllamaEmbeddingFunction(EmbeddingFunction):
    """Ollama-backed embedding function for semantic retrieval."""

    def __init__(self, model: str, base_url: str, timeout_sec: float = 30.0):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    def __call__(self, texts: Sequence[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/embeddings",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            embedding = data.get("embedding")
            if not isinstance(embedding, list):
                raise RuntimeError("Ollama embeddings response missing 'embedding'")
            vectors.append(embedding)
        return vectors


def get_embedding_function() -> EmbeddingFunction:
    provider = os.getenv("EMBEDDING_PROVIDER", "hash").lower()
    if provider == "ollama":
        model = os.getenv("OLLAMA_EMBED_MODEL") or os.getenv("OLLAMA_MODEL")
        if not model:
            raise RuntimeError("OLLAMA_EMBED_MODEL (or OLLAMA_MODEL) is required for Ollama embeddings")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        timeout_sec = float(os.getenv("OLLAMA_TIMEOUT_SEC", "30"))
        return OllamaEmbeddingFunction(model=model, base_url=base_url, timeout_sec=timeout_sec)
    dim = int(os.getenv("EMBED_DIM", "256"))
    return HashEmbeddingFunction(dim=dim)
