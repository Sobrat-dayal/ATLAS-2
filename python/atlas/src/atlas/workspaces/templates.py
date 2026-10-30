"""
Built-in Canonical Workspace Templates (Stage 120).
"""

from atlas.workspaces.enums import LayoutNodeType, PanelTypeId, SplitOrientation
from atlas.workspaces.errors import WorkspaceTemplateNotFoundError
from atlas.workspaces.models import (
    WorkspaceTemplate,
)


def build_blank_template() -> WorkspaceTemplate:
    """Creates a blank workspace template."""
    return WorkspaceTemplate(
        template_id="BLANK_DESK",
        name="Blank Workspace",
        description="A clean, unconstrained analytical canvas ready for custom panel configuration.",
        category="General",
        layout_definition={
            "root_node": {
                "node_id": "root_blank",
                "node_type": LayoutNodeType.PANEL.value,
                "panel_instance_id": "panel_chart_default",
            }
        },
        panel_definitions=[
            {
                "panel_instance_id": "panel_chart_default",
                "panel_type_id": PanelTypeId.INSTRUMENT_CHART.value,
                "title_override": "Main Chart",
                "configuration": {"symbol": "AAPL", "timeframe": "1D"},
                "link_group_id": "link_group_default",
            }
        ],
        required_capabilities=[],
        version=1,
    )


def build_equity_research_template() -> WorkspaceTemplate:
    """Creates the 4-panel Equity Research Desk."""
    return WorkspaceTemplate(
        template_id="EQUITY_RESEARCH_DESK",
        name="Equity Research Desk",
        description="Four-quadrant fundamental analysis desk: Watchlist, Price Chart, Financial Statements, and Company News.",
        category="Equity",
        layout_definition={
            "root_node": {
                "node_id": "split_root_vertical",
                "node_type": LayoutNodeType.SPLIT.value,
                "orientation": SplitOrientation.VERTICAL.value,
                "children": [
                    {
                        "node_id": "split_top_horizontal",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.HORIZONTAL.value,
                        "children": [
                            {
                                "node_id": "node_watchlist",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_eq_watchlist",
                            },
                            {
                                "node_id": "node_chart",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_eq_chart",
                            },
                        ],
                        "size_ratios": [0.35, 0.65],
                    },
                    {
                        "node_id": "split_bottom_horizontal",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.HORIZONTAL.value,
                        "children": [
                            {
                                "node_id": "node_company",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_eq_company",
                            },
                            {
                                "node_id": "node_news",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_eq_news",
                            },
                        ],
                        "size_ratios": [0.55, 0.45],
                    },
                ],
                "size_ratios": [0.55, 0.45],
            }
        },
        panel_definitions=[
            {
                "panel_instance_id": "p_eq_watchlist",
                "panel_type_id": PanelTypeId.WATCHLIST.value,
                "title_override": "Equities Focus List",
                "configuration": {"watchlist_name": "Mega-Cap Tech"},
                "link_group_id": "link_group_a",
            },
            {
                "panel_instance_id": "p_eq_chart",
                "panel_type_id": PanelTypeId.INSTRUMENT_CHART.value,
                "title_override": "Technical Analysis",
                "configuration": {"timeframe": "1D", "chart_type": "candlestick"},
                "link_group_id": "link_group_a",
            },
            {
                "panel_instance_id": "p_eq_company",
                "panel_type_id": PanelTypeId.COMPANY_OVERVIEW.value,
                "title_override": "Financial Statements & Valuation",
                "configuration": {"view": "FINANCIALS"},
                "link_group_id": "link_group_a",
            },
            {
                "panel_instance_id": "p_eq_news",
                "panel_type_id": PanelTypeId.NEWS_FEED.value,
                "title_override": "Company Headlines",
                "configuration": {"filter": "ALL"},
                "link_group_id": "link_group_a",
            },
        ],
        required_capabilities=["markets", "charts", "companies", "news"],
        version=1,
    )


