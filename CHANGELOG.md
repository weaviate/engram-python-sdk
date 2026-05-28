# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-05-08

- Added a `properties` parameter to `memories.add()` and `memories.search()` for attaching and filtering on arbitrary string key-value pairs (e.g. `conversation_id`).
- Added per-topic property filters via the new `Topic` model, letting search override or clear inherited global filters on a per-topic basis.

## [0.5.0] - 2026-03-20

- `memories.add()` now accepts a list of strings as input, producing one memory per string.
- Added `PreExtractedInput` and `PreExtractedItem` for callers that already have extracted facts and want to bypass the extraction step in the pipeline.

## [0.4.0] - 2026-03-10

- Standardised conversation input on the OpenAI Chat Completions format. Added `ConversationInput`, `MessageInput`, and the `ToolCallInput` / `ToolCallFuncInput` / `ToolCallCustomInput` models.
- Added `"fetch"` as a `retrieval_type` option on `RetrievalConfig`.

## [0.3.0] - 2026-03-05

- Updated input content types on `memories.add()`.
- Removed an unnecessary memory body wrapper from request payloads.

## [0.2.0] - 2026-03-02

- Updated request and response models for `memories.get()` and `memories.delete()`.
- README touch-up.

## [0.1.0] - 2026-02-20

- Initial functional release.
- Added `memories.add()`, `memories.get()`, `memories.delete()`, and `memories.search()`.
- Added `runs.get()` and `runs.wait()` for tracking the asynchronous pipeline.
- Sync (`EngramClient`) and async (`AsyncEngramClient`) clients.
- Initial SDK bootstrap with `uv` + `uv_build`, `src` package layout, typed `engram` client skeletons, ruff/mypy/pytest/pre-commit/CI, and OIDC-based PyPI release workflow.
