"""Paper Position Registry — tracks open positions (Stage 144)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from atlas.trading.paper.domain import (
    PaperFill,
    PaperOrderSide,
    PaperPosition,
)


class PaperPositionRegistry:
    """Manages paper trading positions per account."""

    def __init__(self) -> None:
        # account_id -> symbol -> PaperPosition
        self._positions: Dict[str, Dict[str, PaperPosition]] = {}

    # ------------------------------------------------------------------
    # Core fill application
    # ------------------------------------------------------------------

    def apply_fill(self, account_id: str, fill: PaperFill) -> Tuple[PaperPosition, float]:
        """Update (or create) a position from a fill.

        Returns (updated_position, realized_pnl).
        """
        self._positions.setdefault(account_id, {})
        positions = self._positions[account_id]
        realized_pnl = 0.0
        now = datetime.now(timezone.utc)

        existing = positions.get(fill.symbol)

        if existing is None or existing.qty <= 0:
            # New position
            position = PaperPosition(
                position_id=str(uuid.uuid4()),
                account_id=account_id,
                symbol=fill.symbol,
                asset_class=fill.asset_class,
                side=fill.side,
                qty=fill.qty,
                avg_cost=fill.price,
                current_price=fill.price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                opened_at=now,
                updated_at=now,
            )
            positions[fill.symbol] = position
            return position, realized_pnl

        # Existing position — determine direction
        same_side = existing.side == fill.side

        if same_side:
            # Adding to position: update average cost
            total_cost = existing.avg_cost * existing.qty + fill.price * fill.qty
            existing.qty += fill.qty
            existing.avg_cost = total_cost / existing.qty
            existing.current_price = fill.price
            existing.unrealized_pnl = (
                (existing.current_price - existing.avg_cost) * existing.qty
                if existing.side == PaperOrderSide.BUY
                else (existing.avg_cost - existing.current_price) * existing.qty
            )
        else:
            # Reducing or closing position
            reduce_qty = min(existing.qty, fill.qty)
            if existing.side == PaperOrderSide.BUY:
                realized_pnl = (fill.price - existing.avg_cost) * reduce_qty
            else:
                realized_pnl = (existing.avg_cost - fill.price) * reduce_qty

            existing.realized_pnl += realized_pnl
            existing.qty -= reduce_qty

            if existing.qty <= 0:
                # Position closed
                existing.qty = 0.0
                existing.unrealized_pnl = 0.0
                # Keep the record but with zero qty
            else:
                existing.current_price = fill.price
                existing.unrealized_pnl = (
                    (existing.current_price - existing.avg_cost) * existing.qty
                    if existing.side == PaperOrderSide.BUY
                    else (existing.avg_cost - existing.current_price) * existing.qty
                )

            remaining_qty = fill.qty - reduce_qty
            if remaining_qty > 0:
                positions[fill.symbol] = PaperPosition(
                    position_id=str(uuid.uuid4()),
                    account_id=account_id,
                    symbol=fill.symbol,
                    asset_class=fill.asset_class,
                    side=fill.side,
                    qty=remaining_qty,
                    avg_cost=fill.price,
                    current_price=fill.price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    opened_at=now,
                    updated_at=now,
                )

        existing.updated_at = now
        positions[fill.symbol] = existing
        return existing, realized_pnl

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_position(self, account_id: str, symbol: str) -> Optional[PaperPosition]:
        """Return the position for a symbol, or None if absent."""
        return self._positions.get(account_id, {}).get(symbol)

    def list_positions(self, account_id: str) -> List[PaperPosition]:
        """Return all non-zero positions for an account."""
        return [p for p in self._positions.get(account_id, {}).values() if p.qty > 0]

    def clear_account(self, account_id: str) -> None:
        self._positions.pop(account_id, None)

    # ------------------------------------------------------------------
    # Price updates
    # ------------------------------------------------------------------

    def update_prices(self, account_id: str, prices: Dict[str, float]) -> None:
        """Refresh current_price and unrealized_pnl for all positions."""
        for symbol, price in prices.items():
            pos = self._positions.get(account_id, {}).get(symbol)
            if pos and pos.qty > 0:
                pos.current_price = price
                if pos.side == PaperOrderSide.BUY:
                    pos.unrealized_pnl = (price - pos.avg_cost) * pos.qty
                else:
                    pos.unrealized_pnl = (pos.avg_cost - price) * pos.qty
                pos.updated_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Corporate actions
    # ------------------------------------------------------------------

    def settle_option_expiry(self, account_id: str, symbol: str, settlement_price: float) -> float:
        """Compute and apply P&L at option expiry.  Returns realized_pnl."""
        pos = self._positions.get(account_id, {}).get(symbol)
        if pos is None or pos.qty == 0:
            return 0.0

        # Each option contract covers 100 shares
        multiplier = 100.0
        if pos.side == PaperOrderSide.BUY:
            pnl = (settlement_price - pos.avg_cost) * pos.qty * multiplier
        else:
            pnl = (pos.avg_cost - settlement_price) * pos.qty * multiplier

        pos.realized_pnl += pnl
        pos.qty = 0.0
        pos.unrealized_pnl = 0.0
        pos.updated_at = datetime.now(timezone.utc)
        return pnl

    def apply_stock_split(self, account_id: str, symbol: str, ratio: float) -> None:
        """Adjust position qty and avg_cost for a stock split.

        *ratio* of 2.0 means 2-for-1 (qty doubles, avg_cost halves).
        """
        pos = self._positions.get(account_id, {}).get(symbol)
        if pos is None or pos.qty == 0:
            return
        pos.qty *= ratio
        pos.avg_cost /= ratio
        pos.updated_at = datetime.now(timezone.utc)
