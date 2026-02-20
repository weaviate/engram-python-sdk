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
        default_headers = _build_headers(api_key=api_key, header_overrides=headers or {})

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


def _build_headers(
    *,
    api_key: str,
    header_overrides: Mapping[str, str],
) -> dict[str, str]:
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"weaviate-engram/{__version__}",
        "Authorization": f"Bearer {api_key}",
    }
    headers.update(header_overrides)
    return headers
