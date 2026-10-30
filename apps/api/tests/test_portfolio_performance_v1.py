"""Tests for ATLAS Portfolio Performance Analytics (Stage 111).

Validates:
1. Part XIII Exact TWR Reference Fixture (Expected: 21.0%, not naive 76%)
2. Part XXXIV Multi-Currency USD/INR Fixture (Expected: 10.0% USD, 23.75% INR)
3. XIRR Root Solver and 1-Year Reference Fixture (Expected: 10.0%)
4. Cash Flow Classifier Integrity and Boundary Scope
5. Periodic Returns and Annualization
6. Benchmark Registry and Rebased Comparison
7. REST API Endpoints and Cross-Tenant Isolation
"""

from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from starlette.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios import (
    AccountCreateRequest,
    AccountType,
    PortfolioCreateRequest,
    PortfolioService,
    PortfolioTransaction,
    PortfolioType,
    TransactionCreateRequest,
    TransactionType,
)
from atlas.portfolios.performance import (
    CANONICAL_BENCHMARKS,
    CashFlowClassification,
    CashFlowClassifier,
    MeasurementScope,
    PerformanceCalculateRequest,
    PerformanceMethodology,
    PerformancePeriodType,
    PortfolioPerformanceAnnualizationInvalidError,
    PortfolioPerformanceBeginningValuationMissingError,
    PortfolioPerformanceService,
    PortfolioPerformanceXirrInvalidCashFlowsError,
    PortfolioPerformanceXirrNoSolutionError,
    calculate_annualized_return,
    calculate_exact_twr,
    calculate_modified_dietz,
    calculate_xirr,
    compare_portfolio_to_benchmark,
    compound_periodic_returns,
)
from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers.portfolios import get_performance_service, get_portfolio_service


# ---------------------------------------------------------------------------
# Test 1: Part XIII Exact TWR Reference Fixture
# ---------------------------------------------------------------------------


def test_part_xiii_exact_twr_reference_fixture():
    """Validates Part XIII mandatory reference test fixture.

    Beginning value: $100.00
    Grows to $110.00 pre-contribution (Subperiod 1 return: 10%)
    Contribution: +$50.00 (Post-contribution capital base: $160.00)
    Grows to $176.00 (Subperiod 2 return: 10%)
    Linked TWR: (1.10 * 1.10) - 1 = 21.00%
    A naive calculation of (176 - 100) / 100 = 76% is strictly incorrect.
    """
    t0 = datetime(2026, 1, 1, 0, 0, 0)
    t1 = datetime(2026, 6, 1, 12, 0, 0)
    t2 = datetime(2026, 12, 31, 23, 59, 59)

    b_val = Decimal("100.00")
    e_val = Decimal("176.00")

    # Flow at t1: $50 external contribution, pre-flow valuation was $110.00
    flows_with_marks = [
        (t1, Decimal("50.00"), Decimal("110.00")),
    ]

    twr, subperiods = calculate_exact_twr(
        period_start=t0,
        period_end=t2,
        beginning_value=b_val,
        ending_value=e_val,
        flows_with_marks=flows_with_marks,
    )

    # 1. Verify Subperiod 1 return is exactly 10%
    assert len(subperiods) == 2
    assert subperiods[0].subperiod_return == Decimal("0.10")
    assert subperiods[0].start_value == Decimal("100.00")
    assert subperiods[0].end_value_pre_flow == Decimal("110.00")
    assert subperiods[0].net_external_flow == Decimal("50.00")
    assert subperiods[0].end_value_post_flow == Decimal("160.00")

    # 2. Verify Subperiod 2 return is exactly 10%
    assert subperiods[1].start_value == Decimal("160.00")
    assert subperiods[1].end_value_pre_flow == Decimal("176.00")
    assert subperiods[1].subperiod_return == Decimal("0.10")

    # 3. Verify geometrically linked TWR is exactly 21%
    assert twr == Decimal("0.21")
    assert round(twr * 100, 2) == Decimal("21.00")
    assert twr != Decimal("0.76")


# ---------------------------------------------------------------------------
# Test 2: Part XXXIV Multi-Currency USD / INR Reference Fixture
# ---------------------------------------------------------------------------


