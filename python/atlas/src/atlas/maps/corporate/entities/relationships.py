"""Corporate relationship semantic models and definitions (Stage 132)."""

from __future__ import annotations

from enum import Enum


class EntityRelationshipCategory(str, Enum):
    """Categorical classification of corporate relationship semantics."""

    OWNERSHIP = "OWNERSHIP"
    CONTROL = "CONTROL"
    AFFILIATION = "AFFILIATION"
    ISSUANCE = "ISSUANCE"


CANONICAL_CORPORATE_RELATIONSHIP_TYPES = {
    "PARENT_OF": {
        "category": EntityRelationshipCategory.OWNERSHIP,
        "inverse": "SUBSIDIARY_OF",
        "description": "Parent entity holds majority equity or consolidation rights in target subsidiary.",
        "implies_ownership": True,
    },
    "SUBSIDIARY_OF": {
        "category": EntityRelationshipCategory.OWNERSHIP,
        "inverse": "PARENT_OF",
        "description": "Target entity is a subsidiary owned or controlled by parent.",
        "implies_ownership": False,
    },
    "CONTROLLED_BY": {
        "category": EntityRelationshipCategory.CONTROL,
        "inverse": "CONTROLS",
        "description": "Target entity exercises governance or operational control.",
        "implies_ownership": False,
    },
    "AFFILIATED_WITH": {
        "category": EntityRelationshipCategory.AFFILIATION,
        "inverse": "AFFILIATED_WITH",
        "description": "Entity shares minority holding, common management, or joint corporate umbrella.",
        "implies_ownership": False,
    },
    "ISSUER_OF": {
        "category": EntityRelationshipCategory.ISSUANCE,
        "inverse": "ISSUED_BY",
        "description": "Legal entity or corporate issuer that issues a tradable security/instrument.",
        "implies_ownership": False,
    },
}

