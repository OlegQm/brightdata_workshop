"""Dependency-injection container for the backend service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.config.config import Config
from src.controller.chat.controller import ChatProxyController
from src.controller.chat.router import router as chat_router
from src.controller.health.controller import HealthController
from src.controller.health.router import router as health_router
from src.controller.hotels.controller import HotelsController
from src.controller.hotels.router import router as hotels_router
from src.controller.refresh.controller import RefreshController
from src.controller.refresh.router import router as refresh_router
from src.infra.http.llm_client import LlmClient
from src.infra.postgresql.pool import PostgresPool
from src.infra.postgresql.repository import PostgresHotelRepository
from src.logger.logger import init_logger
from src.service.brightdata import BrightDataService
from src.service.embedding import EmbeddingService
from src.service.hotels_service import HotelsService
from src.service.refresh_service import RefreshService


@dataclass
class Container:
    """Lazy DI container that wires backend infrastructure and controllers."""

    config: Config

    def __post_init__(self) -> None:
        """Initialise logging immediately after container construction."""
        init_logger(self.config.service.log_level)

    @cached_property
    def _postgres_pool(self) -> PostgresPool:
        """Lazily create the PostgreSQL connection factory."""
        logger.debug("Initialising PostgreSQL connection factory")
        return PostgresPool(self.config.db.url)

    @cached_property
    def _llm_client(self) -> LlmClient:
        """Lazily create the internal LLM HTTP client."""
        logger.debug("Initialising LLM client")
        return LlmClient(self.config.llm.url, self.config.llm.timeout_seconds)

    @cached_property
    def _hotel_repository(self) -> PostgresHotelRepository:
        """Lazily construct the hotel repository."""
        return PostgresHotelRepository(
            self._postgres_pool,
            Path(self.config.data.hotels_seed_path),
            self._embedding_service.dimensions,
        )

    @cached_property
    def _embedding_service(self) -> EmbeddingService:
        """Lazily construct the embedding service."""
        return EmbeddingService()

    @cached_property
    def _brightdata_service(self) -> BrightDataService:
        """Lazily construct the BrightData MCP service."""
        return BrightDataService(
            self.config.brightdata.api_token,
            self.config.brightdata.timeout_seconds,
        )

    @cached_property
    def _hotels_service(self) -> HotelsService:
        """Lazily construct the hotel query service."""
        return HotelsService(self._hotel_repository, self._embedding_service)

    @cached_property
    def _refresh_service(self) -> RefreshService:
        """Lazily construct the live refresh service."""
        return RefreshService(
            self._hotel_repository,
            self._brightdata_service,
            self._embedding_service,
            self.config.brightdata.batch_size,
        )

    @cached_property
    def health_controller(self) -> HealthController:
        """Lazily construct the health controller."""
        return HealthController()

    @cached_property
    def hotels_controller(self) -> HotelsController:
        """Lazily construct the hotels controller."""
        return HotelsController(self._hotels_service)

    @cached_property
    def refresh_controller(self) -> RefreshController:
        """Lazily construct the refresh controller."""
        return RefreshController(self._refresh_service)

    @cached_property
    def chat_proxy_controller(self) -> ChatProxyController:
        """Lazily construct the chat proxy controller."""
        return ChatProxyController(self._llm_client)

    @property
    def app(self) -> FastAPI:
        """Build and return a configured FastAPI application."""
        container = self

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            """Initialise schema, expose controllers, and clean up clients."""
            logger.info("Backend startup")
            container._hotels_service.ensure_schema()
            app.state.health_controller = container.health_controller
            app.state.hotels_controller = container.hotels_controller
            app.state.refresh_controller = container.refresh_controller
            app.state.chat_proxy_controller = container.chat_proxy_controller
            try:
                yield
            finally:
                if "_llm_client" in container.__dict__:
                    await container._llm_client.close()
                logger.info("Backend shutdown")

        application = FastAPI(
            title="CZ/SK Hotels API",
            version="1.0.0",
            lifespan=lifespan,
        )
        application.add_middleware(
            CORSMiddleware,
            allow_origins=container.config.cors.allow_origins,
            allow_credentials=True,
            allow_methods=container.config.cors.allow_methods,
            allow_headers=container.config.cors.allow_headers,
        )
        application.mount(
            "/data",
            StaticFiles(directory=container.config.data.root),
            name="data",
        )
        application.include_router(health_router)
        application.include_router(refresh_router)
        application.include_router(hotels_router)
        application.include_router(chat_router)
        return application
