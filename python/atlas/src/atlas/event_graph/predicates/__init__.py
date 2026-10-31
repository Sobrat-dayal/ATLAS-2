"""Predicates module exports."""

from .registry import (
    ALLOWED_NODE_PAIRS,
    PROHIBITED_PREDICATES,
    validate_predicate_allowed,
)

__all__ = [
    "ALLOWED_NODE_PAIRS",
    "PROHIBITED_PREDICATES",
    "validate_predicate_allowed",
]
