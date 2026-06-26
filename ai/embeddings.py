from __future__ import annotations

import hashlib
from functools import lru_cache

import numpy as np

from backend.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def _fallback_embedding(text: str, dimension: int = 384) -> np.ndarray:
    vector = np.zeros(dimension, dtype=np.float32)
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "little") % dimension
        vector[index] += 1.0
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector


def embed_text(text: str) -> np.ndarray:
    text = text.strip()
    if not text:
        return np.zeros(384, dtype=np.float32)
    try:
        return np.asarray(_load_model().encode(text), dtype=np.float32)
    except Exception:
        return _fallback_embedding(text)


def photo_embedding_text(caption: str, objects: list[str], people: list[str], date: str | None, location: str | None) -> str:
    return " ".join(
        part
        for part in [
            caption,
            " ".join(objects),
            " ".join(people),
            date or "",
            location or "",
        ]
        if part
    )
