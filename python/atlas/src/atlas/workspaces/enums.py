"""
Canonical Enums for ATLAS Workspaces Architecture (Stage 120).
"""

from enum import Enum


class WorkspaceStatus(str, Enum):
    """Lifecycle status of a workspace."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    SOFT_DELETED = "SOFT_DELETED"
    UNAVAILABLE = "UNAVAILABLE"


class WorkspaceType(str, Enum):
    """Origin type of the workspace."""

    CUSTOM = "CUSTOM"
    TEMPLATE_DERIVED = "TEMPLATE_DERIVED"
    SYSTEM_DEFAULT = "SYSTEM_DEFAULT"


class LayoutNodeType(str, Enum):
    """Types of nodes in the workspace layout tree."""

    SPLIT = "SPLIT"
    TAB_STACK = "TAB_STACK"
    PANEL = "PANEL"


class SplitOrientation(str, Enum):
    """Orientation of a split container."""

    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"


class PanelTypeId(str, Enum):
    """Canonical registered workspace panel types."""

    # Core Financial Panels
    MARKET_OVERVIEW = "MARKET_OVERVIEW"
    INSTRUMENT_CHART = "INSTRUMENT_CHART"
    WATCHLIST = "WATCHLIST"
    SCREENER = "SCREENER"
    COMPANY_OVERVIEW = "COMPANY_OVERVIEW"
    ECONOMIC_SERIES = "ECONOMIC_SERIES"
    NEWS_FEED = "NEWS_FEED"
    RESEARCH_DOCUMENT = "RESEARCH_DOCUMENT"
    RESEARCH_REPORT = "RESEARCH_REPORT"
    PORTFOLIO_SUMMARY = "PORTFOLIO_SUMMARY"
    PORTFOLIO_PERFORMANCE = "PORTFOLIO_PERFORMANCE"
    RISK_OVERVIEW = "RISK_OVERVIEW"
    RISK_ANALYSIS = "RISK_ANALYSIS"
    DATA_TABLE = "DATA_TABLE"

    # Optional / Future Integration Panels
    OPTIONS_ANALYTICS = "OPTIONS_ANALYTICS"
    MAP_VIEW = "MAP_VIEW"
    INTELLIGENCE_RESULT = "INTELLIGENCE_RESULT"
    AI_ASSISTANT_VIEW = "AI_ASSISTANT_VIEW"
    AGENT_STATUS = "AGENT_STATUS"


class ContextDimension(str, Enum):
    """Financial dimensions supported by the cross-panel context engine."""

    INSTRUMENT = "INSTRUMENT"
    COMPANY = "COMPANY"
    PORTFOLIO = "PORTFOLIO"
    BENCHMARK = "BENCHMARK"
    DATE_RANGE = "DATE_RANGE"
    AS_OF_DATE = "AS_OF_DATE"
    TIMEFRAME = "TIMEFRAME"
    REPORTING_CURRENCY = "REPORTING_CURRENCY"


class WorkspaceSortOption(str, Enum):
    """Sorting options for workspace listing."""

    RECENTLY_OPENED = "RECENTLY_OPENED"
    RECENTLY_MODIFIED = "RECENTLY_MODIFIED"
    NAME = "NAME"
    FAVORITES = "FAVORITES"


class WorkspaceAuditEventType(str, Enum):
    """Audit event types for workspace mutations."""

    WORKSPACE_CREATED = "WORKSPACE_CREATED"
    WORKSPACE_UPDATED = "WORKSPACE_UPDATED"
    WORKSPACE_DUPLICATED = "WORKSPACE_DUPLICATED"
    WORKSPACE_DELETED = "WORKSPACE_DELETED"
    WORKSPACE_RESTORED = "WORKSPACE_RESTORED"
    LAYOUT_UPDATED = "LAYOUT_UPDATED"
    PANEL_ADDED = "PANEL_ADDED"
    PANEL_REMOVED = "PANEL_REMOVED"
    LINK_GROUP_UPDATED = "LINK_GROUP_UPDATED"
