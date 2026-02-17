from __future__ import annotations

from typing import Any


class EngramError(Exception):
    """Base error for the Engram SDK."""


class APIError(EngramError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        body: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(APIError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str, *, body: object = None) -> None:
        super().__init__(message, status_code=401, body=body)


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str, *, body: object = None) -> None:
        super().__init__(message, status_code=404, body=body)


class ValidationError(EngramError):
    """Raised when configuration or request input is invalid."""


class ConnectionError(EngramError):
    """Raised when a connection to the Engram server fails."""


class EngramTimeoutError(EngramError):
    """Raised when a run does not reach a terminal status within the timeout."""

    def __init__(self, run_id: str, timeout: float) -> None:
        super().__init__(f"Run {run_id!r} did not reach a terminal status within {timeout}s")
        self.run_id = run_id
        self.timeout = timeout
