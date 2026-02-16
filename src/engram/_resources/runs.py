from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from .._models import RunStatus
from .._serialization import parse_run_status

if TYPE_CHECKING:
    from ..async_client import AsyncEngramClient
    from ..client import EngramClient

_RUNS_PATH = "/v1/runs"

_TERMINAL_STATUSES = frozenset(("completed", "failed"))


def _run_path(run_id: str) -> str:
    return f"{_RUNS_PATH}/{run_id}"


class Runs:
    """Sync sub-resource for run operations: client.runs.*"""

    _client: EngramClient

    def __init__(self, client: EngramClient) -> None:
        self._client = client

    def get(self, run_id: str) -> RunStatus:
        data = self._client._request("GET", _run_path(run_id))
        return parse_run_status(data)

    def wait(
        self,
        run_id: str,
        *,
        timeout: float = 30.0,
        interval: float = 0.5,
    ) -> RunStatus:
        deadline = time.monotonic() + timeout
        while True:
            status = self.get(run_id)
            if status.status in _TERMINAL_STATUSES:
                return status
            if time.monotonic() + interval > deadline:
                return status
            time.sleep(interval)


class AsyncRuns:
    """Async sub-resource for run operations: client.runs.*"""

    _client: AsyncEngramClient

    def __init__(self, client: AsyncEngramClient) -> None:
        self._client = client

    async def get(self, run_id: str) -> RunStatus:
        data = await self._client._request("GET", _run_path(run_id))
        return parse_run_status(data)

    async def wait(
        self,
        run_id: str,
        *,
        timeout: float = 30.0,
        interval: float = 0.5,
    ) -> RunStatus:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            status = await self.get(run_id)
            if status.status in _TERMINAL_STATUSES:
                return status
            if loop.time() + interval > deadline:
                return status
            await asyncio.sleep(interval)
