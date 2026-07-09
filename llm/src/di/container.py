"""Dependency-injection container for the LLM service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.config.config import Config
from src.controller.chat.controller import ChatController
from src.controller.chat.router import router as chat_router
from src.infra.mcp.client import build_mcp_client
from src.logger.logger import init_logger
from src.service.chat.chat_service import ChatService


@dataclass
class Container:
    """Lazy DI container for the LLM service."""

    config: Config

    def __post_init__(self) -> None:
        """Initialise logging after construction."""
        init_logger(self.config.service.log_level)

    @cached_property
    def _mcp_client(self):
        """Lazily construct the shared MCP client."""
        return build_mcp_client(self.config)

    @cached_property
    def _chat_service(self) -> ChatService:
        """Lazily construct the chat service."""
        return ChatService(self.config, self._mcp_client)

    @cached_property
    def chat_controller(self) -> ChatController:
        """Lazily construct the chat controller."""
        return ChatController(self._chat_service)

    @property
    def app(self) -> FastAPI:
        """Build and return a configured FastAPI app."""
        container = self

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            """Attach controllers to app state."""
            logger.info("LLM service startup")
            app.state.chat_controller = container.chat_controller
            yield
            logger.info("LLM service shutdown")

        application = FastAPI(title="CZ/SK Hotels LLM", lifespan=lifespan)
        application.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @application.get("/health")
        def health() -> dict[str, str]:
            """Return service health."""
            return {"status": "ok"}

        application.include_router(chat_router)
        return application
