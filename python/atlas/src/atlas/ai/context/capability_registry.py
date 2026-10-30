"""Capability Registry for Stage 125 AI Context Awareness."""

from typing import Dict, List, Optional

from .domain import AiContextCapability, ContextType, ProviderDisclosureStatus

CAPABILITIES_CATALOG: Dict[str, AiContextCapability] = {
    "cap_page": AiContextCapability(
        module_id="global_page",
        context_type=ContextType.PAGE_CONTEXT,
        supported_fields=["route", "module_name", "summary", "view_mode"],
        maximum_payload_size=512,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=[],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_page",
    ),
    "cap_instrument": AiContextCapability(
        module_id="markets",
        context_type=ContextType.INSTRUMENT_CONTEXT,
        supported_fields=[
            "entity_id",
            "symbol",
            "canonical_name",
            "exchange",
            "currency",
            "country",
            "sector",
            "figi",
            "isin",
        ],
        maximum_payload_size=1024,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=["markets:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_instrument",
    ),
    "cap_company": AiContextCapability(
        module_id="companies",
        context_type=ContextType.COMPANY_CONTEXT,
        supported_fields=[
            "company_id",
            "legal_name",
            "sector",
            "industry",
            "reporting_currency",
            "fiscal_year",
            "fiscal_period",
            "statement_type",
            "facts",
            "as_of",
        ],
        maximum_payload_size=4096,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=["companies:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_company",
    ),
    "cap_chart": AiContextCapability(
        module_id="charts",
        context_type=ContextType.CHART_CONTEXT,
        supported_fields=[
            "instrument_id",
            "chart_type",
            "interval",
            "timeframe",
            "date_range",
            "indicators",
            "overlays",
            "adjustment_basis",
            "currency",
            "source_timestamp",
            "data_coverage",
        ],
        maximum_payload_size=2048,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=["charts:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_chart",
    ),
    "cap_watchlist": AiContextCapability(
        module_id="watchlists",
        context_type=ContextType.WATCHLIST_CONTEXT,
        supported_fields=[
            "watchlist_id",
            "name",
            "instrument_ids",
            "selected_instrument",
            "columns",
            "sort_order",
        ],
        maximum_payload_size=2048,
        sensitivity_class="INTERNAL",
        requires_explicit_share=False,
        required_permissions=["watchlists:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_watchlist",
    ),
    "cap_screener": AiContextCapability(
        module_id="screeners",
        context_type=ContextType.SCREENER_CONTEXT,
        supported_fields=[
            "screener_id",
            "name",
            "universe",
            "filters",
            "sort_order",
            "result_count",
            "selected_row_summary",
        ],
        maximum_payload_size=3072,
        sensitivity_class="INTERNAL",
        requires_explicit_share=False,
        required_permissions=["screeners:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_screener",
    ),
    "cap_economics": AiContextCapability(
        module_id="economics",
        context_type=ContextType.ECONOMICS_CONTEXT,
        supported_fields=[
            "series_id",
            "canonical_name",
            "country",
            "units",
            "frequency",
            "seasonal_adjustment",
            "vintage_date",
            "publication_date",
            "as_of",
        ],
        maximum_payload_size=1536,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=["economics:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_economics",
    ),
    "cap_news": AiContextCapability(
        module_id="news",
        context_type=ContextType.NEWS_CONTEXT,
        supported_fields=[
            "article_id",
            "headline",
            "publisher",
            "publication_timestamp",
            "related_entity_id",
            "licensed_summary",
        ],
        maximum_payload_size=2048,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=["news:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_news",
    ),
    "cap_research": AiContextCapability(
        module_id="research",
        context_type=ContextType.RESEARCH_CONTEXT,
        supported_fields=[
            "report_id",
            "title",
            "version",
            "review_status",
            "author",
            "published_at",
            "as_of",
            "permitted_summary",
            "related_instruments",
        ],
        maximum_payload_size=4096,
        sensitivity_class="CONFIDENTIAL",
        requires_explicit_share=True,
        required_permissions=["research:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_research",
    ),
    "cap_portfolio": AiContextCapability(
        module_id="portfolios",
        context_type=ContextType.PORTFOLIO_CONTEXT,
        supported_fields=[
            "portfolio_id",
            "portfolio_name",
            "reporting_currency",
            "valuation_as_of",
            "benchmark_id",
            "allocation_summary",
            "top_concentration",
            "holdings_shared",
        ],
        maximum_payload_size=3072,
        sensitivity_class="CONFIDENTIAL",
        requires_explicit_share=True,
        required_permissions=["portfolios:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_portfolio",
    ),
    "cap_risk": AiContextCapability(
        module_id="risk",
        context_type=ContextType.RISK_CONTEXT,
        supported_fields=[
            "risk_run_id",
            "portfolio_id",
            "as_of_date",
            "confidence_level",
            "horizon_days",
            "var_metric",
            "cvar_metric",
            "volatility",
            "factor_exposures",
            "model_version",
        ],
        maximum_payload_size=2048,
        sensitivity_class="CONFIDENTIAL",
        requires_explicit_share=True,
        required_permissions=["risk:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_risk",
    ),
    "cap_options": AiContextCapability(
        module_id="options",
        context_type=ContextType.OPTIONS_CONTEXT,
        supported_fields=[
            "underlying_symbol",
            "contract_symbol",
            "expiration",
            "strike",
            "option_type",
            "implied_volatility",
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
        ],
        maximum_payload_size=1536,
        sensitivity_class="PUBLIC",
        requires_explicit_share=False,
        required_permissions=["options:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_options",
    ),
    "cap_data": AiContextCapability(
        module_id="data",
        context_type=ContextType.DATA_CONTEXT,
        supported_fields=[
            "dataset_id",
            "dataset_name",
            "schema_name",
            "column_count",
            "row_count",
            "updated_at",
            "data_quality",
        ],
        maximum_payload_size=1536,
        sensitivity_class="INTERNAL",
        requires_explicit_share=False,
        required_permissions=["data:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_data",
    ),
    "cap_saved": AiContextCapability(
        module_id="saved",
        context_type=ContextType.SAVED_RESOURCE_CONTEXT,
        supported_fields=[
            "saved_id",
            "target_type",
            "target_id",
            "name",
            "version",
            "permission_status",
        ],
        maximum_payload_size=1024,
        sensitivity_class="INTERNAL",
        requires_explicit_share=False,
        required_permissions=["saved:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_saved",
    ),
    "cap_workspace": AiContextCapability(
        module_id="workspaces",
        context_type=ContextType.WORKSPACE_CONTEXT,
        supported_fields=[
            "workspace_id",
            "name",
            "panel_count",
            "active_panel_id",
            "panels_summary",
            "link_groups",
        ],
        maximum_payload_size=2560,
        sensitivity_class="INTERNAL",
        requires_explicit_share=False,
        required_permissions=["workspaces:read"],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_workspace",
    ),
    "cap_linking": AiContextCapability(
        module_id="global_linking",
        context_type=ContextType.LINKED_CONTEXT,
        supported_fields=[
            "channel_id",
            "channel_name",
            "color_token",
            "synchronized_dimensions",
            "snapshot",
            "revision",
        ],
        maximum_payload_size=1536,
        sensitivity_class="INTERNAL",
        requires_explicit_share=False,
        required_permissions=[],
        provider_disclosure_policy=ProviderDisclosureStatus.ALLOWED,
        adapter_id="adapter_global_linking",
    ),
}


def get_capability_by_type(context_type: ContextType) -> Optional[AiContextCapability]:
    """Retrieve capability descriptor by context type."""
    for cap in CAPABILITIES_CATALOG.values():
        if cap.context_type == context_type:
            return cap
    return None


def get_capability_by_module(module_id: str) -> List[AiContextCapability]:
    """Retrieve capabilities supported by a module."""
    return [cap for cap in CAPABILITIES_CATALOG.values() if cap.module_id == module_id]


def list_capabilities() -> List[AiContextCapability]:
    """Return all registered context capabilities."""
    return list(CAPABILITIES_CATALOG.values())


class AiContextCapabilityRegistry:
    """Registry for discovering module context capabilities and disclosure policies."""

    @classmethod
    def list_capabilities(cls) -> List[AiContextCapability]:
        return list_capabilities()

    @classmethod
    def get_by_type(cls, context_type: ContextType) -> Optional[AiContextCapability]:
        return get_capability_by_type(context_type)

    @classmethod
    def get_by_module(cls, module_id: str) -> List[AiContextCapability]:
        return get_capability_by_module(module_id)
