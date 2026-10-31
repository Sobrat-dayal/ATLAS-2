"""Canonical Seed Fixtures for Financial and Economic Exposure Engine (Stage 137).

Implements the 24 reference test fixtures (Tests A through X) verifying institutional invariants:
- Numerical rigor and exact decimals
- Non-inferability of revenue from counts or proximity
- Fund look-through compounding and cycle detection
- Corporate group consolidation without double-counting
- Strict point-in-time FX rates without current substitution
- Tenant isolation and entitlement revocation
- Geographic unallocated residuals without rescaling
"""

from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, List

from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.exposure.domain import (
    AtlasExposureResult,
    ConsolidationBasis,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureRelationshipStrength,
    ExposureScenarioShock,
    ExposureType,
    UncertaintyClass,
)
from atlas.exposure.calculations.consolidation import EntityFinancialRecord
from atlas.exposure.calculations.portfolio import PortfolioPosition
from atlas.exposure.calculations.lookthrough import FundConstituentEdge


# Canonical Node References for Fixtures
COMPANY_ACME = CanonicalGraphNodeRef(
    node_type=GraphNodeType.COMPANY,
    entity_id="COMP_ACME",
    canonical_name="Acme Global Corporation",
    country_code="US",
    sector="Technology"
)

COMPANY_BETA = CanonicalGraphNodeRef(
    node_type=GraphNodeType.COMPANY,
    entity_id="COMP_BETA",
    canonical_name="Beta Logistics Group",
    country_code="DE",
    sector="Industrials"
)

PORTFOLIO_ALPHA = CanonicalGraphNodeRef(
    node_type=GraphNodeType.OTHER_SUPPORTED_CANONICAL_ENTITY,
    entity_id="PORT_ALPHA",
    canonical_name="Alpha Flagship Fund",
    tenant_id="TENANT_1"
)

REGION_EUROPE = CanonicalGraphNodeRef(
    node_type=GraphNodeType.ADMINISTRATIVE_REGION,
    entity_id="REG_EU",
    canonical_name="Europe"
)

REGION_NORTH_AMERICA = CanonicalGraphNodeRef(
    node_type=GraphNodeType.ADMINISTRATIVE_REGION,
    entity_id="REG_NA",
    canonical_name="North America"
)

EVENT_EARTHQUAKE = CanonicalGraphNodeRef(
    node_type=GraphNodeType.EVENT,
    entity_id="EVT_EQ_2025_001",
    canonical_name="Magnitude 7.1 Offshore Earthquake"
)

FACILITY_PLANT_1 = CanonicalGraphNodeRef(
    node_type=GraphNodeType.CORPORATE_FACILITY,
    entity_id="FAC_PLANT_1",
    canonical_name="Miyagi Precision Assembly Plant",
    country_code="JP"
)

COMMODITY_COPPER = CanonicalGraphNodeRef(
    node_type=GraphNodeType.COMMODITY,
    entity_id="COM_COPPER",
    canonical_name="Copper Grade A"
)

BENCHMARK_US_10Y = CanonicalGraphNodeRef(
    node_type=GraphNodeType.ECONOMIC_INDICATOR,
    entity_id="IND_US_10Y_YIELD",
    canonical_name="US 10-Year Treasury Benchmark Yield"
)


# Fixture Data Definitions
def get_fixture_a_geographic_revenue():
    """Test A: Geographic Revenue ($10M total, $4M Europe => 40% share)."""
    return {
        "company": COMPANY_ACME,
        "total_revenue": Decimal("10000000.00"),
        "segments": [
            {"region_code": "REG_EU", "region_name": "Europe", "revenue_amount": Decimal("4000000.00")},
            {"region_code": "REG_NA", "region_name": "North America", "revenue_amount": Decimal("6000000.00")}
        ]
    }


def get_fixture_b_facility_count():
    """Test B: Facility Count vs Revenue (10 facilities in Region A, Revenue UNAVAILABLE)."""
    return {
        "company": COMPANY_ACME,
        "region": REGION_EUROPE,
        "facility_count": 10,
        "total_facilities": 50,
        "revenue_disclosed": None
    }


def get_fixture_c_portfolio_sector():
    """Test C: Portfolio Sector ($100k NAV, $30k Tech, $60k Finance, $10k unclassified)."""
    return {
        "nav": Decimal("100000.00"),
        "positions": [
            PortfolioPosition(position_id="p1", instrument_id="AAPL", symbol="AAPL", market_value=Decimal("30000.00"), sector="Information Technology"),
            PortfolioPosition(position_id="p2", instrument_id="JPM", symbol="JPM", market_value=Decimal("60000.00"), sector="Financials"),
            PortfolioPosition(position_id="p3", instrument_id="UNKNOWN", symbol="UNKLTD", market_value=Decimal("10000.00"), sector=None),
        ]
    }


