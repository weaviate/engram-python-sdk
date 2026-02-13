def test_public_imports() -> None:
    import engram
    from engram import (
        APIError,
        AsyncEngramClient,
        AuthError,
        EngramClient,
        EngramError,
        ValidationError,
    )

    assert isinstance(EngramClient, type)
    assert isinstance(AsyncEngramClient, type)
    assert isinstance(EngramError, type)
    assert isinstance(APIError, type)
    assert isinstance(AuthError, type)
    assert isinstance(ValidationError, type)

    expected_exports = {
        "APIError",
        "AsyncEngramClient",
        "AuthError",
        "EngramClient",
        "EngramError",
        "ValidationError",
        "__version__",
    }
    assert set(engram.__all__) == expected_exports


def test_version_present() -> None:
    import engram

    assert isinstance(engram.__version__, str)
    assert engram.__version__
