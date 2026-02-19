import json
from typing import Any

import httpx
import pytest

from engram._models import PreExtractedContent, RetrievalConfig
from engram.async_client import DEFAULT_BASE_URL, AsyncEngramClient
from engram.errors import APIError, AuthenticationError, NotFoundError, ValidationError


@pytest.mark.asyncio
async def test_async_client_defaults() -> None:
    client = AsyncEngramClient()
    try:
        assert client.config.base_url == DEFAULT_BASE_URL
        assert client.config.timeout == 30.0
        assert client.default_headers["Accept"] == "application/json"
        assert client.default_headers["Content-Type"] == "application/json"
        assert "Authorization" not in client.default_headers
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_async_client_custom_config_and_header_merging() -> None:
    client = AsyncEngramClient(
        base_url="https://example.com/",
        timeout=22.0,
        api_key="test-key",
        headers={"X-Custom": "from-client"},
    )
    try:
        assert client.config.base_url == "https://example.com"
        assert client.config.timeout == 22.0
        assert client.default_headers["Authorization"] == "Bearer test-key"
        assert client.default_headers["X-Custom"] == "from-client"

        request = client._transport.build_request(
            "GET",
            "v1/items",
            headers={"X-Custom": "from-request", "X-Request": "value"},
        )
        assert str(request.url) == "https://example.com/v1/items"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["X-Custom"] == "from-request"
        assert request.headers["X-Request"] == "value"
    finally:
        await client.aclose()


def test_async_client_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValidationError):
        AsyncEngramClient(timeout=-1)


def test_async_client_has_sub_resources() -> None:
    client = AsyncEngramClient()
    assert hasattr(client, "memories")
    assert hasattr(client, "runs")


# ── Helpers ─────────────────────────────────────────────────────────────


def _make_client(
    status_code: int = 200,
    body: dict[str, Any] | None = None,
) -> AsyncEngramClient:
    transport = httpx.MockTransport(
        lambda _: httpx.Response(status_code, json=body if body is not None else {})
    )
    return AsyncEngramClient(
        base_url="https://test.example.com",
        api_key="test-key",
        http_client=httpx.AsyncClient(transport=transport),
    )


# ── memories.add ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_str() -> None:
    client = _make_client(body={"run_id": "r1", "status": "pending"})
    result = await client.memories.add("hello")
    assert result.run_id == "r1"
    assert result.status == "pending"


@pytest.mark.asyncio
async def test_add_pre_extracted() -> None:
    client = _make_client(body={"run_id": "r2", "status": "pending"})
    result = await client.memories.add(
        PreExtractedContent(content="fact", tags=["a"]),
        user_id="u1",
    )
    assert result.run_id == "r2"


@pytest.mark.asyncio
async def test_add_conversation() -> None:
    client = _make_client(body={"run_id": "r3", "status": "pending"})
    result = await client.memories.add(
        [{"role": "user", "content": "hi"}],
        user_id="u1",
        conversation_id="c1",
    )
    assert result.run_id == "r3"


@pytest.mark.asyncio
async def test_add_sends_content_envelope() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"run_id": "r1", "status": "pending"})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = AsyncEngramClient(
        base_url="https://test.example.com",
        api_key="k",
        http_client=http_client,
    )
    await client.memories.add("hello", user_id="u1", group="g1")
    body = json.loads(captured[0].content)
    assert body == {
        "content": {"type": "string", "content": "hello"},
        "user_id": "u1",
        "group": "g1",
    }


# ── memories.get ────────────────────────────────────────────────────────

SAMPLE_MEMORY_RESPONSE: dict[str, Any] = {
    "id": "m1",
    "project_id": "p1",
    "content": "some content",
    "topic": "t1",
    "group": "g1",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z",
}


@pytest.mark.asyncio
async def test_get_memory() -> None:
    client = _make_client(body=SAMPLE_MEMORY_RESPONSE)
    mem = await client.memories.get("m1", topic="t1")
    assert mem.id == "m1"
    assert mem.content == "some content"


