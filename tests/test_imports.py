def test_public_imports() -> None:
    import engram
    from engram import (  # noqa: F401
        APIError,
        AsyncEngramClient,
        AuthenticationError,
        CommittedOperation,
        CommittedOperations,
        ConnectionError,
        EngramClient,
        EngramError,
        EngramTimeoutError,
        Memory,
        PreExtractedContent,
        RetrievalConfig,
        Run,
        RunStatus,
        SearchResults,
        ValidationError,
    )

    assert isinstance(EngramClient, type)
    assert isinstance(AsyncEngramClient, type)
    assert isinstance(EngramError, type)
    assert isinstance(APIError, type)
    assert isinstance(AuthenticationError, type)
    assert isinstance(ValidationError, type)
    assert isinstance(EngramTimeoutError, type)
    assert isinstance(Memory, type)
    assert isinstance(Run, type)
    assert isinstance(RunStatus, type)
    assert isinstance(SearchResults, type)
    assert isinstance(PreExtractedContent, type)
    assert isinstance(RetrievalConfig, type)
    assert isinstance(CommittedOperation, type)
    assert isinstance(CommittedOperations, type)

    expected_exports = {
        "APIError",
        "AsyncEngramClient",
        "AuthenticationError",
        "CommittedOperation",
        "CommittedOperations",
        "ConnectionError",
        "EngramClient",
        "EngramError",
        "EngramTimeoutError",
        "Memory",
        "PreExtractedContent",
        "RetrievalConfig",
        "Run",
        "RunStatus",
        "SearchResults",
        "ValidationError",
        "__version__",
    }
    assert set(engram.__all__) == expected_exports


def test_version_present() -> None:
    import engram

    assert isinstance(engram.__version__, str)
    assert engram.__version__
