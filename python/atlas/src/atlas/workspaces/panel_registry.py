"""
Canonical Workspace Panel Type Registry and Metadata Specifications (Stage 120).
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from atlas.workspaces.enums import ContextDimension, PanelTypeId
from atlas.workspaces.errors import WorkspacePanelTypeUnsupportedError


@dataclass
class PanelTypeDefinition:
    """Specification of an embeddable workspace panel type."""

    panel_type_id: PanelTypeId
    display_name: str
    source_module: str
    description: str
    category: str
    min_width_px: int = 240
    min_height_px: int = 180
    default_width_ratio: float = 0.5
    default_height_ratio: float = 0.5
    context_capabilities: list[ContextDimension] = field(default_factory=list)
    supported_actions: list[str] = field(
        default_factory=lambda: ["MAXIMIZE", "SPLIT", "RENAME", "SETTINGS", "CLOSE"]
    )
    is_available: bool = True
    unavailability_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel_type_id": self.panel_type_id.value,
            "display_name": self.display_name,
            "source_module": self.source_module,
            "description": self.description,
            "category": self.category,
            "min_width_px": self.min_width_px,
            "min_height_px": self.min_height_px,
            "default_width_ratio": self.default_width_ratio,
            "default_height_ratio": self.default_height_ratio,
            "context_capabilities": [c.value for c in self.context_capabilities],
            "supported_actions": self.supported_actions,
            "is_available": self.is_available,
            "unavailability_reason": self.unavailability_reason,
        }


PANEL_TYPE_CATALOG: dict[PanelTypeId, PanelTypeDefinition] = {
    PanelTypeId.MARKET_OVERVIEW: PanelTypeDefinition(
        panel_type_id=PanelTypeId.MARKET_OVERVIEW,
        display_name="Market Overview",
        source_module="markets",
        description="Global market indices, asset-class heatmaps, and top movers.",
        category="Markets",
        min_width_px=300,
        min_height_px=220,
        context_capabilities=[ContextDimension.INSTRUMENT],
    ),
    PanelTypeId.INSTRUMENT_CHART: PanelTypeDefinition(
        panel_type_id=PanelTypeId.INSTRUMENT_CHART,
        display_name="Interactive Chart",
        source_module="charts",
        description="High-performance candlestick and line chart with technical indicators.",
        category="Charts",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[
            ContextDimension.INSTRUMENT,
            ContextDimension.TIMEFRAME,
            ContextDimension.DATE_RANGE,
        ],
    ),
    PanelTypeId.WATCHLIST: PanelTypeDefinition(
        panel_type_id=PanelTypeId.WATCHLIST,
        display_name="Watchlist",
        source_module="watchlists",
        description="Real-time streaming watchlist with selection context publishing.",
        category="Markets",
        min_width_px=260,
        min_height_px=200,
        context_capabilities=[ContextDimension.INSTRUMENT],
    ),
    PanelTypeId.SCREENER: PanelTypeDefinition(
        panel_type_id=PanelTypeId.SCREENER,
        display_name="Stock Screener",
        source_module="screeners",
        description="Multi-factor equity screener and universe filtering table.",
        category="Research",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[ContextDimension.INSTRUMENT],
    ),
    PanelTypeId.COMPANY_OVERVIEW: PanelTypeDefinition(
        panel_type_id=PanelTypeId.COMPANY_OVERVIEW,
        display_name="Company Financials",
        source_module="companies",
        description="Corporate fundamentals, balance sheet, income statement, and valuation metrics.",
        category="Fundamental",
        min_width_px=300,
        min_height_px=220,
        context_capabilities=[
            ContextDimension.COMPANY,
            ContextDimension.INSTRUMENT,
            ContextDimension.REPORTING_CURRENCY,
        ],
    ),
    PanelTypeId.ECONOMIC_SERIES: PanelTypeDefinition(
        panel_type_id=PanelTypeId.ECONOMIC_SERIES,
        display_name="Macro & Economic Series",
        source_module="economics",
        description="Macroeconomic indicators, central bank rates, inflation, and yield curves.",
        category="Macro",
        min_width_px=280,
        min_height_px=220,
        context_capabilities=[ContextDimension.DATE_RANGE, ContextDimension.AS_OF_DATE],
    ),
    PanelTypeId.NEWS_FEED: PanelTypeDefinition(
        panel_type_id=PanelTypeId.NEWS_FEED,
        display_name="News & Events Feed",
        source_module="news",
        description="Institutional real-time financial headlines and corporate events.",
        category="News",
        min_width_px=280,
        min_height_px=200,
        context_capabilities=[ContextDimension.INSTRUMENT, ContextDimension.COMPANY],
    ),
    PanelTypeId.RESEARCH_DOCUMENT: PanelTypeDefinition(
        panel_type_id=PanelTypeId.RESEARCH_DOCUMENT,
        display_name="Research Document Viewer",
        source_module="research",
        description="Institutional research reports, quantitative notes, and analyst filings.",
        category="Research",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[ContextDimension.COMPANY, ContextDimension.AS_OF_DATE],
    ),
    PanelTypeId.RESEARCH_REPORT: PanelTypeDefinition(
        panel_type_id=PanelTypeId.RESEARCH_REPORT,
        display_name="Quantitative Report",
        source_module="research",
        description="Structured algorithmic report reader with evidence attachments.",
        category="Research",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[ContextDimension.COMPANY, ContextDimension.AS_OF_DATE],
    ),
    PanelTypeId.PORTFOLIO_SUMMARY: PanelTypeDefinition(
        panel_type_id=PanelTypeId.PORTFOLIO_SUMMARY,
        display_name="Portfolio Holdings",
        source_module="portfolios",
        description="Real-time portfolio positions, weights, and cash balances.",
        category="Portfolios",
        min_width_px=320,
        min_height_px=220,
        context_capabilities=[ContextDimension.PORTFOLIO, ContextDimension.REPORTING_CURRENCY],
    ),
    PanelTypeId.PORTFOLIO_PERFORMANCE: PanelTypeDefinition(
        panel_type_id=PanelTypeId.PORTFOLIO_PERFORMANCE,
        display_name="Portfolio Performance",
        source_module="portfolios",
        description="Time-weighted returns, cumulative NAV, and benchmark alpha/beta.",
        category="Portfolios",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[
            ContextDimension.PORTFOLIO,
            ContextDimension.BENCHMARK,
            ContextDimension.DATE_RANGE,
        ],
    ),
    PanelTypeId.RISK_OVERVIEW: PanelTypeDefinition(
        panel_type_id=PanelTypeId.RISK_OVERVIEW,
        display_name="Portfolio Risk Summary",
        source_module="risk",
        description="Core portfolio volatility, drawdowns, beta, and security risk contributions.",
        category="Risk",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[ContextDimension.PORTFOLIO, ContextDimension.AS_OF_DATE],
    ),
    PanelTypeId.RISK_ANALYSIS: PanelTypeDefinition(
        panel_type_id=PanelTypeId.RISK_ANALYSIS,
        display_name="VaR & Scenario Testing",
        source_module="risk",
        description="Historical and parametric Value at Risk, Expected Shortfall, and macro stress tests.",
        category="Risk",
        min_width_px=340,
        min_height_px=250,
        context_capabilities=[ContextDimension.PORTFOLIO, ContextDimension.AS_OF_DATE],
    ),
    PanelTypeId.DATA_TABLE: PanelTypeDefinition(
        panel_type_id=PanelTypeId.DATA_TABLE,
        display_name="Financial Data Explorer",
        source_module="data",
        description="Custom queryable tabular dataset explorer.",
        category="Data",
        min_width_px=300,
        min_height_px=220,
        context_capabilities=[],
    ),
    # Additional / Optional Panels
    PanelTypeId.OPTIONS_ANALYTICS: PanelTypeDefinition(
        panel_type_id=PanelTypeId.OPTIONS_ANALYTICS,
        display_name="Options Greeks & Chains",
        source_module="options",
        description="Options chains, implied volatility surface, and Greek sensitivities.",
        category="Derivatives",
        min_width_px=340,
        min_height_px=260,
        context_capabilities=[ContextDimension.INSTRUMENT],
        is_available=True,
    ),
    PanelTypeId.MAP_VIEW: PanelTypeDefinition(
        panel_type_id=PanelTypeId.MAP_VIEW,
        display_name="Geopolitical Intelligence Map",
        source_module="maps",
        description="Interactive 2D PostGIS and MapLibre geospatial monetary and reference maps.",
        category="Maps",
        min_width_px=360,
        min_height_px=280,
        context_capabilities=[ContextDimension.INSTRUMENT],
        is_available=True,
    ),
    PanelTypeId.INTELLIGENCE_RESULT: PanelTypeDefinition(
        panel_type_id=PanelTypeId.INTELLIGENCE_RESULT,
        display_name="Intelligence Dossier",
        source_module="intelligence",
        description="Entity graph connections and cross-border corporate intelligence.",
        category="Intelligence",
        min_width_px=320,
        min_height_px=240,
        context_capabilities=[ContextDimension.COMPANY],
        is_available=False,
        unavailability_reason="Intelligence graph requires elevated institutional clearance.",
    ),
    PanelTypeId.AI_ASSISTANT_VIEW: PanelTypeDefinition(
        panel_type_id=PanelTypeId.AI_ASSISTANT_VIEW,
        display_name="AI Quantitative Copilot",
        source_module="ai",
        description="Interactive natural language analytical assistant overlay.",
        category="AI",
        min_width_px=300,
        min_height_px=240,
        context_capabilities=[ContextDimension.INSTRUMENT, ContextDimension.PORTFOLIO],
        is_available=False,
        unavailability_reason="AI Copilot workspace docking is scheduled for Stage 124-128.",
    ),
    PanelTypeId.AGENT_STATUS: PanelTypeDefinition(
        panel_type_id=PanelTypeId.AGENT_STATUS,
        display_name="Autonomous Agent Status",
        source_module="agents",
        description="Real-time execution telemetry and task graphs for deployed agents.",
        category="Agents",
        min_width_px=300,
        min_height_px=220,
        context_capabilities=[],
        is_available=False,
        unavailability_reason="Autonomous agent workspace integration is scheduled for Stage 146-149.",
    ),
}


def get_panel_type_definition(panel_type_id: PanelTypeId) -> PanelTypeDefinition:
    """Retrieves definition or raises typed error."""
    defn = PANEL_TYPE_CATALOG.get(panel_type_id)
    if not defn:
        raise WorkspacePanelTypeUnsupportedError(panel_type_id.value)
    return defn


def list_panel_type_definitions() -> list[PanelTypeDefinition]:
    """Returns all registered panel type definitions."""
    return list(PANEL_TYPE_CATALOG.values())
