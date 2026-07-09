# Backend Dependency Injection

`container.py` wires the backend service graph.

It owns:

- logger initialization;
- PostgreSQL pool and repository construction;
- BrightData, embedding, hotel and refresh services;
- internal `llm` HTTP client;
- FastAPI app creation, CORS, static `/data` mount and router registration;
- startup schema creation and shutdown cleanup.

When adding a new backend feature, register its controller/router here after the
service and infra dependencies exist.
