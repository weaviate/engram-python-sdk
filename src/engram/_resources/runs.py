from __future__ import annotations

import asyncio
import time

from .._http import AsyncHttpTransport, HttpTransport
from .._models import RunStatus
from .._serialization import parse_run_status
from ..errors import EngramTimeoutError

_RUNS_PATH = "/v1/runs"

_TERMINAL_STATUSES = frozenset(("completed", "failed"))


def _run_path(run_id: str) -> str:
    return f"{_RUNS_PATH}/{run_id}"


class Runs:
    """Sync sub-resource for run operations: client.runs.*"""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def get(self, run_id: str) -> RunStatus:
        data = self._transport.request("GET", _run_path(run_id))
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
                raise EngramTimeoutError(run_id, timeout)
            time.sleep(interval)


class AsyncRuns:
    """Async sub-resource for run operations: client.runs.*"""

    def __init__(self, transport: AsyncHttpTransport) -> None:
        self._transport = transport

    async def get(self, run_id: str) -> RunStatus:
        data = await self._transport.request("GET", _run_path(run_id))
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
                raise EngramTimeoutError(run_id, timeout)
            await asyncio.sleep(interval)
