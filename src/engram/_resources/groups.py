from __future__ import annotations

import builtins

from .._http import AsyncHttpTransport, HttpTransport
from .._models import Group
from .._serialization import parse_group_list

_GROUPS_PATH = "/v1/groups"


class Groups:
    """Sync sub-resource for group operations: client.groups.*"""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def list(self) -> builtins.list[Group]:
        data = self._transport.request("GET", _GROUPS_PATH)
        return parse_group_list(data)


class AsyncGroups:
    """Async sub-resource for group operations: client.groups.*"""

    def __init__(self, transport: AsyncHttpTransport) -> None:
        self._transport = transport

    async def list(self) -> builtins.list[Group]:
        data = await self._transport.request("GET", _GROUPS_PATH)
        return parse_group_list(data)
