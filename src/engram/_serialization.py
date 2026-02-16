from __future__ import annotations

from typing import Any

from ._models import (
    AddContent,
    CommittedOperation,
    CommittedOperations,
    Memory,
    PreExtractedContent,
    RetrievalConfig,
    Run,
    RunStatus,
    SearchResults,
)

# ── Body builders ───────────────────────────────────────────────────────


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


# ── Response parsers ────────────────────────────────────────────────────


def parse_run(data: dict[str, Any]) -> Run:
    return Run(
        run_id=data["run_id"],
        status=data["status"],
        error=data.get("error"),
    )


def parse_memory(data: dict[str, Any]) -> Memory:
    return Memory(
        id=data["id"],
        project_id=data["project_id"],
        content=data["content"],
        topic=data["topic"],
        group=data["group"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        user_id=data.get("user_id"),
        conversation_id=data.get("conversation_id"),
        tags=data.get("tags"),
        score=data.get("score"),
    )


def parse_search_results(data: dict[str, Any]) -> SearchResults:
    return SearchResults(
        memories=[parse_memory(m) for m in data["memories"]],
        total=data["total"],
    )


def _parse_committed_operation(data: dict[str, Any]) -> CommittedOperation:
    return CommittedOperation(
        memory_id=data["memory_id"],
        committed_at=data["committed_at"],
    )


def _parse_committed_operations(data: dict[str, Any]) -> CommittedOperations:
    return CommittedOperations(
        created=[_parse_committed_operation(op) for op in data.get("created", [])],
        updated=[_parse_committed_operation(op) for op in data.get("updated", [])],
        deleted=[_parse_committed_operation(op) for op in data.get("deleted", [])],
    )


def parse_run_status(data: dict[str, Any]) -> RunStatus:
    committed_ops = data.get("committed_operations")
    return RunStatus(
        run_id=data["run_id"],
        status=data["status"],
        group_id=data["group_id"],
        starting_step=data["starting_step"],
        input_type=data["input_type"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        committed_operations=_parse_committed_operations(committed_ops)
        if committed_ops is not None
        else None,
        error=data.get("error"),
    )
