"""Predicate Registry and Validation Rules (Stage 136).

Enforces strictly typed directional semantics, source-to-target compatibility,
and explicit prohibitions against speculative or causal predicates (e.g., AFFECTS, DAMAGED).
"""

from typing import Dict, List, Set, Tuple
from ..domain import GraphNodeType, PredicateType
from ..errors import InvalidPredicateError, ProhibitedPredicateError

# Prohibited predicates that imply economic loss or unverified causality without evidence
PROHIBITED_PREDICATES: Set[str] = {
    "AFFECTS",
    "AFFECTED_BY",
    "CAUSED_LOSS",
    "DAMAGED",
    "EXPOSED_TO",
    "RISK_OF",
    "IMPACTED",
    "DESTROYED",
    "BANKRUPTED",
}

# Compatibility mapping: Predicate -> Allowed (Source Type, Target Type) tuples
# Note: An empty set or wildcard allows broad compatibility when designated.
ALLOWED_NODE_PAIRS: Dict[PredicateType, Set[Tuple[GraphNodeType, GraphNodeType]]] = {
    PredicateType.DIRECT_SUBJECT: {
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
        (GraphNodeType.EVENT, GraphNodeType.ISSUER),
        (GraphNodeType.EVENT, GraphNodeType.LEGAL_ENTITY),
        (GraphNodeType.EVENT, GraphNodeType.FINANCIAL_INSTRUMENT),
        (GraphNodeType.EVENT, GraphNodeType.CENTRAL_BANK),
        (GraphNodeType.EVENT, GraphNodeType.REGULATORY_AUTHORITY),
        (GraphNodeType.EVENT, GraphNodeType.COUNTRY),
    },
    PredicateType.EXPLICITLY_MENTIONS: {
        (GraphNodeType.EVENT, nt) for nt in GraphNodeType
    },
    PredicateType.ANNOUNCED_BY: {
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
        (GraphNodeType.EVENT, GraphNodeType.ISSUER),
        (GraphNodeType.EVENT, GraphNodeType.CENTRAL_BANK),
        (GraphNodeType.EVENT, GraphNodeType.REGULATORY_AUTHORITY),
        (GraphNodeType.EVENT, GraphNodeType.LEGAL_ENTITY),
    },
    PredicateType.ISSUED_BY: {
        (GraphNodeType.EVENT, GraphNodeType.ISSUER),
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
        (GraphNodeType.EVENT, GraphNodeType.CENTRAL_BANK),
        (GraphNodeType.EVENT, GraphNodeType.REGULATORY_AUTHORITY),
    },
    PredicateType.REGULATED_BY: {
        (GraphNodeType.EVENT, GraphNodeType.REGULATORY_AUTHORITY),
    },
    PredicateType.OFFICIALLY_DESIGNATES: {
        (GraphNodeType.EVENT, GraphNodeType.LEGAL_ENTITY),
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
    },
    PredicateType.OFFICIAL_ACTION_TARGET: {
        (GraphNodeType.EVENT, GraphNodeType.LEGAL_ENTITY),
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
        (GraphNodeType.EVENT, GraphNodeType.ISSUER),
    },
    PredicateType.CORPORATE_ACTION_PARTICIPANT: {
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
        (GraphNodeType.EVENT, GraphNodeType.ISSUER),
        (GraphNodeType.EVENT, GraphNodeType.LEGAL_ENTITY),
    },
    PredicateType.CORPORATE_ACTION_TARGET: {
        (GraphNodeType.EVENT, GraphNodeType.COMPANY),
        (GraphNodeType.EVENT, GraphNodeType.ISSUER),
        (GraphNodeType.EVENT, GraphNodeType.LEGAL_ENTITY),
    },
    PredicateType.CONCERNS_INSTRUMENT: {
        (GraphNodeType.EVENT, GraphNodeType.FINANCIAL_INSTRUMENT),
    },
    PredicateType.RELEASES_INDICATOR: {
        (GraphNodeType.EVENT, GraphNodeType.ECONOMIC_INDICATOR),
    },
    PredicateType.DECIDED_BY: {
        (GraphNodeType.EVENT, GraphNodeType.CENTRAL_BANK),
    },
    PredicateType.HAS_ISSUING_JURISDICTION: {
        (GraphNodeType.EVENT, GraphNodeType.COUNTRY),
        (GraphNodeType.EVENT, GraphNodeType.ADMINISTRATIVE_REGION),
    },
    PredicateType.OCCURRED_IN: {
        (GraphNodeType.EVENT, GraphNodeType.COUNTRY),
        (GraphNodeType.EVENT, GraphNodeType.ADMINISTRATIVE_REGION),
    },
    PredicateType.REPORTED_AT: {
        (GraphNodeType.EVENT, GraphNodeType.COUNTRY),
        (GraphNodeType.EVENT, GraphNodeType.ADMINISTRATIVE_REGION),
    },
    PredicateType.REFERENCES_COMMODITY: {
        (GraphNodeType.EVENT, GraphNodeType.COMMODITY),
    },
    PredicateType.REFERENCES_SECTOR: {
        (GraphNodeType.EVENT, GraphNodeType.SECTOR),
    },
    PredicateType.REFERENCES_INDUSTRY: {
        (GraphNodeType.EVENT, GraphNodeType.INDUSTRY),
    },
    PredicateType.REFERENCES_FACILITY: {
        (GraphNodeType.EVENT, GraphNodeType.CORPORATE_FACILITY),
    },
    PredicateType.REFERENCES_INFRASTRUCTURE_ASSET: {
        (GraphNodeType.EVENT, GraphNodeType.INFRASTRUCTURE_ASSET),
    },
    PredicateType.GEOGRAPHICALLY_NEAR: {
        (GraphNodeType.EVENT, GraphNodeType.INFRASTRUCTURE_ASSET),
        (GraphNodeType.EVENT, GraphNodeType.CORPORATE_FACILITY),
    },
    PredicateType.SOURCE_REPORTED_ASSOCIATION: {
        (GraphNodeType.EVENT, nt) for nt in GraphNodeType
    },
    # Event-to-Event
    PredicateType.REVISES: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    PredicateType.SUPERSEDES: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    PredicateType.CORRECTS: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    PredicateType.RETRACTS: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    PredicateType.FORMAL_FOLLOW_UP_TO: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    PredicateType.IMPLEMENTS: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    PredicateType.OFFICIALLY_RESPONDS_TO: {(GraphNodeType.EVENT, GraphNodeType.EVENT)},
    # Entity-to-Entity Structural Relations
    PredicateType.SUBSIDIARY_OF: {
        (GraphNodeType.COMPANY, GraphNodeType.COMPANY),
        (GraphNodeType.LEGAL_ENTITY, GraphNodeType.LEGAL_ENTITY),
        (GraphNodeType.LEGAL_ENTITY, GraphNodeType.COMPANY),
        (GraphNodeType.COMPANY, GraphNodeType.LEGAL_ENTITY),
    },
    PredicateType.PARENT_OF: {
        (GraphNodeType.COMPANY, GraphNodeType.COMPANY),
        (GraphNodeType.LEGAL_ENTITY, GraphNodeType.LEGAL_ENTITY),
        (GraphNodeType.LEGAL_ENTITY, GraphNodeType.COMPANY),
        (GraphNodeType.COMPANY, GraphNodeType.LEGAL_ENTITY),
    },
    PredicateType.ISSUED_BY_COMPANY: {
        (GraphNodeType.FINANCIAL_INSTRUMENT, GraphNodeType.COMPANY),
        (GraphNodeType.FINANCIAL_INSTRUMENT, GraphNodeType.ISSUER),
    },
    PredicateType.OPERATED_BY: {
        (GraphNodeType.CORPORATE_FACILITY, GraphNodeType.COMPANY),
        (GraphNodeType.CORPORATE_FACILITY, GraphNodeType.LEGAL_ENTITY),
        (GraphNodeType.INFRASTRUCTURE_ASSET, GraphNodeType.COMPANY),
        (GraphNodeType.INFRASTRUCTURE_ASSET, GraphNodeType.LEGAL_ENTITY),
    },
    PredicateType.LOCATED_IN: {
        (GraphNodeType.CORPORATE_FACILITY, GraphNodeType.COUNTRY),
        (GraphNodeType.CORPORATE_FACILITY, GraphNodeType.ADMINISTRATIVE_REGION),
        (GraphNodeType.INFRASTRUCTURE_ASSET, GraphNodeType.COUNTRY),
        (GraphNodeType.INFRASTRUCTURE_ASSET, GraphNodeType.ADMINISTRATIVE_REGION),
        (GraphNodeType.COMPANY, GraphNodeType.COUNTRY),
    },
    PredicateType.PRIMARY_EXCHANGE_IN: {
        (GraphNodeType.FINANCIAL_INSTRUMENT, GraphNodeType.COUNTRY),
    },
    PredicateType.COMPRISING_SECTOR: {
        (GraphNodeType.COMPANY, GraphNodeType.SECTOR),
    },
}


def validate_predicate_allowed(
    predicate_str: str,
    source_type: GraphNodeType,
    target_type: GraphNodeType,
) -> PredicateType:
    """Validates that a predicate exists, is not prohibited, and is compatible with source/target types."""
    # Check prohibited predicates
    upper_pred = predicate_str.upper()
    if upper_pred in PROHIBITED_PREDICATES:
        raise ProhibitedPredicateError(predicate=upper_pred)

    try:
        predicate = PredicateType(upper_pred)
    except ValueError:
        raise InvalidPredicateError(
            predicate=predicate_str,
            reason=f"Unknown predicate '{predicate_str}'."
        )

    allowed_pairs = ALLOWED_NODE_PAIRS.get(predicate)
    if allowed_pairs is not None:
        if (source_type, target_type) not in allowed_pairs:
            raise InvalidPredicateError(
                predicate=predicate.value,
                reason=f"Cannot link source type '{source_type.value}' to target type '{target_type.value}' using '{predicate.value}'."
            )

    return predicate
