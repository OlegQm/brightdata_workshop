# Backend Infrastructure

Adapters for systems outside backend business logic.

Subdirectories:

- `postgresql/` - database connection factory and hotel repository.
- `http/` - internal HTTP clients, currently the LLM service client.

Services should depend on these adapters through clear methods, not raw SQL or
HTTP calls scattered through controllers.
