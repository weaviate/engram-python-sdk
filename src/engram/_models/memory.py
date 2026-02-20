from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import Literal, TypeAlias


@dataclass(slots=True)
class PreExtractedContent:
    """Pre-extracted content that bypasses the extraction pipeline."""

    content: str
    tags: list[str] = field(default_factory=list)


# Type alias for the content argument to memories.add()
AddContent: TypeAlias = str | list[dict[str, str]] | PreExtractedContent


@dataclass(slots=True)
class RetrievalConfig:
    retrieval_type: Literal["vector", "bm25", "hybrid"] = "hybrid"
    limit: int = 10


@dataclass(slots=True)
class Memory:
    id: str
    project_id: str
    content: str
    topic: str
    group: str
    created_at: str
    updated_at: str
    user_id: str | None = None
    conversation_id: str | None = None
    tags: list[str] | None = None
    score: float | None = None


class SearchResults(Sequence[Memory]):
    """List-like wrapper over search results with a total count."""

    def __init__(self, memories: list[Memory], total: int) -> None:
        self._memories = memories
        self.total = total

    def __getitem__(self, index: int) -> Memory:  # type: ignore[override]
        return self._memories[index]

    def __len__(self) -> int:
        return len(self._memories)

    def __iter__(self) -> Iterator[Memory]:
        return iter(self._memories)

    def __repr__(self) -> str:
        return f"SearchResults(total={self.total}, returned={len(self._memories)})"
