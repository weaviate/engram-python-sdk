from datetime import UTC, datetime, timedelta, timezone

from engram._models import (
    ConversationInput,
    MessageInput,
    PreExtractedInput,
    PreExtractedItem,
    Scoping,
    StringInput,
    ToolCallCustomInput,
    ToolCallFuncInput,
    ToolCallInput,
    Topic,
    VectorRetrieval,
)
from engram._serialization import (
    build_add_body,
    build_memory_params,
    build_search_body,
    parse_group,
    parse_group_list,
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
        group=None,
    )
    assert body == {"input": {"string": {"content": ["hello world"]}}}


def test_build_add_body_str_with_options() -> None:
    body = build_add_body(
        "hello",
        user_id="u1",
        group="g1",
    )
    assert body == {
        "input": {"string": {"content": ["hello"]}},
        "user_id": "u1",
        "group": "g1",
    }


def test_build_add_body_pre_extracted() -> None:
    body = build_add_body(
        PreExtractedInput(items=[PreExtractedItem(content="fact", topic="topic")]),
        user_id=None,
        group=None,
    )
    assert body == {
        "input": {"pre_extracted": {"items": [{"content": "fact", "topic": "topic"}]}},
    }


def test_build_add_body_conversation() -> None:
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]
    body = build_add_body(
        messages,
        user_id="u1",
        group=None,
    )
    assert body == {
        "input": {"conversation": {"messages": messages}},
        "user_id": "u1",
    }


def test_build_add_body_string_content() -> None:
    body = build_add_body(
        StringInput(content="hello world"),
        user_id=None,
        group=None,
    )
    assert body == {"input": {"string": {"content": ["hello world"]}}}


def test_build_add_body_string_content_with_options() -> None:
    body = build_add_body(
        StringInput(content="hello"),
        user_id="u1",
        group="g1",
    )
    assert body == {
        "input": {"string": {"content": ["hello"]}},
        "user_id": "u1",
        "group": "g1",
    }


def test_build_add_body_string_content_with_timestamps() -> None:
    body = build_add_body(
        StringInput(
            content="hello world",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
        ),
        user_id=None,
        group=None,
    )
    assert body == {
        "input": {
            "string": {
                "content": ["hello world"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        },
    }


def test_build_add_body_string_content_with_datetime_timestamps() -> None:
    body = build_add_body(
        StringInput(
            content="hello world",
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone(timedelta(hours=-5))),
        ),
        user_id=None,
        group=None,
    )
    string_body = body["input"]["string"]
    assert string_body["created_at"] == "2024-01-01T00:00:00Z"
    assert string_body["updated_at"] == "2024-01-02T00:00:00-05:00"


def test_build_add_body_string_content_naive_datetime_assumed_utc() -> None:
    body = build_add_body(
        StringInput(content="hello", created_at=datetime(2024, 1, 1)),
        user_id=None,
        group=None,
    )
    assert body["input"]["string"]["created_at"] == "2024-01-01T00:00:00Z"


def test_build_add_body_conversation_content() -> None:
    messages = [
        MessageInput(role="user", content="hi"),
        MessageInput(role="assistant", content="hello"),
    ]
    body = build_add_body(
        ConversationInput(messages=messages),
        user_id="u1",
        group=None,
    )
    assert body == {
        "input": {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                ],
            },
        },
        "user_id": "u1",
    }


def test_build_add_body_conversation_content_with_metadata() -> None:
    messages = [MessageInput(role="user", content="hi")]
    body = build_add_body(
        ConversationInput(
            messages=messages,
            metadata={"session_id": "s1"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
        ),
        user_id=None,
        group=None,
    )
    conv = body["input"]["conversation"]
    assert conv["metadata"] == {"session_id": "s1"}
    assert conv["created_at"] == "2024-01-01T00:00:00Z"
    assert conv["updated_at"] == "2024-01-02T00:00:00Z"


def test_build_add_body_conversation_content_with_message_timestamps() -> None:
    messages = [MessageInput(role="user", content="hi", created_at="2024-01-01T00:00:00Z")]
    body = build_add_body(
        ConversationInput(messages=messages),
        user_id=None,
        group=None,
    )
    msg = body["input"]["conversation"]["messages"][0]
    assert msg["created_at"] == "2024-01-01T00:00:00Z"
    assert "tool_call_metadata" not in msg


def test_build_add_body_conversation_content_with_datetime_timestamps() -> None:
    messages = [
        MessageInput(role="user", content="hi", created_at=datetime(2024, 1, 1, tzinfo=UTC))
    ]
    body = build_add_body(
        ConversationInput(
            messages=messages,
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone(timedelta(hours=-5))),
        ),
        user_id=None,
        group=None,
    )
    conv = body["input"]["conversation"]
    assert conv["messages"][0]["created_at"] == "2024-01-01T00:00:00Z"
    assert conv["created_at"] == "2024-01-01T00:00:00Z"
    assert conv["updated_at"] == "2024-01-02T00:00:00-05:00"


