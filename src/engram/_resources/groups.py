from __future__ import annotations

import builtins

from .._http import AsyncHttpTransport, HttpTransport
from .._models import Group
from .._serialization import parse_group, parse_group_list

_GROUPS_PATH = "/v1/groups"
_GET_PATH = f"{_GROUPS_PATH}/by-name"


class Groups:
    """Sync sub-resource for group operations: client.groups.*"""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def get(self, name: str | None = None) -> Group:
        params = {"name": name} if name else None
        data = self._transport.request("GET", _GET_PATH, params=params)
        return parse_group(data)

    def list(self) -> builtins.list[Group]:
        data = self._transport.request("GET", _GROUPS_PATH)
        return parse_group_list(data)


class AsyncGroups:
    """Async sub-resource for group operations: client.groups.*"""

    def __init__(self, transport: AsyncHttpTransport) -> None:
        self._transport = transport

    async def get(self, name: str | None = None) -> Group:
        params = {"name": name} if name else None
        data = await self._transport.request("GET", _GET_PATH, params=params)
        return parse_group(data)

    async def list(self) -> builtins.list[Group]:
        data = await self._transport.request("GET", _GROUPS_PATH)
        return parse_group_list(data)
