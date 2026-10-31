"""Event Taxonomy Module (Stage 135)."""

from .classifications import CANONICAL_TAXONOMY
from .payloads import (
    CentralBankEventPayload,
    CorporateActionEventPayload,
    EarningsEventPayload,
    EconomicReleasePayload,
    GeopoliticalEventPayload,
    PhysicalDisasterEventPayload,
    RegulatoryEventPayload,
    SanctionsEventPayload,
)
from .registry import EventTaxonomyRegistry, event_taxonomy_registry

__all__ = [
    "CANONICAL_TAXONOMY",
    "CentralBankEventPayload",
    "CorporateActionEventPayload",
    "EarningsEventPayload",
    "EconomicReleasePayload",
    "GeopoliticalEventPayload",
    "PhysicalDisasterEventPayload",
    "RegulatoryEventPayload",
    "SanctionsEventPayload",
    "EventTaxonomyRegistry",
    "event_taxonomy_registry",
]
