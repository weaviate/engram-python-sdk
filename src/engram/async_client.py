from __future__ import annotations

from collections.abc import Mapping

import httpx

from ._base_client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, _BaseClient

__all__ = ["DEFAULT_BASE_URL", "DEFAULT_TIMEOUT", "AsyncEngramClient"]


class AsyncEngramClient(_BaseClient):
    """Asynchronous Engram client"""

    _http_client: httpx.AsyncClient

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
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> AsyncEngramClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.aclose()
