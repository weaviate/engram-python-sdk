from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ClientConfig:
    base_url: str
    timeout: float
    headers: dict[str, str] = field(default_factory=dict)
    api_key: str | None = None
