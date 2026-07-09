"""Application entry point for the LLM service."""

from __future__ import annotations

import uvicorn
from loguru import logger

from src.config.config import Config
from src.di.container import Container


def build_app():
    """Build and return the FastAPI app through the DI container."""
    return Container(config=Config()).app


def main() -> int:
    """Load config, build the ASGI app, and run uvicorn."""
    config = Config()
    logger.info("Starting LLM service on {}:{}", config.http.host, config.http.port)
    app = Container(config=config).app
    uvicorn.run(app, host=config.http.host, port=config.http.port, log_config=None)
    return 0
