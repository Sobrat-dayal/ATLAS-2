"""Tool Adapters Registration for Stage 126: ATLAS AI Tool Gateway.

Registers all canonical financial tool adapters into the central tool registry.
"""

from typing import Dict, Type

from atlas.ai.tools.adapters.base import BaseAiToolAdapter
from atlas.ai.tools.adapters.company import CompanyFinancialsAdapter, CompanyGetAdapter
from atlas.ai.tools.adapters.data import DataListSourcesAdapter
from atlas.ai.tools.adapters.economics import (
    EconomicsGetObservationsAdapter,
    EconomicsSearchSeriesAdapter,
)
from atlas.ai.tools.adapters.instrument import (
    InstrumentGetAdapter,
    InstrumentSearchAdapter,
)
from atlas.ai.tools.adapters.market import (
    MarketHistorySummaryAdapter,
    MarketQuoteAdapter,
)
from atlas.ai.tools.adapters.news import NewsSearchHeadlinesAdapter
from atlas.ai.tools.adapters.portfolio import (
    PortfolioGetPerformanceAdapter,
    PortfolioGetSummaryAdapter,
    PortfolioListAdapter,
)
from atlas.ai.tools.adapters.research import ResearchListMetadataAdapter
from atlas.ai.tools.adapters.risk import (
    RiskGetRunSummaryAdapter,
    RiskListRunsAdapter,
)
from atlas.ai.tools.adapters.saved import SavedListAdapter
from atlas.ai.tools.adapters.screener import ScreenerGetDefinitionAdapter
from atlas.ai.tools.adapters.watchlist import WatchlistListAdapter
from atlas.ai.tools.adapters.workspace import WorkspaceListAdapter
from atlas.ai.tools.registry import AtlasAiToolRegistry

CANONICAL_ADAPTER_MAP: Dict[str, Type[BaseAiToolAdapter]] = {
    "atlas.instrument.search": InstrumentSearchAdapter,
    "atlas.instrument.get": InstrumentGetAdapter,
    "atlas.company.get": CompanyGetAdapter,
    "atlas.company.financials": CompanyFinancialsAdapter,
    "atlas.market.quote": MarketQuoteAdapter,
    "atlas.market.history_summary": MarketHistorySummaryAdapter,
    "atlas.watchlist.list": WatchlistListAdapter,
    "atlas.screener.get_definition": ScreenerGetDefinitionAdapter,
    "atlas.economics.search_series": EconomicsSearchSeriesAdapter,
    "atlas.economics.get_observations": EconomicsGetObservationsAdapter,
    "atlas.news.search_headlines": NewsSearchHeadlinesAdapter,
    "atlas.research.list_metadata": ResearchListMetadataAdapter,
    "atlas.portfolio.list": PortfolioListAdapter,
    "atlas.portfolio.get_summary": PortfolioGetSummaryAdapter,
    "atlas.portfolio.get_performance": PortfolioGetPerformanceAdapter,
    "atlas.risk.list_runs": RiskListRunsAdapter,
    "atlas.risk.get_run_summary": RiskGetRunSummaryAdapter,
    "atlas.data.list_sources": DataListSourcesAdapter,
    "atlas.saved.list": SavedListAdapter,
    "atlas.workspace.list": WorkspaceListAdapter,
}


def register_all_adapters(registry: AtlasAiToolRegistry) -> None:
    """Binds all adapter handler classes to their canonical tool definitions."""
    for tool_id, adapter_cls in CANONICAL_ADAPTER_MAP.items():
        if registry.is_registered(tool_id):
            tool_def = registry.get_tool(tool_id)
            registry.register_tool(tool_def, adapter_cls)


# Automatically bind all adapters into the default registry singleton
register_all_adapters(AtlasAiToolRegistry.get_instance())

