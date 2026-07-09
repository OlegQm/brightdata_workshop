"""Deterministic text embedding helpers used by pgvector search."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any


TOKEN_RE = re.compile(r"[\w']+", re.UNICODE)
EMBEDDING_DIMENSIONS = 384


class EmbeddingService:
    """Create deterministic normalized bag-of-token embeddings."""

    dimensions = EMBEDDING_DIMENSIONS

    def hotel_text(self, record: dict[str, Any]) -> str:
        """Build searchable hotel text from a record dict."""
        return " ".join(
            str(record.get(key) or "")
            for key in ("name", "country", "city", "address", "rating", "description")
        )

    def embed_text(self, text: str) -> list[float]:
        """Return a normalized deterministic vector for *text*."""
        vector = [0.0] * self.dimensions
        tokens = TOKEN_RE.findall(text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if not norm:
            return vector
        return [round(value / norm, 6) for value in vector]

    def vector_literal(self, values: list[float]) -> str:
        """Format a vector for PostgreSQL pgvector casts."""
        return "[" + ",".join(f"{value:.6f}" for value in values) + "]"

    def embed_record_literal(self, record: dict[str, Any]) -> str:
        """Return a pgvector literal for a hotel record."""
        return self.vector_literal(self.embed_text(self.hotel_text(record)))
