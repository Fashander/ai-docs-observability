from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

from .embeddings import HashEmbeddingFunction

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_data")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "docs")

_embed = HashEmbeddingFunction(dim=int(os.getenv("EMBED_DIM", "256")))


def get_collection():
    os.makedirs(PERSIST_DIR, exist_ok=True)
    client = chromadb.PersistentClient(
        path=PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embed,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_docs(docs: List[Dict[str, Any]]) -> None:
    col = get_collection()
    col.upsert(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[d["meta"] for d in docs],
    )


def query(text: str, n_results: int = 4) -> List[Dict[str, Any]]:
    col = get_collection()
    res = col.query(
        query_texts=[text],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    out: List[Dict[str, Any]] = []
    for i in range(len(res["ids"][0])):
        out.append(
            {
                "id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "meta": res["metadatas"][0][i],
                "distance": res["distances"][0][i],
            }
        )
    return out