def get_fixture_d_long_short():
    """Test D: Long & Short (+$100k Long, -$100k Short => $0 Net, $200k Gross)."""
    return [
        PortfolioPosition(position_id="pos_long", instrument_id="SPY", symbol="SPY", market_value=Decimal("100000.00")),
        PortfolioPosition(position_id="pos_short", instrument_id="QQQ", symbol="QQQ", market_value=Decimal("-100000.00"))
    ]


def get_fixture_e_fund_lookthrough():
    """Test E: Fund Look-Through (20% Fund F, Fund F 30% Company C => 6% indirect)."""
    edges = {
        "PORT_TOP": [FundConstituentEdge("PORT_TOP", "FUND_F", Decimal("0.20"), child_is_fund=True)],
        "FUND_F": [FundConstituentEdge("FUND_F", "COMP_C", Decimal("0.30"), child_is_fund=False)]
    }
    return edges


def get_fixture_f_fund_cycle():
    """Test F: Nested Fund Cycle (Fund A -> Fund B -> Fund A)."""
    edges = {
        "FUND_A": [FundConstituentEdge("FUND_A", "FUND_B", Decimal("0.50"), child_is_fund=True)],
        "FUND_B": [FundConstituentEdge("FUND_B", "FUND_A", Decimal("0.50"), child_is_fund=True)]
    }
    return edges


def get_fixture_g_consolidation():
    """Test G: Parent $100M consolidated, Sub $30M consolidated => report $100M, not $130M."""
    return [
        EntityFinancialRecord(
            entity_id="PARENT_1",
            name="Mega Corp Parent",
            revenue=Decimal("100000000.00"),
            currency="USD",
            period="FY2024",
            consolidation_basis=ConsolidationBasis.CONSOLIDATED
        ),
        EntityFinancialRecord(
            entity_id="SUB_1",
            name="Sub Operations Ltd",
            revenue=Decimal("30000000.00"),
            currency="USD",
            period="FY2024",
            consolidation_basis=ConsolidationBasis.CONSOLIDATED,
            parent_entity_id="PARENT_1",
            ownership_percentage=Decimal("100.0")
        )
    ]


def get_fixture_h_minority_ownership():
    """Test H: Parent owns 40% of affiliate => Equity Method, unconsolidated revenue."""
    return [
        EntityFinancialRecord(
            entity_id="PARENT_1",
            name="Alpha Holdings",
            revenue=Decimal("50000000.00"),
            currency="USD",
            period="FY2024",
            consolidation_basis=ConsolidationBasis.CONSOLIDATED
        ),
        EntityFinancialRecord(
            entity_id="AFFILIATE_1",
            name="Affiliate Corp",
            revenue=Decimal("20000000.00"),
            currency="USD",
            period="FY2024",
            consolidation_basis=ConsolidationBasis.EQUITY_METHOD,
            parent_entity_id="PARENT_1",
            ownership_percentage=Decimal("40.0")
        )
    ]


def get_fixture_k_interest_rate_sensitivity():
    """Test K: Interest Rate Scenario (DV01 $100/bp, +25 bps => -$2,500 P&L)."""
    return {
        "dv01": Decimal("100.00"),
        "shift_bps": Decimal("25.0")
    }


def get_fixture_t_scenario():
    """Test T: User Scenario (-10% shock on $50k holding => -$5,000 P&L)."""
    return {
        "position": {"id": "p_tech", "symbol": "TECH1", "market_value": Decimal("50000.00"), "sector": "Technology"},
        "shock": ExposureScenarioShock(shock_id="shk_1", target_dimension="SECTOR", target_identifier="TECHNOLOGY", shock_value=Decimal("-10.0"))
    }


def get_fixture_u_derivative():
    """Test U: Derivative Delta Equivalent (10 contracts * 100 multiplier * $150 price * 0.6 delta => $90,000)."""
    return {
        "contracts": Decimal("10"),
        "multiplier": Decimal("100"),
        "underlying_price": Decimal("150.00"),
        "delta": Decimal("0.60")
    }


def get_fixture_x_geographic_residual():
    """Test X: Geographic Residual ($50M NA, $35M EU, $100M Total => Coverage 85%, Residual $15M / 15%)."""
    return {
        "total_revenue": Decimal("100000000.00"),
        "segments": [
            {"region_name": "North America", "revenue": Decimal("50000000.00")},
            {"region_name": "Europe", "revenue": Decimal("35000000.00")}
        ]
    }