@pytest.mark.asyncio
async def test_get_memory_sends_query_params() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json=SAMPLE_MEMORY_RESPONSE)

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = AsyncEngramClient(
        base_url="https://test.example.com",
        api_key="k",
        http_client=http_client,
    )
    await client.memories.get("m1", topic="t1", user_id="u1", group="g1")
    url = captured[0].url
    assert url.params["topic"] == "t1"
    assert url.params["user_id"] == "u1"
    assert url.params["group"] == "g1"


# ── memories.delete ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_memory() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(204, content=b""))
    http_client = httpx.AsyncClient(transport=transport)
    client = AsyncEngramClient(
        base_url="https://test.example.com",
        api_key="k",
        http_client=http_client,
    )
    await client.memories.delete("m1", topic="t1")


# ── memories.search ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_memories() -> None:
    response_body: dict[str, Any] = {
        "memories": [{"Body": SAMPLE_MEMORY_RESPONSE}],
        "total": 1,
    }
    client = _make_client(body=response_body)
    result = await client.memories.search(query="test")
    assert result.total == 1
    assert len(result) == 1


@pytest.mark.asyncio
async def test_search_memories_iterable() -> None:
    response_body: dict[str, Any] = {
        "memories": [
            {"Body": SAMPLE_MEMORY_RESPONSE},
            {"Body": {**SAMPLE_MEMORY_RESPONSE, "id": "m2", "score": 0.85}},
        ],
        "total": 2,
    }
    client = _make_client(body=response_body)
    results = await client.memories.search(query="test")
    ids = [m.id for m in results]
    assert ids == ["m1", "m2"]
    assert results[1].score == 0.85


@pytest.mark.asyncio
async def test_search_sends_correct_body() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"memories": [], "total": 0})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = AsyncEngramClient(
        base_url="https://test.example.com",
        api_key="k",
        http_client=http_client,
    )
    await client.memories.search(
        query="find this",
        topics=["a"],
        retrieval_config=RetrievalConfig(retrieval_type="vector", limit=5),
    )
    body = json.loads(captured[0].content)
    assert body["query"] == "find this"
    assert body["topics"] == ["a"]
    assert body["retrieval_config"]["retrieval_type"] == "vector"
    assert body["retrieval_config"]["limit"] == 5


# ── runs.get ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_run() -> None:
    response_body: dict[str, Any] = {
        "run_id": "r1",
        "status": "completed",
        "group_id": "g1",
        "starting_step": 0,
        "input_type": "string",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "committed_operations": {
            "created": [{"memory_id": "m1", "committed_at": "2024-01-01T00:00:00Z"}],
            "updated": [],
            "deleted": [],
        },
    }
    client = _make_client(body=response_body)
    result = await client.runs.get("r1")
    assert result.run_id == "r1"
    assert result.status == "completed"
    assert len(result.memories_created) == 1


# ── Error handling ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_401_raises_authentication_error() -> None:
    client = _make_client(status_code=401, body={"detail": "Invalid token"})
    with pytest.raises(AuthenticationError) as exc_info:
        await client.memories.add("hello")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value)


@pytest.mark.asyncio
async def test_404_raises_not_found_error() -> None:
    client = _make_client(status_code=404, body={"detail": "Not found"})
    with pytest.raises(NotFoundError) as exc_info:
        await client.memories.get("missing", topic="t1")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_400_raises_api_error() -> None:
    client = _make_client(status_code=400, body={"detail": "Bad request"})
    with pytest.raises(APIError) as exc_info:
        await client.memories.search(query="test")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_500_raises_api_error() -> None:
    client = _make_client(status_code=500, body={"detail": "Internal server error"})
    with pytest.raises(APIError) as exc_info:
        await client.runs.get("r1")
    assert exc_info.value.status_code == 500
