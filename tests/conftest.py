from typing import Any

import pytest


@pytest.fixture
def sample_group_response() -> dict[str, Any]:
    """The "default" group: user-scoped with scope properties and an unbounded topic."""
    return {
        "group_id": "11111111-2222-3333-4444-555555555555",
        "name": "default",
        "scoping": {"user_scoped": True, "scope_properties": ["account_id"]},
        "topics": [
            {
                "topic_name": "facts",
                "description": "General facts about the user",
                "is_bounded": False,
                "scoping": {"user_scoped": True, "scope_properties": ["account_id"]},
            }
        ],
    }


@pytest.fixture
def support_group_response() -> dict[str, Any]:
    """The "support" group: unscoped (scope_properties omitted, per the server's
    omitempty behaviour) with a bounded topic."""
    return {
        "group_id": "66666666-7777-8888-9999-000000000000",
        "name": "support",
        "scoping": {"user_scoped": False},
        "topics": [
            {
                "topic_name": "tickets",
                "description": "Support tickets",
                "is_bounded": True,
                "scoping": {"user_scoped": False},
            }
        ],
    }


@pytest.fixture
def sample_group_list_response(
    sample_group_response: dict[str, Any],
    support_group_response: dict[str, Any],
) -> dict[str, Any]:
    return {"groups": [sample_group_response, support_group_response]}
