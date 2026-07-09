"""Application configuration loaded from environment variables and ``.env``."""

from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import LogLevel

_BASE_PREFIX = "BACKEND__"


class Db(BaseSettings):
    """PostgreSQL connection settings."""

    url: str = "postgresql://hotels:hotels@postgres:5432/hotels"


class Data(BaseSettings):
    """Local data file and static directory settings."""

    root: str = "/app/data"
    hotels_seed_path: str = "/app/data/hotels_seed.json"


class BrightData(BaseSettings):
    """BrightData MCP settings used for live hotel refresh."""

    api_token: str = ""
    batch_size: int = 5
    timeout_seconds: float = 120.0


class Llm(BaseSettings):
    """Internal LLM service settings used by the chat proxy."""

    url: str = "http://llm:8003/api"
    timeout_seconds: float = 120.0


class Http(BaseSettings):
    """HTTP server binding settings."""

    host: str = "0.0.0.0"
    port: int = 8002


class Cors(BaseSettings):
    """CORS middleware settings."""

    allow_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


class Service(BaseSettings):
    """General backend service settings."""

    log_level: LogLevel = LogLevel.INFO


class Config(BaseSettings):
    """Root backend configuration object.

    Values can be overridden using ``BACKEND__`` nested environment variables,
    while legacy compose variables are still read in ``model_post_init``.
    """

    db: Db = Db()
    data: Data = Data()
    brightdata: BrightData = BrightData()
    llm: Llm = Llm()
    http: Http = Http()
    cors: Cors = Cors()
    service: Service = Service()

    model_config = SettingsConfigDict(
        env_prefix=_BASE_PREFIX,
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    def model_post_init(self, __context: object) -> None:
        """Apply legacy environment variables used by the current compose file."""
        if os.getenv("DATABASE_URL"):
            self.db.url = os.environ["DATABASE_URL"]
        if os.getenv("HOTELS_SEED_PATH"):
            self.data.hotels_seed_path = os.environ["HOTELS_SEED_PATH"]
        if os.getenv("BRIGHTDATA_API_TOKEN"):
            self.brightdata.api_token = os.environ["BRIGHTDATA_API_TOKEN"]
        if os.getenv("LLM_URL"):
            self.llm.url = os.environ["LLM_URL"]
