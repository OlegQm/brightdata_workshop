"""Hotel query service."""

from __future__ import annotations

from fastapi import HTTPException

from src.infra.postgresql.repository import PostgresHotelRepository
from src.model.hotel import Hotel
from src.service.embedding import EmbeddingService


class HotelsService:
    """Application service for hotel search and lookup."""

    def __init__(self, repository: PostgresHotelRepository, embeddings: EmbeddingService) -> None:
        """Initialise the service with its repository and embedding dependency."""
        self._repository = repository
        self._embeddings = embeddings

    def ensure_schema(self) -> None:
        """Create database schema and seed records when needed."""
        self._repository.ensure_schema(self._embeddings.embed_record_literal)

    def list_hotels(self, q: str | None, country: str | None) -> list[Hotel]:
        """Return hotels filtered by country and optionally ranked by query."""
        query_embedding = None
        if q:
            query_embedding = self._embeddings.vector_literal(self._embeddings.embed_text(q))
        return self._repository.list(country=country, query_embedding=query_embedding)

    def get_hotel(self, hotel_id: str) -> Hotel:
        """Return one hotel or raise a 404 HTTP error."""
        hotel = self._repository.get(hotel_id)
        if hotel is None:
            raise HTTPException(status_code=404, detail="Hotel not found")
        return hotel
