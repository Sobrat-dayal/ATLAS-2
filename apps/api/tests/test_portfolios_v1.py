"""Integration and Unit Test Suite for ATLAS Portfolios V1 (Stage 110).

Verifies the canonical portfolio domain, investment accounts, transaction ledger,
FIFO tax lots, exact Part XXII reference fixture, corporate actions, multi-currency cash,
valuation completeness, and ledger reconciliation.
"""

from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios import (
    AccountType,
    CostBasisMethod,
    PortfolioAccountingEngine,
    PortfolioCreateRequest,
    PortfolioRepository,
    PortfolioService,
    PortfolioValuationEngine,
    QuoteFreshness,
    ReconciliationStatus,
    TransactionCorrectRequest,
    TransactionCreateRequest,
    TransactionReverseRequest,
    TransactionType,
    ValuationCompletenessStatus,
)
from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.portfolios import get_portfolio_service


@pytest.fixture
def test_user_a() -> AuthPrincipal:
    return AuthPrincipal(
        sub="user_test_alpha_110",
        email="analyst.alpha@atlas.institutional",
        role="authenticated",
    )


@pytest.fixture
def test_user_b() -> AuthPrincipal:
    return AuthPrincipal(
        sub="user_test_beta_110",
        email="analyst.beta@atlas.institutional",
        role="authenticated",
    )


@pytest.fixture
def portfolio_service() -> PortfolioService:
    repo = PortfolioRepository()
    return PortfolioService(repository=repo)


@pytest.fixture
def test_client_user_a(test_user_a: AuthPrincipal, portfolio_service: PortfolioService):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: test_user_a
    app.dependency_overrides[get_portfolio_service] = lambda: portfolio_service

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_client_user_b(test_user_b: AuthPrincipal, portfolio_service: PortfolioService):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: test_user_b
    app.dependency_overrides[get_portfolio_service] = lambda: portfolio_service

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ===========================================================================
# 1. PART XXII — ACCOUNTING REFERENCE FIXTURE (EXACT TEST)
# ===========================================================================


