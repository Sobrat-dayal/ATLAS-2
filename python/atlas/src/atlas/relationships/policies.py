from typing import Callable, Dict

from atlas.entities.models import Entity, EntityType

PolicyValidator = Callable[[Entity], bool]

_POLICIES: Dict[str, PolicyValidator] = {}


def register_policy(key: str, validator: PolicyValidator) -> None:
    _POLICIES[key] = validator


def get_policy(key: str) -> PolicyValidator:
    if key not in _POLICIES:
        raise ValueError(f"Unknown policy key: {key}")
    return _POLICIES[key]


# Define policies
register_policy("company", lambda e: e.entity_type == EntityType.COMPANY)
register_policy("security", lambda e: e.entity_type == EntityType.SECURITY)
register_policy("exchange", lambda e: e.entity_type == EntityType.EXCHANGE)
register_policy("facility", lambda e: e.entity_type == EntityType.FACILITY)
register_policy(
    "facility_or_exchange", lambda e: e.entity_type in (EntityType.FACILITY, EntityType.EXCHANGE)
)
register_policy("person", lambda e: e.entity_type == EntityType.PERSON)
register_policy("research_document", lambda e: e.entity_type == EntityType.RESEARCH_DOCUMENT)