def build_market_monitoring_template() -> WorkspaceTemplate:
    """Creates Market Monitoring Desk."""
    return WorkspaceTemplate(
        template_id="MARKET_MONITORING_DESK",
        name="Market Monitoring Desk",
        description="High-velocity market monitoring desk with indices, streaming watchlists, chart, and research screener.",
        category="Markets",
        layout_definition={
            "root_node": {
                "node_id": "split_mm_root",
                "node_type": LayoutNodeType.SPLIT.value,
                "orientation": SplitOrientation.HORIZONTAL.value,
                "children": [
                    {
                        "node_id": "split_mm_left",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.VERTICAL.value,
                        "children": [
                            {
                                "node_id": "node_mm_markets",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_mm_markets",
                            },
                            {
                                "node_id": "node_mm_watchlist",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_mm_watchlist",
                            },
                        ],
                        "size_ratios": [0.45, 0.55],
                    },
                    {
                        "node_id": "split_mm_right",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.VERTICAL.value,
                        "children": [
                            {
                                "node_id": "node_mm_chart",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_mm_chart",
                            },
                            {
                                "node_id": "tab_mm_stack",
                                "node_type": LayoutNodeType.TAB_STACK.value,
                                "panel_instance_ids": ["p_mm_news", "p_mm_screener"],
                                "active_panel_instance_id": "p_mm_news",
                            },
                        ],
                        "size_ratios": [0.55, 0.45],
                    },
                ],
                "size_ratios": [0.42, 0.58],
            }
        },
        panel_definitions=[
            {
                "panel_instance_id": "p_mm_markets",
                "panel_type_id": PanelTypeId.MARKET_OVERVIEW.value,
                "title_override": "Global Indices",
                "configuration": {},
                "link_group_id": None,
            },
            {
                "panel_instance_id": "p_mm_watchlist",
                "panel_type_id": PanelTypeId.WATCHLIST.value,
                "title_override": "Active Movers",
                "configuration": {},
                "link_group_id": "link_group_a",
            },
            {
                "panel_instance_id": "p_mm_chart",
                "panel_type_id": PanelTypeId.INSTRUMENT_CHART.value,
                "title_override": "Intraday Price Action",
                "configuration": {"timeframe": "15m"},
                "link_group_id": "link_group_a",
            },
            {
                "panel_instance_id": "p_mm_news",
                "panel_type_id": PanelTypeId.NEWS_FEED.value,
                "title_override": "Breaking Headlines",
                "configuration": {},
                "link_group_id": "link_group_a",
            },
            {
                "panel_instance_id": "p_mm_screener",
                "panel_type_id": PanelTypeId.SCREENER.value,
                "title_override": "Market Screener",
                "configuration": {},
                "link_group_id": "link_group_a",
            },
        ],
        required_capabilities=["markets", "charts", "watchlists", "news", "screeners"],
        version=1,
    )


def build_macro_desk_template() -> WorkspaceTemplate:
    """Creates Global Macro Desk."""
    return WorkspaceTemplate(
        template_id="MACRO_DESK",
        name="Macro & Economics Desk",
        description="Comprehensive macroeconomic analytical environment for central bank policies, inflation, and rate curves.",
        category="Macro",
        layout_definition={
            "root_node": {
                "node_id": "split_macro_root",
                "node_type": LayoutNodeType.SPLIT.value,
                "orientation": SplitOrientation.HORIZONTAL.value,
                "children": [
                    {
                        "node_id": "node_macro_series",
                        "node_type": LayoutNodeType.PANEL.value,
                        "panel_instance_id": "p_macro_series",
                    },
                    {
                        "node_id": "split_macro_right",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.VERTICAL.value,
                        "children": [
                            {
                                "node_id": "node_macro_chart",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_macro_chart",
                            },
                            {
                                "node_id": "node_macro_news",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_macro_news",
                            },
                        ],
                        "size_ratios": [0.55, 0.45],
                    },
                ],
                "size_ratios": [0.48, 0.52],
            }
        },
        panel_definitions=[
            {
                "panel_instance_id": "p_macro_series",
                "panel_type_id": PanelTypeId.ECONOMIC_SERIES.value,
                "title_override": "Central Bank Rates & Inflation",
                "configuration": {"series": ["CPI", "FEDFUNDS"]},
                "link_group_id": None,
            },
            {
                "panel_instance_id": "p_macro_chart",
                "panel_type_id": PanelTypeId.INSTRUMENT_CHART.value,
                "title_override": "10Y Treasury Benchmark Yield",
                "configuration": {"symbol": "US10Y", "timeframe": "1D"},
                "link_group_id": "link_group_macro",
            },
            {
                "panel_instance_id": "p_macro_news",
                "panel_type_id": PanelTypeId.NEWS_FEED.value,
                "title_override": "Macro & Monetary Policy News",
                "configuration": {"topic": "CENTRAL_BANKS"},
                "link_group_id": None,
            },
        ],
        required_capabilities=["economics", "charts", "news"],
        version=1,
    )


