import pytest

from engram.client import DEFAULT_BASE_URL, EngramClient
from engram.errors import ValidationError


def test_client_defaults() -> None:
    client = EngramClient()
    try:
        assert client.config.base_url == DEFAULT_BASE_URL
        assert client.config.timeout == 30.0
        assert client.default_headers["Accept"] == "application/json"
        assert client.default_headers["Content-Type"] == "application/json"
        assert "Authorization" not in client.default_headers
    finally:
        client.close()


def test_client_custom_config_and_header_merging() -> None:
    client = EngramClient(
        base_url="https://example.com/",
        timeout=12.5,
        api_key="test-key",
        headers={"X-Custom": "from-client"},
    )
    try:
        assert client.config.base_url == "https://example.com"
        assert client.config.timeout == 12.5
        assert client.default_headers["Authorization"] == "Bearer test-key"
        assert client.default_headers["X-Custom"] == "from-client"

        request = client.build_request(
            "GET",
            "/v1/items",
            headers={"X-Custom": "from-request", "X-Request": "value"},
        )
        assert str(request.url) == "https://example.com/v1/items"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["X-Custom"] == "from-request"
        assert request.headers["X-Request"] == "value"
    finally:
        client.close()


def test_client_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValidationError):
        EngramClient(timeout=0)
