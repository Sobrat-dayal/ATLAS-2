"""Adapter Registry for Stage 125 AI Context Awareness."""

from typing import Dict, List, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.adapters.chart import ChartContextAdapter
from atlas.ai.context.adapters.company import CompanyContextAdapter
from atlas.ai.context.adapters.data import DataContextAdapter
from atlas.ai.context.adapters.economics import EconomicsContextAdapter
from atlas.ai.context.adapters.global_linking import GlobalLinkingContextAdapter
from atlas.ai.context.adapters.instrument import InstrumentContextAdapter
from atlas.ai.context.adapters.news import NewsContextAdapter
from atlas.ai.context.adapters.options import OptionsContextAdapter
from atlas.ai.context.adapters.page import PageContextAdapter
from atlas.ai.context.adapters.portfolio import PortfolioContextAdapter
from atlas.ai.context.adapters.research import ResearchContextAdapter
from atlas.ai.context.adapters.risk import RiskContextAdapter
from atlas.ai.context.adapters.saved import SavedResourceContextAdapter
from atlas.ai.context.adapters.screener import ScreenerContextAdapter
from atlas.ai.context.adapters.watchlist import WatchlistContextAdapter
from atlas.ai.context.adapters.workspace import WorkspaceContextAdapter
from atlas.ai.context.domain import ContextType
from atlas.ai.context.errors import AiContextTypeUnsupportedError


class ContextAdapterRegistry:
    """Thread-safe registry of canonical server-side context adapters."""

    _instance: Optional["ContextAdapterRegistry"] = None

    def __init__(self):
        self._adapters_by_type: Dict[ContextType, BaseAiContextAdapter] = {}
        self._adapters_by_id: Dict[str, BaseAiContextAdapter] = {}
        self._register_default_adapters()

    @classmethod
    def get_instance(cls) -> "ContextAdapterRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _register_default_adapters(self) -> None:
        adapters: List[BaseAiContextAdapter] = [
            PageContextAdapter(),
            InstrumentContextAdapter(),
            CompanyContextAdapter(),
            ChartContextAdapter(),
            WatchlistContextAdapter(),
            ScreenerContextAdapter(),
            EconomicsContextAdapter(),
            NewsContextAdapter(),
            ResearchContextAdapter(),
            PortfolioContextAdapter(),
            RiskContextAdapter(),
            OptionsContextAdapter(),
            DataContextAdapter(),
            SavedResourceContextAdapter(),
            WorkspaceContextAdapter(),
            GlobalLinkingContextAdapter(),
        ]
        for adapter in adapters:
            self._adapters_by_type[adapter.context_type] = adapter
            self._adapters_by_id[adapter.adapter_id] = adapter

    def get_adapter_by_type(self, context_type: ContextType) -> BaseAiContextAdapter:
        adapter = self._adapters_by_type.get(context_type)
        if not adapter:
            raise AiContextTypeUnsupportedError(str(context_type))
        return adapter

    def get_adapter_by_id(self, adapter_id: str) -> Optional[BaseAiContextAdapter]:
        return self._adapters_by_id.get(adapter_id)

    def list_adapters(self) -> List[BaseAiContextAdapter]:
        return list(self._adapters_by_id.values())

    def list_all_adapters(self) -> List[BaseAiContextAdapter]:
        return self.list_adapters()
