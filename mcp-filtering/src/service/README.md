# MCP Filtering Services

Reserved package for service-level orchestration in the MCP filtering service.

Current tool behavior is small enough to live in `controller/tools`, while SQL
filtering lives in `infra/postgresql`. Add service objects here when tool logic
starts coordinating multiple repositories or external systems.
