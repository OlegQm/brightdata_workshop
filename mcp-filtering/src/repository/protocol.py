"""Abstract repository protocols for hotel filtering."""

from __future__ import annotations

from typing import Protocol


class HotelRepository(Protocol):
    """Protocol for reading collected hotel records."""

    def search(self, filters: dict) -> list[dict]:
        """Return hotels matching arbitrary filters."""
        ...

    def facets(self) -> dict:
        """Return available filter facets."""
        ...
