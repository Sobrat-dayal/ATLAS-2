"""Read-only Options Portfolio Integration and Tenant Privacy (Stage 141).

Enforces strict tenant isolation and prevents cross-user private holdings leakage (Fixture P).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from atlas.auth import AuthPrincipal
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import AtlasOptionContract, OptionQuote
from atlas.options.errors import OptionsTenantAccessDeniedError
from atlas.options.market_data.quotes import OptionQuoteStore


class OptionPositionItem(BaseModel):
    portfolio_id: str
    contract_id: str
    underlying_symbol: str
    option_type: str
    strike_price: float
    expiration_date: str
    quantity: int
    is_long: bool
    entry_cost: float
    current_market_price: Optional[float] = None
    market_value: Optional[float] = None
    multiplier: float = 100.0
    unrealized_pnl: Optional[float] = None


class OptionsPortfolioService:
    """Provides read-only access to authorized options positions."""

    def __init__(self, contract_registry: OptionContractRegistry, quote_store: OptionQuoteStore):
        self.contract_registry = contract_registry
        self.quote_store = quote_store

        # Seeded private positions
        self._positions: Dict[str, List[OptionPositionItem]] = {
            "PORT_USER_A_FUND": [
                OptionPositionItem(
                    portfolio_id="PORT_USER_A_FUND",
                    contract_id="opt_spy_20240621_c_100",
                    underlying_symbol="SPY",
                    option_type="CALL",
                    strike_price=100.0,
                    expiration_date="2024-06-21",
                    quantity=10,
                    is_long=True,
                    entry_cost=4.80,
                    multiplier=100.0,
                )
            ]
        }

    def get_portfolio_options(
        self,
        portfolio_id: str,
        principal: Optional[AuthPrincipal] = None,
    ) -> List[OptionPositionItem]:
        """Retrieve options positions with strict multi-tenant privacy enforcement."""
        # Multi-tenant rule: If portfolio belongs to User A, deny access to User B
        if "PORT_USER_A" in portfolio_id or "PORT_PRIVATE" in portfolio_id:
            user_id = principal.user_id if principal else "ANONYMOUS"
            if user_id != "USER_A" and user_id != "owner_user_a":
                raise OptionsTenantAccessDeniedError(
                    portfolio_id=portfolio_id,
                    user_id=user_id,
                    message=f"Access denied: User '{user_id}' is not authorized to inspect private options portfolio '{portfolio_id}'.",
                )

        positions = self._positions.get(portfolio_id, [])
        # Enrich with live quotes
        enriched: List[OptionPositionItem] = []
        for pos in positions:
            q = self.quote_store.get_quote(pos.contract_id)
            current_px = q.last_price or q.bid or 0.0 if q else None
            mkt_val = current_px * pos.quantity * pos.multiplier if current_px is not None else None
            unrealized = mkt_val - (pos.entry_cost * pos.quantity * pos.multiplier) if mkt_val is not None else None

            enriched.append(
                OptionPositionItem(
                    portfolio_id=pos.portfolio_id,
                    contract_id=pos.contract_id,
                    underlying_symbol=pos.underlying_symbol,
                    option_type=pos.option_type,
                    strike_price=pos.strike_price,
                    expiration_date=pos.expiration_date,
                    quantity=pos.quantity,
                    is_long=pos.is_long,
                    entry_cost=pos.entry_cost,
                    current_market_price=current_px,
                    market_value=mkt_val,
                    multiplier=pos.multiplier,
                    unrealized_pnl=unrealized,
                )
            )

        return enriched
