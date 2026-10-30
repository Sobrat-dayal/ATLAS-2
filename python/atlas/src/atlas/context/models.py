"""
Domain models for ATLAS Stage 121: Global Workspace Linking.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .enums import ContextDimension, ContextScope, SubscriptionMode


@dataclass
class ResolvedEntity:
    """Canonical verified financial entity resolution result."""

    entity_id: str
    entity_type: str  # e.g. INSTRUMENT, COMPANY, PORTFOLIO, BENCHMARK, ECONOMIC_SERIES
    canonical_name: str
    display_name: str
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "canonical_name": self.canonical_name,
            "display_name": self.display_name,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "currency": self.currency,
            "country": self.country,
            "metadata": self.metadata,
        }


@dataclass
class LinkSubscription:
    """Panel instance membership in a link channel."""

    subscription_id: str
    channel_id: str
    panel_instance_id: str
    mode: SubscriptionMode = SubscriptionMode.BIDIRECTIONAL
    inbound_dimensions: list[ContextDimension] = field(default_factory=list)
    outbound_dimensions: list[ContextDimension] = field(default_factory=list)
    active: bool = True
    priority_policy: str = "NORMAL"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "channel_id": self.channel_id,
            "panel_instance_id": self.panel_instance_id,
            "mode": self.mode.value,
            "inbound_dimensions": [d.value for d in self.inbound_dimensions],
            "outbound_dimensions": [d.value for d in self.outbound_dimensions],
            "active": self.active,
            "priority_policy": self.priority_policy,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class LinkChannel:
    """A synchronized communication channel for financial context."""

    channel_id: str
    owner_user_id: str
    name: str
    display_color_token: str
    workspace_id: Optional[str] = None
    scope: ContextScope = ContextScope.WORKSPACE
    enabled: bool = True
    supported_dimensions: list[ContextDimension] = field(
        default_factory=lambda: [
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
            ContextDimension.PORTFOLIO,
            ContextDimension.DATE_RANGE,
            ContextDimension.TIMEFRAME,
            ContextDimension.REPORTING_CURRENCY,
        ]
    )
    context_snapshot: dict[str, Any] = field(default_factory=dict)
    revision: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "owner_user_id": self.owner_user_id,
            "workspace_id": self.workspace_id,
            "scope": self.scope.value,
            "name": self.name,
            "display_color_token": self.display_color_token,
            "enabled": self.enabled,
            "supported_dimensions": [d.value for d in self.supported_dimensions],
            "context_snapshot": self.context_snapshot,
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ContextSelectionEvent:
    """Envelope for a user selection event propagated across linked subscribers."""

    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    causation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    origin_user_id: str = ""
    origin_workspace_id: Optional[str] = None
    origin_panel_instance_id: Optional[str] = None
    channel_id: str = ""
    scope: ContextScope = ContextScope.WORKSPACE
    dimension: ContextDimension = ContextDimension.INSTRUMENT
    canonical_target_id: str = ""
    target_type: str = "INSTRUMENT"
    payload: dict[str, Any] = field(default_factory=dict)
    context_revision: int = 1
    emitted_at: datetime = field(default_factory=datetime.utcnow)
    selection_reason: str = "USER_CLICK"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "causation_id": self.causation_id,
            "correlation_id": self.correlation_id,
            "origin_user_id": self.origin_user_id,
            "origin_workspace_id": self.origin_workspace_id,
            "origin_panel_instance_id": self.origin_panel_instance_id,
            "channel_id": self.channel_id,
            "scope": self.scope.value,
            "dimension": self.dimension.value,
            "canonical_target_id": self.canonical_target_id,
            "target_type": self.target_type,
            "payload": self.payload,
            "context_revision": self.context_revision,
            "emitted_at": self.emitted_at.isoformat(),
            "selection_reason": self.selection_reason,
        }


@dataclass
class PanelContextCapability:
    """Contract describing a panel type's inbound/outbound linking abilities."""

    panel_type_id: str
    publishable_dimensions: list[ContextDimension]
    subscribable_dimensions: list[ContextDimension]
    accepted_entity_types: list[str]
    required_transformations: dict[str, str] = field(default_factory=dict)
    supported_timeframes: list[str] = field(default_factory=list)
    supports_as_of: bool = False
    supports_currency: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel_type_id": self.panel_type_id,
            "publishable_dimensions": [d.value for d in self.publishable_dimensions],
            "subscribable_dimensions": [d.value for d in self.subscribable_dimensions],
            "accepted_entity_types": self.accepted_entity_types,
            "required_transformations": self.required_transformations,
            "supported_timeframes": self.supported_timeframes,
            "supports_as_of": self.supports_as_of,
            "supports_currency": self.supports_currency,
        }
