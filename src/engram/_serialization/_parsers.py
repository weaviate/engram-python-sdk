from __future__ import annotations

from typing import Any

from .._models import (
    CommittedOperation,
    CommittedOperations,
    Group,
    Memory,
    Run,
    RunStatus,
    Scoping,
    SearchResults,
    TopicDetails,
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
        tags=data.get("tags"),
        score=data.get("score"),
        properties=data.get("properties"),
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
        user_id=data.get("user_id"),
    )


def _parse_scoping(data: dict[str, Any]) -> Scoping:
    return Scoping(
        user_scoped=data["user_scoped"],
        scope_properties=data.get("scope_properties", []),
    )


def _parse_topic(data: dict[str, Any]) -> TopicDetails:
    return TopicDetails(
        name=data["topic_name"],
        description=data["description"],
        is_bounded=data["is_bounded"],
        scoping=_parse_scoping(data["scoping"]),
    )


def parse_group(data: dict[str, Any]) -> Group:
    return Group(
        group_id=data["group_id"],
        name=data["name"],
        topics=[_parse_topic(topic) for topic in data["topics"]],
        scoping=_parse_scoping(data["scoping"]),
    )


def parse_group_list(data: dict[str, Any]) -> list[Group]:
    return [parse_group(group) for group in data["groups"]]
