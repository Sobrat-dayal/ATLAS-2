"""Domain Models for Stage 119 - Universal Saved System and Cross-Module Library."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.saved.enums import (
    ResourceAvailabilityStatus,
    SavedAuditEventType,
    SavedModule,
    SavedReferenceSemantics,
    SavedTargetType,
    ViewConfigurationType,
)


@dataclass
class SavedItem:
    """Canonical pointer to an ATLAS resource or analytical configuration."""

    saved_item_id: str
    owner_user_id: str
    target_type: SavedTargetType
    target_id: str
    target_module: SavedModule
    canonical_title: str
    organization_id: Optional[str] = None
    target_revision_id: Optional[str] = None
    display_title_override: Optional[str] = None
    user_note: Optional[str] = None
    favorite: bool = False
    pinned: bool = False
    view_configuration_id: Optional[str] = None
    semantics: SavedReferenceSemantics = SavedReferenceSemantics.LIVE_REFERENCE
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
    row_version: int = 1

    @property
    def effective_title(self) -> str:
        """User title override takes precedence over canonical resource title."""
        if self.display_title_override and self.display_title_override.strip():
            return self.display_title_override.strip()
        return self.canonical_title

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


@dataclass
class SavedCollection:
    """Organizational folder/collection for grouping saved references."""

    collection_id: str
    owner_user_id: str
    name: str
    organization_id: Optional[str] = None
    description: Optional[str] = None
    parent_collection_id: Optional[str] = None
    sort_order: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
    row_version: int = 1

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


@dataclass
class SavedCollectionMembership:
    """Many-to-many relationship linking a saved item to a collection."""

    collection_id: str
    saved_item_id: str
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sort_order: int = 0


@dataclass
class SavedTag:
    """User-scoped label for categorizing saved items."""

    tag_id: str
    owner_user_id: str
    name: str
    normalized_name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SavedItemTag:
    """Association linking a tag to a saved item."""

    saved_item_id: str
    tag_id: str


@dataclass
class SavedViewConfiguration:
    """Versioned, validated user presentation and filter settings."""

    configuration_id: str
    configuration_type: ViewConfigurationType
    schema_version: int
    owner_user_id: str
    payload: Dict[str, Any]
    payload_hash: str
    target_module: SavedModule
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SavedTargetDefinition:
    """Static catalog definition describing a registered target type."""

    target_type: SavedTargetType
    module: SavedModule
    display_name: str
    description: str
    supports_view_config: bool
    supports_revision_pin: bool
    semantics: SavedReferenceSemantics


@dataclass
class ResolvedTarget:
    """Runtime result of evaluating a saved target against canonical sources."""

    target_type: SavedTargetType
    target_id: str
    exists: bool
    authorized: bool
    entitled: bool
    status: ResourceAvailabilityStatus
    canonical_title: str
    target_module: SavedModule
    safe_deep_link: str
    target_revision_id: Optional[str] = None
    latest_revision_id: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class SavedAuditEvent:
    """Immutable audit record for a saved system operation."""

    event_id: str
    event_type: SavedAuditEventType
    actor_user_id: str
    target_entity_id: str
    details: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
