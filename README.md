# weaviate-engram

Python SDK for Engram by Weaviate.

## Requirements

- Python 3.11 to 3.14
- [uv](https://docs.astral.sh/uv/)

## Local Development

```bash
uv sync --all-groups
```

Run quality checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q
```

## Basic Usage

```python
from engram import AsyncEngramClient, EngramClient

client = EngramClient(api_key="example-api-key")
async_client = AsyncEngramClient(api_key="example-api-key")
```
