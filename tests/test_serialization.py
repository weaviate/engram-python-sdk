from engram._models import PreExtractedContent, RetrievalConfig
from engram._serialization import (
    build_add_body,
    build_memory_params,
    build_search_body,
    parse_memory,
    parse_run,
    parse_run_status,
    parse_search_results,
)

# ── build_add_body ──────────────────────────────────────────────────────


def test_build_add_body_str() -> None:
    body = build_add_body(
        "hello world",
        user_id=None,
        conversation_id=None,
        group=None,
    )
    assert body == {"content": {"type": "string", "content": "hello world"}}


def test_build_add_body_str_with_options() -> None:
    body = build_add_body(
        "hello",
        user_id="u1",
        conversation_id="c1",
        group="g1",
    )
    assert body == {
        "content": {"type": "string", "content": "hello"},
        "user_id": "u1",
        "conversation_id": "c1",
        "group": "g1",
    }


def test_build_add_body_pre_extracted() -> None:
    body = build_add_body(
        PreExtractedContent(content="fact", tags=["a", "b"]),
        user_id=None,
        conversation_id=None,
        group=None,
    )
    assert body == {
        "content": {"type": "pre_extracted", "content": "fact", "tags": ["a", "b"]},
    }


def test_build_add_body_pre_extracted_no_tags() -> None:
    body = build_add_body(
        PreExtractedContent(content="fact"),
        user_id=None,
        conversation_id=None,
        group=None,
    )
    assert body == {
        "content": {"type": "pre_extracted", "content": "fact"},
    }


def test_build_add_body_conversation() -> None:
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]
    body = build_add_body(
        messages,
        user_id="u1",
        conversation_id="c1",
        group=None,
    )
    assert body == {
        "content": {
            "type": "conversation",
            "conversation": {"messages": messages},
        },
        "user_id": "u1",
        "conversation_id": "c1",
    }


# ── build_memory_params ─────────────────────────────────────────────────


def test_build_memory_params_minimal() -> None:
    params = build_memory_params(topic="t1", user_id=None, conversation_id=None, group=None)
    assert params == {"topic": "t1"}


def test_build_memory_params_full() -> None:
    params = build_memory_params(topic="t1", user_id="u1", conversation_id="c1", group="g1")
    assert params == {
        "topic": "t1",
        "user_id": "u1",
        "conversation_id": "c1",
        "group": "g1",
    }


# ── build_search_body ───────────────────────────────────────────────────


def test_build_search_body_defaults() -> None:
    body = build_search_body(
        query="test",
        topics=None,
        user_id=None,
        conversation_id=None,
        group=None,
        retrieval_config=RetrievalConfig(),
    )
    assert body == {
        "query": "test",
        "retrieval_config": {"retrieval_type": "hybrid", "limit": 10},
    }


def test_build_search_body_full() -> None:
    body = build_search_body(
        query="test",
        topics=["a", "b"],
        user_id="u1",
        conversation_id="c1",
        group="g1",
        retrieval_config=RetrievalConfig(retrieval_type="vector", limit=5),
    )
    assert body["topics"] == ["a", "b"]
    assert body["user_id"] == "u1"
    assert body["retrieval_config"]["retrieval_type"] == "vector"
    assert body["retrieval_config"]["limit"] == 5


# ── parse_run ───────────────────────────────────────────────────────────


def test_parse_run() -> None:
    result = parse_run({"run_id": "r1", "status": "pending"})
    assert result.run_id == "r1"
    assert result.status == "pending"
    assert result.error is None


def test_parse_run_with_error() -> None:
    result = parse_run({"run_id": "r1", "status": "failed", "error": "boom"})
    assert result.error == "boom"


# ── parse_memory ────────────────────────────────────────────────────────


SAMPLE_MEMORY = {
    "id": "m1",
    "project_id": "p1",
    "content": "some content",
    "topic": "t1",
    "group": "g1",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z",
}


def test_parse_memory_minimal() -> None:
    mem = parse_memory(SAMPLE_MEMORY)
    assert mem.id == "m1"
    assert mem.project_id == "p1"
    assert mem.user_id is None
    assert mem.score is None


def test_parse_memory_with_optional_fields() -> None:
    data = {
        **SAMPLE_MEMORY,
        "user_id": "u1",
        "conversation_id": "c1",
        "tags": ["x"],
        "score": 0.95,
    }
    mem = parse_memory(data)
    assert mem.user_id == "u1"
    assert mem.tags == ["x"]
    assert mem.score == 0.95


# ── parse_search_results ────────────────────────────────────────────────


def test_parse_search_results() -> None:
    data = {"memories": [{"Body": SAMPLE_MEMORY}], "total": 1}
    result = parse_search_results(data)
    assert result.total == 1
    assert len(result) == 1
    assert result[0].id == "m1"


def test_parse_search_results_empty() -> None:
    result = parse_search_results({"memories": [], "total": 0})
    assert result.total == 0
    assert len(result) == 0


def test_search_results_iterable() -> None:
    data = {
        "memories": [{"Body": SAMPLE_MEMORY}, {"Body": {**SAMPLE_MEMORY, "id": "m2"}}],
        "total": 2,
    }
    result = parse_search_results(data)
    ids = [m.id for m in result]
    assert ids == ["m1", "m2"]


# ── parse_run_status ────────────────────────────────────────────────────


SAMPLE_RUN_STATUS = {
    "run_id": "r1",
    "status": "completed",
    "group_id": "g1",
    "starting_step": 0,
    "input_type": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z",
}


def test_parse_run_status_minimal() -> None:
    result = parse_run_status(SAMPLE_RUN_STATUS)
    assert result.run_id == "r1"
    assert result.starting_step == 0
    assert result.committed_operations is None
    assert result.error is None
    assert result.memories_created == []


def test_parse_run_status_with_committed_operations() -> None:
    data = {
        **SAMPLE_RUN_STATUS,
        "committed_operations": {
            "created": [{"memory_id": "m1", "committed_at": "2024-01-01T00:00:00Z"}],
            "updated": [],
            "deleted": [],
        },
    }
    result = parse_run_status(data)
    assert result.committed_operations is not None
    assert len(result.memories_created) == 1
    assert result.memories_created[0].memory_id == "m1"
    assert result.memories_updated == []


def test_parse_run_status_with_error() -> None:
    data = {**SAMPLE_RUN_STATUS, "status": "failed", "error": "boom"}
    result = parse_run_status(data)
    assert result.error == "boom"
