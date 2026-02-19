from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from .errors import APIError, AuthenticationError, NotFoundError
from .errors import ConnectionError as EngramConnectionError
from .types import ClientConfig


class HttpTransport:
    """Wraps a sync httpx.Client and handles request building and response processing."""

    def __init__(self, config: ClientConfig, http_client: httpx.Client | None = None) -> None:
        self._config = config
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(timeout=config.timeout)

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        req = self.build_request(method, path, params=params, json=json)
        try:
            response = self._http_client.send(req)
        except httpx.ConnectError as exc:
            raise EngramConnectionError(str(exc)) from exc
        return _process_response(response)

    def build_request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Request:
        merged_headers = dict(self._config.headers)
        if headers:
            merged_headers.update(headers)
        clean_path = path.lstrip("/")
        url = f"{self._config.base_url}/{clean_path}" if clean_path else self._config.base_url
        return self._http_client.build_request(
            method=method,
            url=url,
            headers=merged_headers,
            params=params,
            json=json,
        )


class AsyncHttpTransport:
    """Wraps an async httpx.AsyncClient and handles request building and response processing."""

    def __init__(self, config: ClientConfig, http_client: httpx.AsyncClient | None = None) -> None:
        self._config = config
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(timeout=config.timeout)

    async def close(self) -> None:
        if self._owns_http_client:
            await self._http_client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        req = self.build_request(method, path, params=params, json=json)
        try:
            response = await self._http_client.send(req)
        except httpx.ConnectError as exc:
            raise EngramConnectionError(str(exc)) from exc
        return _process_response(response)

    def build_request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Request:
        merged_headers = dict(self._config.headers)
        if headers:
            merged_headers.update(headers)
        clean_path = path.lstrip("/")
        url = f"{self._config.base_url}/{clean_path}" if clean_path else self._config.base_url
        return self._http_client.build_request(
            method=method,
            url=url,
            headers=merged_headers,
            params=params,
            json=json,
        )


def _process_response(response: httpx.Response) -> dict[str, Any]:
    data = _safe_json(response)

    if response.status_code == 401:
        detail = _extract_detail(data, "Authentication failed")
        raise AuthenticationError(detail, body=data)

    if response.status_code == 404:
        detail = _extract_detail(data, "Not found")
        raise NotFoundError(detail, body=data)

    if response.status_code >= 400:
        detail = _extract_detail(data, response.reason_phrase)
        raise APIError(detail, status_code=response.status_code, body=data)

    if data is None:
        return {}
    if isinstance(data, dict):
        return data
    return {"data": data}


def _extract_detail(data: Any, fallback: str) -> str:
    if isinstance(data, dict):
        return str(data.get("detail", fallback))
    if data:
        return str(data)
    return fallback


def _safe_json(response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except Exception:
        return None