def test_part_xxxiv_multi_currency_fixture():
    """Validates Part XXXIV multi-currency calculation fixture.

    USD Investment:
      Start Value: $100.00
      End Value: $110.00
      Native USD Return: 10.0%

    Historical FX:
      Start: 1 USD = 80 INR
      End: 1 USD = 90 INR

    INR Valuations:
      Start: 100 * 80 = 8,000 INR
      End: 110 * 90 = 9,900 INR
      Base INR Return: (9,900 / 8,000) - 1 = 23.75%
    """
    t0 = datetime(2026, 1, 1)
    t1 = datetime(2026, 12, 31)

    # Native USD calculation
    usd_ret, _ = calculate_exact_twr(
        period_start=t0,
        period_end=t1,
        beginning_value=Decimal("100.00"),
        ending_value=Decimal("110.00"),
        flows_with_marks=[],
    )
    assert usd_ret == Decimal("0.10")

    # Base INR calculation
    fx_start = Decimal("80.00")
    fx_end = Decimal("90.00")

    inr_start = Decimal("100.00") * fx_start  # 8000.00
    inr_end = Decimal("110.00") * fx_end      # 9900.00

    inr_ret, _ = calculate_exact_twr(
        period_start=t0,
        period_end=t1,
        beginning_value=inr_start,
        ending_value=inr_end,
        flows_with_marks=[],
    )
    assert inr_ret == Decimal("0.2375")
    assert round(inr_ret * 100, 2) == Decimal("23.75")


# ---------------------------------------------------------------------------
# Test 3: XIRR Numerical Solver and Reference Fixtures
# ---------------------------------------------------------------------------


def test_xirr_solver_and_fixtures():
    """Validates Money-Weighted Return (MWR) / XIRR calculations."""
    t0 = datetime(2025, 1, 1)
    t1 = datetime(2026, 1, 1)

    # Part XIX Simple 1-Year Fixture: -$1000 at t0, +$1100 at t0+365 days -> 10%
    flows_1yr = [
        (t0, Decimal("-1000.00")),
        (t1, Decimal("+1100.00")),
    ]
    rate, multi, status = calculate_xirr(flows_1yr)
    assert round(rate, 2) == Decimal("0.10")
    assert not multi
    assert "CONVERGED" in status

    # Irregular flows with mid-year withdrawal
    t_mid = datetime(2025, 7, 1)
    flows_with_withdrawal = [
        (t0, Decimal("-1000.00")),
        (t_mid, Decimal("+200.00")),
        (t1, Decimal("+950.00")),
    ]
    rate_w, _, _ = calculate_xirr(flows_with_withdrawal)
    assert rate_w > Decimal("0.10")  # Early withdrawal increases IRR

    # Invalid cash flows (all negative)
    with pytest.raises(PortfolioPerformanceXirrInvalidCashFlowsError):
        calculate_xirr([(t0, Decimal("-500.00")), (t1, Decimal("-200.00"))])

    # Invalid cash flows (all positive)
    with pytest.raises(PortfolioPerformanceXirrInvalidCashFlowsError):
        calculate_xirr([(t0, Decimal("+500.00")), (t1, Decimal("+200.00"))])


# ---------------------------------------------------------------------------
# Test 4: Cash Flow Classification Integrity
# ---------------------------------------------------------------------------


