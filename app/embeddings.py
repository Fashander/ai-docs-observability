from __future__ import annotations

import hashlib
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
