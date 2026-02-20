import json
from typing import Any

import httpx
import pytest

from engram._http import HttpTransport
from engram._models import PreExtractedContent, RetrievalConfig
from engram.client import DEFAULT_BASE_URL, EngramClient
from engram.errors import APIError, AuthenticationError, ValidationError


def test_client_defaults() -> None:
    client = EngramClient(api_key="test-key")
    try:
        assert client.config.base_url == DEFAULT_BASE_URL
        assert client.config.timeout == 30.0
        assert client.default_headers["Accept"] == "application/json"
        assert client.default_headers["Content-Type"] == "application/json"
        assert client.default_headers["Authorization"] == "Bearer test-key"
    finally:
        client.close()


def test_client_custom_config_and_header_merging() -> None:
    client = EngramClient(
        base_url="https://example.com/",
        timeout=12.5,
        api_key="test-key",
        headers={"X-Custom": "from-client"},
    )
    try:
        assert client.config.base_url == "https://example.com"
        assert client.config.timeout == 12.5
        assert client.default_headers["Authorization"] == "Bearer test-key"
        assert client.default_headers["X-Custom"] == "from-client"

        request = client._transport.build_request(
            "GET",
            "/v1/items",
            headers={"X-Custom": "from-request", "X-Request": "value"},
        )
        assert str(request.url) == "https://example.com/v1/items"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["X-Custom"] == "from-request"
        assert request.headers["X-Request"] == "value"
    finally:
        client.close()


def test_client_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValidationError):
        EngramClient(api_key="test-key", timeout=0)


def test_client_has_sub_resources() -> None:
    client = EngramClient(api_key="test-key")
    try:
        assert hasattr(client, "memories")
        assert hasattr(client, "runs")
    finally:
        client.close()


# ── Helpers ─────────────────────────────────────────────────────────────


def _make_client(
    status_code: int = 200,
    body: dict[str, Any] | None = None,
) -> EngramClient:
    mock = httpx.MockTransport(
        lambda _: httpx.Response(status_code, json=body if body is not None else {})
    )
    client = EngramClient(base_url="https://test.example.com", api_key="test-key")
    transport = HttpTransport(client._config, httpx.Client(transport=mock))
    client._transport.close()
    client._transport = transport
    client.memories._transport = transport
    client.runs._transport = transport
    return client


def _make_client_with_handler(
    handler: Any,
    *,
    base_url: str = "https://test.example.com",
    api_key: str = "k",
) -> EngramClient:
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = EngramClient(base_url=base_url, api_key=api_key)
    transport = HttpTransport(client._config, http_client)
    client._transport.close()
    client._transport = transport
    client.memories._transport = transport
    client.runs._transport = transport
    return client


# ── memories.add ────────────────────────────────────────────────────────


def test_add_str() -> None:
    client = _make_client(body={"run_id": "r1", "status": "pending"})
    result = client.memories.add("hello")
    assert result.run_id == "r1"
    assert result.status == "pending"


def test_add_pre_extracted() -> None:
    client = _make_client(body={"run_id": "r2", "status": "pending"})
    result = client.memories.add(
        PreExtractedContent(content="fact", tags=["a"]),
        user_id="u1",
    )
    assert result.run_id == "r2"


def test_add_conversation() -> None:
    client = _make_client(body={"run_id": "r3", "status": "pending"})
    result = client.memories.add(
        [{"role": "user", "content": "hi"}],
        user_id="u1",
        conversation_id="c1",
    )
    assert result.run_id == "r3"


def test_add_sends_content_envelope() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"run_id": "r1", "status": "pending"})

    client = _make_client_with_handler(handler)
    client.memories.add("hello", user_id="u1", group="g1")
    body = json.loads(captured[0].content)
    assert body == {
        "content": {"type": "string", "content": "hello"},
        "user_id": "u1",
        "group": "g1",
    }


