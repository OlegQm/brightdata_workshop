"""Hotel refresh orchestration service."""

from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException
from psycopg.types.json import Jsonb

from src.infra.postgresql.repository import PostgresHotelRepository
from src.model.refresh import RefreshResult
from src.service.brightdata import BrightDataService
from src.service.embedding import EmbeddingService


EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\+\d[\d\s()/.-]{7,}\d")


class RefreshService:
    """Refresh existing hotel records from BrightData source URLs."""

    def __init__(
        self,
        repository: PostgresHotelRepository,
        brightdata: BrightDataService,
        embeddings: EmbeddingService,
        batch_size: int,
    ) -> None:
        """Initialise refresh orchestration dependencies."""
        self._repository = repository
        self._brightdata = brightdata
        self._embeddings = embeddings
        self._batch_size = batch_size

    def status(self) -> dict[str, Any]:
        """Return BrightData token state and aggregate refresh metrics."""
        row = self._repository.refresh_status()
        return {
            "token_configured": self._brightdata.token_configured,
            "total": row["total"],
            "refreshed": row["refreshed"],
            "last_refreshed_at": row["last_refreshed_at"].isoformat() if row["last_refreshed_at"] else None,
        }

    async def refresh(self) -> RefreshResult:
        """Refresh all configured hotel source pages through BrightData MCP."""
        if not self._brightdata.token_configured:
            raise HTTPException(status_code=400, detail="BRIGHTDATA_API_TOKEN is not configured")

        updated = 0
        failed = 0
        records = self._repository.select_for_refresh()
        by_url = {record["source_url"]: record for record in records if record.get("source_url")}
        urls = list(by_url)
        for index in range(0, len(urls), self._batch_size):
            batch_urls = urls[index:index + self._batch_size]
            batch = await self._brightdata.scrape_batch(batch_urls)
            for scrape in batch:
                value = scrape.get("value") or {}
                url = value.get("url")
                record = by_url.get(url)
                if not record or scrape.get("status") != "fulfilled":
                    failed += 1
                    continue
                self._repository.update_refreshed(self._update_record_from_scrape(record, scrape))
                updated += 1

        return RefreshResult(
            updated=updated,
            failed=failed,
            token_configured=True,
            message=f"Updated {updated} hotel source(s) from BrightData.",
        )

    def _update_record_from_scrape(self, record: dict[str, Any], scrape: dict[str, Any]) -> dict[str, Any]:
        """Return an updated hotel record based on one BrightData scrape result."""
        value = scrape.get("value") or {}
        content = value.get("content") or ""
        cleaned = self._clean_markdown(content)
        updated = dict(record)
        email = self._first_match(EMAIL_RE, cleaned)
        phone = self._first_match(PHONE_RE, cleaned)
        if email:
            updated["email"] = email
        if phone:
            updated["phone"] = phone
        if cleaned and not updated.get("description"):
            updated["description"] = cleaned[:280]
        updated["source_payload"] = Jsonb(
            {
                "brightdata_url": value.get("url") or record["source_url"],
                "status": scrape.get("status"),
                "content": content,
            }
        )
        embedding_text = f"{self._embeddings.hotel_text(updated)} {cleaned[:1400]}"
        updated["embedding"] = self._embeddings.vector_literal(self._embeddings.embed_text(embedding_text))
        return updated

    def _clean_markdown(self, text: str) -> str:
        """Remove common Markdown syntax and collapse whitespace."""
        text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"[*_`#>]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _first_match(self, pattern: re.Pattern[str], text: str) -> str | None:
        """Return the first regex match from text with trailing punctuation removed."""
        match = pattern.search(text)
        if not match:
            return None
        value = re.sub(r"\s+", " ", match.group(0)).strip()
        return value.rstrip(".,;")
