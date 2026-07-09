# Backend Health Controller

Health endpoint for Docker, local checks and quick service diagnostics.

`router.py` exposes `GET /health`; `controller.py` returns the small response
object. Avoid adding dependency-heavy checks here unless compose healthchecks
need them.
