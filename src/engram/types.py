from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ClientConfig:
    base_url: str
    timeout: float
    headers: dict[str, str] = field(default_factory=dict)
    api_key: str | None = None


@dataclass(slots=True)
class APIRequest:
    method: str
    path: str
    params: dict[str, Any] | None = None
    json: dict[str, Any] | None = None


@dataclass(slots=True)
class APIResponse:
    status_code: int
    data: dict[str, Any] | list[Any] | str | None = None
