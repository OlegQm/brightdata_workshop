# Backend Source

Layered backend implementation.

Directory map:

- `app.py` and `__main__.py` - application startup.
- `config/` - Pydantic settings and environment compatibility.
- `di/` - dependency injection and FastAPI wiring.
- `controller/` - HTTP routers and thin request handlers.
- `model/` - Pydantic response/domain models.
- `service/` - application business logic.
- `infra/` - PostgreSQL and internal HTTP adapters.
- `logger/` - shared loguru setup.

Keep route parsing in `controller/`, orchestration in `service/`, and external
systems in `infra/`.
