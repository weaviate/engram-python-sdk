from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Run:
    """Returned from memories.add() — represents a pipeline run."""

    run_id: str
    status: str
    error: str | None = None


@dataclass(slots=True)
class CommittedOperation:
    memory_id: str
    committed_at: str


@dataclass(slots=True)
class CommittedOperations:
    created: list[CommittedOperation] = field(default_factory=list)
    updated: list[CommittedOperation] = field(default_factory=list)
    deleted: list[CommittedOperation] = field(default_factory=list)


@dataclass(slots=True)
class RunStatus:
    run_id: str
    status: str
    group_id: str
    starting_step: int
    input_type: str
    created_at: str
    updated_at: str
    committed_operations: CommittedOperations | None = None
    error: str | None = None

    @property
    def memories_created(self) -> list[CommittedOperation]:
        if self.committed_operations is None:
            return []
        return self.committed_operations.created

    @property
    def memories_updated(self) -> list[CommittedOperation]:
        if self.committed_operations is None:
            return []
        return self.committed_operations.updated

    @property
    def memories_deleted(self) -> list[CommittedOperation]:
        if self.committed_operations is None:
            return []
        return self.committed_operations.deleted
