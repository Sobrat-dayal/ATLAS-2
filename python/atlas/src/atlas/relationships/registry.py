from dataclasses import dataclass
from typing import Dict, List, Optional

from .types import RelationshipCategory


@dataclass
class RelationshipTypeDefinition:
    key: str
    name: str
    category: str
    canonical_key: str
    source_policy_key: str
    target_policy_key: str
    inverse_key: Optional[str] = None
    is_symmetric: bool = False
    allows_self: bool = False
    description: Optional[str] = None
    is_system: bool = True


_RELATIONSHIP_TYPES: Dict[str, RelationshipTypeDefinition] = {}


def register_relationship_type(
    key: str,
    name: str,
    category: str,
    canonical_key: str,
    source_policy_key: str,
    target_policy_key: str,
    inverse_key: Optional[str] = None,
    is_symmetric: bool = False,
    allows_self: bool = False,
    description: Optional[str] = None,
    is_system: bool = True,
) -> None:
    _RELATIONSHIP_TYPES[key] = RelationshipTypeDefinition(
        key=key,
        name=name,
        category=category,
        canonical_key=canonical_key,
        source_policy_key=source_policy_key,
        target_policy_key=target_policy_key,
        inverse_key=inverse_key,
        is_symmetric=is_symmetric,
        allows_self=allows_self,
        description=description,
        is_system=is_system,
    )


def get_relationship_type_definition(key: str) -> Optional[RelationshipTypeDefinition]:
    return _RELATIONSHIP_TYPES.get(key)


def get_all_relationship_type_definitions() -> List[RelationshipTypeDefinition]:
    return list(_RELATIONSHIP_TYPES.values())


# Register core relationship types
register_relationship_type(
    "issued",
    "Issued",
    RelationshipCategory.CORPORATE.value,
    "issued",
    "company",
    "security",
    "issued_by",
    False,
    False,
    "Company issued Security",
)
register_relationship_type(
    "issued_by",
    "Issued By",
    RelationshipCategory.CORPORATE.value,
    "issued",
    "security",
    "company",
    "issued",
    False,
    False,
    "Security issued by Company",
)

register_relationship_type(
    "listed_on",
    "Listed On",
    RelationshipCategory.MARKET.value,
    "listed_on",
    "security",
    "exchange",
    "lists",
    False,
    False,
    "Security listed on Exchange",
)
register_relationship_type(
    "lists",
    "Lists",
    RelationshipCategory.MARKET.value,
    "listed_on",
    "exchange",
    "security",
    "listed_on",
    False,
    False,
    "Exchange lists Security",
)

register_relationship_type(
    "parent_of",
    "Parent Of",
    RelationshipCategory.OWNERSHIP.value,
    "parent_of",
    "company",
    "company",
    "subsidiary_of",
    False,
    False,
    "Company is parent of Company",
)
register_relationship_type(
    "subsidiary_of",
    "Subsidiary Of",
    RelationshipCategory.OWNERSHIP.value,
    "parent_of",
    "company",
    "company",
    "parent_of",
    False,
    False,
    "Company is subsidiary of Company",
)

register_relationship_type(
    "competitor_of",
    "Competitor Of",
    RelationshipCategory.COMPETITION.value,
    "competitor_of",
    "company",
    "company",
    "competitor_of",
    True,
    False,
    "Company is competitor of Company",
)

register_relationship_type(
    "supplies",
    "Supplies",
    RelationshipCategory.SUPPLY_CHAIN.value,
    "supplies",
    "company",
    "company",
    "supplied_by",
    False,
    False,
    "Company supplies Company",
)
register_relationship_type(
    "supplied_by",
    "Supplied By",
    RelationshipCategory.SUPPLY_CHAIN.value,
    "supplies",
    "company",
    "company",
    "supplies",
    False,
    False,
    "Company supplied by Company",
)

register_relationship_type(
    "owns",
    "Owns",
    RelationshipCategory.OWNERSHIP.value,
    "owns",
    "company",
    "facility",
    "owned_by",
    False,
    False,
    "Company owns Facility",
)
register_relationship_type(
    "owned_by",
    "Owned By",
    RelationshipCategory.OWNERSHIP.value,
    "owns",
    "facility",
    "company",
    "owns",
    False,
    False,
    "Facility owned by Company",
)

register_relationship_type(
    "operates",
    "Operates",
    RelationshipCategory.OPERATIONS.value,
    "operates",
    "company",
    "facility_or_exchange",
    "operated_by",
    False,
    False,
    "Company operates Facility or Exchange",
)
register_relationship_type(
    "operated_by",
    "Operated By",
    RelationshipCategory.OPERATIONS.value,
    "operates",
    "facility_or_exchange",
    "company",
    "operates",
    False,
    False,
    "Facility or Exchange operated by Company",
)

register_relationship_type(
    "authored",
    "Authored",
    RelationshipCategory.RESEARCH.value,
    "authored",
    "person",
    "research_document",
    "authored_by",
    False,
    False,
    "Person authored Research Document",
)
register_relationship_type(
    "authored_by",
    "Authored By",
    RelationshipCategory.RESEARCH.value,
    "authored",
    "research_document",
    "person",
    "authored",
    False,
    False,
    "Research Document authored by Person",
)