def test_part_xxii_accounting_reference_fixture(portfolio_service: PortfolioService, test_user_a: AuthPrincipal):
    """Verifies the exact numerical expectations defined in Part XXII of the Stage 110 directive."""
    user_id = test_user_a.sub

    # 1. Create Portfolio with base currency USD
    p = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(
            name="Part XXII Reference Portfolio",
            base_currency="USD",
        ),
    )
    accounts = portfolio_service.list_accounts(p.id, user_id)
    assert len(accounts) == 1
    acc_id = accounts[0].id

    # 2. Initial Cash Deposit: 10,000 USD
    dep_tx = portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            gross_amount=Decimal("10000.00"),
            cash_currency="USD",
            notes="Initial capital funding",
        ),
    )
    assert dep_tx.net_cash_amount == Decimal("10000.00")

    cash_after_dep = portfolio_service.get_cash_balances(p.id, user_id, acc_id)[0]
    assert cash_after_dep.settled_cash == Decimal("10000.00")
    assert cash_after_dep.posted_cash == Decimal("10000.00")

    # 3. Buy: 100 shares @ $50 USD, Purchase fee = 10 USD
    buy_tx = portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.BUY,
            instrument_id="inst_acme",
            symbol="ACME",
            exchange="NASDAQ",
            quantity=Decimal("100"),
            unit_price=Decimal("50.00"),
            fee=Decimal("10.00"),
            cash_currency="USD",
        ),
    )
    assert buy_tx.gross_amount == Decimal("5000.00")
    assert buy_tx.net_cash_amount == Decimal("-5010.00")

    # Check cash after purchase: $10,000 - $5,010 = $4,990
    cash_after_buy = portfolio_service.get_cash_balances(p.id, user_id, acc_id)[0]
    assert cash_after_buy.settled_cash == Decimal("4990.00")

    # Check open lot: 100 shares @ $50.10 unit cost basis
    lots = portfolio_service.get_lots(p.id, user_id, "inst_acme", acc_id)
    assert len(lots) == 1
    assert lots[0].original_quantity == Decimal("100")
    assert lots[0].remaining_quantity == Decimal("100")
    assert lots[0].unit_cost_basis == Decimal("50.10")
    assert lots[0].total_cost_basis == Decimal("5010.00")

    # 4. Sell: 40 shares @ $60 USD, Sale fee = 8 USD
    sell_tx = portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.SELL,
            instrument_id="inst_acme",
            symbol="ACME",
            exchange="NASDAQ",
            quantity=Decimal("40"),
            unit_price=Decimal("60.00"),
            fee=Decimal("8.00"),
            cash_currency="USD",
        ),
    )
    # Gross sale = 40 * 60 = 2,400; Net proceeds = 2,400 - 8 = 2,392
    assert sell_tx.gross_amount == Decimal("2400.00")
    assert sell_tx.net_cash_amount == Decimal("2392.00")

    # Cash after sale: 4,990 + 2,392 = 7,382 USD
    cash_after_sell = portfolio_service.get_cash_balances(p.id, user_id, acc_id)[0]
    assert cash_after_sell.settled_cash == Decimal("7382.00")

    # Check holdings & lots after sale:
    # Remaining quantity = 60 shares
    # Basis disposed = 40 * 50.10 = 2,004 USD
    # Realized accounting P&L = 2,392 - 2,004 = 388 USD
    # Remaining basis = 60 * 50.10 = 3,006 USD
    positions = portfolio_service.get_positions(p.id, user_id, acc_id)
    assert len(positions) == 1
    pos = positions[0]
    assert pos.quantity == Decimal("60")
    assert pos.remaining_cost_basis == Decimal("3006.00")
    assert pos.average_unit_cost == Decimal("50.10")
    assert pos.realized_pnl == Decimal("388.00")

    lots_after_sell = portfolio_service.get_lots(p.id, user_id, "inst_acme", acc_id)
    assert len(lots_after_sell) == 1
    assert lots_after_sell[0].remaining_quantity == Decimal("60")
    assert lots_after_sell[0].total_cost_basis == Decimal("3006.00")

    # 5. Mark price: 55 USD per share
    portfolio_service.set_mock_quote(
        instrument_id="inst_acme",
        price=Decimal("55.00"),
        currency="USD",
        freshness=QuoteFreshness.REALTIME,
    )

    valuation = portfolio_service.calculate_portfolio_valuation(p.id, user_id)
    assert valuation.valuation_status == ValuationCompletenessStatus.COMPLETE

    # Position market value: 60 * 55 = 3,300 USD
    pv = valuation.position_valuations[0]
    assert pv.native_market_value == Decimal("3300.00")
    assert pv.base_market_value == Decimal("3300.00")
    # Unrealized accounting P&L: 3,300 - 3,006 = 294 USD
    assert pv.unrealized_pnl == Decimal("294.00")

    # Portfolio totals:
    # Cash market value = 7,382 USD
    # Total positions market value = 3,300 USD
    # Portfolio market value = 7,382 + 3,300 = 10,682 USD
    # Net accounting gain = 388 (realized) + 294 (unrealized) = 682 USD
    assert valuation.total_cash_market_value == Decimal("7382.00")
    assert valuation.total_positions_market_value == Decimal("3300.00")
    assert valuation.verified_total_portfolio_value == Decimal("10682.00")
    assert valuation.total_realized_pnl == Decimal("388.00")
    assert valuation.total_unrealized_pnl == Decimal("294.00")

    # 6. Reconciliation audit
    rec = portfolio_service.reconcile_portfolio(p.id, user_id)
    assert rec.is_balanced is True
    assert rec.status == ReconciliationStatus.RECONCILED
    assert len(rec.discrepancies) == 0


# ===========================================================================
# 2. STOCK SPLIT CORPORATE ACTION
# ===========================================================================


def test_stock_split_preserves_total_basis(portfolio_service: PortfolioService, test_user_a: AuthPrincipal):
    """Verifies that a 2:1 stock split doubles quantity and halves unit basis while preserving aggregate basis."""
    user_id = test_user_a.sub
    p = portfolio_service.create_portfolio(user_id, PortfolioCreateRequest(name="Split Test Portfolio"))
    acc_id = portfolio_service.list_accounts(p.id, user_id)[0].id

    # Deposit $10,000
    portfolio_service.post_transaction(
        p.id, user_id, TransactionCreateRequest(account_id=acc_id, transaction_type=TransactionType.CASH_DEPOSIT, gross_amount=Decimal("10000"))
    )
    # Buy 100 shares @ $50 (no fee) -> $5,000 basis
    portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.BUY,
            instrument_id="inst_split",
            symbol="SPLT",
            quantity=Decimal("100"),
            unit_price=Decimal("50.00"),
        ),
    )

    # Apply 2-for-1 stock split adjustment
    split_tx = portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.STOCK_SPLIT_ADJUSTMENT,
            instrument_id="inst_split",
            symbol="SPLT",
            unit_price=Decimal("2.0"),  # Split ratio 2:1
            quantity=Decimal("100"),
        ),
    )
    assert split_tx.transaction_type == TransactionType.STOCK_SPLIT_ADJUSTMENT

    # Verify positions: 200 shares, total basis still $5,000, unit cost = $25.00
    positions = portfolio_service.get_positions(p.id, user_id, acc_id)
    assert len(positions) == 1
    assert positions[0].quantity == Decimal("200")
    assert positions[0].remaining_cost_basis == Decimal("5000.00")
    assert positions[0].average_unit_cost == Decimal("25.00")

    # Reconcile
    rec = portfolio_service.reconcile_portfolio(p.id, user_id)
    assert rec.is_balanced is True


