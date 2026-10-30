"""Domain models, enums, and data contracts for Stage 125 AI Context Awareness."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ContextType(str, Enum):
    """Canonical categories of financial and platform context."""

    PAGE_CONTEXT = "PAGE_CONTEXT"
    MODULE_CONTEXT = "MODULE_CONTEXT"
    INSTRUMENT_CONTEXT = "INSTRUMENT_CONTEXT"
    COMPANY_CONTEXT = "COMPANY_CONTEXT"
    CHART_CONTEXT = "CHART_CONTEXT"
    WATCHLIST_CONTEXT = "WATCHLIST_CONTEXT"
    SCREENER_CONTEXT = "SCREENER_CONTEXT"
    ECONOMICS_CONTEXT = "ECONOMICS_CONTEXT"
    NEWS_CONTEXT = "NEWS_CONTEXT"
    RESEARCH_CONTEXT = "RESEARCH_CONTEXT"
    PORTFOLIO_CONTEXT = "PORTFOLIO_CONTEXT"
    RISK_CONTEXT = "RISK_CONTEXT"
    OPTIONS_CONTEXT = "OPTIONS_CONTEXT"
    DATA_CONTEXT = "DATA_CONTEXT"
    SAVED_RESOURCE_CONTEXT = "SAVED_RESOURCE_CONTEXT"
    WORKSPACE_CONTEXT = "WORKSPACE_CONTEXT"
    WORKSPACE_PANEL_CONTEXT = "WORKSPACE_PANEL_CONTEXT"
    LINKED_CONTEXT = "LINKED_CONTEXT"
    USER_SUPPLIED_CONTEXT = "USER_SUPPLIED_CONTEXT"


class ContextMode(str, Enum):
    """User-controlled context sharing modes."""

    OFF = "OFF"
    FOCUSED = "FOCUSED"
    WORKSPACE = "WORKSPACE"
    CUSTOM = "CUSTOM"


class DataQualityStatus(str, Enum):
    """Source data quality and integrity ratings."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    MISSING = "MISSING"
    RESTRICTED = "RESTRICTED"
    UNVERIFIED = "UNVERIFIED"
    INCONSISTENT = "INCONSISTENT"


class ProviderDisclosureStatus(str, Enum):
    """Permitted model provider disclosure policy."""

    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    ANONYMIZED_ONLY = "ANONYMIZED_ONLY"
    PROHIBITED = "PROHIBITED"


class ContextExclusionReason(str, Enum):
    """Reasons why an available source was excluded from prompt assembly."""

    NOT_RELEVANT = "NOT_RELEVANT"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    PROVIDER_DISCLOSURE_RESTRICTED = "PROVIDER_DISCLOSURE_RESTRICTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    TOO_LARGE = "TOO_LARGE"
    STALE = "STALE"
    INCOMPATIBLE_AS_OF = "INCOMPATIBLE_AS_OF"
    AMBIGUOUS_ENTITY = "AMBIGUOUS_ENTITY"
    UNSUPPORTED_CONTEXT_TYPE = "UNSUPPORTED_CONTEXT_TYPE"
    EXPLICITLY_EXCLUDED = "EXPLICITLY_EXCLUDED"
    MODE_RESTRICTED = "MODE_RESTRICTED"


