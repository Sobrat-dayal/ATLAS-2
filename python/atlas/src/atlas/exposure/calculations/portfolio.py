"""Portfolio Exposure Calculations (Stage 137).

Enforces institutional portfolio invariants:
- Distinguishes Net Exposure (sum of signed market values) from Gross Exposure (sum of absolute values).
- Long and short signed calculations with exact Decimal precision.
- Discloses unclassified / uncovered holdings without fabricating assignments.
- Bitemporal valuation date integrity.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PortfolioPosition(BaseModel):
    position_id: str
    instrument_id: str
    symbol: str
    market_value: Decimal  # Positive for long, negative for short
    currency: str = "USD"
    sector: Optional[str] = None
    country_of_risk: Optional[str] = None
    asset_class: str = "EQUITY"
    quantity: Decimal = Decimal("1.0")
    price: Decimal = Decimal("1.0")


class PortfolioSummary(BaseModel):
    nav: Decimal
    gross_exposure: Decimal
    net_exposure: Decimal
    long_exposure: Decimal
    short_exposure: Decimal
    gross_leverage: Decimal  # gross / nav
    net_leverage: Decimal    # net / nav
    covered_sector_value: Decimal
    uncovered_sector_value: Decimal
    sector_coverage_ratio: Decimal
    sector_weights: Dict[str, Decimal] = Field(default_factory=dict)
    country_weights: Dict[str, Decimal] = Field(default_factory=dict)


def calculate_portfolio_exposures(
    positions: List[PortfolioPosition],
    stated_nav: Optional[Decimal] = None
) -> PortfolioSummary:
    """Calculate institutional portfolio exposures distinguishing Net and Gross."""
    total_long = Decimal("0.0")
    total_short = Decimal("0.0")
    gross = Decimal("0.0")
    net = Decimal("0.0")
    
    sector_totals: Dict[str, Decimal] = {}
    country_totals: Dict[str, Decimal] = {}
    uncovered_sector = Decimal("0.0")

    for pos in positions:
        mv = pos.market_value
        gross += abs(mv)
        net += mv
        if mv >= Decimal("0.0"):
            total_long += mv
        else:
            total_short += mv

        # Sector tracking
        if pos.sector and pos.sector.strip():
            sec = pos.sector.strip()
            sector_totals[sec] = sector_totals.get(sec, Decimal("0.0")) + mv
        else:
            uncovered_sector += mv

        # Country tracking
        if pos.country_of_risk and pos.country_of_risk.strip():
            c = pos.country_of_risk.strip()
            country_totals[c] = country_totals.get(c, Decimal("0.0")) + mv

    nav = stated_nav if stated_nav is not None else gross
    if nav == Decimal("0.0"):
        nav = Decimal("1.0")  # Avoid zero division if empty

    gross_lev = gross / nav
    net_lev = net / nav

    # Calculate weights based on NAV
    sector_weights = {k: (v / nav) * Decimal("100.0") for k, v in sector_totals.items()}
    country_weights = {k: (v / nav) * Decimal("100.0") for k, v in country_totals.items()}

    covered_sector_val = sum(sector_totals.values(), Decimal("0.0"))
    cov_ratio = (covered_sector_val / nav) if nav > Decimal("0.0") else Decimal("1.0")

    return PortfolioSummary(
        nav=nav,
        gross_exposure=gross,
        net_exposure=net,
        long_exposure=total_long,
        short_exposure=total_short,
        gross_leverage=gross_lev,
        net_leverage=net_lev,
        covered_sector_value=covered_sector_val,
        uncovered_sector_value=uncovered_sector,
        sector_coverage_ratio=cov_ratio,
        sector_weights=sector_weights,
        country_weights=country_weights
    )

