"""Enums for Stage 119 - Universal Saved System and Cross-Module Library."""

from __future__ import annotations

from enum import Enum


class SavedTargetType(str, Enum):
    """Canonical registry of supported targets across ATLAS modules."""

    INSTRUMENT = "INSTRUMENT"
    COMPANY = "COMPANY"
    CHART_CONFIG = "CHART_CONFIG"
    SCREENER_CONFIG = "SCREENER_CONFIG"
    WATCHLIST_REFERENCE = "WATCHLIST_REFERENCE"
    ECONOMIC_SERIES = "ECONOMIC_SERIES"
    NEWS_ARTICLE = "NEWS_ARTICLE"
    RESEARCH_INVESTIGATION = "RESEARCH_INVESTIGATION"
    RESEARCH_DOCUMENT = "RESEARCH_DOCUMENT"
    RESEARCH_REPORT = "RESEARCH_REPORT"
    RESEARCH_ANALYSIS_RUN = "RESEARCH_ANALYSIS_RUN"
    PORTFOLIO_REFERENCE = "PORTFOLIO_REFERENCE"
    PORTFOLIO_VIEW_CONFIG = "PORTFOLIO_VIEW_CONFIG"
    PORTFOLIO_ANALYSIS_RUN = "PORTFOLIO_ANALYSIS_RUN"
    RISK_RUN = "RISK_RUN"
    RISK_SCENARIO = "RISK_SCENARIO"
    MARKET_VIEW_CONFIG = "MARKET_VIEW_CONFIG"
    MAP_VIEW_CONFIG = "MAP_VIEW_CONFIG"
    DATA_RESOURCE = "DATA_RESOURCE"
    AI_ARTIFACT = "AI_ARTIFACT"
    INTELLIGENCE_ARTIFACT = "INTELLIGENCE_ARTIFACT"
    OTHER_REGISTERED_RESOURCE = "OTHER_REGISTERED_RESOURCE"


class SavedModule(str, Enum):
    """Canonical ATLAS module routes."""

    HOME = "home"
    MARKETS = "markets"
    CHARTS = "charts"
    WATCHLISTS = "watchlists"
    SCREENERS = "screeners"
    COMPANIES = "companies"
    ECONOMICS = "economics"
    NEWS = "news"
    RESEARCH = "research"
    MAPS = "maps"
    INTELLIGENCE = "intelligence"
    OPTIONS = "options"
    TRADING = "trading"
    PORTFOLIOS = "portfolios"
    RISK = "risk"
    AI = "ai"
    DATA = "data"
    SAVED = "saved"
    WORKSPACES = "workspaces"
    AGENTS = "agents"


class ResourceAvailabilityStatus(str, Enum):
    """Evaluated runtime availability of a saved target resource."""

    AVAILABLE = "AVAILABLE"
    AVAILABLE_WITH_WARNINGS = "AVAILABLE_WITH_WARNINGS"
    TARGET_UPDATED = "TARGET_UPDATED"
    TARGET_SUPERSEDED = "TARGET_SUPERSEDED"
    TARGET_DELETED = "TARGET_DELETED"
    TARGET_NOT_FOUND = "TARGET_NOT_FOUND"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    SOURCE_RESTRICTED = "SOURCE_RESTRICTED"
    UNSUPPORTED_CONFIG_VERSION = "UNSUPPORTED_CONFIG_VERSION"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"


class SavedReferenceSemantics(str, Enum):
    """Semantic mode defining how the saved item resolves at read-time."""

    LIVE_REFERENCE = "LIVE_REFERENCE"
    IMMUTABLE_RUN_REFERENCE = "IMMUTABLE_RUN_REFERENCE"
    USER_OWNED_VIEW_CONFIGURATION = "USER_OWNED_VIEW_CONFIGURATION"


class SavedSortOption(str, Enum):
    """Sorting criteria for saved library queries."""

    RECENTLY_SAVED = "RECENTLY_SAVED"
    RECENTLY_UPDATED = "RECENTLY_UPDATED"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    RESOURCE_TYPE = "RESOURCE_TYPE"
    CUSTOM_ORDER = "CUSTOM_ORDER"


class SavedBulkActionType(str, Enum):
    """Bulk batch action types executable on multiple saved items."""

    FAVORITE = "FAVORITE"
    UNFAVORITE = "UNFAVORITE"
    PIN = "PIN"
    UNPIN = "UNPIN"
    ADD_TO_COLLECTION = "ADD_TO_COLLECTION"
    REMOVE_FROM_COLLECTION = "REMOVE_FROM_COLLECTION"
    ADD_TAG = "ADD_TAG"
    REMOVE_TAG = "REMOVE_TAG"
    DELETE = "DELETE"
    RESTORE = "RESTORE"


class SavedAuditEventType(str, Enum):
    """Immutable audit trail event types for saved operations."""

    ITEM_SAVED = "ITEM_SAVED"
    ITEM_UPDATED = "ITEM_UPDATED"
    ITEM_REMOVED = "ITEM_REMOVED"
    ITEM_RESTORED = "ITEM_RESTORED"
    ITEM_FAVORITED = "ITEM_FAVORITED"
    ITEM_UNFAVORITED = "ITEM_UNFAVORITED"
    ITEM_PINNED = "ITEM_PINNED"
    ITEM_UNPINNED = "ITEM_UNPINNED"
    COLLECTION_CREATED = "COLLECTION_CREATED"
    COLLECTION_UPDATED = "COLLECTION_UPDATED"
    COLLECTION_DELETED = "COLLECTION_DELETED"
    TAG_CREATED = "TAG_CREATED"
    TAG_ASSIGNED = "TAG_ASSIGNED"
    TAG_REMOVED = "TAG_REMOVED"
    CONFIG_SAVED = "CONFIG_SAVED"
    CONFIG_MIGRATED = "CONFIG_MIGRATED"


class ViewConfigurationType(str, Enum):
    """Typed analytical and presentation view configuration types."""

    CHART = "CHART"
    SCREENER = "SCREENER"
    ECONOMICS = "ECONOMICS"
    PORTFOLIO = "PORTFOLIO"
    RISK = "RISK"
    MAP = "MAP"
    DATA_QUERY = "DATA_QUERY"

