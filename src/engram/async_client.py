from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from .errors import ValidationError
from .types import ClientConfig
from .version import __version__

DEFAULT_BASE_URL = "https://api.engram.weaviate.io"
DEFAULT_TIMEOUT = 30.0


class AsyncEngramClient:
    """Asynchronous Engram client"""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValidationError("Timeout must be greater than 0.")

        normalized_base_url = base_url.rstrip("/")
        header_overrides = dict(headers) if headers is not None else {}
        default_headers = _build_headers(api_key=api_key, header_overrides=header_overrides)

        self._config = ClientConfig(
            base_url=normalized_base_url,
            timeout=timeout,
            headers=dict(default_headers),
            api_key=api_key,
        )
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(timeout=timeout)

    @property
    def config(self) -> ClientConfig:
        return self._config

    @property
    def default_headers(self) -> dict[str, str]:
        return dict(self._config.headers)

    def build_request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Request:
        merged_headers = self.default_headers
        if headers:
            merged_headers.update(dict(headers))

        return self._http_client.build_request(
            method=method,
            url=_build_url(self._config.base_url, path),
            headers=merged_headers,
            params=params,
            json=json,
        )

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> AsyncEngramClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.aclose()


def _build_headers(
    *,
    api_key: str | None,
    header_overrides: Mapping[str, str],
) -> dict[str, str]:
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"weaviate-engram/{__version__}",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    headers.update(dict(header_overrides))
    return headers


def _build_url(base_url: str, path: str) -> str:
    clean_path = path.lstrip("/")
    if not clean_path:
        return base_url
    return f"{base_url}/{clean_path}"
