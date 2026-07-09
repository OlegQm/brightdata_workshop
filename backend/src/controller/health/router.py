"""Health router."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    """Return service health."""
    return request.app.state.health_controller.check()
