from __future__ import annotations

from collections.abc import Mapping

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
        api_key: str,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            headers=headers,
            timeout=timeout,
        )
        self._transport = HttpTransport(self._config)
        self.memories = Memories(self._transport)
        self.runs = Runs(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> EngramClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