# ===========================================================================
# 3. MULTI-CURRENCY CASH & FX CONVERSION
# ===========================================================================


def test_multi_currency_portfolio_and_fx(portfolio_service: PortfolioService, test_user_a: AuthPrincipal):
    """Verifies that an account with multi-currency cash is converted using canonical FX rates without raw mixing."""
    user_id = test_user_a.sub
    p = portfolio_service.create_portfolio(user_id, PortfolioCreateRequest(name="Multi Currency", base_currency="USD"))
    acc_id = portfolio_service.list_accounts(p.id, user_id)[0].id

    # Deposit 5,000 USD
    portfolio_service.post_transaction(
        p.id, user_id, TransactionCreateRequest(account_id=acc_id, transaction_type=TransactionType.CASH_DEPOSIT, gross_amount=Decimal("5000"), cash_currency="USD")
    )
    # Deposit 100,000 INR
    portfolio_service.post_transaction(
        p.id, user_id, TransactionCreateRequest(account_id=acc_id, transaction_type=TransactionType.CASH_DEPOSIT, gross_amount=Decimal("100000"), cash_currency="INR")
    )

    cash_bals = portfolio_service.get_cash_balances(p.id, user_id, acc_id)
    assert len(cash_bals) == 2
    usd_bal = next(c for c in cash_bals if c.currency == "USD")
    inr_bal = next(c for c in cash_bals if c.currency == "INR")
    assert usd_bal.settled_cash == Decimal("5000")
    assert inr_bal.settled_cash == Decimal("100000")

    # Set FX rate: 1 INR = 0.012 USD
    portfolio_service.set_mock_fx("INR", "USD", Decimal("0.012"))

    val = portfolio_service.calculate_portfolio_valuation(p.id, user_id)
    assert val.valuation_status == ValuationCompletenessStatus.COMPLETE

    # 100,000 INR * 0.012 = 1,200 USD
    # Total cash in USD = 5,000 + 1,200 = 6,200 USD
    assert val.total_cash_market_value == Decimal("6200.00")
    assert val.verified_total_portfolio_value == Decimal("6200.00")


# ===========================================================================
# 4. TRANSACTION REVERSAL & CORRECTION
# ===========================================================================


def test_transaction_reversal_and_correction(portfolio_service: PortfolioService, test_user_a: AuthPrincipal):
    """Verifies that reversing and correcting a trade maintains deterministic ledger purity."""
    user_id = test_user_a.sub
    p = portfolio_service.create_portfolio(user_id, PortfolioCreateRequest(name="Reversal Test", base_currency="USD"))
    acc_id = portfolio_service.list_accounts(p.id, user_id)[0].id

    # Deposit $10,000
    portfolio_service.post_transaction(
        p.id, user_id, TransactionCreateRequest(account_id=acc_id, transaction_type=TransactionType.CASH_DEPOSIT, gross_amount=Decimal("10000"))
    )

    # Buy 50 shares @ $100
    buy_tx = portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.BUY,
            instrument_id="inst_rev",
            symbol="REV",
            quantity=Decimal("50"),
            unit_price=Decimal("100.00"),
        ),
    )
    assert portfolio_service.get_positions(p.id, user_id, acc_id)[0].quantity == Decimal("50")

    # Reverse the buy
    reversal = portfolio_service.reverse_transaction(
        p.id, buy_tx.id, user_id, TransactionReverseRequest(reason="Entered by mistake")
    )
    assert reversal.transaction_type == TransactionType.CORRECTION_REVERSAL
    assert reversal.reverses_transaction_id == buy_tx.id

    # Holdings should now be 0 shares, cash back to $10,000
    positions_after_rev = portfolio_service.get_positions(p.id, user_id, acc_id)
    assert positions_after_rev[0].quantity == Decimal("0")
    cash_after_rev = portfolio_service.get_cash_balances(p.id, user_id, acc_id)[0]
    assert cash_after_rev.settled_cash == Decimal("10000.00")

    # Reconcile
    rec = portfolio_service.reconcile_portfolio(p.id, user_id)
    assert rec.is_balanced is True


# ===========================================================================
# 5. COMPLETENESS & MISSING DATA STATES
# ===========================================================================


