"""Health controller."""


class HealthController:
    """Return service health."""

    def check(self) -> dict[str, str]:
        """Return a simple status payload."""
        return {"status": "ok"}
