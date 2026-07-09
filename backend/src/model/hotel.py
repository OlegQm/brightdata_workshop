"""Hotel domain models."""

from __future__ import annotations

from pydantic import BaseModel


class Hotel(BaseModel):
    """Public hotel representation returned by the API."""

    id: str
    name: str
    country: str
    city: str
    address: str
    latitude: float
    longitude: float
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    rating: str | None = None
    description: str | None = None
    source_url: str
    source_kind: str = "brightdata"
