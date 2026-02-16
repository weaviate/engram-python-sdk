from __future__ import annotations

from typing import TYPE_CHECKING

from .._models import AddContent, Memory, RetrievalConfig, Run, SearchResults
from .._serialization import (
    build_add_body,
    build_memory_params,
    build_search_body,
    parse_memory,
    parse_run,
    parse_search_results,
)

if TYPE_CHECKING:
    from ..async_client import AsyncEngramClient
    from ..client import EngramClient

_MEMORIES_PATH = "/v1/memories"
_MEMORIES_SEARCH_PATH = "/v1/memories/search"


def _memory_path(memory_id: str) -> str:
    return f"{_MEMORIES_PATH}/{memory_id}"


class Memories:
    """Sync sub-resource for memory operations: client.memories.*"""

    _client: EngramClient

    def __init__(self, client: EngramClient) -> None:
        self._client = client

    def add(
        self,
        content: AddContent,
        *,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
    ) -> Run:
        body = build_add_body(
            content,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
        )
        data = self._client._request("POST", _MEMORIES_PATH, json=body)
        return parse_run(data)

    def get(
        self,
        memory_id: str,
        *,
        topic: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
    ) -> Memory:
        params = build_memory_params(
            topic=topic,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
        )
        data = self._client._request("GET", _memory_path(memory_id), params=params)
        return parse_memory(data)

    def delete(
        self,
        memory_id: str,
        *,
        topic: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
    ) -> None:
        params = build_memory_params(
            topic=topic,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
        )
        self._client._request("DELETE", _memory_path(memory_id), params=params)

    def search(
        self,
        *,
        query: str,
        topics: list[str] | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
        retrieval_config: RetrievalConfig | None = None,
    ) -> SearchResults:
        body = build_search_body(
            query=query,
            topics=topics,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
            retrieval_config=retrieval_config or RetrievalConfig(),
        )
        data = self._client._request("POST", _MEMORIES_SEARCH_PATH, json=body)
        return parse_search_results(data)


class AsyncMemories:
    """Async sub-resource for memory operations: client.memories.*"""

    _client: AsyncEngramClient

    def __init__(self, client: AsyncEngramClient) -> None:
        self._client = client

    async def add(
        self,
        content: AddContent,
        *,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
    ) -> Run:
        body = build_add_body(
            content,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
        )
        data = await self._client._request("POST", _MEMORIES_PATH, json=body)
        return parse_run(data)

    async def get(
        self,
        memory_id: str,
        *,
        topic: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
    ) -> Memory:
        params = build_memory_params(
            topic=topic,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
        )
        data = await self._client._request("GET", _memory_path(memory_id), params=params)
        return parse_memory(data)

    async def delete(
        self,
        memory_id: str,
        *,
        topic: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
    ) -> None:
        params = build_memory_params(
            topic=topic,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
        )
        await self._client._request("DELETE", _memory_path(memory_id), params=params)

    async def search(
        self,
        *,
        query: str,
        topics: list[str] | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
        group: str | None = None,
        retrieval_config: RetrievalConfig | None = None,
    ) -> SearchResults:
        body = build_search_body(
            query=query,
            topics=topics,
            user_id=user_id,
            conversation_id=conversation_id,
            group=group,
            retrieval_config=retrieval_config or RetrievalConfig(),
        )
        data = await self._client._request("POST", _MEMORIES_SEARCH_PATH, json=body)
        return parse_search_results(data)
