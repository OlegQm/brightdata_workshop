"""Hotels router."""

from fastapi import APIRouter, Query, Request

from src.model.hotel import Hotel

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.get("", response_model=list[Hotel])
def list_hotels(
    request: Request,
    q: str | None = Query(default=None),
    country: str | None = Query(default=None),
) -> list[Hotel]:
    """Return hotels matching optional query and country filters."""
    return request.app.state.hotels_controller.list_hotels(q=q, country=country)


@router.get("/{hotel_id}", response_model=Hotel)
def get_hotel(request: Request, hotel_id: str) -> Hotel:
    """Return one hotel by id."""
    return request.app.state.hotels_controller.get_hotel(hotel_id)
