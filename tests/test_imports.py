def test_public_imports() -> None:
    import engram
    from engram import (  # noqa: F401
        APIError,
        AsyncEngramClient,
        AuthenticationError,
        BM25Retrieval,
        CommittedOperation,
        CommittedOperations,
        ConnectionError,
        ConversationInput,
        EngramClient,
        EngramError,
        EngramTimeoutError,
        FetchRetrieval,
        Group,
        HybridRetrieval,
        Memory,
        MessageInput,
        NamedRetrievalType,
        PreExtractedInput,
        PreExtractedItem,
        RetrievalConfigModel,
        Run,
        RunStatus,
        Scoping,
        SearchResults,
        StringInput,
        ToolCallCustomInput,
        ToolCallFuncInput,
        ToolCallInput,
        Topic,
        TopicDetails,
        ValidationError,
        VectorRetrieval,
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
    assert isinstance(PreExtractedInput, type)
    assert isinstance(PreExtractedItem, type)
    assert isinstance(VectorRetrieval, type)
    assert isinstance(BM25Retrieval, type)
    assert isinstance(HybridRetrieval, type)
    assert isinstance(FetchRetrieval, type)
    assert isinstance(CommittedOperation, type)
    assert isinstance(CommittedOperations, type)
    assert isinstance(ConversationInput, type)
    assert isinstance(MessageInput, type)
    assert isinstance(StringInput, type)
    assert isinstance(ToolCallCustomInput, type)
    assert isinstance(ToolCallFuncInput, type)
    assert isinstance(ToolCallInput, type)
    assert isinstance(Topic, type)
    assert isinstance(Group, type)
    assert isinstance(Scoping, type)
    assert isinstance(TopicDetails, type)

    expected_exports = {
        "APIError",
        "AsyncEngramClient",
        "AuthenticationError",
        "BM25Retrieval",
        "CommittedOperation",
        "CommittedOperations",
        "ConnectionError",
        "ConversationInput",
        "EngramClient",
        "EngramError",
        "EngramTimeoutError",
        "FetchRetrieval",
        "Group",
        "HybridRetrieval",
        "Memory",
        "MessageInput",
        "NamedRetrievalType",
        "PreExtractedInput",
        "PreExtractedItem",
        "RetrievalConfigModel",
        "Run",
        "RunStatus",
        "Scoping",
        "SearchResults",
        "StringInput",
        "ToolCallCustomInput",
        "ToolCallFuncInput",
        "ToolCallInput",
        "Topic",
        "TopicDetails",
        "ValidationError",
        "VectorRetrieval",
        "__version__",
    }
    assert set(engram.__all__) == expected_exports


def test_version_present() -> None:
    import engram

    assert isinstance(engram.__version__, str)
    assert engram.__version__
