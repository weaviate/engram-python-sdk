<img src="https://raw.githubusercontent.com/weaviate/engram-python-sdk/main/docs/assets/weaviate-logo.png" alt="Weaviate" width="140" align="right" />

# weaviate-engram

[![PyPI version](https://img.shields.io/pypi/v/weaviate-engram.svg)](https://pypi.org/project/weaviate-engram/)
[![Python versions](https://img.shields.io/pypi/pyversions/weaviate-engram.svg)](https://pypi.org/project/weaviate-engram/)
[![License](https://img.shields.io/pypi/l/weaviate-engram.svg)](https://github.com/weaviate/engram-python-sdk/blob/main/LICENSE)
[![CI](https://github.com/weaviate/engram-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/weaviate/engram-python-sdk/actions/workflows/ci.yml)

The official Python SDK for **Engram**, the fully managed memory service by Weaviate.

Engram lets you add persistent, personalized memory to AI assistants and agents, with no infrastructure to set up or manage. When you add a memory, Engram processes it asynchronously through a background pipeline that extracts, deduplicates, and reconciles facts. Memories are scoped by project and user, along with any custom scope properties you define, and these scopes can be mixed and matched freely. Each scope is backed by Weaviate's multi-tenant architecture, ensuring strong isolation between tenants.

[Learn more about Engram →](https://weaviate.io/product/engram)

## Requirements

- Python 3.11 to 3.14

## Installation

```bash
pip install weaviate-engram
```

```bash
uv add weaviate-engram
```

## Get an API key

Engram runs on [Weaviate Cloud](https://console.weaviate.cloud). To get started:

1. **Sign up** (or log in) at [console.weaviate.cloud](https://console.weaviate.cloud).
2. **Open Engram** and create a project at [console.weaviate.cloud/engram](https://console.weaviate.cloud/engram).
3. **Generate an API key** from the project's **API Keys** page. Keys are shown once, so copy yours somewhere safe.

## Quick start

**1. Initialize the client**

```python
from engram import EngramClient

client = EngramClient(api_key="YOUR_API_KEY")
```

**2. Add a memory from a string**

```python
# add() returns immediately. Memory processing happens asynchronously
# in the background via Engram's pipeline.
run = client.memories.add(
    "User prefers concise responses and dark mode",
    user_id="alice@example.com",
)
print(run.run_id)  # e.g. "run_abc123"
```

**3. Add a memory from a conversation**

Conversations use the OpenAI Chat Completions message format. Separately, you can pass scope `properties` to control where a memory lives — here a `conversation_id` scopes it to a specific session. Properties work with any input type, not just conversations:

```python
run = client.memories.add(
    [
        {"role": "user", "content": "I just moved to Berlin and I am looking for a good coffee shop."},
        {"role": "assistant", "content": "Welcome to Berlin! Here are some popular coffee shops in the city..."},
        {"role": "user", "content": "I prefer specialty coffee, not chains."},
    ],
    user_id="alice@example.com",
    properties={"conversation_id": "session-abc123"},
)

print(run.run_id)  # e.g. "run_abc123"
```

**4. Search memories**

```python
results = client.memories.search(
    query="What does the user prefer?",
    user_id="alice@example.com",
)
for memory in results:
    print(memory.content)
```

## Async client

An async client with the same surface is available:

```python
from engram import AsyncEngramClient

client = AsyncEngramClient(api_key="YOUR_API_KEY")

run = await client.memories.add(
    "User prefers concise responses and dark mode",
    user_id="alice@example.com",
)
results = await client.memories.search(
    query="What does the user prefer?",
    user_id="alice@example.com",
)
```

## Error handling

All SDK exceptions inherit from `EngramError`:

```python
from engram import (
    APIError,             # raised on any non-2xx response
    AuthenticationError,  # 401, invalid or missing API key
    ValidationError,      # invalid client configuration or request input
    ConnectionError,      # network failure reaching the Engram API
    EngramTimeoutError,   # runs.wait() did not reach a terminal status in time
)
```

## Waiting for a run to complete

Each run is processed asynchronously. Under normal conditions you should **not** wait on runs — treat `add()` as fire-and-forget to keep latency low and let the pipeline reconcile memories in the background. Blocking on every run defeats the purpose of the async pipeline and will slow your application down, especially when ingesting at volume.

`runs.wait()` exists for the cases where you genuinely need the outcome of a specific run before proceeding — primarily debugging and tests:

```python
status = client.runs.wait(run.run_id, timeout=60.0)
print(status.status)  # "completed" or "failed"
print(f"+{len(status.memories_created)} ~{len(status.memories_updated)} -{len(status.memories_deleted)}")
```

## Learn more

- **Product page:** [weaviate.io/product/engram](https://weaviate.io/product/engram)
- **Weaviate Cloud console:** [console.weaviate.cloud/engram](https://console.weaviate.cloud/engram)
- **Sign up:** [console.weaviate.cloud](https://console.weaviate.cloud)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [BSD 3-Clause License](LICENSE).

## Support

For questions or help, reach out to [support@weaviate.io](mailto:support@weaviate.io).