def test_cash_flow_classification_rules():
    """Validates that investment trades are internal and deposits are external."""
    classifier = CashFlowClassifier(base_currency="USD")
    p_id = "00000000-0000-0000-0000-000000000001"
    a1_id = "00000000-0000-0000-0000-000000000002"
    a2_id = "00000000-0000-0000-0000-000000000003"
    now = datetime.utcnow()

    # 1. Deposit -> EXTERNAL_CONTRIBUTION
    tx_dep = PortfolioTransaction(
        id="tx1",
        portfolio_id=p_id,
        account_id=a1_id,
        user_id="u1",
        transaction_type=TransactionType.CASH_DEPOSIT,
        net_cash_amount=Decimal("5000.00"),
        cash_currency="USD",
        trade_date=now,
        settlement_date=now,
    )
    cf_dep = classifier.classify_transaction(tx_dep, scope=MeasurementScope.PORTFOLIO)
    assert cf_dep.classification == CashFlowClassification.EXTERNAL_CONTRIBUTION
    assert cf_dep.portfolio_flow_amount == Decimal("5000.00")
    assert cf_dep.investor_flow_amount == Decimal("-5000.00")

    # 2. Buy security -> INTERNAL_SECURITY_TRADE (0 external flow!)
    tx_buy = PortfolioTransaction(
        id="tx2",
        portfolio_id=p_id,
        account_id=a1_id,
        user_id="u1",
        transaction_type=TransactionType.BUY,
        instrument_id="inst_aapl",
        symbol="AAPL",
        quantity=Decimal("50"),
        unit_price=Decimal("100.00"),
        net_cash_amount=Decimal("-5010.00"),
        cash_currency="USD",
        trade_date=now,
        settlement_date=now,
    )
    cf_buy = classifier.classify_transaction(tx_buy, scope=MeasurementScope.PORTFOLIO)
    assert cf_buy.classification == CashFlowClassification.INTERNAL_SECURITY_TRADE
    assert cf_buy.portfolio_flow_amount == Decimal("0.00")
    assert cf_buy.investor_flow_amount == Decimal("0.00")

    # 3. Dividend received -> INTERNAL_INCOME (not an external deposit!)
    tx_div = PortfolioTransaction(
        id="tx3",
        portfolio_id=p_id,
        account_id=a1_id,
        user_id="u1",
        transaction_type=TransactionType.CASH_DIVIDEND,
        net_cash_amount=Decimal("150.00"),
        cash_currency="USD",
        trade_date=now,
        settlement_date=now,
    )
    cf_div = classifier.classify_transaction(tx_div, scope=MeasurementScope.PORTFOLIO)
    assert cf_div.classification == CashFlowClassification.INTERNAL_INCOME
    assert cf_div.portfolio_flow_amount == Decimal("0.00")

    # 4. Account-to-Account transfer:
    # At PORTFOLIO scope: INTERNAL_TRANSFER
    # At ACCOUNT scope: EXTERNAL
    tx_xfer = PortfolioTransaction(
        id="tx4",
        portfolio_id=p_id,
        account_id=a1_id,
        user_id="u1",
        transaction_type=TransactionType.CASH_TRANSFER_IN,
        net_cash_amount=Decimal("1000.00"),
        cash_currency="USD",
        trade_date=now,
        settlement_date=now,
    )
    cf_port = classifier.classify_transaction(tx_xfer, scope=MeasurementScope.PORTFOLIO)
    assert cf_port.classification == CashFlowClassification.INTERNAL_TRANSFER
    assert cf_port.portfolio_flow_amount == Decimal("0.00")

    cf_acc = classifier.classify_transaction(tx_xfer, scope=MeasurementScope.ACCOUNT, target_account_id=a1_id)
    assert cf_acc.classification == CashFlowClassification.EXTERNAL_CONTRIBUTION
    assert cf_acc.portfolio_flow_amount == Decimal("1000.00")


# ---------------------------------------------------------------------------
# Test 5: Periodic Returns and Geometric Annualization
# ---------------------------------------------------------------------------


def test_periodic_returns_and_annualization():
    """Validates compounding of monthly returns and geometric annualization."""
    # 1. Annualization over 2 years (730.5 days) of 21% cumulative return:
    # (1 + 0.21)^(1/2) - 1 = 1.10 - 1 = 10%
    ann_ret = calculate_annualized_return(Decimal("0.21"), duration_days=730.5)
    assert ann_ret is not None
    assert round(ann_ret, 2) == Decimal("0.10")

    # 2. Under 1 year (< 365 days): must return None to prevent extrapolation error
    short_ann = calculate_annualized_return(Decimal("0.05"), duration_days=180.0)
    assert short_ann is None

    # 3. Geometric linking of 12 monthly returns:
    # 1% per month for 12 months: (1.01)^12 - 1 = 12.68%
    m_returns = [Decimal("0.01")] * 12
    annual_linked = compound_periodic_returns(m_returns)
    assert round(annual_linked * 100, 2) == Decimal("12.68")


# ---------------------------------------------------------------------------
# Test 6: Benchmark Registry and Relative Comparison
# ---------------------------------------------------------------------------


def test_benchmark_registry_and_comparison():
    """Validates benchmark comparison, rebased growth index, and basis warnings."""
    assert "BENCHMARK_SP500" in CANONICAL_BENCHMARKS
    assert "BENCHMARK_SPY" in CANONICAL_BENCHMARKS

    t0 = datetime(2026, 1, 1)
    t1 = datetime(2026, 12, 31)

    # Portfolio return 15%, S&P 500 grew from 5000 to 5500 (10%)
    comp = compare_portfolio_to_benchmark(
        benchmark_id="BENCHMARK_SP500",
        portfolio_return=Decimal("0.15"),
        period_start=t0,
        period_end=t1,
        start_level=Decimal("5000.00"),
        end_level=Decimal("5500.00"),
    )

    assert comp.benchmark_return == Decimal("0.10")
    # Difference: 15% - 10% = +5%
    assert comp.arithmetic_difference == Decimal("0.05")
    # Rebased indexes start at 100.0
    assert comp.rebased_portfolio_index_end == Decimal("115.00")
    assert comp.rebased_benchmark_index_end == Decimal("110.00")
    # S&P 500 is price-return; expect warning
    assert comp.warning is not None
    assert "Price Return" in comp.warning


