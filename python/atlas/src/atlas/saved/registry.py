"""Canonical Target Registry and Safe Deep Link Builders for Stage 119."""

from __future__ import annotations

import urllib.parse
from typing import Dict, List, Optional

from atlas.saved.enums import (
    SavedModule,
    SavedReferenceSemantics,
    SavedTargetType,
)
from atlas.saved.models import SavedTargetDefinition

TARGET_CATALOG: Dict[SavedTargetType, SavedTargetDefinition] = {
    SavedTargetType.INSTRUMENT: SavedTargetDefinition(
        target_type=SavedTargetType.INSTRUMENT,
        module=SavedModule.MARKETS,
        display_name="Financial Instrument",
        description="Canonical equity, bond, ETF, crypto, FX, or commodity instrument reference.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.COMPANY: SavedTargetDefinition(
        target_type=SavedTargetType.COMPANY,
        module=SavedModule.COMPANIES,
        display_name="Company Profile",
        description="Public or private corporate entity profile, filings, earnings, and fundamentals.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.CHART_CONFIG: SavedTargetDefinition(
        target_type=SavedTargetType.CHART_CONFIG,
        module=SavedModule.CHARTS,
        display_name="Saved Chart Configuration",
        description="Configured interactive chart with timeframe, technical indicators, and overlays.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION,
    ),
    SavedTargetType.SCREENER_CONFIG: SavedTargetDefinition(
        target_type=SavedTargetType.SCREENER_CONFIG,
        module=SavedModule.SCREENERS,
        display_name="Saved Screener Configuration",
        description="Saved quantitative filter criteria, metrics thresholds, and universe criteria.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION,
    ),
    SavedTargetType.WATCHLIST_REFERENCE: SavedTargetDefinition(
        target_type=SavedTargetType.WATCHLIST_REFERENCE,
        module=SavedModule.WATCHLISTS,
        display_name="Watchlist Reference",
        description="Pointer to an existing personal or organizational watchlist.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.ECONOMIC_SERIES: SavedTargetDefinition(
        target_type=SavedTargetType.ECONOMIC_SERIES,
        module=SavedModule.ECONOMICS,
        display_name="Macroeconomic Series",
        description="Central bank, sovereign, or global macro economic time-series indicator.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.NEWS_ARTICLE: SavedTargetDefinition(
        target_type=SavedTargetType.NEWS_ARTICLE,
        module=SavedModule.NEWS,
        display_name="News Article Reference",
        description="Curated news dispatch or research intelligence wire reference.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.RESEARCH_INVESTIGATION: SavedTargetDefinition(
        target_type=SavedTargetType.RESEARCH_INVESTIGATION,
        module=SavedModule.RESEARCH,
        display_name="Research Investigation",
        description="Institutional research investigation workspace with theses, claims, and notes.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.RESEARCH_DOCUMENT: SavedTargetDefinition(
        target_type=SavedTargetType.RESEARCH_DOCUMENT,
        module=SavedModule.RESEARCH,
        display_name="Research Source Document",
        description="Official filing, earnings transcript, or verified regulatory document.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.RESEARCH_REPORT: SavedTargetDefinition(
        target_type=SavedTargetType.RESEARCH_REPORT,
        module=SavedModule.RESEARCH,
        display_name="Research Report",
        description="Formal analyst research report with versioned review and approval lifecycle.",
        supports_view_config=False,
        supports_revision_pin=True,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.RESEARCH_ANALYSIS_RUN: SavedTargetDefinition(
        target_type=SavedTargetType.RESEARCH_ANALYSIS_RUN,
        module=SavedModule.RESEARCH,
        display_name="Research Analysis Run",
        description="Immutable quantitative research model execution and hypothesis evaluation run.",
        supports_view_config=False,
        supports_revision_pin=True,
        semantics=SavedReferenceSemantics.IMMUTABLE_RUN_REFERENCE,
    ),
    SavedTargetType.PORTFOLIO_REFERENCE: SavedTargetDefinition(
        target_type=SavedTargetType.PORTFOLIO_REFERENCE,
        module=SavedModule.PORTFOLIOS,
        display_name="Portfolio Reference",
        description="Bookmarked investment portfolio, account group, or mandate overview.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.PORTFOLIO_VIEW_CONFIG: SavedTargetDefinition(
        target_type=SavedTargetType.PORTFOLIO_VIEW_CONFIG,
        module=SavedModule.PORTFOLIOS,
        display_name="Portfolio View Configuration",
        description="Configured portfolio presentation view with benchmark, date-range, and panels.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION,
    ),
    SavedTargetType.PORTFOLIO_ANALYSIS_RUN: SavedTargetDefinition(
        target_type=SavedTargetType.PORTFOLIO_ANALYSIS_RUN,
        module=SavedModule.PORTFOLIOS,
        display_name="Portfolio Performance Run",
        description="Immutable portfolio accounting, valuation, performance, or attribution run.",
        supports_view_config=False,
        supports_revision_pin=True,
        semantics=SavedReferenceSemantics.IMMUTABLE_RUN_REFERENCE,
    ),
    SavedTargetType.RISK_RUN: SavedTargetDefinition(
        target_type=SavedTargetType.RISK_RUN,
        module=SavedModule.RISK,
        display_name="Risk Calculation Run",
        description="Immutable Stage 115-118 market risk, VaR, factor, options, or fixed-income run.",
        supports_view_config=False,
        supports_revision_pin=True,
        semantics=SavedReferenceSemantics.IMMUTABLE_RUN_REFERENCE,
    ),
    SavedTargetType.RISK_SCENARIO: SavedTargetDefinition(
        target_type=SavedTargetType.RISK_SCENARIO,
        module=SavedModule.RISK,
        display_name="Risk Stress Scenario",
        description="Defined macroeconomic stress test, historical replay, or custom shock scenario.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION,
    ),
    SavedTargetType.MARKET_VIEW_CONFIG: SavedTargetDefinition(
        target_type=SavedTargetType.MARKET_VIEW_CONFIG,
        module=SavedModule.MARKETS,
        display_name="Market View Configuration",
        description="Cross-asset market overview layout, heatmap settings, and movers filters.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION,
    ),
    SavedTargetType.MAP_VIEW_CONFIG: SavedTargetDefinition(
        target_type=SavedTargetType.MAP_VIEW_CONFIG,
        module=SavedModule.MAPS,
        display_name="Geographic Map Configuration",
        description="Geographic exposure, supply chain map layers, and regional filters.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION,
    ),
    SavedTargetType.DATA_RESOURCE: SavedTargetDefinition(
        target_type=SavedTargetType.DATA_RESOURCE,
        module=SavedModule.DATA,
        display_name="Data Resource Reference",
        description="Cataloged financial dataset, custom time-series, or data query definition.",
        supports_view_config=True,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.AI_ARTIFACT: SavedTargetDefinition(
        target_type=SavedTargetType.AI_ARTIFACT,
        module=SavedModule.AI,
        display_name="AI Artifact Reference",
        description="Saved financial AI synthesis document or quantitative model artifact.",
        supports_view_config=False,
        supports_revision_pin=True,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.INTELLIGENCE_ARTIFACT: SavedTargetDefinition(
        target_type=SavedTargetType.INTELLIGENCE_ARTIFACT,
        module=SavedModule.INTELLIGENCE,
        display_name="Intelligence Artifact",
        description="Intelligence feed highlight, central bank dispatch, or geopolitical note.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
    SavedTargetType.OTHER_REGISTERED_RESOURCE: SavedTargetDefinition(
        target_type=SavedTargetType.OTHER_REGISTERED_RESOURCE,
        module=SavedModule.SAVED,
        display_name="Generic Registered Resource",
        description="Extensible pointer to any authorized canonical ATLAS resource.",
        supports_view_config=False,
        supports_revision_pin=False,
        semantics=SavedReferenceSemantics.LIVE_REFERENCE,
    ),
}


def build_safe_deep_link(
    target_type: SavedTargetType,
    target_id: str,
    target_revision_id: Optional[str] = None,
    configuration_id: Optional[str] = None,
) -> str:
    """
    Constructs a strictly internal, sanitized deep link to reopen the original resource
    in the authoritative ATLAS module.

    Security guarantees:
    - Never generates external URLs (no 'http://' or 'https://')
    - Never permits pseudo-protocols ('javascript:', 'data:', 'file:')
    - Properly URL-encodes all query parameters
    - Enforces verified route roots matching the 20 global routes
    """
    safe_id = urllib.parse.quote_plus(str(target_id).strip())
    safe_rev = (
        urllib.parse.quote_plus(str(target_revision_id).strip()) if target_revision_id else None
    )
    safe_config = (
        urllib.parse.quote_plus(str(configuration_id).strip()) if configuration_id else None
    )

    if target_type == SavedTargetType.INSTRUMENT:
        return f"/markets?instrument_id={safe_id}"
    elif target_type == SavedTargetType.COMPANY:
        return f"/companies?id={safe_id}"
    elif target_type == SavedTargetType.CHART_CONFIG:
        path = f"/charts?config_id={safe_id}"
        if safe_config and safe_config != safe_id:
            path += f"&view_config_id={safe_config}"
        return path
    elif target_type == SavedTargetType.SCREENER_CONFIG:
        path = f"/screeners?screen_id={safe_id}"
        if safe_config and safe_config != safe_id:
            path += f"&view_config_id={safe_config}"
        return path
    elif target_type == SavedTargetType.WATCHLIST_REFERENCE:
        return f"/watchlists?id={safe_id}"
    elif target_type == SavedTargetType.ECONOMIC_SERIES:
        return f"/economics?series_id={safe_id}"
    elif target_type == SavedTargetType.NEWS_ARTICLE:
        return f"/news?article_id={safe_id}"
    elif target_type == SavedTargetType.RESEARCH_INVESTIGATION:
        return f"/research?investigation_id={safe_id}"
    elif target_type == SavedTargetType.RESEARCH_DOCUMENT:
        return f"/research?document_id={safe_id}"
    elif target_type == SavedTargetType.RESEARCH_REPORT:
        path = f"/research?report_id={safe_id}"
        if safe_rev:
            path += f"&revision_id={safe_rev}"
        return path
    elif target_type == SavedTargetType.RESEARCH_ANALYSIS_RUN:
        return f"/research?analysis_run_id={safe_id}"
    elif target_type == SavedTargetType.PORTFOLIO_REFERENCE:
        return f"/portfolios?portfolio_id={safe_id}"
    elif target_type == SavedTargetType.PORTFOLIO_VIEW_CONFIG:
        path = f"/portfolios?portfolio_id={safe_id}"
        if safe_config:
            path += f"&view_config_id={safe_config}"
        return path
    elif target_type == SavedTargetType.PORTFOLIO_ANALYSIS_RUN:
        return f"/portfolios?analysis_run_id={safe_id}"
    elif target_type == SavedTargetType.RISK_RUN:
        return f"/risk?run_id={safe_id}"
    elif target_type == SavedTargetType.RISK_SCENARIO:
        return f"/risk?scenario_id={safe_id}"
    elif target_type == SavedTargetType.MARKET_VIEW_CONFIG:
        return f"/markets?view_config_id={safe_id}"
    elif target_type == SavedTargetType.MAP_VIEW_CONFIG:
        return f"/maps?config_id={safe_id}"
    elif target_type == SavedTargetType.DATA_RESOURCE:
        return f"/data?resource_id={safe_id}"
    elif target_type == SavedTargetType.AI_ARTIFACT:
        return f"/ai?artifact_id={safe_id}"
    elif target_type == SavedTargetType.INTELLIGENCE_ARTIFACT:
        return f"/intelligence?artifact_id={safe_id}"
    else:
        return f"/saved?target_id={safe_id}"


def get_target_definition(target_type: SavedTargetType) -> Optional[SavedTargetDefinition]:
    """Retrieves target definition from catalog."""
    return TARGET_CATALOG.get(target_type)


def list_supported_target_types() -> List[SavedTargetDefinition]:
    """Lists all cataloged target types."""
    return list(TARGET_CATALOG.values())