@dataclass
class AtlasAiContextItem:
    """Individual typed context item verified from authorized financial foundations."""

    context_item_id: str
    context_type: ContextType
    canonical_target_id: str
    source_module: str
    source_reference: str
    schema_version: int = 1
    as_of: Optional[str] = None
    observed_at: Optional[str] = None
    source_updated_at: Optional[str] = None
    reporting_currency: Optional[str] = None
    units: Optional[str] = None
    data_quality_status: DataQualityStatus = DataQualityStatus.COMPLETE
    permission_status: str = "AUTHORIZED"
    model_disclosure_status: ProviderDisclosureStatus = ProviderDisclosureStatus.ALLOWED
    content_summary: str = ""
    structured_payload: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""
    estimated_tokens: int = 0
    is_pinned: bool = False
    relevance_score: float = 1.0
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def provider_disclosure_status(self) -> ProviderDisclosureStatus:
        return self.model_disclosure_status

    @provider_disclosure_status.setter
    def provider_disclosure_status(self, value: ProviderDisclosureStatus) -> None:
        self.model_disclosure_status = value

    def compute_content_hash(self) -> str:
        """Computes deterministic SHA-256 hash of structured payload."""
        payload_str = json.dumps(self.structured_payload, sort_keys=True)
        self.content_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        return self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_item_id": self.context_item_id,
            "context_type": self.context_type.value
            if hasattr(self.context_type, "value")
            else str(self.context_type),
            "canonical_target_id": self.canonical_target_id,
            "source_module": self.source_module,
            "source_reference": self.source_reference,
            "schema_version": self.schema_version,
            "as_of": self.as_of,
            "observed_at": self.observed_at,
            "source_updated_at": self.source_updated_at,
            "reporting_currency": self.reporting_currency,
            "units": self.units,
            "data_quality_status": self.data_quality_status.value
            if hasattr(self.data_quality_status, "value")
            else str(self.data_quality_status),
            "permission_status": self.permission_status,
            "model_disclosure_status": self.model_disclosure_status.value
            if hasattr(self.model_disclosure_status, "value")
            else str(self.model_disclosure_status),
            "content_summary": self.content_summary,
            "structured_payload": self.structured_payload,
            "content_hash": self.content_hash or self.compute_content_hash(),
            "estimated_tokens": self.estimated_tokens,
            "is_pinned": self.is_pinned,
            "relevance_score": self.relevance_score,
            "provenance": self.provenance,
            "provider_disclosure_status": self.model_disclosure_status.value
            if hasattr(self.model_disclosure_status, "value")
            else str(self.model_disclosure_status),
        }


@dataclass
class AtlasAiContextEnvelope:
    """Complete assembled context envelope accompanying an AI prompt generation."""

    context_request_id: str
    conversation_id: str
    generation_id: Optional[str]
    authenticated_user_scope: str
    tenant_id: Optional[str]
    source_page: str
    active_module: str
    active_workspace_id: Optional[str] = None
    focused_panel_id: Optional[str] = None
    global_link_channel_id: Optional[str] = None
    context_mode: ContextMode = ContextMode.FOCUSED
    requested_dimensions: List[str] = field(default_factory=list)
    resolved_context_items: List[AtlasAiContextItem] = field(default_factory=list)
    excluded_items: List[Dict[str, Any]] = field(default_factory=list)
    context_revision: int = 1
    assembled_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_estimated_tokens: int = 0
    token_budget: int = 8000
    quality_summary: str = "COMPLETE"
    source_manifest_id: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_request_id": self.context_request_id,
            "conversation_id": self.conversation_id,
            "generation_id": self.generation_id,
            "authenticated_user_scope": self.authenticated_user_scope,
            "tenant_id": self.tenant_id,
            "source_page": self.source_page,
            "active_module": self.active_module,
            "active_workspace_id": self.active_workspace_id,
            "focused_panel_id": self.focused_panel_id,
            "global_link_channel_id": self.global_link_channel_id,
            "context_mode": self.context_mode.value
            if hasattr(self.context_mode, "value")
            else str(self.context_mode),
            "requested_dimensions": self.requested_dimensions,
            "resolved_context_items": [item.to_dict() for item in self.resolved_context_items],
            "excluded_items": self.excluded_items,
            "context_revision": self.context_revision,
            "assembled_at": self.assembled_at,
            "total_estimated_tokens": self.total_estimated_tokens,
            "token_budget": self.token_budget,
            "quality_summary": self.quality_summary,
            "source_manifest_id": self.source_manifest_id,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class AiContextCapability:
    """Registered context capability descriptor for an ATLAS module."""

    module_id: str
    context_type: ContextType
    supported_fields: List[str]
    maximum_payload_size: int
    sensitivity_class: str  # "PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"
    requires_explicit_share: bool
    required_permissions: List[str]
    provider_disclosure_policy: ProviderDisclosureStatus
    adapter_id: str
    schema_version: int = 1


@dataclass
class AiContextPreferences:
    """User preferences for AI context sharing, privacy, and pinned/excluded resources."""

    preference_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    context_mode: ContextMode = ContextMode.FOCUSED
    allow_workspace_context: bool = True
    allow_portfolio_holdings_context: bool = False
    allow_research_drafts_context: bool = False
    pinned_context_references: List[str] = field(default_factory=list)
    excluded_context_references: List[str] = field(default_factory=list)
    provider_disclosure_enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AiContextSourceManifest:
    """Immutable audit manifest of context sources used during a model generation."""

    manifest_id: str
    generation_id: str
    owner_user_id: str
    tenant_id: Optional[str]
    source_items: List[Dict[str, Any]]
    total_tokens: int
    context_mode: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