def test_add_conversation_sends_correct_envelope() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"run_id": "r1", "status": "pending"})

    client = _make_client_with_handler(handler)
    messages = [{"role": "user", "content": "hi"}]
    client.memories.add(messages, conversation_id="c1")
    body = json.loads(captured[0].content)
    assert body == {
        "content": {
            "type": "conversation",
            "conversation": {"messages": messages},
        },
        "conversation_id": "c1",
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


def test_get_memory() -> None:
    client = _make_client(body=SAMPLE_MEMORY_RESPONSE)
    mem = client.memories.get("m1", topic="t1")
    assert mem.id == "m1"
    assert mem.content == "some content"


def test_get_memory_sends_query_params() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json=SAMPLE_MEMORY_RESPONSE)

    client = _make_client_with_handler(handler)
    client.memories.get("m1", topic="t1", user_id="u1", group="g1")
    url = captured[0].url
    assert url.params["topic"] == "t1"
    assert url.params["user_id"] == "u1"
    assert url.params["group"] == "g1"


# ── memories.delete ─────────────────────────────────────────────────────


def test_delete_memory() -> None:
    client = _make_client_with_handler(lambda _: httpx.Response(204, content=b""))
    client.memories.delete("m1", topic="t1")


# ── memories.search ─────────────────────────────────────────────────────


def test_search_memories() -> None:
    response_body: dict[str, Any] = {
        "memories": [{"Body": SAMPLE_MEMORY_RESPONSE}],
        "total": 1,
    }
    client = _make_client(body=response_body)
    result = client.memories.search(query="test")
    assert result.total == 1
    assert len(result) == 1


def test_search_memories_iterable() -> None:
    response_body: dict[str, Any] = {
        "memories": [
            {"Body": SAMPLE_MEMORY_RESPONSE},
            {"Body": {**SAMPLE_MEMORY_RESPONSE, "id": "m2", "score": 0.85}},
        ],
        "total": 2,
    }
    client = _make_client(body=response_body)
    results = client.memories.search(query="test")
    ids = [m.id for m in results]
    assert ids == ["m1", "m2"]
    assert results[1].score == 0.85


def test_search_sends_correct_body() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"memories": [], "total": 0})

    client = _make_client_with_handler(handler)
    client.memories.search(
        query="find this",
        topics=["a"],
        retrieval_config=RetrievalConfig(retrieval_type="vector", limit=5),
    )
    body = json.loads(captured[0].content)
    assert body["query"] == "find this"
    assert body["topics"] == ["a"]
    assert body["retrieval_config"]["retrieval_type"] == "vector"
    assert body["retrieval_config"]["limit"] == 5


def test_search_default_retrieval_config() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"memories": [], "total": 0})

    client = _make_client_with_handler(handler)
    client.memories.search(query="test")
    body = json.loads(captured[0].content)
    assert body["retrieval_config"] == {
        "retrieval_type": "hybrid",
        "limit": 10,
    }


# ── runs.get ────────────────────────────────────────────────────────────


def test_get_run() -> None:
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
    result = client.runs.get("r1")
    assert result.run_id == "r1"
    assert result.status == "completed"
    assert len(result.memories_created) == 1


# ── Error handling ──────────────────────────────────────────────────────


def test_401_raises_authentication_error() -> None:
    client = _make_client(status_code=401, body={"detail": "Invalid token"})
    with pytest.raises(AuthenticationError) as exc_info:
        client.memories.add("hello")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value)


def test_404_raises_api_error() -> None:
    client = _make_client(status_code=404, body={"detail": "Not found"})
    with pytest.raises(APIError) as exc_info:
        client.memories.get("missing", topic="t1")
    assert exc_info.value.status_code == 404


def test_400_raises_api_error() -> None:
    client = _make_client(status_code=400, body={"detail": "Bad request"})
    with pytest.raises(APIError) as exc_info:
        client.memories.search(query="test")
    assert exc_info.value.status_code == 400


def test_500_raises_api_error() -> None:
    client = _make_client(status_code=500, body={"detail": "Internal server error"})
    with pytest.raises(APIError) as exc_info:
        client.runs.get("r1")
    assert exc_info.value.status_code == 500
