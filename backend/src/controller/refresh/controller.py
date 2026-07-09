"""BrightData refresh controller."""

from __future__ import annotations

from typing import Any

from src.model.refresh import RefreshResult
from src.service.refresh_service import RefreshService


class RefreshController:
    """HTTP adapter for live hotel refresh operations."""

    def __init__(self, service: RefreshService) -> None:
        """Initialise the controller with the refresh service."""
        self._service = service

    def status(self) -> dict[str, Any]:
        """Return refresh status metrics."""
        return self._service.status()

    async def refresh(self) -> RefreshResult:
        """Run a live BrightData refresh."""
        return await self._service.refresh()
