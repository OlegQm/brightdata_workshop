"""BrightData refresh router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from src.model.refresh import RefreshResult

router = APIRouter(prefix="/api/hotels/refresh", tags=["refresh"])


@router.get("/status")
def refresh_status(request: Request) -> dict[str, Any]:
    """Return current refresh status metrics."""
    return request.app.state.refresh_controller.status()


@router.post("", response_model=RefreshResult)
async def refresh_hotels(request: Request) -> RefreshResult:
    """Refresh hotel records through BrightData MCP."""
    return await request.app.state.refresh_controller.refresh()
