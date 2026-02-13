# Contributing

## Setup

```bash
uv sync --all-groups
```

## Run Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q
```

## Pre-commit

Install hooks:

```bash
uv run pre-commit install
```

Run hooks manually:

```bash
uv run pre-commit run --all-files
```

## Release Process

1. Update `version` in `pyproject.toml` (SemVer).
2. Merge changes to `main`.
3. Create and push a matching tag: `vX.Y.Z`.
4. GitHub Actions runs `.github/workflows/release.yml`:
   - validates tag/version match,
   - builds with `uv build --no-sources`,
   - publishes with PyPI Trusted Publishing (OIDC).

No `PYPI_API_TOKEN` secret is required. Trusted Publisher must be configured in the PyPI project settings.
