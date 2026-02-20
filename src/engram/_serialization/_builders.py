from __future__ import annotations

from typing import Any

from .._models import AddContent, PreExtractedContent, RetrievalConfig


def _serialize_content(content: AddContent) -> dict[str, Any]:
    """Build the content envelope with the type discriminator."""
    if isinstance(content, str):
        return {"type": "string", "content": content}
    if isinstance(content, PreExtractedContent):
        d: dict[str, Any] = {"type": "pre_extracted", "content": content.content}
        if content.tags:
            d["tags"] = content.tags
        return d
    if isinstance(content, list):
        return {
            "type": "conversation",
            "conversation": {"messages": content},
        }
    raise TypeError(f"Unsupported content type: {type(content)}")  # pragma: no cover


def build_add_body(
    content: AddContent,
    *,
    user_id: str | None,
    conversation_id: str | None,
    group: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"content": _serialize_content(content)}
    if user_id is not None:
        body["user_id"] = user_id
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    if group is not None:
        body["group"] = group
    return body


def build_memory_params(
    *,
    topic: str,
    user_id: str | None,
    conversation_id: str | None,
    group: str | None,
) -> dict[str, str]:
    params: dict[str, str] = {"topic": topic}
    if user_id is not None:
        params["user_id"] = user_id
    if conversation_id is not None:
        params["conversation_id"] = conversation_id
    if group is not None:
        params["group"] = group
    return params


def build_search_body(
    *,
    query: str,
    topics: list[str] | None,
    user_id: str | None,
    conversation_id: str | None,
    group: str | None,
    retrieval_config: RetrievalConfig,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "query": query,
        "retrieval_config": {
            "retrieval_type": retrieval_config.retrieval_type,
            "limit": retrieval_config.limit,
        },
    }
    if topics is not None:
        body["topics"] = topics
    if user_id is not None:
        body["user_id"] = user_id
    if conversation_id is not None:
        body["conversation_id"] = conversation_id
    if group is not None:
        body["group"] = group
    return body