def test_build_add_body_conversation_content_with_tool_calls() -> None:
    messages = [
        MessageInput(
            role="assistant",
            tool_calls=[
                ToolCallInput(
                    id="tc1", function=ToolCallFuncInput(name="search", arguments='{"q":"x"}')
                )
            ],
        )
    ]
    body = build_add_body(
        ConversationInput(messages=messages),
        user_id=None,
        group=None,
    )
    msg = body["input"]["conversation"]["messages"][0]
    assert msg["tool_calls"] == [
        {"id": "tc1", "type": "function", "function": {"name": "search", "arguments": '{"q":"x"}'}}
    ]


def test_build_add_body_conversation_content_with_custom_tool_calls() -> None:
    messages = [
        MessageInput(
            role="assistant",
            tool_calls=[
                ToolCallInput(
                    id="tc2",
                    type="custom",
                    custom=ToolCallCustomInput(name="my_tool", input="some input"),
                )
            ],
        )
    ]
    body = build_add_body(
        ConversationInput(messages=messages),
        user_id=None,
        group=None,
    )
    msg = body["input"]["conversation"]["messages"][0]
    assert msg["tool_calls"] == [
        {"id": "tc2", "type": "custom", "custom": {"name": "my_tool", "input": "some input"}}
    ]


def test_build_add_body_conversation_content_with_tool_role() -> None:
    messages = [MessageInput(role="tool", content="result", tool_call_id="tc1", name="search")]
    body = build_add_body(
        ConversationInput(messages=messages),
        user_id=None,
        group=None,
    )
    msg = body["input"]["conversation"]["messages"][0]
    assert msg["role"] == "tool"
    assert msg["tool_call_id"] == "tc1"
    assert msg["name"] == "search"
    assert msg["content"] == "result"


def test_build_add_body_conversation_content_with_developer_role() -> None:
    messages = [MessageInput(role="developer", content="You are a helpful assistant.")]
    body = build_add_body(
        ConversationInput(messages=messages),
        user_id=None,
        group=None,
    )
    msg = body["input"]["conversation"]["messages"][0]
    assert msg["role"] == "developer"
    assert msg["content"] == "You are a helpful assistant."


# ── build_memory_params ─────────────────────────────────────────────────


def test_build_memory_params_minimal() -> None:
    params = build_memory_params(user_id=None, group=None)
    assert params == {}


def test_build_memory_params_full() -> None:
    params = build_memory_params(user_id="u1", group="g1")
    assert params == {
        "user_id": "u1",
        "group": "g1",
    }


# ── build_search_body ───────────────────────────────────────────────────


def test_build_search_body_defaults() -> None:
    body = build_search_body(
        query="test",
        topics=None,
        user_id=None,
        group=None,
        retrieval_config=None,
    )
    assert body == {"query": "test"}


def test_build_search_body_full() -> None:
    body = build_search_body(
        query="test",
        topics=["a", "b"],
        user_id="u1",
        group="g1",
        retrieval_config=VectorRetrieval(limit=5),
    )
    assert body["topics"] == ["a", "b"]
    assert body["user_id"] == "u1"
    assert body["retrieval_config"]["retrieval_type"] == "vector"
    assert body["retrieval_config"]["limit"] == 5


def test_build_search_body_string_retrieval_config() -> None:
    for retrieval_type in ("vector", "bm25", "hybrid", "fetch"):
        body = build_search_body(
            query="test",
            topics=None,
            user_id=None,
            group=None,
            retrieval_config=retrieval_type,
        )
        assert body["retrieval_config"]["retrieval_type"] == retrieval_type
        assert body["retrieval_config"]["limit"] is None


# ── properties on add ───────────────────────────────────────────────────


def test_build_add_body_with_properties() -> None:
    body = build_add_body(
        "hello",
        user_id=None,
        group=None,
        properties={"region": "eu", "tier": "pro"},
    )
    assert body == {
        "input": {"string": {"content": ["hello"]}},
        "properties": {"region": "eu", "tier": "pro"},
    }


def test_build_add_body_properties_none_omitted() -> None:
    body = build_add_body(
        "hello",
        user_id=None,
        group=None,
        properties=None,
    )
    assert "properties" not in body


