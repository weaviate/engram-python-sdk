from dataclasses import dataclass


@dataclass(slots=True)
class Scoping:
    user_scoped: bool
    scope_properties: list[str]


@dataclass(slots=True)
class TopicDetails:
    name: str
    description: str
    is_bounded: bool
    scoping: Scoping


@dataclass(slots=True)
class Group:
    group_id: str
    name: str
    topics: list[TopicDetails]
    scoping: Scoping
