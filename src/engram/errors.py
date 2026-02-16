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


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""


class ValidationError(EngramError):
    """Raised when configuration or request input is invalid."""


class ConnectionError(EngramError):
    """Raised when a connection to the Engram server fails."""
