from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from .errors import ValidationError
from .types import ClientConfig
from .version import __version__

DEFAULT_BASE_URL = "https://api.engram.weaviate.io"
DEFAULT_TIMEOUT = 30.0


class _BaseClient:
    """Shared client behavior for sync and async clients."""

    _http_client: httpx.Client | httpx.AsyncClient
    _owns_http_client: bool

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if timeout <= 0:
            raise ValidationError("Timeout must be greater than 0.")

        normalized_base_url = base_url.rstrip("/")
        header_overrides = headers if headers is not None else {}
        default_headers = _build_headers(api_key=api_key, header_overrides=header_overrides)

        self._config = ClientConfig(
            base_url=normalized_base_url,
            timeout=timeout,
            headers=default_headers,
            api_key=api_key,
        )

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
            merged_headers.update(headers)

        return self._http_client.build_request(
            method=method,
            url=_build_url(self._config.base_url, path),
            headers=merged_headers,
            params=params,
            json=json,
        )


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
    headers.update(header_overrides)
    return headers


def _build_url(base_url: str, path: str) -> str:
    clean_path = path.lstrip("/")
    if not clean_path:
        return base_url
    return f"{base_url}/{clean_path}"
