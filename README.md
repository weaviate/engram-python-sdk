# weaviate-engram

> [!WARNING]
> **Engram is currently in preview.** While in preview (pre-1.0), the API is subject to breaking changes without notice. Use in production at your own risk.

Engram is a fully managed memory service by Weaviate. It lets you add persistent, personalized memory to AI assistants and agents — no infrastructure to set up or manage. When you add a memory, Engram processes it asynchronously through a background pipeline that extracts, deduplicates, and reconciles facts. Memories are scoped at three levels — project, user, and conversation — which can be mixed and matched freely. Each scope is backed by Weaviate's multi-tenant architecture, ensuring strong isolation between tenants.

## Requirements

- Python 3.11 to 3.14

## Installation

```bash
pip install weaviate-engram
```

```bash
uv add weaviate-engram
```

## Quick Start

Create a project and get an API key at [console.weaviate.cloud/engram](https://console.weaviate.cloud/engram).

```python
from engram import EngramClient

client = EngramClient(api_key="your-api-key")
```

**Add a memory from a string:**

```python
run = client.memories.add("Alice prefers async Python and avoids Java.", user_id="user_123")
```

**Add a memory from a conversation:**

```python
run = client.memories.add(
    [
        {"role": "user", "content": "What's the best way to handle retries?"},
        {"role": "assistant", "content": "Exponential backoff with jitter is the standard approach."},
        {"role": "user", "content": "Got it — I'll use that in my HTTP client."},
    ],
    user_id="user_123",
)
```

**Search memories:**

```python
results = client.memories.search(query="What does Alice think about Python?", user_id="user_123")
for memory in results:
    print(memory.content)
```

**Wait for a run to complete** (memory processing is asynchronous):

```python
status = client.runs.wait(run.run_id, timeout=60.0)
print(status.status)  # "completed" or "failed"
print(f"+{len(status.memories_created)} ~{len(status.memories_updated)} -{len(status.memories_deleted)}")
```

## Async Client

An async client is also available:

```python
from engram import AsyncEngramClient

client = AsyncEngramClient(api_key="your-api-key")

run = await client.memories.add("Alice prefers async Python and avoids Java.", user_id="user_123")
results = await client.memories.search(query="What does Alice think about Python?", user_id="user_123")
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [BSD 3-Clause License](LICENSE).

## Support

For questions or help, reach out to [support@weaviate.io](mailto:support@weaviate.io).
