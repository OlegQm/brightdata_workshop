"""Hotels controller."""

from __future__ import annotations

from src.model.hotel import Hotel
from src.service.hotels_service import HotelsService


class HotelsController:
    """HTTP adapter for hotel query use cases."""

    def __init__(self, service: HotelsService) -> None:
        """Initialise the controller with the hotel service."""
        self._service = service

    def list_hotels(self, q: str | None, country: str | None) -> list[Hotel]:
        """Return hotels matching optional search parameters."""
        return self._service.list_hotels(q=q, country=country)

    def get_hotel(self, hotel_id: str) -> Hotel:
        """Return a single hotel by id."""
        return self._service.get_hotel(hotel_id)
