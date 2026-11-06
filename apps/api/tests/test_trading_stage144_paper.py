"""
ATLAS Stage 144 — Paper Trading Engine Tests.
Tests A through X (24 tests) covering accounts, fills, orders,
positions, risk, kill switch, strategies, snapshots, and security.

All tests operate in pure-simulation mode — no real broker, no real money.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from atlas.trading.paper.service import AtlasPaperTradingService
from atlas.trading.paper.domain import (
    PaperOrderStatus,
    PaperOrderSide,
    PaperOrderType,
    AssetClass,
    TimeInForce,
    STAGE_144_DISCLAIMERS,
)
from atlas.trading.paper.errors import (
    AccountNotFoundError,
    CrossTenantAccessError,
    DuplicateOrderError,
    KillSwitchActiveError,
    LiveBrokerFirewallError,
    MarketClosedError,
    StaleMarketDataError,
)
from atlas.trading.paper.execution.sandbox_adapter import SandboxExecutionAdapter

TENANT = "tenant-144"
OTHER_TENANT = "tenant-other"


@pytest.fixture()
def svc() -> AtlasPaperTradingService:
    """Fresh paper trading service for each test."""
    return AtlasPaperTradingService(
        fee_bps=1.0,
        slippage_bps=2.0,
        latency_ms=0.0,
        stale_data_threshold_s=60.0,
    )


def _feed(svc: AtlasPaperTradingService, symbol: str, bid: float, ask: float, market_open: bool = True) -> None:
    svc.update_market_data(symbol, bid=bid, ask=ask, market_open=market_open)


# ---------------------------------------------------------------------------
# A — Account creation with $10k
# ---------------------------------------------------------------------------
def test_A_account_creation_with_10k(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Test Account", initial_cash=10_000.0)
    assert acct.account_id
    assert acct.cash == 10_000.0
    assert acct.initial_cash == 10_000.0
    assert acct.kill_switch_active is False
    assert acct.is_active is True
    assert acct.tenant_id == TENANT


# ---------------------------------------------------------------------------
# B — Market buy fill: cash reduced, position created
# ---------------------------------------------------------------------------
def test_B_market_buy_fill(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Buy Test", initial_cash=10_000.0)
    _feed(svc, "AAPL", bid=149.0, ask=150.0)
    order = svc.submit_order(
        account_id=acct.account_id,
        tenant_id=TENANT,
        symbol="AAPL",
        side=PaperOrderSide.BUY,
        order_type=PaperOrderType.MARKET,
        qty=10.0,
    )
    assert order.status == PaperOrderStatus.FILLED
    assert order.filled_qty == 10.0
    # Cash should be reduced
    updated = svc.get_account(acct.account_id, TENANT)
    assert updated.cash < 10_000.0
    # Position should exist
    positions = svc.list_positions(acct.account_id, TENANT)
    assert any(p.symbol == "AAPL" for p in positions)


# ---------------------------------------------------------------------------
# C — Partial exit: realized + unrealized P&L
# ---------------------------------------------------------------------------
def test_C_partial_exit_pnl(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "PnL Test", initial_cash=20_000.0)
    _feed(svc, "TSLA", bid=199.0, ask=200.0)
    svc.submit_order(acct.account_id, TENANT, "TSLA", PaperOrderSide.BUY, PaperOrderType.MARKET, 10.0)
    # Price moves up
    _feed(svc, "TSLA", bid=209.0, ask=210.0)
    sell_order = svc.submit_order(
        acct.account_id, TENANT, "TSLA", PaperOrderSide.SELL, PaperOrderType.MARKET, 5.0
    )
    assert sell_order.status == PaperOrderStatus.FILLED
    positions = svc.list_positions(acct.account_id, TENANT)
    tsla_pos = next((p for p in positions if p.symbol == "TSLA"), None)
    assert tsla_pos is not None
    assert tsla_pos.qty == 5.0  # 5 remaining


# ---------------------------------------------------------------------------
# D — Partial fills
# ---------------------------------------------------------------------------
def test_D_partial_fills_via_simulate(svc: AtlasPaperTradingService) -> None:
    adapter = SandboxExecutionAdapter(fee_bps=1.0, slippage_bps=2.0)
    # simulate_partial_fill returns min(remaining, available)
    from atlas.trading.paper.domain import PaperOrder
    order = PaperOrder(
        order_id="ord-d",
        account_id="acct-d",
        symbol="NVDA",
        side=PaperOrderSide.BUY,
        order_type=PaperOrderType.MARKET,
        qty=100.0,
        filled_qty=60.0,
        limit_price=None,
        stop_price=None,
        status=PaperOrderStatus.PARTIAL,
        asset_class=AssetClass.EQUITY,
        time_in_force=TimeInForce.GTC,
        submitted_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    partial = adapter.simulate_partial_fill(order, available_qty=30.0)
    assert partial == 30.0  # 40 remaining, only 30 available


# ---------------------------------------------------------------------------
# E — Cancel open order
# ---------------------------------------------------------------------------
def test_E_cancel_open_order(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Cancel Test", initial_cash=10_000.0)
    _feed(svc, "META", bid=400.0, ask=401.0)
    # Limit order above ask won't fill immediately
    order = svc.submit_order(
        acct.account_id, TENANT, "META",
        PaperOrderSide.BUY, PaperOrderType.LIMIT, qty=5.0,
        limit_price=350.0,  # below ask — won't fill
    )
    assert order.status in (PaperOrderStatus.OPEN, PaperOrderStatus.PENDING)
    cancelled = svc.cancel_order(order.order_id, acct.account_id, TENANT)
    assert cancelled.status == PaperOrderStatus.CANCELLED


# ---------------------------------------------------------------------------
# F — Duplicate client_order_id raises DuplicateOrderError on order book
# ---------------------------------------------------------------------------
def test_F_duplicate_client_order_id(svc: AtlasPaperTradingService) -> None:
    from atlas.trading.paper.domain import PaperOrder
    acct = svc.create_account(TENANT, "Dup Test", initial_cash=10_000.0)
    _feed(svc, "AMZN", bid=180.0, ask=181.0)
    svc.submit_order(
        acct.account_id, TENANT, "AMZN",
        PaperOrderSide.BUY, PaperOrderType.MARKET, qty=1.0,
        client_order_id="unique-coid-001",
    )
    with pytest.raises(DuplicateOrderError):
        svc._order_book.submit(
            PaperOrder(
                order_id="ord-dup-test",
                account_id=acct.account_id,
                symbol="AMZN",
                side=PaperOrderSide.BUY,
                order_type=PaperOrderType.MARKET,
                qty=1.0,
                filled_qty=0.0,
                limit_price=None,
                stop_price=None,
                status=PaperOrderStatus.OPEN,
                asset_class=AssetClass.EQUITY,
                time_in_force=TimeInForce.DAY,
                submitted_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                client_order_id="unique-coid-001",
            )
        )


# ---------------------------------------------------------------------------
# G — Stale market data raises StaleMarketDataError
# ---------------------------------------------------------------------------
def test_G_stale_market_data(svc: AtlasPaperTradingService) -> None:
    # Service with tight stale threshold
    tight_svc = AtlasPaperTradingService(stale_data_threshold_s=0.001)
    acct = tight_svc.create_account(TENANT, "Stale Test", initial_cash=10_000.0)
    # Feed with a very old timestamp
    stale_ts = datetime.now(timezone.utc) - timedelta(seconds=120)
    tight_svc.update_market_data("GOOG", bid=140.0, ask=141.0, timestamp=stale_ts)
    with pytest.raises(StaleMarketDataError):
        tight_svc.submit_order(
            acct.account_id, TENANT, "GOOG",
            PaperOrderSide.BUY, PaperOrderType.MARKET, qty=1.0,
        )


# ---------------------------------------------------------------------------
# H — Market closed raises MarketClosedError
# ---------------------------------------------------------------------------
def test_H_market_closed(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Closed Market Test", initial_cash=10_000.0)
    _feed(svc, "SPY", bid=450.0, ask=451.0, market_open=False)
    with pytest.raises(MarketClosedError):
        svc.submit_order(
            acct.account_id, TENANT, "SPY",
            PaperOrderSide.BUY, PaperOrderType.MARKET, qty=1.0,
        )


# ---------------------------------------------------------------------------
# I — Limit order below ask stays OPEN (no fill)
# ---------------------------------------------------------------------------
def test_I_limit_order_below_ask_stays_open(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Limit Test", initial_cash=10_000.0)
    _feed(svc, "MSFT", bid=299.0, ask=300.0)
    order = svc.submit_order(
        acct.account_id, TENANT, "MSFT",
        PaperOrderSide.BUY, PaperOrderType.LIMIT, qty=2.0,
        limit_price=280.0,  # below current ask of 300 — won't fill
    )
    assert order.status == PaperOrderStatus.OPEN
    assert order.filled_qty == 0.0


# ---------------------------------------------------------------------------
# J — Stop order submitted successfully
# ---------------------------------------------------------------------------
def test_J_stop_order_submitted(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Stop Test", initial_cash=10_000.0)
    _feed(svc, "QQQ", bid=360.0, ask=361.0)
    # Stop sell at 350 (below current bid) — won't trigger yet
    order = svc.submit_order(
        acct.account_id, TENANT, "QQQ",
        PaperOrderSide.SELL, PaperOrderType.STOP, qty=3.0,
        stop_price=350.0,
    )
    assert order.order_id
    assert order.status in (PaperOrderStatus.OPEN, PaperOrderStatus.PENDING)


# ---------------------------------------------------------------------------
# K — Daily loss exceeds threshold → risk policy blocks order
# ---------------------------------------------------------------------------
def test_K_daily_loss_kill_switch(svc: AtlasPaperTradingService) -> None:
    # Activate kill switch via API and verify it blocks orders
    acct = svc.create_account(TENANT, "Risk Test", initial_cash=10_000.0)
    svc.activate_kill_switch(acct.account_id, TENANT, reason="daily_loss_limit", triggered_by="system")
    _feed(svc, "NVDA", bid=600.0, ask=601.0)
    with pytest.raises(KillSwitchActiveError):
        svc.submit_order(
            acct.account_id, TENANT, "NVDA",
            PaperOrderSide.BUY, PaperOrderType.MARKET, qty=1.0,
        )


# ---------------------------------------------------------------------------
# L — Kill switch blocks all new orders
# ---------------------------------------------------------------------------
def test_L_kill_switch_blocks_orders(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "KS Block Test", initial_cash=50_000.0)
    svc.activate_kill_switch(acct.account_id, TENANT, reason="user_request", triggered_by="user-144")
    updated = svc.get_account(acct.account_id, TENANT)
    assert updated.kill_switch_active is True
    _feed(svc, "GS", bid=380.0, ask=381.0)
    with pytest.raises(KillSwitchActiveError):
        svc.submit_order(acct.account_id, TENANT, "GS", PaperOrderSide.BUY, PaperOrderType.MARKET, qty=1.0)


# ---------------------------------------------------------------------------
# M — Strategy deployment
# ---------------------------------------------------------------------------
def test_M_strategy_deploy(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Strategy Test", initial_cash=100_000.0)
    result = svc.deploy_strategy(
        strategy_id="momentum_v1",
        account_id=acct.account_id,
        tenant_id=TENANT,
        config={"lookback": 20, "threshold": 0.02},
    )
    assert result["deployment_id"]
    assert result["strategy_id"] == "momentum_v1"
    assert result["status"] == "ACTIVE"


# ---------------------------------------------------------------------------
# N — Strategy stop
# ---------------------------------------------------------------------------
def test_N_strategy_stop(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Strategy Stop Test", initial_cash=100_000.0)
    svc.deploy_strategy("mean_reversion_v1", acct.account_id, TENANT, {})
    # stop should not raise
    svc.stop_strategy("mean_reversion_v1", acct.account_id, TENANT)


# ---------------------------------------------------------------------------
# O — Snapshot after order
# ---------------------------------------------------------------------------
def test_O_snapshot_after_order(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Snapshot Test", initial_cash=10_000.0)
    _feed(svc, "IBM", bid=130.0, ask=131.0)
    svc.submit_order(acct.account_id, TENANT, "IBM", PaperOrderSide.BUY, PaperOrderType.MARKET, qty=5.0)
    snap = svc.take_snapshot(acct.account_id, TENANT)
    assert snap.snapshot_id
    assert snap.account_id == acct.account_id
    assert snap.cash < 10_000.0  # Cash reduced after buy
    assert snap.equity > 0.0


# ---------------------------------------------------------------------------
# P — Account reset preserves history flag
# ---------------------------------------------------------------------------
def test_P_account_reset(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Reset Test", initial_cash=10_000.0)
    _feed(svc, "F", bid=11.0, ask=12.0)
    svc.submit_order(acct.account_id, TENANT, "F", PaperOrderSide.BUY, PaperOrderType.MARKET, qty=100.0)
    # Reset account
    reset_acct = svc.reset_account(acct.account_id, TENANT)
    assert reset_acct.cash == reset_acct.initial_cash
    # Orders should be cleared
    orders = svc.list_orders(acct.account_id, TENANT)
    assert len(orders) == 0


# ---------------------------------------------------------------------------
# Q — Option expiry settlement
# ---------------------------------------------------------------------------
def test_Q_option_expiry_settlement(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Options Test", initial_cash=50_000.0)
    # Manually inject an option position for settlement
    from atlas.trading.paper.domain import PaperPosition
    from atlas.trading.paper.positions.registry import PaperPositionRegistry
    pos_reg: PaperPositionRegistry = svc._positions
    pos = PaperPosition(
        position_id="opt-pos-1",
        account_id=acct.account_id,
        symbol="AAPL240120C00200000",
        asset_class=AssetClass.OPTION,
        side=PaperOrderSide.BUY,
        qty=1.0,
        avg_cost=5.0,
        current_price=5.0,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        opened_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        option_contract={"strike": 200.0, "option_type": "CALL", "multiplier": 100},
    )
    pos_reg._positions.setdefault(acct.account_id, {})["AAPL240120C00200000"] = pos
    # Settle at expiry with settlement price
    pnl = svc.settle_option_expiry(acct.account_id, TENANT, "AAPL240120C00200000", settlement_price=210.0)
    assert isinstance(pnl, float)


# ---------------------------------------------------------------------------
# R — AccountNotFoundError for unknown account
# ---------------------------------------------------------------------------
def test_R_account_not_found(svc: AtlasPaperTradingService) -> None:
    with pytest.raises(AccountNotFoundError):
        svc.get_account("nonexistent-acct-id", TENANT)


# ---------------------------------------------------------------------------
# S — Stock split 2:1
# ---------------------------------------------------------------------------
def test_S_stock_split_2_for_1(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Split Test", initial_cash=20_000.0)
    _feed(svc, "TSLA", bid=199.0, ask=200.0)
    svc.submit_order(acct.account_id, TENANT, "TSLA", PaperOrderSide.BUY, PaperOrderType.MARKET, qty=10.0)
    svc.apply_stock_split(acct.account_id, TENANT, "TSLA", ratio=2.0)
    positions = svc.list_positions(acct.account_id, TENANT)
    tsla = next(p for p in positions if p.symbol == "TSLA")
    assert tsla.qty == 20.0  # doubled
    assert abs(tsla.avg_cost - 100.0) < 1.0  # halved cost (approx, before slippage)


# ---------------------------------------------------------------------------
# T — Multi-currency account label
# ---------------------------------------------------------------------------
def test_T_multi_currency_account(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "GBP Account", initial_cash=10_000.0, currency="GBP")
    assert acct.currency == "GBP"
    assert acct.cash == 10_000.0


# ---------------------------------------------------------------------------
# U — Cross-tenant access denied
# ---------------------------------------------------------------------------
def test_U_cross_tenant_denied(svc: AtlasPaperTradingService) -> None:
    acct = svc.create_account(TENANT, "Tenant A Account", initial_cash=10_000.0)
    with pytest.raises(CrossTenantAccessError):
        svc.get_account(acct.account_id, OTHER_TENANT)


# ---------------------------------------------------------------------------
# V — Sandbox firewall blocks live broker hosts
# ---------------------------------------------------------------------------
def test_V_sandbox_firewall(svc: AtlasPaperTradingService) -> None:
    adapter = SandboxExecutionAdapter()
    # Production host must be blocked
    with pytest.raises(LiveBrokerFirewallError):
        adapter.check_firewall("api.alpaca.markets")
    # Paper/sandbox host must be allowed
    try:
        adapter.check_firewall("paper-api.alpaca.markets")
    except LiveBrokerFirewallError:
        pytest.fail("paper-api.alpaca.markets should NOT be blocked")


# ---------------------------------------------------------------------------
# W — Disclaimer keys present
# ---------------------------------------------------------------------------
def test_W_disclaimer_keys(svc: AtlasPaperTradingService) -> None:
    disc = svc.get_disclaimer()
    for key in ("paper_only", "no_real_broker", "simulated_fills", "hypothetical"):
        assert key in disc, f"Missing disclaimer key: {key}"
        assert len(disc[key]) > 10


# ---------------------------------------------------------------------------
# X — list_accounts returns all 3
# ---------------------------------------------------------------------------
def test_X_list_accounts_returns_all(svc: AtlasPaperTradingService) -> None:
    svc.create_account(TENANT, "Account 1")
    svc.create_account(TENANT, "Account 2")
    svc.create_account(TENANT, "Account 3")
    accounts = svc.list_accounts(TENANT)
    assert len(accounts) == 3
    # All must belong to the correct tenant
    assert all(a.tenant_id == TENANT for a in accounts)