def build_portfolio_desk_template() -> WorkspaceTemplate:
    """Creates Portfolio Management Desk."""
    return WorkspaceTemplate(
        template_id="PORTFOLIO_DESK",
        name="Portfolio Management Desk",
        description="Unified desk for tracking portfolio positions, asset allocation, historical performance, and risk metrics.",
        category="Portfolios",
        layout_definition={
            "root_node": {
                "node_id": "split_pf_root",
                "node_type": LayoutNodeType.SPLIT.value,
                "orientation": SplitOrientation.HORIZONTAL.value,
                "children": [
                    {
                        "node_id": "node_pf_summary",
                        "node_type": LayoutNodeType.PANEL.value,
                        "panel_instance_id": "p_pf_summary",
                    },
                    {
                        "node_id": "split_pf_right",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.VERTICAL.value,
                        "children": [
                            {
                                "node_id": "node_pf_perf",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_pf_perf",
                            },
                            {
                                "node_id": "node_pf_risk",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_pf_risk",
                            },
                        ],
                        "size_ratios": [0.55, 0.45],
                    },
                ],
                "size_ratios": [0.50, 0.50],
            }
        },
        panel_definitions=[
            {
                "panel_instance_id": "p_pf_summary",
                "panel_type_id": PanelTypeId.PORTFOLIO_SUMMARY.value,
                "title_override": "Positions & Weights",
                "configuration": {},
                "link_group_id": "link_group_pf",
            },
            {
                "panel_instance_id": "p_pf_perf",
                "panel_type_id": PanelTypeId.PORTFOLIO_PERFORMANCE.value,
                "title_override": "Performance & Cumulative NAV",
                "configuration": {"benchmark": "SPY"},
                "link_group_id": "link_group_pf",
            },
            {
                "panel_instance_id": "p_pf_risk",
                "panel_type_id": PanelTypeId.RISK_OVERVIEW.value,
                "title_override": "Volatility & Drawdown Health",
                "configuration": {},
                "link_group_id": "link_group_pf",
            },
        ],
        required_capabilities=["portfolios", "risk"],
        version=1,
    )


def build_risk_desk_template() -> WorkspaceTemplate:
    """Creates Risk Management Desk."""
    return WorkspaceTemplate(
        template_id="RISK_DESK",
        name="Quantitative Risk Desk",
        description="Institutional risk oversight desk with market-risk volatility, drawdown diagnostics, VaR/ES, and scenario testing.",
        category="Risk",
        layout_definition={
            "root_node": {
                "node_id": "split_risk_root",
                "node_type": LayoutNodeType.SPLIT.value,
                "orientation": SplitOrientation.VERTICAL.value,
                "children": [
                    {
                        "node_id": "split_risk_top",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.HORIZONTAL.value,
                        "children": [
                            {
                                "node_id": "node_risk_core",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_risk_core",
                            },
                            {
                                "node_id": "node_risk_var",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_risk_var",
                            },
                        ],
                        "size_ratios": [0.50, 0.50],
                    },
                    {
                        "node_id": "split_risk_bottom",
                        "node_type": LayoutNodeType.SPLIT.value,
                        "orientation": SplitOrientation.HORIZONTAL.value,
                        "children": [
                            {
                                "node_id": "node_risk_contrib",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_risk_contrib",
                            },
                            {
                                "node_id": "node_risk_scen",
                                "node_type": LayoutNodeType.PANEL.value,
                                "panel_instance_id": "p_risk_scen",
                            },
                        ],
                        "size_ratios": [0.50, 0.50],
                    },
                ],
                "size_ratios": [0.50, 0.50],
            }
        },
        panel_definitions=[
            {
                "panel_instance_id": "p_risk_core",
                "panel_type_id": PanelTypeId.RISK_OVERVIEW.value,
                "title_override": "Market-Risk Volatility & Drawdowns",
                "configuration": {},
                "link_group_id": "link_group_risk",
            },
            {
                "panel_instance_id": "p_risk_var",
                "panel_type_id": PanelTypeId.RISK_ANALYSIS.value,
                "title_override": "Value at Risk & Expected Shortfall",
                "configuration": {"confidence": 0.95, "horizon_days": 1},
                "link_group_id": "link_group_risk",
            },
            {
                "panel_instance_id": "p_risk_contrib",
                "panel_type_id": PanelTypeId.RISK_OVERVIEW.value,
                "title_override": "Security Risk Contributions",
                "configuration": {"view": "CONTRIBUTIONS"},
                "link_group_id": "link_group_risk",
            },
            {
                "panel_instance_id": "p_risk_scen",
                "panel_type_id": PanelTypeId.RISK_ANALYSIS.value,
                "title_override": "Historical Macro Stress Tests",
                "configuration": {"view": "SCENARIOS"},
                "link_group_id": "link_group_risk",
            },
        ],
        required_capabilities=["risk", "portfolios"],
        version=1,
    )


CANONICAL_TEMPLATES: dict[str, WorkspaceTemplate] = {
    "BLANK_DESK": build_blank_template(),
    "EQUITY_RESEARCH_DESK": build_equity_research_template(),
    "MARKET_MONITORING_DESK": build_market_monitoring_template(),
    "MACRO_DESK": build_macro_desk_template(),
    "PORTFOLIO_DESK": build_portfolio_desk_template(),
    "RISK_DESK": build_risk_desk_template(),
}


def get_workspace_template(template_id: str) -> WorkspaceTemplate:
    """Returns the requested template or raises WorkspaceTemplateNotFoundError."""
    tmpl = CANONICAL_TEMPLATES.get(template_id)
    if not tmpl:
        raise WorkspaceTemplateNotFoundError(template_id)
    return tmpl


def list_workspace_templates() -> list[WorkspaceTemplate]:
    """Lists all built-in desk templates."""
    return list(CANONICAL_TEMPLATES.values())
