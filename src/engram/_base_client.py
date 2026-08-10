from __future__ import annotations

from collections.abc import Mapping

from .errors import ValidationError
from .types import ClientConfig
from .version import __version__

DEFAULT_BASE_URL = "https://api.engram.weaviate.io"
DEFAULT_TIMEOUT = 30.0


class _BaseClient:
    """Shared config and header logic for sync and async clients."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if timeout <= 0:
            raise ValidationError("Timeout must be greater than 0.")

        normalized_base_url = base_url.rstrip("/")
        default_headers = _build_headers(api_key=api_key, extra_headers=headers or {})

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


CLIENT_ORIGIN_HEADER = "X-Engram-Client"
SDK_CLIENT_TOKEN = f"python-sdk/{__version__}"


def _build_headers(
    *,
    api_key: str,
    extra_headers: Mapping[str, str],
) -> dict[str, str]:
    headers = dict(extra_headers)
    headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
    )

    caller = extra_headers.get(CLIENT_ORIGIN_HEADER)
    headers[CLIENT_ORIGIN_HEADER] = f"{caller} {SDK_CLIENT_TOKEN}" if caller else SDK_CLIENT_TOKEN
    return headers
