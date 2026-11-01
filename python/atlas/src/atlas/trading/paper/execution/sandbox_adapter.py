"""Sandbox Execution Adapter — simulates order fills (Stage 144)."""

from __future__ import annotations

from typing import Optional, Tuple

from atlas.trading.paper.domain import (
    PaperOrder,
    PaperOrderSide,
    PaperOrderType,
)
from atlas.trading.paper.errors import LiveBrokerFirewallError


class SandboxExecutionAdapter:
    """Simulates broker execution inside the paper trading sandbox.

    This adapter never connects to real brokers.  All fills, fees, and
    slippage are computed synthetically using configurable parameters.
    """

    LIVE_BROKER_HOSTS: frozenset = frozenset(
        [
            "api.alpaca.markets",
            "api.tradier.com",
            "api1.ibkr.com",
            "api.upstox.com",
        ]
    )

    def __init__(
        self,
        fee_bps: float = 1.0,
        slippage_bps: float = 2.0,
        latency_ms: float = 5.0,
    ) -> None:
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.latency_ms = latency_ms

    # ------------------------------------------------------------------
    # Firewall
    # ------------------------------------------------------------------

    def check_firewall(self, host: str) -> None:
        """Block any attempt to reach a live brokerage host."""
        if host in self.LIVE_BROKER_HOSTS:
            raise LiveBrokerFirewallError(
                f"PAPER MODE: Connection to live broker host '{host}' is blocked. "
                "Use paper-api variants or the sandbox adapter only."
            )

    # ------------------------------------------------------------------
    # Fill Simulation
    # ------------------------------------------------------------------

    def compute_fill_price(
        self,
        order_type: PaperOrderType,
        side: PaperOrderSide,
        limit_price: Optional[float],
        stop_price: Optional[float],
        bid: float,
        ask: float,
    ) -> float:
        """Return a simulated fill price including slippage."""
        slip_mult = self.slippage_bps / 10_000.0

        if order_type == PaperOrderType.MARKET:
            base = ask if side == PaperOrderSide.BUY else bid
            # Add slippage away from mid
            if side == PaperOrderSide.BUY:
                return base * (1 + slip_mult)
            else:
                return base * (1 - slip_mult)

        if order_type == PaperOrderType.LIMIT:
            # For limit orders we fill at the limit price (or better);
            # eligibility is checked in should_fill().
            base = limit_price  # type: ignore[assignment]
            if side == PaperOrderSide.BUY:
                return min(base * (1 + slip_mult), base)
            else:
                return max(base * (1 - slip_mult), base)

        if order_type in (PaperOrderType.STOP, PaperOrderType.STOP_LIMIT):
            # Once triggered, fill at stop price (with slippage).
            base = stop_price  # type: ignore[assignment]
            if side == PaperOrderSide.BUY:
                return base * (1 + slip_mult)
            else:
                return base * (1 - slip_mult)

        if order_type == PaperOrderType.TRAILING_STOP:
            base = bid if side == PaperOrderSide.SELL else ask
            if side == PaperOrderSide.BUY:
                return base * (1 + slip_mult)
            else:
                return base * (1 - slip_mult)

        # Default: market-like
        return ask if side == PaperOrderSide.BUY else bid

    def compute_fee(self, qty: float, price: float) -> float:
        """Return the simulated commission fee."""
        return (self.fee_bps / 10_000.0) * qty * price

    def compute_slippage(self, qty: float, price: float, side: PaperOrderSide) -> float:
        """Return the simulated slippage cost (always positive)."""
        return (self.slippage_bps / 10_000.0) * qty * price

    def should_fill(
        self,
        order: PaperOrder,
        bid: float,
        ask: float,
        market_open: bool,
    ) -> Tuple[bool, str]:
        """Determine whether an order should be filled at current prices.

        Returns (can_fill, reason_string).
        """
        if not market_open:
            return False, "market_closed"

        ot = order.order_type
        side = order.side

        if ot == PaperOrderType.MARKET:
            return True, "market_order_immediate_fill"

        if ot == PaperOrderType.LIMIT:
            if side == PaperOrderSide.BUY:
                if order.limit_price is not None and ask <= order.limit_price:
                    return True, "limit_ask_lte_limit"
                return False, "limit_ask_above_limit"
            else:  # SELL
                if order.limit_price is not None and bid >= order.limit_price:
                    return True, "limit_bid_gte_limit"
                return False, "limit_bid_below_limit"

        if ot == PaperOrderType.STOP:
            if side == PaperOrderSide.BUY:
                # Triggered when ask >= stop_price
                if order.stop_price is not None and ask >= order.stop_price:
                    return True, "stop_triggered_buy"
                return False, "stop_not_triggered"
            else:  # SELL
                # Triggered when bid <= stop_price
                if order.stop_price is not None and bid <= order.stop_price:
                    return True, "stop_triggered_sell"
                return False, "stop_not_triggered"

        if ot == PaperOrderType.STOP_LIMIT:
            if side == PaperOrderSide.BUY:
                triggered = order.stop_price is not None and ask >= order.stop_price
                if triggered and order.limit_price is not None and ask <= order.limit_price:
                    return True, "stop_limit_triggered_buy"
                return False, "stop_limit_not_triggered_or_outside_limit"
            else:
                triggered = order.stop_price is not None and bid <= order.stop_price
                if triggered and order.limit_price is not None and bid >= order.limit_price:
                    return True, "stop_limit_triggered_sell"
                return False, "stop_limit_not_triggered_or_outside_limit"

        if ot == PaperOrderType.TRAILING_STOP:
            # Simplified: treat like a stop using stop_price
            if side == PaperOrderSide.SELL:
                if order.stop_price is not None and bid <= order.stop_price:
                    return True, "trailing_stop_triggered_sell"
                return False, "trailing_stop_not_triggered"
            else:
                if order.stop_price is not None and ask >= order.stop_price:
                    return True, "trailing_stop_triggered_buy"
                return False, "trailing_stop_not_triggered"

        return False, "unknown_order_type"

    def simulate_partial_fill(self, order: PaperOrder, available_qty: float) -> float:
        """Return the quantity to fill for a partial fill scenario."""
        remaining = order.qty - order.filled_qty
        return min(remaining, available_qty)
