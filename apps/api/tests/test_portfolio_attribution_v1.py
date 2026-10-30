"""Tests for ATLAS Portfolio Performance Attribution Architecture (Stage 113).

Verifies:
1. Part XVII Brinson-Fachler reference fixture (Tech 60/40, Fin 40/60 => Active Return +2.20 pp,
   Alloc +0.40 pp, Select +0.20 pp, Inter +1.60 pp, Residual 0.00 pp).
2. Part XVIII Brinson-Hood-Beebower (BHB) allocation comparison (+2.00% Tech, -1.60% Fin).
3. Part XXVII Security Return Contribution reference fixture (50/50, +10% & -4% => Port +3.0%).
4. Part XXXVI Currency attribution reference fixture (100->110 USD, 80->90 INR => +23.75% Base Return).
5. Carino multi-period logarithmic linking algorithm and equal-return limiting cases.
6. Absent sector handling (w_P = 0 and w_B = 0 / cash drag).
7. Mathematical reconciliation engine and residual integrity.
8. FastAPI REST endpoints, calculation requests, and strict cross-tenant isolation.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas_api.auth.dependencies import get_current_user
from atlas.portfolios import (
    AccountCreateRequest,
    PortfolioCreateRequest,
    PortfolioService,
    TransactionCreateRequest,
    TransactionType,
)
from atlas.portfolios.attribution import (
    AttributionDimension,
    AttributionMethod,
    BenchmarkCompositionEngine,
    BenchmarkPointInTimeSnapshot,
    BenchmarkSectorSnapshot,
    BrinsonEngine,
    CalculateAttributionRequest,
    CurrencyAttributionEngine,
    MultiPeriodLinkingEngine,
    MultiPeriodLinkingMethod,
    PortfolioAttributionService,
    ReconciliationStatus,
    SecurityContributionEngine,
)
from atlas_api.main import app
from atlas_api.routers.portfolios import get_attribution_service, get_portfolio_service


# ---------------------------------------------------------------------------
# Test Fixtures & Utilities
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_services():
    """Provides isolated, clean service instances for testing."""
    port_svc = PortfolioService()
    bench_engine = BenchmarkCompositionEngine()
    attr_svc = PortfolioAttributionService(
        portfolio_service=port_svc,
        benchmark_engine=bench_engine,
    )
    return port_svc, bench_engine, attr_svc


@pytest.fixture
def test_client(clean_services):
    """Provides TestClient with overridden service dependencies."""
    port_svc, bench_engine, attr_svc = clean_services
    app.dependency_overrides[get_portfolio_service] = lambda: port_svc
    app.dependency_overrides[get_attribution_service] = lambda: attr_svc
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def make_auth_headers(sub: str = "usr_tenant_a", email: str = "analyst@atlas.financial") -> dict:
    """Mock headers matching dev authentication principal."""
    return {
        "X-User-Id": sub,
        "X-User-Email": email,
        "X-User-Roles": "authenticated,portfolio_manager",
    }


# ---------------------------------------------------------------------------
# 1. Part XVII — Brinson-Fachler Reference Fixture (+2.20 pp Active Return)
# ---------------------------------------------------------------------------

def test_part_xvii_brinson_fachler_reference_fixture():
    """
    Mandatory Part XVII Brinson-Fachler Reference Fixture:
    Technology: Portfolio weight 60%, Benchmark weight 40%, Portfolio return 15%, Benchmark return 10%
    Financials: Portfolio weight 40%, Benchmark weight 60%, Portfolio return 5%, Benchmark return 8%

    Expected:
    Portfolio Return = 0.60(0.15) + 0.40(0.05) = 11.00%
    Benchmark Return = 0.40(0.10) + 0.60(0.08) = 8.80%
    Active Return    = 11.00% - 8.80% = +2.20 percentage points

    BF Allocation:
    Tech: (0.60 - 0.40)(0.10 - 0.088) = 0.20 * 0.012 = +0.0024 = +0.24%
    Fin:  (0.40 - 0.60)(0.08 - 0.088) = -0.20 * (-0.008) = +0.0016 = +0.16%
    Total Allocation = +0.40%

    BF Selection:
    Tech: 0.40 * (0.15 - 0.10) = +0.0200 = +2.00%
    Fin:  0.60 * (0.05 - 0.08) = -0.0180 = -1.80%
    Total Selection = +0.20%

    BF Interaction:
    Tech: (0.60 - 0.40)(0.15 - 0.10) = 0.20 * 0.05 = +0.0100 = +1.00%
    Fin:  (0.40 - 0.60)(0.05 - 0.08) = -0.20 * (-0.03) = +0.0060 = +0.60%
    Total Interaction = +1.60%

    Total Attributed = 0.40% + 0.20% + 1.60% = +2.20%
    Reconciliation Residual = 0.00%
    """
    engine = BrinsonEngine()

    portfolio_groups = {
        "technology": (Decimal("0.600000"), Decimal("0.150000")),
        "financials": (Decimal("0.400000"), Decimal("0.050000")),
    }
    benchmark_groups = {
        "technology": (Decimal("0.400000"), Decimal("0.100000")),
        "financials": (Decimal("0.600000"), Decimal("0.080000")),
    }
    labels = {
        "technology": "Information Technology",
        "financials": "Financials",
    }

    total_p = Decimal("0.110000")  # 11%
    total_b = Decimal("0.088000")  # 8.8%
    active_expected = Decimal("0.022000")  # +2.20%

    results = engine.decompose(
        portfolio_groups=portfolio_groups,
        benchmark_groups=benchmark_groups,
        category_labels=labels,
        total_portfolio_return=total_p,
        total_benchmark_return=total_b,
        method=AttributionMethod.BRINSON_FACHLER,
    )

    res_dict = {r.category_id: r for r in results}
    tech = res_dict["technology"]
    fin = res_dict["financials"]

    # Tech Sector Verification
    assert tech.allocation_effect == Decimal("0.002400"), f"Tech alloc expected +0.24%, got {tech.allocation_effect}"
    assert tech.selection_effect == Decimal("0.020000"), f"Tech select expected +2.00%, got {tech.selection_effect}"
    assert tech.interaction_effect == Decimal("0.010000"), f"Tech inter expected +1.00%, got {tech.interaction_effect}"
    assert tech.total_effect == Decimal("0.032400"), f"Tech total expected +3.24%, got {tech.total_effect}"

    # Financials Sector Verification
    assert fin.allocation_effect == Decimal("0.001600"), f"Fin alloc expected +0.16%, got {fin.allocation_effect}"
    assert fin.selection_effect == Decimal("-0.018000"), f"Fin select expected -1.80%, got {fin.selection_effect}"
    assert fin.interaction_effect == Decimal("0.006000"), f"Fin inter expected +0.60%, got {fin.interaction_effect}"
    assert fin.total_effect == Decimal("-0.010400"), f"Fin total expected -1.04%, got {fin.total_effect}"

    # Totals Verification
    total_alloc = tech.allocation_effect + fin.allocation_effect
    total_select = tech.selection_effect + fin.selection_effect
    total_inter = tech.interaction_effect + fin.interaction_effect
    total_attr = total_alloc + total_select + total_inter

    assert total_alloc == Decimal("0.004000"), f"Total alloc expected +0.40%, got {total_alloc}"
    assert total_select == Decimal("0.002000"), f"Total select expected +0.20%, got {total_select}"
    assert total_inter == Decimal("0.016000"), f"Total inter expected +1.60%, got {total_inter}"
    assert total_attr == active_expected, f"Total attr expected {active_expected}, got {total_attr}"

    residual = active_expected - total_attr
    assert residual == Decimal("0.000000"), f"Residual must be exactly 0.00%, got {residual}"


# ---------------------------------------------------------------------------
# 2. Part XVIII — Brinson-Hood-Beebower (BHB) Allocation Comparison
# ---------------------------------------------------------------------------

def test_part_xviii_brinson_hood_beebower_fixture():
    """
    Mandatory Part XVIII BHB Allocation Comparison:
    Using the exact same Part XVII two-sector input data:
    BHB Allocation:
    Tech: (0.60 - 0.40) * 0.10 = 0.20 * 0.10 = +0.0200 = +2.00%
    Fin:  (0.40 - 0.60) * 0.08 = -0.20 * 0.08 = -0.0160 = -1.60%
    Total Allocation = +2.00% - 1.60% = +0.40%
    """
    engine = BrinsonEngine()

    portfolio_groups = {
        "technology": (Decimal("0.600000"), Decimal("0.150000")),
        "financials": (Decimal("0.400000"), Decimal("0.050000")),
    }
    benchmark_groups = {
        "technology": (Decimal("0.400000"), Decimal("0.100000")),
        "financials": (Decimal("0.600000"), Decimal("0.080000")),
    }
    labels = {
        "technology": "Information Technology",
        "financials": "Financials",
    }

    total_p = Decimal("0.110000")
    total_b = Decimal("0.088000")

    results = engine.decompose(
        portfolio_groups=portfolio_groups,
        benchmark_groups=benchmark_groups,
        category_labels=labels,
        total_portfolio_return=total_p,
        total_benchmark_return=total_b,
        method=AttributionMethod.BRINSON_HOOD_BEEBOWER,
    )

    res_dict = {r.category_id: r for r in results}
    tech = res_dict["technology"]
    fin = res_dict["financials"]

    # BHB Category Allocation Differences
    assert tech.allocation_effect == Decimal("0.020000"), f"Tech BHB alloc expected +2.00%, got {tech.allocation_effect}"
    assert fin.allocation_effect == Decimal("-0.016000"), f"Fin BHB alloc expected -1.60%, got {fin.allocation_effect}"

    # Aggregate BHB Allocation still equals +0.40% for complete partition!
    total_bhb_alloc = tech.allocation_effect + fin.allocation_effect
    assert total_bhb_alloc == Decimal("0.004000"), f"Total BHB alloc expected +0.40%, got {total_bhb_alloc}"


# ---------------------------------------------------------------------------
# 3. Part XXVII — Security Return Contribution Reference Fixture
# ---------------------------------------------------------------------------

def test_part_xxvii_security_return_contribution_fixture():
    """
    Mandatory Part XXVII Security Contribution Reference Fixture:
    Security A weight: 50%, Return: +10% => Contribution C_A = 0.50 * 0.10 = +5.0%
    Security B weight: 50%, Return: -4%  => Contribution C_B = 0.50 * (-0.04) = -2.0%
    Portfolio Return = +5.0% - 2.0% = +3.0%
    """
    engine = SecurityContributionEngine()

    records = [
        ("sec_a", "SECA", "Security A Inc.", Decimal("0.500000"), Decimal("0.100000"), "technology", "software", "USD", False),
        ("sec_b", "SECB", "Security B Corp.", Decimal("0.500000"), Decimal("-0.040000"), "financials", "banks", "USD", False),
    ]

    all_items, top_c, top_d = engine.compute_all_contributions(records)

    c_dict = {i.symbol: i for i in all_items}
    assert c_dict["SECA"].contribution == Decimal("0.050000"), f"SECA contrib expected +5.0%, got {c_dict['SECA'].contribution}"
    assert c_dict["SECB"].contribution == Decimal("-0.020000"), f"SECB contrib expected -2.0%, got {c_dict['SECB'].contribution}"

    total_contrib = sum((i.contribution for i in all_items), Decimal("0.000000"))
    assert total_contrib == Decimal("0.030000"), f"Total portfolio return expected +3.0%, got {total_contrib}"

    # Verify Contributor / Detractor Rankings
    assert top_c[0].symbol == "SECA"
    assert top_d[0].symbol == "SECB"


# ---------------------------------------------------------------------------
# 4. Part XXXVI — Currency Attribution Reference Fixture (+23.75%)
# ---------------------------------------------------------------------------

def test_part_xxxvi_currency_attribution_reference_fixture():
    """
    Mandatory Part XXXVI Currency Attribution Reference Fixture:
    Initial: 100 USD @ 1 USD = 80 INR
    Ending:  110 USD @ 1 USD = 90 INR

    Local return R_local = (110 - 100) / 100 = +10.0%
    FX return R_FX       = (90 - 80) / 80     = +12.5%
    Interaction          = 10% * 12.5%        = +1.25%
    Base INR Return      = 10% + 12.5% + 1.25%= +23.75%
    """
    engine = CurrencyAttributionEngine()

    res = engine.decompose_currency_return(
        currency="USD",
        portfolio_weight=Decimal("1.000000"),
        local_return=Decimal("0.100000"),
        fx_start_rate=Decimal("80.000000"),
        fx_end_rate=Decimal("90.000000"),
    )

    assert res.local_return == Decimal("0.100000"), f"Local return expected +10%, got {res.local_return}"
    assert res.fx_return == Decimal("0.125000"), f"FX return expected +12.5%, got {res.fx_return}"
    assert res.interaction_return == Decimal("0.012500"), f"Cross-term expected +1.25%, got {res.interaction_return}"
    assert res.base_currency_return == Decimal("0.237500"), f"Base INR return expected +23.75%, got {res.base_currency_return}"


# ---------------------------------------------------------------------------
# 5. Part XLV — Carino Multi-Period Logarithmic Linking
# ---------------------------------------------------------------------------

def test_multi_period_carino_logarithmic_linking():
    """
    Verifies Carino multi-period logarithmic linking preserves exact reconciliation:
    sum(A_linked + S_linked + I_linked) = R_P_cum - R_B_cum.
    """
    from atlas.portfolios.attribution.models import (
        AttributionCategoryResult,
        HistoricalPeriodAttribution,
    )

    engine = MultiPeriodLinkingEngine()

    now = datetime.utcnow()
    # Period 1: R_P = 10%, R_B = 5% => Active = +5%
    p1 = HistoricalPeriodAttribution(
        period_label="Month 1",
        period_start=now - timedelta(days=60),
        period_end=now - timedelta(days=31),
        portfolio_return=Decimal("0.100000"),
        benchmark_return=Decimal("0.050000"),
        active_return=Decimal("0.050000"),
        allocation_effect=Decimal("0.020000"),
        selection_effect=Decimal("0.020000"),
        interaction_effect=Decimal("0.010000"),
        total_attributed=Decimal("0.050000"),
        residual=Decimal("0.000000"),
    )
    p1_cats = [
        AttributionCategoryResult(
            category_id="tech",
            category_label="Tech",
            portfolio_weight=Decimal("0.5"),
            benchmark_weight=Decimal("0.5"),
            portfolio_return=Decimal("0.10"),
            benchmark_return=Decimal("0.05"),
            allocation_effect=Decimal("0.020000"),
            selection_effect=Decimal("0.020000"),
            interaction_effect=Decimal("0.010000"),
            total_effect=Decimal("0.050000"),
        )
    ]

    # Period 2: R_P = 8%, R_B = 4% => Active = +4%
    p2 = HistoricalPeriodAttribution(
        period_label="Month 2",
        period_start=now - timedelta(days=30),
        period_end=now,
        portfolio_return=Decimal("0.080000"),
        benchmark_return=Decimal("0.040000"),
        active_return=Decimal("0.040000"),
        allocation_effect=Decimal("0.015000"),
        selection_effect=Decimal("0.015000"),
        interaction_effect=Decimal("0.010000"),
        total_attributed=Decimal("0.040000"),
        residual=Decimal("0.000000"),
    )
    p2_cats = [
        AttributionCategoryResult(
            category_id="tech",
            category_label="Tech",
            portfolio_weight=Decimal("0.5"),
            benchmark_weight=Decimal("0.5"),
            portfolio_return=Decimal("0.08"),
            benchmark_return=Decimal("0.04"),
            allocation_effect=Decimal("0.015000"),
            selection_effect=Decimal("0.015000"),
            interaction_effect=Decimal("0.010000"),
            total_effect=Decimal("0.040000"),
        )
    ]

    linked = engine.link_periods([p1, p2], [p1_cats, p2_cats], MultiPeriodLinkingMethod.CARINO)

    # Cumulative R_P = (1 + 0.10)*(1 + 0.08) - 1 = 1.188 - 1 = 0.188 (18.8%)
    # Cumulative R_B = (1 + 0.05)*(1 + 0.04) - 1 = 1.092 - 1 = 0.092 (9.2%)
    # Cumulative Active = 0.188 - 0.092 = 0.096 (9.6%)
    assert abs(linked.cumulative_active_return - Decimal("0.096000")) < Decimal("0.0001")

    # Linked attributed effects must reconcile to cumulative active return
    assert abs(linked.reconciliation_residual) < Decimal("0.0001")


# ---------------------------------------------------------------------------
# 6. Absent Sector and Off-Benchmark Cash Drag Handling
# ---------------------------------------------------------------------------

def test_absent_sector_and_cash_drag_attribution():
    """
    Tests institutional handling of:
    1. Sector in benchmark but 0% held in portfolio (absent portfolio sector).
    2. Off-benchmark category (Cash drag) held in portfolio but 0% in benchmark.
    """
    engine = BrinsonEngine()

    portfolio_groups = {
        "technology": (Decimal("0.800000"), Decimal("0.120000")),
        "cash": (Decimal("0.200000"), Decimal("0.010000")),  # Off-benchmark cash
    }
    benchmark_groups = {
        "technology": (Decimal("0.600000"), Decimal("0.100000")),
        "energy": (Decimal("0.400000"), Decimal("0.050000")),  # Absent in portfolio
    }
    labels = {
        "technology": "Tech",
        "energy": "Energy",
        "cash": "Cash",
    }

    total_p = (Decimal("0.80") * Decimal("0.12")) + (Decimal("0.20") * Decimal("0.01"))  # 0.096 + 0.002 = 0.098 (9.8%)
    total_b = (Decimal("0.60") * Decimal("0.10")) + (Decimal("0.40") * Decimal("0.05"))  # 0.060 + 0.020 = 0.080 (8.0%)
    active_return = total_p - total_b  # +1.80%

    results = engine.decompose(
        portfolio_groups=portfolio_groups,
        benchmark_groups=benchmark_groups,
        category_labels=labels,
        total_portfolio_return=total_p,
        total_benchmark_return=total_b,
        method=AttributionMethod.BRINSON_FACHLER,
    )

    res_dict = {r.category_id: r for r in results}

    # Energy is absent in portfolio (w_P = 0)
    energy = res_dict["energy"]
    assert energy.portfolio_weight == Decimal("0.000000")
    assert energy.selection_effect == Decimal("0.000000")
    # Energy alloc: (0 - 0.40) * (0.05 - 0.08) = -0.40 * (-0.03) = +0.012 (+1.2%)
    assert abs(energy.allocation_effect - Decimal("0.012000")) < Decimal("0.000001")

    # Cash is off-benchmark (w_B = 0)
    cash = res_dict["cash"]
    assert cash.benchmark_weight == Decimal("0.000000")
    assert cash.selection_effect == Decimal("0.000000")
    # Cash drag effect: 0.20 * (0.01 - 0.08) = -0.014 (-1.4%)
    assert abs(cash.interaction_effect - Decimal("-0.014000")) < Decimal("0.000001")

    # Total attribution reconciles to active return (+1.80%)
    total_attr = sum((r.total_effect for r in results), Decimal("0.000000"))
    assert abs(total_attr - active_return) < Decimal("0.000001")


# ---------------------------------------------------------------------------
# 7. End-to-End REST API Workflow & Multi-Tenant Security
# ---------------------------------------------------------------------------

def test_rest_api_attribution_endpoints_and_tenant_isolation(test_client):
    """
    Tests the complete REST API workflow:
    1. Create portfolio, investment account, and post transactions.
    2. Request /attribution, /attribution/calculate, /attribution/sectors, /attribution/securities.
    3. Verify Tenant Isolation: User B cannot access User A's attribution.
    """
    user_a = AuthPrincipal(sub="usr_pm_alice", email="alice@atlas.financial", role="authenticated")
    user_b = AuthPrincipal(sub="usr_pm_bob", email="bob@atlas.financial", role="authenticated")

    app.dependency_overrides[get_current_user] = lambda: user_a

    # 1. Create Portfolio for Alice
    create_port_res = test_client.post(
        "/api/v1/portfolios",
        json={"name": "Alice Global Tech Alpha", "base_currency": "USD"},
    )
    assert create_port_res.status_code == 201
    port_id = create_port_res.json()["id"]

    # Get default Investment Account created with portfolio
    accs_res = test_client.get(f"/api/v1/portfolios/{port_id}/accounts")
    assert accs_res.status_code == 200
    account_id = accs_res.json()["items"][0]["id"]

    # Post Deposit
    now = datetime.utcnow()
    dep_res = test_client.post(
        f"/api/v1/portfolios/{port_id}/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "CASH_DEPOSIT",
            "trade_date": (now - timedelta(days=60)).isoformat(),
            "cash_currency": "USD",
            "gross_amount": "100000.00",
        },
    )
    assert dep_res.status_code == 201

    # Buy AAPL ($50,000)
    buy_res = test_client.post(
        f"/api/v1/portfolios/{port_id}/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "BUY",
            "trade_date": (now - timedelta(days=45)).isoformat(),
            "symbol": "AAPL",
            "quantity": "250.0",
            "unit_price": "200.00",
            "gross_amount": "50000.00",
            "cash_currency": "USD",
        },
    )
    assert buy_res.status_code == 201

    # 2. Query /attribution default
    attr_res = test_client.get(
        f"/api/v1/portfolios/{port_id}/attribution",
    )
    assert attr_res.status_code == 200
    data = attr_res.json()
    assert data["portfolio_id"] == port_id
    assert "active_return" in data
    assert "total_allocation_effect" in data
    assert "total_selection_effect" in data
    assert "total_interaction_effect" in data
    assert "reconciliation" in data
    assert data["reconciliation"]["status"] in ("RECONCILED", "RECONCILED_WITH_ROUNDING_TOLERANCE")

    # 3. Post /attribution/calculate on-demand with custom benchmark
    calc_res = test_client.post(
        f"/api/v1/portfolios/{port_id}/attribution/calculate",
        json={
            "benchmark_id": "BENCHMARK_SPY",
            "attribution_method": "BRINSON_FACHLER",
            "classification_dimension": "SECTOR",
        },
    )
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["attribution_method"] == "BRINSON_FACHLER"
    assert len(calc_data["category_results"]) > 0

    # 4. Check /attribution/securities
    sec_res = test_client.get(
        f"/api/v1/portfolios/{port_id}/attribution/securities",
    )
    assert sec_res.status_code == 200
    sec_data = sec_res.json()
    assert len(sec_data) >= 1
    symbols = [s["symbol"] for s in sec_data]
    assert "AAPL" in symbols

    # 5. Check /attribution/sectors
    sec_attr_res = test_client.get(
        f"/api/v1/portfolios/{port_id}/attribution/sectors",
    )
    assert sec_attr_res.status_code == 200
    assert len(sec_attr_res.json()) > 0

    # 6. Check /attribution/reconciliation
    rec_res = test_client.get(
        f"/api/v1/portfolios/{port_id}/attribution/reconciliation",
    )
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["attribution_reconciled"] is True

    # 7. Check /attribution/benchmarks
    bench_res = test_client.get(
        f"/api/v1/portfolios/{port_id}/attribution/benchmarks",
    )
    assert bench_res.status_code == 200
    benchmarks = bench_res.json()
    assert len(benchmarks) >= 4
    b_ids = [b["benchmark_id"] for b in benchmarks]
    assert "BENCHMARK_SPY" in b_ids

    # 8. Multi-Tenant Isolation Enforcement:
    # User B (Bob) must be rejected with 403 or 404 when querying Alice's portfolio attribution
    app.dependency_overrides[get_current_user] = lambda: user_b
    unauthorized_res = test_client.get(
        f"/api/v1/portfolios/{port_id}/attribution",
    )
    assert unauthorized_res.status_code in (403, 404)

    unauthorized_calc = test_client.post(
        f"/api/v1/portfolios/{port_id}/attribution/calculate",
        json={"benchmark_id": "BENCHMARK_SPY"},
    )
    assert unauthorized_calc.status_code in (403, 404)