# ---------------------------------------------------------------------------
# Test 7: End-to-End REST API Flow and Tenant Isolation
# ---------------------------------------------------------------------------


def test_rest_api_performance_flow_and_tenant_isolation():
    """Validates FastAPI performance endpoints and multi-tenant security."""
    port_service = PortfolioService()
    perf_service = PortfolioPerformanceService(port_service)

    # User A setup
    user_a = AuthPrincipal(sub="user_perf_a", email="a@institutional.atlas", role="authenticated")
    user_b = AuthPrincipal(sub="user_perf_b", email="b@institutional.atlas", role="authenticated")

    app.dependency_overrides[get_portfolio_service] = lambda: port_service
    app.dependency_overrides[get_performance_service] = lambda: perf_service
    app.dependency_overrides[get_current_user] = lambda: user_a

    client = TestClient(app)

    # 1. Create Portfolio for User A
    p_res = client.post(
        "/api/v1/portfolios",
        json={"name": "Alpha Fund", "base_currency": "USD", "portfolio_type": "INSTITUTIONAL"},
    )
    assert p_res.status_code == 201
    p_id = p_res.json()["id"]

    # 2. Get default Account created for the portfolio
    accs_res = client.get(f"/api/v1/portfolios/{p_id}/accounts")
    assert accs_res.status_code == 200
    a_id = accs_res.json()["items"][0]["id"]

    # 3. Post Deposit: $10,000.00
    d_res = client.post(
        f"/api/v1/portfolios/{p_id}/transactions",
        json={
            "account_id": a_id,
            "transaction_type": "CASH_DEPOSIT",
            "gross_amount": 10000,
            "cash_currency": "USD",
            "trade_date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
        },
    )
    assert d_res.status_code == 201

    # 4. Post Buy: 100 shares of AAPL @ $50.00 + $10 fee = $5,010.00
    port_service.set_mock_quote("inst_aapl", Decimal("55.00"), "USD")
    b_res = client.post(
        f"/api/v1/portfolios/{p_id}/transactions",
        json={
            "account_id": a_id,
            "transaction_type": "BUY",
            "instrument_id": "inst_aapl",
            "symbol": "AAPL",
            "quantity": 100,
            "unit_price": 50.00,
            "gross_amount": 5000,
            "fee": 10.00,
            "cash_currency": "USD",
            "trade_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        },
    )
    assert b_res.status_code == 201

    # 5. List Benchmarks endpoint
    bench_res = client.get("/api/v1/portfolios/benchmarks")
    assert bench_res.status_code == 200
    assert bench_res.json()["total"] >= 4

    # 6. Query Performance Summary
    summary_res = client.get(f"/api/v1/portfolios/{p_id}/performance?period_type=INCEPTION")
    assert summary_res.status_code == 200
    data = summary_res.json()
    assert data["portfolio_id"] == p_id
    assert data["total_contributions"] == "10000.00"
    assert data["total_withdrawals"] == "0.00"
    # Valuation: 100 shares @ $55 = $5,500 + $4,990 cash = $10,490.00
    # Gain: $10,490 - $10,000 = $490.00
    assert data["ending_value"] == "10490.00"
    assert data["investment_gain"] == "490.00"
    assert Decimal(data["twr_cumulative"]) > Decimal("0.04")

    # 7. Query Performance Series
    series_res = client.get(f"/api/v1/portfolios/{p_id}/performance/series?period_type=INCEPTION")
    assert series_res.status_code == 200
    series_data = series_res.json()
    assert len(series_data["points"]) >= 2
    assert series_data["points"][0]["indexed_twr"] == "100.00"

    # 8. Query Periodic Returns
    periodic_res = client.get(f"/api/v1/portfolios/{p_id}/performance/periodic")
    assert periodic_res.status_code == 200
    assert len(periodic_res.json()["returns"]) >= 1

    # 9. Query Classified Cash Flows
    flows_res = client.get(f"/api/v1/portfolios/{p_id}/performance/cash-flows")
    assert flows_res.status_code == 200
    assert len(flows_res.json()) >= 2

    # 10. Cross-Tenant Security: User B tries to access User A's performance
    app.dependency_overrides[get_current_user] = lambda: user_b
    b_access = client.get(f"/api/v1/portfolios/{p_id}/performance")
    assert b_access.status_code in (403, 404)

    # Clean overrides
    app.dependency_overrides.clear()
