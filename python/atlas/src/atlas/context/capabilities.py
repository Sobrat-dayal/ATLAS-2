"""
Capability Registry for ATLAS Stage 121: Global Workspace Linking.
Declares inbound/outbound linking contracts for all panel types.
"""

from typing import Optional

from .enums import ContextDimension
from .models import PanelContextCapability

CAPABILITIES_CATALOG: dict[str, PanelContextCapability] = {
    "MARKET_OVERVIEW": PanelContextCapability(
        panel_type_id="MARKET_OVERVIEW",
        publishable_dimensions=[ContextDimension.INSTRUMENT],
        subscribable_dimensions=[ContextDimension.REPORTING_CURRENCY],
        accepted_entity_types=["INSTRUMENT", "CURRENCY"],
        supports_currency=True,
    ),
    "INSTRUMENT_CHART": PanelContextCapability(
        panel_type_id="INSTRUMENT_CHART",
        publishable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.TIMEFRAME,
            ContextDimension.DATE_RANGE,
        ],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.TIMEFRAME,
            ContextDimension.DATE_RANGE,
            ContextDimension.AS_OF_DATE,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["INSTRUMENT"],
        required_transformations={
            "COMPANY": "PRIMARY_LISTING",
            "OPTION": "UNDERLYING",
        },
        supported_timeframes=["1m", "5m", "15m", "1h", "1D", "1W", "1M", "1Y"],
        supports_as_of=True,
        supports_currency=True,
    ),
    "WATCHLIST": PanelContextCapability(
        panel_type_id="WATCHLIST",
        publishable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
        ],
        subscribable_dimensions=[],
        accepted_entity_types=["INSTRUMENT"],
    ),
    "SCREENER": PanelContextCapability(
        panel_type_id="SCREENER",
        publishable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
        ],
        subscribable_dimensions=[],
        accepted_entity_types=["INSTRUMENT"],
    ),
    "COMPANY_OVERVIEW": PanelContextCapability(
        panel_type_id="COMPANY_OVERVIEW",
        publishable_dimensions=[ContextDimension.COMPANY],
        subscribable_dimensions=[
            ContextDimension.COMPANY,
            ContextDimension.INSTRUMENT,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["COMPANY", "INSTRUMENT"],
        required_transformations={
            "INSTRUMENT": "COMPANY",
        },
        supports_currency=True,
    ),
    "ECONOMIC_SERIES": PanelContextCapability(
        panel_type_id="ECONOMIC_SERIES",
        publishable_dimensions=[
            ContextDimension.ECONOMIC_SERIES,
            ContextDimension.DATE_RANGE,
        ],
        subscribable_dimensions=[
            ContextDimension.ECONOMIC_SERIES,
            ContextDimension.DATE_RANGE,
            ContextDimension.REGION,
        ],
        accepted_entity_types=["ECONOMIC_SERIES"],
        supports_as_of=True,
    ),
    "NEWS_FEED": PanelContextCapability(
        panel_type_id="NEWS_FEED",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
            ContextDimension.REGION,
        ],
        accepted_entity_types=["INSTRUMENT", "COMPANY"],
    ),
    "RESEARCH_DOCUMENT": PanelContextCapability(
        panel_type_id="RESEARCH_DOCUMENT",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
        ],
        accepted_entity_types=["INSTRUMENT", "COMPANY"],
    ),
    "RESEARCH_REPORT": PanelContextCapability(
        panel_type_id="RESEARCH_REPORT",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
        ],
        accepted_entity_types=["INSTRUMENT", "COMPANY"],
    ),
    "PORTFOLIO_SUMMARY": PanelContextCapability(
        panel_type_id="PORTFOLIO_SUMMARY",
        publishable_dimensions=[
            ContextDimension.PORTFOLIO,
            ContextDimension.INSTRUMENT,
        ],
        subscribable_dimensions=[
            ContextDimension.PORTFOLIO,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["PORTFOLIO"],
        supports_currency=True,
    ),
    "PORTFOLIO_PERFORMANCE": PanelContextCapability(
        panel_type_id="PORTFOLIO_PERFORMANCE",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.PORTFOLIO,
            ContextDimension.BENCHMARK,
            ContextDimension.DATE_RANGE,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["PORTFOLIO", "BENCHMARK"],
        supports_as_of=True,
        supports_currency=True,
    ),
    "RISK_OVERVIEW": PanelContextCapability(
        panel_type_id="RISK_OVERVIEW",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.PORTFOLIO,
            ContextDimension.BENCHMARK,
            ContextDimension.AS_OF_DATE,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["PORTFOLIO"],
        supports_as_of=True,
        supports_currency=True,
    ),
    "RISK_ANALYSIS": PanelContextCapability(
        panel_type_id="RISK_ANALYSIS",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.PORTFOLIO,
            ContextDimension.BENCHMARK,
            ContextDimension.AS_OF_DATE,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["PORTFOLIO"],
        supports_as_of=True,
        supports_currency=True,
    ),
    "DATA_TABLE": PanelContextCapability(
        panel_type_id="DATA_TABLE",
        publishable_dimensions=[ContextDimension.INSTRUMENT],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.DATE_RANGE,
            ContextDimension.REPORTING_CURRENCY,
        ],
        accepted_entity_types=["INSTRUMENT"],
        supports_currency=True,
    ),
    # Optional / Future Integration Panels
    "OPTIONS_ANALYTICS": PanelContextCapability(
        panel_type_id="OPTIONS_ANALYTICS",
        publishable_dimensions=[ContextDimension.INSTRUMENT],
        subscribable_dimensions=[ContextDimension.INSTRUMENT, ContextDimension.TIMEFRAME],
        accepted_entity_types=["INSTRUMENT"],
        required_transformations={"OPTION": "UNDERLYING"},
        supports_currency=True,
    ),
    "MAP_VIEW": PanelContextCapability(
        panel_type_id="MAP_VIEW",
        publishable_dimensions=[ContextDimension.REGION],
        subscribable_dimensions=[ContextDimension.REGION, ContextDimension.COMPANY],
        accepted_entity_types=["REGION", "COMPANY"],
    ),
    "INTELLIGENCE_RESULT": PanelContextCapability(
        panel_type_id="INTELLIGENCE_RESULT",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
            ContextDimension.PORTFOLIO,
        ],
        accepted_entity_types=["INSTRUMENT", "COMPANY", "PORTFOLIO"],
    ),
    "AI_ASSISTANT_VIEW": PanelContextCapability(
        panel_type_id="AI_ASSISTANT_VIEW",
        publishable_dimensions=[],
        subscribable_dimensions=[
            ContextDimension.INSTRUMENT,
            ContextDimension.COMPANY,
            ContextDimension.PORTFOLIO,
            ContextDimension.DATE_RANGE,
        ],
        accepted_entity_types=["INSTRUMENT", "COMPANY", "PORTFOLIO"],
    ),
    "AGENT_STATUS": PanelContextCapability(
        panel_type_id="AGENT_STATUS",
        publishable_dimensions=[],
        subscribable_dimensions=[],
        accepted_entity_types=[],
    ),
    "MAP_VIEW": PanelContextCapability(
        panel_type_id="MAP_VIEW",
        publishable_dimensions=[
            ContextDimension.REGION,
            ContextDimension.INSTRUMENT,
        ],
        subscribable_dimensions=[
            ContextDimension.REGION,
            ContextDimension.INSTRUMENT,
        ],
        accepted_entity_types=["INSTRUMENT"],
    ),
}


def get_panel_capability(panel_type_id: str) -> Optional[PanelContextCapability]:
    """Retrieve capability descriptor for a panel type."""
    return CAPABILITIES_CATALOG.get(panel_type_id)


def is_dimension_compatible(
    panel_type_id: str, dimension: ContextDimension, is_outbound: bool = False
) -> bool:
    """Check if a panel type supports publishing or subscribing to a dimension."""
    cap = get_panel_capability(panel_type_id)
    if not cap:
        return False
    if is_outbound:
        return dimension in cap.publishable_dimensions
    return dimension in cap.subscribable_dimensions

