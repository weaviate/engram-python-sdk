from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from ._base_client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, _BaseClient
from ._http import AsyncHttpTransport
from ._resources import AsyncMemories, AsyncRuns

__all__ = ["DEFAULT_BASE_URL", "DEFAULT_TIMEOUT", "AsyncEngramClient"]


class AsyncEngramClient(_BaseClient):
    """Asynchronous Engram client."""

    _transport: AsyncHttpTransport
    memories: AsyncMemories
    runs: AsyncRuns

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            headers=headers,
            timeout=timeout,
        )
        self._owns_http_client = http_client is None
        http = http_client or httpx.AsyncClient(timeout=timeout)
        self._transport = AsyncHttpTransport(self._config, http)
        self.memories = AsyncMemories(self._transport)
        self.runs = AsyncRuns(self._transport)

    def build_request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Request:
        return self._transport.build_request(
            method, path, headers=headers, params=params, json=json
        )

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self._transport._http_client.aclose()

    async def __aenter__(self) -> AsyncEngramClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.aclose()