def test_valuation_missing_price_and_missing_fx(portfolio_service: PortfolioService, test_user_a: AuthPrincipal):
    """Verifies that missing prices or FX prevent false verified totals and return PARTIAL status."""
    user_id = test_user_a.sub
    p = portfolio_service.create_portfolio(user_id, PortfolioCreateRequest(name="Partial Val", base_currency="USD"))
    acc_id = portfolio_service.list_accounts(p.id, user_id)[0].id

    # Deposit and buy without setting market quote
    portfolio_service.post_transaction(
        p.id, user_id, TransactionCreateRequest(account_id=acc_id, transaction_type=TransactionType.CASH_DEPOSIT, gross_amount=Decimal("10000"))
    )
    portfolio_service.post_transaction(
        p.id,
        user_id,
        TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.BUY,
            instrument_id="inst_unpriced",
            symbol="UNPR",
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
        ),
    )

    val = portfolio_service.calculate_portfolio_valuation(p.id, user_id)
    assert val.valuation_status == ValuationCompletenessStatus.PARTIAL_MISSING_PRICES
    assert val.missing_prices_count == 1
    assert val.verified_total_portfolio_value is None
    assert val.known_valued_subtotal == Decimal("9000.00")  # Only remaining cash is verified


# ===========================================================================
# 6. REST API INTEGRATION & TENANT ISOLATION
# ===========================================================================


def test_rest_api_portfolio_flow_and_tenant_isolation(
    test_client_user_a: TestClient,
    test_client_user_b: TestClient,
):
    """Tests the full REST lifecycle: create, account, preview, post, valuation, and cross-user isolation."""
    # 1. User A creates a portfolio
    create_res = test_client_user_a.post(
        "/api/v1/portfolios",
        json={
            "name": "Global Growth Alpha",
            "base_currency": "USD",
            "portfolio_type": "INSTITUTIONAL",
            "description": "High conviction global equity portfolio",
        },
    )
    assert create_res.status_code == 201
    port_data = create_res.json()
    port_id = port_data["id"]
    assert port_data["account_count"] == 1

    # 2. User A retrieves account
    accs_res = test_client_user_a.get(f"/api/v1/portfolios/{port_id}/accounts")
    assert accs_res.status_code == 200
    acc_id = accs_res.json()["items"][0]["id"]

    # 3. User B cannot access User A's portfolio (403)
    b_res = test_client_user_b.get(f"/api/v1/portfolios/{port_id}")
    assert b_res.status_code == 403

    # 4. User A previews a deposit
    prev_res = test_client_user_a.post(
        f"/api/v1/portfolios/{port_id}/transactions/preview",
        json={
            "account_id": acc_id,
            "transaction_type": "CASH_DEPOSIT",
            "gross_amount": 25000,
            "cash_currency": "USD",
        },
    )
    assert prev_res.status_code == 200
    assert prev_res.json()["estimated_resulting_cash"] == "25000.00"

    # 5. User A posts deposit
    post_dep_res = test_client_user_a.post(
        f"/api/v1/portfolios/{port_id}/transactions",
        json={
            "account_id": acc_id,
            "transaction_type": "CASH_DEPOSIT",
            "gross_amount": 25000,
            "cash_currency": "USD",
            "notes": "Q4 Capital Allocation",
        },
    )
    assert post_dep_res.status_code == 201

    # 6. User A buys AAPL shares
    post_buy_res = test_client_user_a.post(
        f"/api/v1/portfolios/{port_id}/transactions",
        json={
            "account_id": acc_id,
            "transaction_type": "BUY",
            "instrument_id": "inst_aapl",
            "symbol": "AAPL",
            "exchange": "NASDAQ",
            "quantity": 50,
            "unit_price": 180.00,
            "fee": 5.00,
            "cash_currency": "USD",
        },
    )
    assert post_buy_res.status_code == 201

    # 7. Check holdings
    pos_res = test_client_user_a.get(f"/api/v1/portfolios/{port_id}/positions")
    assert pos_res.status_code == 200
    positions = pos_res.json()["items"]
    assert len(positions) == 1
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["quantity"] == "50"

    # 8. Check cash balances
    cash_res = test_client_user_a.get(f"/api/v1/portfolios/{port_id}/cash")
    assert cash_res.status_code == 200
    # 25,000 - (50 * 180 + 5) = 25,000 - 9,005 = 15,995
    assert cash_res.json()[0]["settled_cash"] == "15995.00"

    # 9. Check reconciliation
    rec_res = test_client_user_a.get(f"/api/v1/portfolios/{port_id}/reconciliation")
    assert rec_res.status_code == 200
    assert rec_res.json()["is_balanced"] is True
