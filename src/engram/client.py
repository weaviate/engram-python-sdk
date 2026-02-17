from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from ._base_client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, _BaseClient
from ._http import HttpTransport
from ._resources import Memories, Runs

__all__ = ["DEFAULT_BASE_URL", "DEFAULT_TIMEOUT", "EngramClient"]


class EngramClient(_BaseClient):
    """Synchronous Engram client."""

    _transport: HttpTransport
    memories: Memories
    runs: Runs

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            headers=headers,
            timeout=timeout,
        )
        self._owns_http_client = http_client is None
        http = http_client or httpx.Client(timeout=timeout)
        self._transport = HttpTransport(self._config, http)
        self.memories = Memories(self._transport)
        self.runs = Runs(self._transport)

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

    def close(self) -> None:
        if self._owns_http_client:
            self._transport._http_client.close()

    def __enter__(self) -> EngramClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
