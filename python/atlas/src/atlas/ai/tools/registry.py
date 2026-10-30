"""Universal AI Tool Registry for Stage 126: ATLAS AI Tool Gateway.

Maintains canonical tool definitions, input/output schemas, permission metadata,
and associated adapter handlers with zero-trust validation.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from atlas.ai.tools.domain import (
    ApprovalClass,
    AtlasAiToolDefinition,
    CapabilityScope,
    ProviderDisclosurePolicy,
    ToolCategory,
    ToolLifecycleStatus,
)
from atlas.ai.tools.errors import AiToolError, AiToolNotFoundError

if TYPE_CHECKING:
    from atlas.ai.tools.adapters.base import BaseAiToolAdapter

logger = logging.getLogger(__name__)

# Strict regex for stable canonical Tool IDs: atlas.<domain>.<action>
TOOL_ID_REGEX = re.compile(r"^atlas\.[a-z0-9_]+\.[a-z0-9_]+$")

# Strictly forbidden generic execution and mutation patterns
PROHIBITED_TOOL_PATTERNS = [
    re.compile(r".*execute.*python.*", re.IGNORECASE),
    re.compile(r".*execute.*sql.*", re.IGNORECASE),
    re.compile(r".*execute.*shell.*", re.IGNORECASE),
    re.compile(r".*execute.*bash.*", re.IGNORECASE),
    re.compile(r".*execute.*code.*", re.IGNORECASE),
    re.compile(r".*system\.execute.*", re.IGNORECASE),
    re.compile(r".*http\.fetch.*", re.IGNORECASE),
    re.compile(r".*curl.*", re.IGNORECASE),
    re.compile(r".*broker\.trade.*", re.IGNORECASE),
    re.compile(r".*order\.submit.*", re.IGNORECASE),
]


class AtlasAiToolRegistry:
    """Thread-safe, central registry for all institutional AI tools."""

    _instance: Optional["AtlasAiToolRegistry"] = None

    def __init__(self) -> None:
        self._tools: Dict[str, AtlasAiToolDefinition] = {}
        self._adapter_classes: Dict[str, Type["BaseAiToolAdapter"]] = {}
        self._init_canonical_tools()

    @classmethod
    def get_instance(cls) -> "AtlasAiToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Resets the singleton instance (useful for clean unit test runs)."""
        cls._instance = None

    def register_tool(
        self,
        definition: AtlasAiToolDefinition,
        adapter_cls: Optional[Type["BaseAiToolAdapter"]] = None,
    ) -> None:
        """Registers a tool definition and its adapter after verifying security constraints."""
        tool_id = definition.tool_id

        # 1. Enforce ID namespace format
        if not TOOL_ID_REGEX.match(tool_id):
            raise AiToolError(
                f"Tool ID '{tool_id}' violates canonical namespace format 'atlas.<module>.<action>'.",
                code="AI_TOOL_INVALID_NAMESPACE",
            )

        # 2. Strict rejection of arbitrary execution or prohibited operations
        for pattern in PROHIBITED_TOOL_PATTERNS:
            if pattern.match(tool_id):
                raise AiToolError(
                    f"Tool ID '{tool_id}' violates security policy. Arbitrary code, shell, or trade execution is prohibited.",
                    code="AI_TOOL_PROHIBITED_CAPABILITY",
                )

        self._tools[tool_id] = definition
        if adapter_cls is not None:
            self._adapter_classes[tool_id] = adapter_cls
        logger.info(
            "Registered AI tool: %s (v%s, %s)", tool_id, definition.version, definition.category
        )

    def get_tool(self, tool_id: str) -> AtlasAiToolDefinition:
        """Retrieves a registered tool definition by ID, throwing if not found."""
        tool = self._tools.get(tool_id)
        if not tool:
            raise AiToolNotFoundError(tool_id)
        return tool

    def get_adapter_class(self, tool_id: str) -> Optional[Type["BaseAiToolAdapter"]]:
        """Retrieves the registered adapter class for a tool ID."""
        return self._adapter_classes.get(tool_id)

    def is_registered(self, tool_id: str) -> bool:
        """Checks if a tool ID is registered."""
        return tool_id in self._tools

    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        include_disabled: bool = False,
    ) -> List[AtlasAiToolDefinition]:
        """Returns all registered tool definitions, optionally filtered by category."""
        tools = list(self._tools.values())
        if not include_disabled:
            tools = [t for t in tools if t.lifecycle_status == ToolLifecycleStatus.ENABLED]
        if category:
            tools = [t for t in tools if t.category == category]
        return sorted(tools, key=lambda t: t.tool_id)

    # ---------------- Canonical Tool Initializer ----------------

    def _init_canonical_tools(self) -> None:
        """Pre-registers all 19 canonical read-only ATLAS AI tools."""
        from atlas.ai.tools.schemas import (
            CompanyFinancialsInput,
            CompanyGetInput,
            DataListSourcesInput,
            EconomicsGetObservationsInput,
            EconomicsSearchSeriesInput,
            InstrumentGetInput,
            InstrumentSearchInput,
            MarketHistorySummaryInput,
            MarketQuoteInput,
            NewsSearchHeadlinesInput,
            PortfolioGetPerformanceInput,
            PortfolioGetSummaryInput,
            PortfolioListInput,
            ResearchListMetadataInput,
            RiskGetRunSummaryInput,
            RiskListRunsInput,
            SavedListInput,
            ScreenerGetDefinitionInput,
            WatchlistListInput,
            WorkspaceListInput,
        )

        canonical_defs = [
            # 1. Instrument Search
            AtlasAiToolDefinition(
                tool_id="atlas.instrument.search",
                version="1.0.0",
                category=ToolCategory.DISCOVERY,
                name="Instrument Search",
                description="Search canonical instruments across global exchanges by symbol, name, or asset class.",
                capability_scope=CapabilityScope.INSTRUMENT_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=InstrumentSearchInput.model_json_schema(),
            ),
            # 2. Instrument Get
            AtlasAiToolDefinition(
                tool_id="atlas.instrument.get",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Instrument Details",
                description="Retrieve authorized metadata for a canonical instrument including FIGI, ISIN, and exchange.",
                capability_scope=CapabilityScope.INSTRUMENT_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=InstrumentGetInput.model_json_schema(),
            ),
            # 3. Company Get
            AtlasAiToolDefinition(
                tool_id="atlas.company.get",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Company Profile",
                description="Retrieve corporate profile, sector classification, and identifier mappings.",
                capability_scope=CapabilityScope.COMPANY_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=CompanyGetInput.model_json_schema(),
            ),
            # 4. Company Financials
            AtlasAiToolDefinition(
                tool_id="atlas.company.financials",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Company Financials",
                description="Retrieve point-in-time financial statement line items (revenue, net income, etc.) with units.",
                capability_scope=CapabilityScope.COMPANY_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=CompanyFinancialsInput.model_json_schema(),
            ),
            # 5. Market Quote
            AtlasAiToolDefinition(
                tool_id="atlas.market.quote",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Market Quote",
                description="Retrieve authorized market price quote with exchange attribution and timestamp.",
                capability_scope=CapabilityScope.MARKET_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=MarketQuoteInput.model_json_schema(),
            ),
            # 6. Market History Summary
            AtlasAiToolDefinition(
                tool_id="atlas.market.history_summary",
                version="1.0.0",
                category=ToolCategory.ANALYTICAL_READ,
                name="Market History Summary",
                description="Summarize historical price action, volatility, and trading ranges for an instrument.",
                capability_scope=CapabilityScope.MARKET_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=MarketHistorySummaryInput.model_json_schema(),
            ),
            # 7. Watchlist List
            AtlasAiToolDefinition(
                tool_id="atlas.watchlist.list",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="List Watchlists",
                description="List permitted watchlists and securities for the authenticated user.",
                capability_scope=CapabilityScope.WATCHLIST_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=WatchlistListInput.model_json_schema(),
            ),
            # 8. Screener Definition
            AtlasAiToolDefinition(
                tool_id="atlas.screener.get_definition",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Get Screener Definition",
                description="Inspect existing screener filter criteria and universe configuration (read-only).",
                capability_scope=CapabilityScope.SCREENER_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=ScreenerGetDefinitionInput.model_json_schema(),
            ),
            # 9. Economics Search Series
            AtlasAiToolDefinition(
                tool_id="atlas.economics.search_series",
                version="1.0.0",
                category=ToolCategory.DISCOVERY,
                name="Search Economic Series",
                description="Discover macroeconomic indicator series (CPI, GDP, unemployment) from official statistical bureaus.",
                capability_scope=CapabilityScope.ECONOMICS_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=EconomicsSearchSeriesInput.model_json_schema(),
            ),
            # 10. Economics Get Observations
            AtlasAiToolDefinition(
                tool_id="atlas.economics.get_observations",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Get Economic Observations",
                description="Retrieve chronological observations for an economic series with units and publication dates.",
                capability_scope=CapabilityScope.ECONOMICS_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=EconomicsGetObservationsInput.model_json_schema(),
            ),
            # 11. News Search Headlines
            AtlasAiToolDefinition(
                tool_id="atlas.news.search_headlines",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Search News Headlines",
                description="Search authorized financial wire headlines and publisher attribution.",
                capability_scope=CapabilityScope.NEWS_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=NewsSearchHeadlinesInput.model_json_schema(),
            ),
            # 12. Research List Metadata
            AtlasAiToolDefinition(
                tool_id="atlas.research.list_metadata",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="List Research Reports",
                description="List authorized research report metadata and analyst notes.",
                capability_scope=CapabilityScope.RESEARCH_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=ResearchListMetadataInput.model_json_schema(),
            ),
            # 13. Portfolio List
            AtlasAiToolDefinition(
                tool_id="atlas.portfolio.list",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="List Portfolios",
                description="List authorized investment portfolios for the authenticated user.",
                capability_scope=CapabilityScope.PORTFOLIO_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=PortfolioListInput.model_json_schema(),
            ),
            # 14. Portfolio Get Summary
            AtlasAiToolDefinition(
                tool_id="atlas.portfolio.get_summary",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="Get Portfolio Summary",
                description="Retrieve authorized portfolio allocation and total value (holdings redacted unless consented).",
                capability_scope=CapabilityScope.PORTFOLIO_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=PortfolioGetSummaryInput.model_json_schema(),
            ),
            # 15. Portfolio Get Performance
            AtlasAiToolDefinition(
                tool_id="atlas.portfolio.get_performance",
                version="1.0.0",
                category=ToolCategory.ANALYTICAL_READ,
                name="Get Portfolio Performance",
                description="Retrieve authorized historical return metrics, benchmark comparison, and tracking error.",
                capability_scope=CapabilityScope.PORTFOLIO_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=PortfolioGetPerformanceInput.model_json_schema(),
            ),
            # 16. Risk List Runs
            AtlasAiToolDefinition(
                tool_id="atlas.risk.list_runs",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="List Risk Runs",
                description="List historical risk calculation runs for permitted portfolios.",
                capability_scope=CapabilityScope.RISK_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=RiskListRunsInput.model_json_schema(),
            ),
            # 17. Risk Get Run Summary
            AtlasAiToolDefinition(
                tool_id="atlas.risk.get_run_summary",
                version="1.0.0",
                category=ToolCategory.ANALYTICAL_READ,
                name="Get Risk Run Summary",
                description="Retrieve immutable historical risk metrics (VaR 95%, CVaR, factor exposures) for a run.",
                capability_scope=CapabilityScope.RISK_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=RiskGetRunSummaryInput.model_json_schema(),
            ),
            # 18. Data List Sources
            AtlasAiToolDefinition(
                tool_id="atlas.data.list_sources",
                version="1.0.0",
                category=ToolCategory.DISCOVERY,
                name="List Data Sources",
                description="Discover eligible financial data catalog sources and vendor coverage.",
                capability_scope=CapabilityScope.DATA_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=DataListSourcesInput.model_json_schema(),
            ),
            # 19. Saved List
            AtlasAiToolDefinition(
                tool_id="atlas.saved.list",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="List Saved Resources",
                description="List user saved charts, screeners, watchlists, and research templates.",
                capability_scope=CapabilityScope.SAVED_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=SavedListInput.model_json_schema(),
            ),
            # 20. Workspace List
            AtlasAiToolDefinition(
                tool_id="atlas.workspace.list",
                version="1.0.0",
                category=ToolCategory.DATA_READ,
                name="List Workspaces",
                description="List user multi-panel quantitative workspaces and layout configurations.",
                capability_scope=CapabilityScope.WORKSPACE_READ,
                approval_class=ApprovalClass.NO_APPROVAL_REQUIRED,
                provider_disclosure_policy=ProviderDisclosurePolicy.ALLOWED,
                parameters_schema=WorkspaceListInput.model_json_schema(),
            ),
        ]

        for defn in canonical_defs:
            self._tools[defn.tool_id] = defn

        try:
            from atlas.ai.tools.adapters import CANONICAL_ADAPTER_MAP

            for tool_id, adapter_cls in CANONICAL_ADAPTER_MAP.items():
                self._adapter_classes[tool_id] = adapter_cls
        except ImportError:
            pass
