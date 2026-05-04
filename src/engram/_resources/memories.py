from __future__ import annotations

from typing import TypeAlias
from uuid import UUID

from .._http import AsyncHttpTransport, HttpTransport
from .._models import (
    AddInput,
    Memory,
    RetrievalConfig,
    Run,
    SearchResults,
    TopicSelector,
)
from .._serialization import (
    build_add_body,
    build_memory_params,
    build_search_body,
    parse_memory,
    parse_run,
    parse_search_results,
)

_MEMORIES_PATH = "/v1/memories"
_MEMORIES_SEARCH_PATH = "/v1/memories/search"

_Topics: TypeAlias = list[TopicSelector] | None


def _memory_path(memory_id: str | UUID) -> str:
    return f"{_MEMORIES_PATH}/{memory_id}"


class Memories:
    """Sync sub-resource for memory operations: client.memories.*"""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def add(
        self,
        input_data: AddInput,
        *,
        user_id: str | None = None,
        group: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> Run:
        body = build_add_body(
            input_data,
            user_id=user_id,
            group=group,
            properties=properties,
        )
        data = self._transport.request("POST", _MEMORIES_PATH, json=body)
        return parse_run(data)

    def get(
        self,
        memory_id: str | UUID,
        *,
        user_id: str | None = None,
        group: str | None = None,
    ) -> Memory:
        params = build_memory_params(
            user_id=user_id,
            group=group,
        )
        data = self._transport.request("GET", _memory_path(memory_id), params=params)
        return parse_memory(data)

    def delete(
        self,
        memory_id: str | UUID,
        *,
        user_id: str | None = None,
        group: str | None = None,
    ) -> None:
        params = build_memory_params(
            user_id=user_id,
            group=group,
        )
        self._transport.request("DELETE", _memory_path(memory_id), params=params)

    def search(
        self,
        *,
        query: str,
        topics: _Topics = None,
        user_id: str | None = None,
        group: str | None = None,
        retrieval_config: RetrievalConfig | None = None,
        properties: dict[str, str] | None = None,
    ) -> SearchResults:
        body = build_search_body(
            query=query,
            topics=topics,
            user_id=user_id,
            group=group,
            retrieval_config=retrieval_config,
            properties=properties,
        )
        data = self._transport.request("POST", _MEMORIES_SEARCH_PATH, json=body)
        return parse_search_results(data)


class AsyncMemories:
    """Async sub-resource for memory operations: client.memories.*"""

    def __init__(self, transport: AsyncHttpTransport) -> None:
        self._transport = transport

    async def add(
        self,
        input_data: AddInput,
        *,
        user_id: str | None = None,
        group: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> Run:
        body = build_add_body(
            input_data,
            user_id=user_id,
            group=group,
            properties=properties,
        )
        data = await self._transport.request("POST", _MEMORIES_PATH, json=body)
        return parse_run(data)

    async def get(
        self,
        memory_id: str | UUID,
        *,
        user_id: str | None = None,
        group: str | None = None,
    ) -> Memory:
        params = build_memory_params(
            user_id=user_id,
            group=group,
        )
        data = await self._transport.request("GET", _memory_path(memory_id), params=params)
        return parse_memory(data)

    async def delete(
        self,
        memory_id: str | UUID,
        *,
        user_id: str | None = None,
        group: str | None = None,
    ) -> None:
        params = build_memory_params(
            user_id=user_id,
            group=group,
        )
        await self._transport.request("DELETE", _memory_path(memory_id), params=params)

    async def search(
        self,
        *,
        query: str,
        topics: _Topics = None,
        user_id: str | None = None,
        group: str | None = None,
        retrieval_config: RetrievalConfig | None = None,
        properties: dict[str, str] | None = None,
    ) -> SearchResults:
        body = build_search_body(
            query=query,
            topics=topics,
            user_id=user_id,
            group=group,
            retrieval_config=retrieval_config,
            properties=properties,
        )
        data = await self._transport.request("POST", _MEMORIES_SEARCH_PATH, json=body)
        return parse_search_results(data)
