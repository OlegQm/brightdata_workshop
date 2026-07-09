# LLM Dependency Injection

`container.py` wires the LLM service graph.

It owns:

- logger initialization;
- MCP client construction;
- chat service construction;
- FastAPI app creation, CORS and router registration;
- health endpoint registration.

Add new LLM dependencies here rather than constructing them inside routers.
