"""Domains module for financial exposure engine."""

from atlas.exposure.domains.company import analyze_company_geographic_revenue
from atlas.exposure.domains.portfolio import analyze_portfolio_holdings
from atlas.exposure.domains.geographic import analyze_geographic_presence_vs_revenue
from atlas.exposure.domains.corporate_group import analyze_corporate_group
from atlas.exposure.domains.supply_chain import analyze_supply_chain_relationship
from atlas.exposure.domains.infrastructure import analyze_facility_event_proximity
from atlas.exposure.domains.derivatives import analyze_option_delta_exposure
from atlas.exposure.domains.macro import analyze_dv01_interest_rate_sensitivity
from atlas.exposure.domains.commodity import analyze_commodity_mention
from atlas.exposure.domains.sector import analyze_entity_sector_classification
from atlas.exposure.domains.event_exposure import analyze_event_driven_exposure

__all__ = [
    "analyze_company_geographic_revenue",
    "analyze_portfolio_holdings",
    "analyze_geographic_presence_vs_revenue",
    "analyze_corporate_group",
    "analyze_supply_chain_relationship",
    "analyze_facility_event_proximity",
    "analyze_option_delta_exposure",
    "analyze_dv01_interest_rate_sensitivity",
    "analyze_commodity_mention",
    "analyze_entity_sector_classification",
    "analyze_event_driven_exposure",
]

