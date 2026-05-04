from __future__ import annotations

from typing import Any

from .._models import (
    AddInput,
    ConversationInput,
    PreExtractedInput,
    RetrievalConfig,
    StringInput,
    ToolCallInput,
    Topic,
    TopicSelector,
)


def _serialize_tool_call(tc: ToolCallInput) -> dict[str, Any]:
    out: dict[str, Any] = {"id": tc.id, "type": tc.type}
    if tc.function is not None:
        out["function"] = {"name": tc.function.name, "arguments": tc.function.arguments}
    if tc.custom is not None:
        out["custom"] = {"name": tc.custom.name, "input": tc.custom.input}
    return out


def _serialize_input(input_data: AddInput) -> dict[str, Any]:
    """Build the input envelope with the type discriminator."""
    if isinstance(input_data, str):
        return {"string": {"content": [input_data]}}
    if isinstance(input_data, StringInput):
        if isinstance(input_data.content, list):
            return {"string": {"content": input_data.content}}
        else:
            return {"string": {"content": [input_data.content]}}
    if isinstance(input_data, PreExtractedInput):
        items = [{"content": item.content, "topic": item.topic} for item in input_data.items]
        return {"pre_extracted": {"items": items}}
    if isinstance(input_data, list):
        return {
            "conversation": {"messages": input_data},
        }
    if isinstance(input_data, ConversationInput):
        return _serialize_conversation_content(input_data)
    raise TypeError(f"Unsupported input type: {type(input_data)}")  # pragma: no cover


def _serialize_conversation_content(content: ConversationInput) -> dict[str, Any]:
    messages = []
    for msg in content.messages:
        m: dict[str, Any] = {"role": msg.role, "content": msg.content}
        if msg.created_at is not None:
            m["created_at"] = msg.created_at
        if msg.tool_call_id is not None:
            m["tool_call_id"] = msg.tool_call_id
        if msg.name is not None:
            m["name"] = msg.name
        if msg.tool_calls is not None:
            m["tool_calls"] = [_serialize_tool_call(tc) for tc in msg.tool_calls]
        messages.append(m)
    conversation: dict[str, Any] = {"messages": messages}
    if content.metadata is not None:
        conversation["metadata"] = content.metadata
    if content.created_at is not None:
        conversation["created_at"] = content.created_at
    if content.updated_at is not None:
        conversation["updated_at"] = content.updated_at
    return {"conversation": conversation}


def _serialize_topic(topic: TopicSelector) -> str | dict[str, Any]:
    if isinstance(topic, str):
        return topic
    if isinstance(topic, Topic):
        out: dict[str, Any] = {"name": topic.name}
        if topic.properties is not None:
            out["properties"] = dict(topic.properties)
        return out
    raise TypeError(f"Unsupported topic type: {type(topic)}")  # pragma: no cover


def _serialize_topics(topics: list[TopicSelector] | None) -> list[str | dict[str, Any]] | None:
    if topics is None:
        return None
    return [_serialize_topic(t) for t in topics]


def build_add_body(
    input_data: AddInput,
    *,
    user_id: str | None,
    conversation_id: str | None,
    group: str | None,
    properties: dict[str, str] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"input": _serialize_input(input_data)}
    if user_id is not None:
        body["user_id"] = user_id
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    if group is not None:
        body["group"] = group
    if properties is not None:
        body["properties"] = dict(properties)
    return body


def build_memory_params(
    *,
    user_id: str | None,
    group: str | None,
) -> dict[str, str]:
    params: dict[str, str] = {}
    if user_id is not None:
        params["user_id"] = user_id
    if group is not None:
        params["group"] = group
    return params


def build_search_body(
    *,
    query: str,
    topics: list[TopicSelector] | None,
    user_id: str | None,
    conversation_id: str | None,
    group: str | None,
    retrieval_config: RetrievalConfig | None,
    properties: dict[str, str] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"query": query}
    if retrieval_config is not None:
        body["retrieval_config"] = {
            "retrieval_type": retrieval_config.retrieval_type,
            "limit": retrieval_config.limit,
        }
    serialized_topics = _serialize_topics(topics)
    if serialized_topics is not None:
        body["topics"] = serialized_topics
    if user_id is not None:
        body["user_id"] = user_id
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    if group is not None:
        body["group"] = group
    if properties is not None:
        body["properties"] = dict(properties)
    return body