# ── properties + topic filters on search ────────────────────────────────


def test_build_search_body_with_properties() -> None:
    body = build_search_body(
        query="q",
        topics=None,
        user_id=None,
        group=None,
        retrieval_config=None,
        properties={"region": "eu"},
    )
    assert body == {"query": "q", "properties": {"region": "eu"}}


def test_build_search_body_with_topic_filter() -> None:
    body = build_search_body(
        query="q",
        topics=[
            "plain",
            Topic(name="scoped", properties={"region": "eu"}),
            Topic(name="cleared", properties={"region": None}),
        ],
        user_id=None,
        group=None,
        retrieval_config=None,
    )
    assert body["topics"] == [
        "plain",
        {"name": "scoped", "properties": {"region": "eu"}},
        {"name": "cleared", "properties": {"region": None}},
    ]


def test_build_search_body_topic_filter_without_properties() -> None:
    body = build_search_body(
        query="q",
        topics=[Topic(name="t1")],
        user_id=None,
        group=None,
        retrieval_config=None,
    )
    assert body["topics"] == [{"name": "t1"}]


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
        "tags": ["x"],
        "score": 0.95,
        "properties": {"region": "eu", "conversation_id": "c1"},
    }
    mem = parse_memory(data)
    assert mem.user_id == "u1"
    assert mem.tags == ["x"]
    assert mem.score == 0.95
    assert mem.properties == {"region": "eu", "conversation_id": "c1"}


# ── parse_search_results ────────────────────────────────────────────────


def test_parse_search_results() -> None:
    data = {"memories": [SAMPLE_MEMORY], "total": 1}
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
        "memories": [SAMPLE_MEMORY, {**SAMPLE_MEMORY, "id": "m2"}],
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
    assert result.user_id is None
    assert result.memories_created == []


def test_parse_run_status_with_user_id() -> None:
    result = parse_run_status({**SAMPLE_RUN_STATUS, "user_id": "alice"})
    assert result.user_id == "alice"


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


# ── parse_group ─────────────────────────────────────────────────────────


SAMPLE_GROUP = {
    "group_id": "11111111-2222-3333-4444-555555555555",
    "name": "default",
    "scoping": {"user_scoped": True, "scope_properties": ["account_id"]},
    "topics": [
        {
            "topic_name": "facts",
            "description": "General facts about the user",
            "is_bounded": False,
            "scoping": {"user_scoped": True, "scope_properties": ["account_id"]},
        },
        {
            "topic_name": "preferences",
            "description": "",
            "is_bounded": True,
            "scoping": {"user_scoped": False},
        },
    ],
}


def test_parse_group() -> None:
    group = parse_group(SAMPLE_GROUP)
    assert group.group_id == "11111111-2222-3333-4444-555555555555"
    assert group.name == "default"
    assert group.scoping == Scoping(user_scoped=True, scope_properties=["account_id"])
    assert [t.name for t in group.topics] == ["facts", "preferences"]
    assert group.topics[0].is_bounded is False
    assert group.topics[0].scoping.scope_properties == ["account_id"]


def test_parse_group_omitted_scope_properties() -> None:
    group = parse_group(SAMPLE_GROUP)
    assert group.topics[1].scoping == Scoping(user_scoped=False, scope_properties=[])


SAMPLE_GROUP_LIST = {
    "groups": [
        {
            "group_id": "11111111-2222-3333-4444-555555555555",
            "name": "default",
            "scoping": {
                "user_scoped": True,
                "scope_properties": ["account_id"],
            },
            "topics": [
                {
                    "topic_name": "facts",
                    "description": "General facts about the user",
                    "is_bounded": False,
                    "scoping": {
                        "user_scoped": True,
                        "scope_properties": ["account_id"],
                    },
                }
            ],
        },
        {
            "group_id": "66666666-7777-8888-9999-000000000000",
            "name": "support",
            "scoping": {"user_scoped": False},
            "topics": [
                {
                    "topic_name": "tickets",
                    "description": "Support tickets",
                    "is_bounded": True,
                    "scoping": {"user_scoped": False},
                }
            ],
        },
    ],
}


def test_parse_group_list() -> None:
    groups = parse_group_list(SAMPLE_GROUP_LIST)
    assert [g.name for g in groups] == ["default", "support"]
    assert groups[1].group_id == "66666666-7777-8888-9999-000000000000"
    assert groups[1].topics[0].is_bounded is True


def test_parse_group_list_empty() -> None:
    assert parse_group_list({"groups": []}) == []
