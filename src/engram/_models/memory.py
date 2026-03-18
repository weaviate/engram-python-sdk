from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias


@dataclass(slots=True)
class PreExtractedContent:
    """Pre-extracted content that skips the extraction step continues through the pipeline as-is.
    Each individual item represents a separate memory.
    """

    items: list[PreExtractedItem]


@dataclass(slots=True)
class PreExtractedItem:
    """A single pre-extracted memory."""

    content: str
    topic: str


@dataclass(slots=True)
class StringContent:
    """String content to extract memories from."""

    content: str | list[str]


@dataclass(slots=True)
class ToolCallFuncInput:
    """The function details of an OpenAI-format function tool call."""

    name: str
    arguments: str


@dataclass(slots=True)
class ToolCallCustomInput:
    """The details of an OpenAI-format custom tool call."""

    name: str
    input: str


@dataclass(slots=True)
class ToolCallInput:
    """A single tool call in OpenAI Chat Completions format.

    Set either `function` or `custom` depending on the tool type.
    """

    id: str
    type: str = "function"
    function: ToolCallFuncInput | None = None
    custom: ToolCallCustomInput | None = None


@dataclass(slots=True)
class MessageContent:
    """A message in a conversation using the OpenAI Chat Completions format.

    - 'tool' role (tool results) is mapped to 'user' by the server.
    - 'developer' role is mapped to 'system' by the server.
    """

    role: Literal["user", "assistant", "system", "tool", "developer"]
    content: str = ""
    created_at: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[ToolCallInput] | None = None


@dataclass(slots=True)
class ConversationContent:
    """Conversation content that bypasses the extraction pipeline."""

    messages: list[MessageContent]
    metadata: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None


# Type alias for the content argument to memories.add()
AddContent: TypeAlias = (
    str | list[dict[str, str]] | PreExtractedContent | ConversationContent | StringContent
)


@dataclass(slots=True)
class RetrievalConfig:
    retrieval_type: Literal["vector", "bm25", "hybrid", "fetch"]
    limit: int | None = None


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
