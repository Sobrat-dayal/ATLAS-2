"""ATLAS Paper Trading Service — Stage 144."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Dict, List, Optional

from atlas.trading.paper.accounts.registry import PaperAccountRegistry
from atlas.trading.paper.domain import (
    STAGE_144_DISCLAIMERS,
    AccountSnapshot,
    AssetClass,
    KillSwitchEvent,
    PaperAccount,
    PaperFill,
    PaperOrder,
    PaperOrderSide,
    PaperOrderStatus,
    PaperOrderType,
    PaperPosition,
    RiskPolicy,
    TimeInForce,
)
from atlas.trading.paper.errors import (
    CrossTenantAccessError,
    KillSwitchActiveError,
    MarketClosedError,
    RiskPolicyViolationError,
    StaleMarketDataError,
)
from atlas.trading.paper.execution.orders import PaperOrderBook
from atlas.trading.paper.execution.sandbox_adapter import SandboxExecutionAdapter
from atlas.trading.paper.positions.registry import PaperPositionRegistry
from atlas.trading.paper.recovery.event_store import PaperEventStore
from atlas.trading.paper.risk.policies import RiskPolicyEngine
from atlas.trading.paper.strategies.deployments import PaperStrategyRegistry


class AtlasPaperTradingService:
    """Orchestrates the ATLAS paper trading sandbox.

    All execution is simulated. No real broker connections are made.
    All account balances, fills, and positions are virtual (PAPER ONLY).
    """

    DISCLAIMER = STAGE_144_DISCLAIMERS

    def __init__(
        self,
        fee_bps: float = 1.0,
        slippage_bps: float = 2.0,
        latency_ms: float = 5.0,
        stale_data_threshold_s: float = 60.0,
    ) -> None:
        self._accounts = PaperAccountRegistry()
        self._order_book = PaperOrderBook()
        self._positions = PaperPositionRegistry()
        self._risk = RiskPolicyEngine()
        self._event_store = PaperEventStore()
        self._strategies = PaperStrategyRegistry()
        self._sandbox = SandboxExecutionAdapter(fee_bps, slippage_bps, latency_ms)
        self._stale_threshold = stale_data_threshold_s
        # symbol -> {bid, ask, timestamp, market_open}
        self._market_data: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Account Management
    # ------------------------------------------------------------------

    def create_account(
        self,
        tenant_id: str,
        label: str,
        initial_cash: float = 10_000.0,
        currency: str = "USD",
        description: str = "",
    ) -> PaperAccount:
        account = self._accounts.create_account(
            tenant_id, label, currency, initial_cash, description
        )
        self._event_store.append(
            "ACCOUNT_CREATED",
            {"account_id": account.account_id, "tenant_id": tenant_id},
        )
        return account

    def get_account(self, account_id: str, tenant_id: str) -> PaperAccount:
        return self._accounts.get_account(account_id, tenant_id)

    def list_accounts(self, tenant_id: str) -> List[PaperAccount]:
        return self._accounts.list_accounts(tenant_id)

    def reset_account(self, account_id: str, tenant_id: str) -> PaperAccount:
        self._accounts.reset_account(account_id, tenant_id)
        self._order_book.clear_account(account_id)
        self._positions.clear_account(account_id)
        account = self._accounts.get_account(account_id, tenant_id)
        self._event_store.append("ACCOUNT_RESET", {"account_id": account_id})
        return account

    # ------------------------------------------------------------------
    # Market Data Feed
    # ------------------------------------------------------------------

    def update_market_data(
        self,
        symbol: str,
        bid: float,
        ask: float,
        market_open: bool = True,
        timestamp: Optional[datetime] = None,
    ) -> None:
        if not symbol.strip():
            raise ValueError("symbol must not be empty")
        if not all(isfinite(value) and value > 0 for value in (bid, ask)):
            raise ValueError("bid and ask must be finite positive values")
        if bid > ask:
            raise ValueError("bid must not exceed ask")
        quote_timestamp = timestamp or datetime.now(timezone.utc)
        if quote_timestamp.tzinfo is None:
            quote_timestamp = quote_timestamp.replace(tzinfo=timezone.utc)
        self._market_data[symbol] = {
            "bid": bid,
            "ask": ask,
            "market_open": market_open,
            "timestamp": quote_timestamp,
        }

    def _get_quote(self, symbol: str) -> Dict[str, Any]:
        quote = self._market_data.get(symbol)
        if not quote:
            raise StaleMarketDataError(f"No market data available for '{symbol}'.")
        age_s = (datetime.now(timezone.utc) - quote["timestamp"]).total_seconds()
        if age_s < 0 or age_s > self._stale_threshold:
            raise StaleMarketDataError(
                f"Market data for '{symbol}' is {age_s:.0f}s old "
                f"(threshold={self._stale_threshold}s)."
            )
        return quote

    # ------------------------------------------------------------------
    # Order Submission
    # ------------------------------------------------------------------

    def submit_order(
        self,
        account_id: str,
        tenant_id: str,
        symbol: str,
        side: PaperOrderSide,
        order_type: PaperOrderType,
        qty: float,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        asset_class: AssetClass = AssetClass.EQUITY,
        time_in_force: TimeInForce = TimeInForce.DAY,
        option_contract: Optional[Dict] = None,
        client_order_id: Optional[str] = None,
        policy: Optional[RiskPolicy] = None,
    ) -> PaperOrder:
        account = self._accounts.get_account(account_id, tenant_id)
        self._risk.check_kill_switch(account)

        if client_order_id:
            existing = self._order_book.get_by_client_order_id(client_order_id)
            if existing is not None:
                if existing.account_id != account_id:
                    raise CrossTenantAccessError(
                        "client_order_id is already used by another account."
                    )
                return existing

        if not isfinite(qty) or qty <= 0:
            raise ValueError("qty must be a finite positive value")
        if order_type in (PaperOrderType.LIMIT, PaperOrderType.STOP_LIMIT):
            if limit_price is None or not isfinite(limit_price) or limit_price <= 0:
                raise ValueError("limit orders require a finite positive limit_price")
        if order_type in (
            PaperOrderType.STOP,
            PaperOrderType.STOP_LIMIT,
            PaperOrderType.TRAILING_STOP,
        ):
            if stop_price is None or not isfinite(stop_price) or stop_price <= 0:
                raise ValueError("stop orders require a finite positive stop_price")

        quote = self._get_quote(symbol)
        if not quote["market_open"]:
            raise MarketClosedError(f"Market is closed for '{symbol}'.")

        order = PaperOrder(
            order_id=str(uuid.uuid4()),
            account_id=account_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=qty,
            filled_qty=0.0,
            limit_price=limit_price,
            stop_price=stop_price,
            status=PaperOrderStatus.OPEN,
            asset_class=asset_class,
            time_in_force=time_in_force,
            submitted_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            fills=[],
            option_contract=option_contract,
            client_order_id=client_order_id,
        )

        open_orders = self._order_book.list_open(account_id)
        positions = self._positions.list_positions(account_id)
        effective_policy = policy or self._risk.DEFAULT_POLICY
        reference_price = quote["ask"] if side == PaperOrderSide.BUY else quote["bid"]
        self._risk.validate_order(
            account,
            order,
            open_orders,
            positions,
            effective_policy,
            reference_price=reference_price,
        )

        self._order_book.submit(order)
        self._event_store.append(
            "ORDER_SUBMITTED",
            {"order_id": order.order_id, "symbol": symbol},
        )
        self._try_fill(order, quote, account, effective_policy)
        return self._order_book.get(order.order_id)

    def _try_fill(
        self,
        order: PaperOrder,
        quote: Dict[str, Any],
        account: PaperAccount,
        policy: RiskPolicy,
    ) -> None:
        can_fill, reason = self._sandbox.should_fill(
            order, quote["bid"], quote["ask"], quote["market_open"]
        )
        if not can_fill:
            return

        fill_price = self._sandbox.compute_fill_price(
            order.order_type,
            order.side,
            order.limit_price,
            order.stop_price,
            quote["bid"],
            quote["ask"],
        )
        fill_qty = order.qty - order.filled_qty
        if fill_qty <= 0:
            return
        fee = self._sandbox.compute_fee(fill_qty, fill_price)
        slippage = self._sandbox.compute_slippage(fill_qty, fill_price, order.side)

        fill = PaperFill(
            fill_id=str(uuid.uuid4()),
            order_id=order.order_id,
            account_id=account.account_id,
            symbol=order.symbol,
            side=order.side,
            qty=fill_qty,
            price=fill_price,
            fee=fee,
            slippage_cost=slippage,
            filled_at=datetime.now(timezone.utc),
            asset_class=order.asset_class,
        )

        order = self._order_book.apply_fill(order.order_id, fill)
        position, realized_pnl = self._positions.apply_fill(account.account_id, fill)

        # Update account cash
        if order.side == PaperOrderSide.BUY:
            account.cash -= fill_qty * fill_price + fee
        else:
            account.cash += fill_qty * fill_price - fee

        account.daily_realized_pnl += realized_pnl
        account.updated_at = datetime.now(timezone.utc)
        self._refresh_account(account)
        self._accounts.update_account(account)

        # Check daily loss after fill
        try:
            self._risk.check_daily_loss(account, policy)
        except KillSwitchActiveError:
            # Kill switch was just activated by daily loss; persist and re-raise
            self._accounts.update_account(account)
            self._event_store.append(
                "KILL_SWITCH_ACTIVATED",
                {"account_id": account.account_id, "reason": "daily_loss_limit"},
            )
            raise

        self._event_store.append(
            "ORDER_FILLED",
            {
                "order_id": order.order_id,
                "fill_id": fill.fill_id,
                "realized_pnl": realized_pnl,
            },
        )

    # ------------------------------------------------------------------
    # Order Management
    # ------------------------------------------------------------------

    def cancel_order(self, order_id: str, account_id: str, tenant_id: str) -> PaperOrder:
        self._accounts.get_account(account_id, tenant_id)
        return self._order_book.cancel(order_id, account_id, tenant_id)

    def get_order(self, order_id: str, account_id: str, tenant_id: str) -> PaperOrder:
        self._accounts.get_account(account_id, tenant_id)
        order = self._order_book.get(order_id)
        if order.account_id != account_id:
            raise CrossTenantAccessError("Order does not belong to this account.")
        return order

    def list_orders(self, account_id: str, tenant_id: str) -> List[PaperOrder]:
        self._accounts.get_account(account_id, tenant_id)
        return self._order_book.list_all(account_id)

    def refresh_orders(self, account_id: str, tenant_id: str) -> List[PaperOrder]:
        """Re-evaluate open conditional orders against the latest quotes."""
        self._accounts.get_account(account_id, tenant_id)
        for order in self._order_book.list_open(account_id):
            quote = self._get_quote(order.symbol)
            if not quote["market_open"]:
                continue
            account = self._accounts.get_account(account_id, tenant_id)
            self._try_fill(order, quote, account, self._risk.DEFAULT_POLICY)
        return self._order_book.list_all(account_id)

    def modify_order(
        self,
        order_id: str,
        account_id: str,
        tenant_id: str,
        *,
        qty: Optional[float] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> PaperOrder:
        self._accounts.get_account(account_id, tenant_id)
        order = self.get_order(order_id, account_id, tenant_id)
        if order.status not in (PaperOrderStatus.OPEN, PaperOrderStatus.PARTIAL):
            raise RiskPolicyViolationError("Only open orders can be modified.")
        if qty is not None:
            if not isfinite(qty) or qty <= order.filled_qty:
                raise ValueError("qty must exceed filled_qty and be finite")
            order.qty = qty
        if limit_price is not None:
            if not isfinite(limit_price) or limit_price <= 0:
                raise ValueError("limit_price must be a finite positive value")
            order.limit_price = limit_price
        if stop_price is not None:
            if not isfinite(stop_price) or stop_price <= 0:
                raise ValueError("stop_price must be a finite positive value")
            order.stop_price = stop_price
        order.updated_at = datetime.now(timezone.utc)
        self._order_book.update(order)
        self._event_store.append("ORDER_MODIFIED", {"order_id": order_id})
        return order

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def list_positions(self, account_id: str, tenant_id: str) -> List[PaperPosition]:
        self._accounts.get_account(account_id, tenant_id)
        return self._positions.list_positions(account_id)

    # ------------------------------------------------------------------
    # Kill Switch
    # ------------------------------------------------------------------

    def activate_kill_switch(
        self,
        account_id: str,
        tenant_id: str,
        reason: str,
        triggered_by: str,
    ) -> KillSwitchEvent:
        account = self._accounts.get_account(account_id, tenant_id)
        event = self._risk.activate_kill_switch(account, reason, triggered_by)
        self._accounts.update_account(account)
        self._event_store.append(
            "KILL_SWITCH_ACTIVATED",
            {"account_id": account_id, "reason": reason},
        )
        return event

    # ------------------------------------------------------------------
    # Corporate Actions
    # ------------------------------------------------------------------

    def settle_option_expiry(
        self,
        account_id: str,
        tenant_id: str,
        symbol: str,
        settlement_price: float,
    ) -> float:
        self._accounts.get_account(account_id, tenant_id)
        pnl = self._positions.settle_option_expiry(account_id, symbol, settlement_price)
        return pnl

    def apply_stock_split(
        self,
        account_id: str,
        tenant_id: str,
        symbol: str,
        ratio: float,
    ) -> None:
        self._accounts.get_account(account_id, tenant_id)
        self._positions.apply_stock_split(account_id, symbol, ratio)

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def take_snapshot(self, account_id: str, tenant_id: str) -> AccountSnapshot:
        account = self._accounts.get_account(account_id, tenant_id)
        self._refresh_account(account)
        positions = self._positions.list_positions(account_id)
        positions_value = sum(p.qty * p.current_price for p in positions if p.current_price)
        unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        snap = AccountSnapshot(
            snapshot_id=str(uuid.uuid4()),
            account_id=account_id,
            cash=account.cash,
            equity=account.cash + positions_value,
            positions_value=positions_value,
            margin_used=account.margin_used,
            realized_pnl=account.daily_realized_pnl,
            unrealized_pnl=unrealized_pnl,
            timestamp=datetime.now(timezone.utc),
        )
        self._event_store.snapshot(account_id, account, positions)
        return snap

    def _refresh_account(self, account: PaperAccount) -> None:
        positions = self._positions.list_positions(account.account_id)
        positions_value = sum(position.qty * position.current_price for position in positions)
        account.equity = account.cash + positions_value
        account.buying_power = max(account.cash, 0.0)
        account.margin_used = max(0.0, positions_value - account.cash)

    # ------------------------------------------------------------------
    # Disclaimers
    # ------------------------------------------------------------------

    def get_disclaimer(self) -> Dict[str, str]:
        return self.DISCLAIMER

    # ------------------------------------------------------------------
    # Strategy Management
    # ------------------------------------------------------------------

    def deploy_strategy(
        self,
        strategy_id: str,
        account_id: str,
        tenant_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._accounts.get_account(account_id, tenant_id)
        return self._strategies.deploy(strategy_id, account_id, tenant_id, config)

    def stop_strategy(self, strategy_id: str, account_id: str, tenant_id: str) -> None:
        self._strategies.stop(strategy_id, account_id, tenant_id)
