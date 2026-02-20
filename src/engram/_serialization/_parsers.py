from __future__ import annotations

from typing import Any

from .._models import (
    CommittedOperation,
    CommittedOperations,
    Memory,
    Run,
    RunStatus,
    SearchResults,
)


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
        memories=[parse_memory(m["Body"]) for m in data["memories"]],
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
