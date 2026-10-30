"""Stage 117 — Multi-Factor, Concentration, Currency, and Sector Risk Intelligence Tests.

Verifies:
1. Part XIV Reference Fixture: Multi-factor portfolio exposure aggregation b = B^T w = [1.04, 0.22].
2. Part XXII Reference Fixture: Systematic vs specific variance decomposition and Euler contributions:
   V_sys = 0.043748, V_spec = 0.009700, V_total = 0.053448, sigma_P ~= 23.11882%,
   VC_MKT = 0.043264, VC_HML = 0.000484, exact reconciliation.
3. Part XXXI Reference Fixture: Herfindahl-Hirschman Index (HHI) & Effective Holdings:
   w = [0.5, 0.3, 0.2] -> HHI = 0.38, N_eff ~= 2.63158, Top 1 = 50%, Top 2 = 80%.
4. Part XLIV Reference Fixture: Multiplicative Base vs Local return interaction:
   Local +10%, FX -5% -> Interaction -0.5%, Base +4.5%.
5. Part LVII Reference Fixture: Sector Euler risk attribution:
   Tech 50%, Fin 50%, Sigma = diag(0.04, 0.09) -> V_P = 0.0325, VC_Tech = 0.0100, VC_Fin = 0.0225.
6. Multi-factor OLS regression rank and collinearity diagnostics.
7. Multi-share class issuer consolidation (GOOG + GOOGL -> Alphabet).
8. 2D Cross-exposure matrix reconciliation (sum_s b_{s,k} == b_k).
9. FastAPI endpoints for Factor, Concentration, Currency, Sector, and Cross-exposure analytics.
10. Strict multi-tenant security isolation.
"""

from datetime import datetime
from decimal import Decimal
import math
from typing import Dict, List
import pytest
import numpy as np
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios.service import PortfolioService
from atlas.risk.enums import (
    ConcentrationDimension,
    CurrencyExposureType,
    FactorFamily,
    ModelDiagnosticStatus,
    RiskModelType,
)
from atlas.risk.errors import (
    RiskConcentrationInvalidWeightsError,
    RiskFactorCollinearityDetectedError,
    RiskFactorCovarianceNotPSDError,
    RiskFactorNotFoundError,
    RiskFactorReturnHistoryInsufficientError,
    RiskStage117RunNotFoundError,
    RiskSubjectAccessDeniedError,
    RiskSubjectNotFoundError,
)
from atlas.risk.factors import FactorRiskEngine, PREDEFINED_FACTORS
from atlas.risk.concentration import ConcentrationEngine
from atlas.risk.currency_risk import CurrencyRiskEngine
from atlas.risk.sector_risk import SectorRiskEngine
from atlas.risk.cross_exposure import CrossExposureEngine
from atlas.risk.service import RiskService
from atlas.risk.schemas import (
    CalculateFactorRiskRequest,
)
from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.risk import get_portfolio_service, get_risk_service


USER_A_ID = "usr_stage117_test_a"
USER_B_ID = "usr_stage117_test_b"

user_a_principal = AuthPrincipal(
    sub=USER_A_ID,
    email="lead_risk_quant@atlas.firm",
    role="authenticated",
)

user_b_principal = AuthPrincipal(
    sub=USER_B_ID,
    email="external_trader@other.firm",
    role="authenticated",
)


@pytest.fixture
def risk_services():
    p_service = PortfolioService()
    r_service = RiskService(portfolio_service=p_service)
    return p_service, r_service


@pytest.fixture
def client_user_a(risk_services):
    p_service, r_service = risk_services
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: user_a_principal
    app.dependency_overrides[get_portfolio_service] = lambda: p_service
    app.dependency_overrides[get_risk_service] = lambda: r_service
    return TestClient(app)


@pytest.fixture
def client_user_b(risk_services):
    p_service, r_service = risk_services
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: user_b_principal
    app.dependency_overrides[get_portfolio_service] = lambda: p_service
    app.dependency_overrides[get_risk_service] = lambda: r_service
    return TestClient(app)


# ============================================================================
# 1. MATHEMATICAL ENGINE & REFERENCE FIXTURE TESTS
# ============================================================================

def test_part_xiv_factor_exposure_fixture():
    """Verifies Part XIV: b = B^T w = [1.04, 0.22] for w=[0.6, 0.4] and B=[[1.2, 0.5], [0.8, -0.2]]."""
    w = [0.6, 0.4]
    B = [
        [1.2, 0.5],
        [0.8, -0.2],
    ]
    b = FactorRiskEngine.aggregate_portfolio_factor_exposures(w, B)
    assert len(b) == 2
    assert pytest.approx(b[0], rel=1e-7) == 1.04
    assert pytest.approx(b[1], rel=1e-7) == 0.22


def test_part_xxii_factor_risk_decomposition_fixture():
    """Verifies Part XXII: Euler variance and volatility risk decomposition with exact reconciliation.
    
    Inputs:
        w = [0.6, 0.4]
        b = [1.04, 0.22]
        F = [[0.04, 0.0], [0.0, 0.01]]
        d = [0.0225, 0.01]
    Outputs:
        V_sys = 0.043748
        V_spec = 0.009700
        V_total = 0.053448
        sigma_P ~= 23.11882%
        VC_MKT = 0.043264
        VC_HML = 0.000484
    """
    w = [0.6, 0.4]
    b = [1.04, 0.22]
    F = [
        [0.04, 0.0],
        [0.0, 0.01],
    ]
    d = [0.0225, 0.01]
    factor_ids = ["MKT", "HML"]

    (
        v_sys,
        v_spec,
        v_tot,
        sigma_p,
        contribs,
        rc_spec,
        _,
        is_reconciled,
        diff,
    ) = FactorRiskEngine.decompose_factor_risk(
        weights=w,
        portfolio_factor_exposures=b,
        factor_covariance=F,
        residual_variances=d,
        factor_ids=factor_ids,
    )

    assert pytest.approx(v_sys, abs=1e-7) == 0.043748
    assert pytest.approx(v_spec, abs=1e-7) == 0.009700
    assert pytest.approx(v_tot, abs=1e-7) == 0.053448
    assert pytest.approx(sigma_p, abs=1e-6) == 0.231188235

    assert len(contribs) == 2
    vc_mkt = contribs[0].variance_contribution
    vc_hml = contribs[1].variance_contribution

    assert pytest.approx(vc_mkt, abs=1e-7) == 0.043264
    assert pytest.approx(vc_hml, abs=1e-7) == 0.000484

    # Reconciliation checks
    assert pytest.approx(vc_mkt + vc_hml, abs=1e-7) == v_sys
    assert pytest.approx(vc_mkt + vc_hml + v_spec, abs=1e-7) == v_tot
    assert is_reconciled is True
    assert diff < 1e-6

    # Volatility contributions reconcile to total portfolio volatility
    rc_mkt = contribs[0].volatility_contribution
    rc_hml = contribs[1].volatility_contribution
    assert pytest.approx(rc_mkt + rc_hml + rc_spec, abs=1e-6) == sigma_p


def test_part_xxxi_concentration_hhi_fixture():
    """Verifies Part XXXI: w = [0.5, 0.3, 0.2] -> HHI = 0.38, N_eff ~= 2.63158, Top-N cumulative sums."""
    w = [0.5, 0.3, 0.2]
    hhi = ConcentrationEngine.calculate_hhi(w)
    assert pytest.approx(hhi, rel=1e-6) == 0.38

    n_eff = ConcentrationEngine.calculate_effective_holdings(hhi)
    assert pytest.approx(n_eff, rel=1e-5) == 2.631578947

    top_n = ConcentrationEngine.calculate_top_n(w, [1, 2, 3])
    assert pytest.approx(top_n["top_1"], rel=1e-6) == 0.50
    assert pytest.approx(top_n["top_2"], rel=1e-6) == 0.80
    assert pytest.approx(top_n["top_3"], rel=1e-6) == 1.00


def test_part_xliv_currency_return_interaction_fixture():
    """Verifies Part XLIV: Local +10%, FX -5% -> Interaction -0.5%, Base return +4.5%."""
    decomp = CurrencyRiskEngine.decompose_base_local_return(0.10, -0.05)
    assert pytest.approx(decomp["local_return"], rel=1e-6) == 0.10
    assert pytest.approx(decomp["fx_return"], rel=1e-6) == -0.05
    assert pytest.approx(decomp["interaction"], rel=1e-6) == -0.005
    assert pytest.approx(decomp["base_return"], rel=1e-6) == 0.045
    assert pytest.approx((1.10 * 0.95) - 1.0, rel=1e-6) == 0.045


def test_part_lvii_sector_euler_risk_fixture():
    """Verifies Part LVII: Tech 50%, Fin 50%, Sigma=diag(0.04, 0.09) -> V_P=0.0325, VC_Tech=0.01, VC_Fin=0.0225."""
    w = [0.5, 0.5]
    Sigma = [
        [0.04, 0.0],
        [0.0, 0.09],
    ]
    symbols = ["TECH_STK", "FIN_STK"]
    sector_map = {"TECH_STK": "Information Technology", "FIN_STK": "Financials"}
    industry_map = {"TECH_STK": "Software", "FIN_STK": "Banks"}

    snapshot = SectorRiskEngine.decompose_sector_risk(
        weights=w,
        covariance_matrix=Sigma,
        symbols=symbols,
        sector_map=sector_map,
        industry_map=industry_map,
    )

    assert pytest.approx(snapshot.portfolio_variance, rel=1e-6) == 0.0325
    assert pytest.approx(snapshot.portfolio_volatility, rel=1e-6) == math.sqrt(0.0325)
    assert snapshot.is_reconciled is True

    sec_map = {s.sector_name: s for s in snapshot.sectors}
    assert "Information Technology" in sec_map
    assert "Financials" in sec_map

    assert pytest.approx(sec_map["Information Technology"].variance_contribution, rel=1e-6) == 0.0100
    assert pytest.approx(sec_map["Financials"].variance_contribution, rel=1e-6) == 0.0225
    assert pytest.approx(
        sec_map["Information Technology"].variance_contribution + sec_map["Financials"].variance_contribution,
        rel=1e-6,
    ) == 0.0325


def test_ols_regression_diagnostics_and_collinearity():
    """Verifies OLS multi-factor regression rank detection and condition number diagnostics."""
    T = 100
    rng = np.random.RandomState(42)
    f1 = rng.normal(0, 0.01, size=T)
    f2 = f1 * 1.0000001
    F_collinear = np.column_stack([f1, f2]).tolist()
    y = f1 * 1.2 + rng.normal(0, 0.005, size=T)

    alpha, betas, res_var, r2, t_stats, diags = FactorRiskEngine.estimate_security_betas(
        security_returns=y.tolist(),
        factor_matrix=F_collinear,
        include_intercept=True,
    )

    assert diags.is_collinear is True
    assert diags.status in (ModelDiagnosticStatus.WARNING_COLLINEARITY, ModelDiagnosticStatus.WARNING_RANK_DEFICIENT)


def test_issuer_consolidation():
    """Verifies consolidation of multiple share classes into canonical issuer."""
    positions = [
        {"symbol": "GOOG", "name": "Alphabet Class C", "weight": 0.08, "market_value": 80000.0},
        {"symbol": "GOOGL", "name": "Alphabet Class A", "weight": 0.07, "market_value": 70000.0},
        {"symbol": "AAPL", "name": "Apple Inc.", "weight": 0.15, "market_value": 150000.0},
    ]
    issuer_map = {
        "GOOG": "Alphabet Inc.",
        "GOOGL": "Alphabet Inc.",
        "AAPL": "Apple Inc.",
    }

    consolidated = ConcentrationEngine.consolidate_issuers(positions, issuer_map)
    assert len(consolidated) == 2
    alph = [c for c in consolidated if c.identifier == "Alphabet Inc."][0]
    assert pytest.approx(alph.weight, rel=1e-6) == 0.15
    assert alph.securities_count == 2
    assert "GOOG" in alph.security_symbols
    assert "GOOGL" in alph.security_symbols


def test_cross_exposure_factor_by_sector_reconciliation():
    """Verifies sum_s b_{s,k} == b_k in 2D Factor x Sector exposure matrix."""
    symbols = ["AAPL", "MSFT", "JPM"]
    weights = [0.4, 0.3, 0.3]
    factor_betas = {
        "AAPL": {"MKT": 1.2, "SMB": -0.2},
        "MSFT": {"MKT": 1.1, "SMB": -0.1},
        "JPM": {"MKT": 0.9, "SMB": 0.3},
    }
    sector_map = {
        "AAPL": "Information Technology",
        "MSFT": "Information Technology",
        "JPM": "Financials",
    }
    factor_ids = ["MKT", "SMB"]

    matrix = CrossExposureEngine.build_factor_by_sector_matrix(
        symbols=symbols,
        weights=weights,
        factor_betas=factor_betas,
        sector_map=sector_map,
        factor_ids=factor_ids,
    )

    mkt_cells = [c for c in matrix.cells if c.row_key == "MKT"]
    mkt_tech = [c for c in mkt_cells if c.col_key == "Information Technology"][0].value
    mkt_fin = [c for c in mkt_cells if c.col_key == "Financials"][0].value

    assert pytest.approx(mkt_tech, rel=1e-6) == 0.81
    assert pytest.approx(mkt_fin, rel=1e-6) == 0.27
    assert pytest.approx(mkt_tech + mkt_fin, rel=1e-6) == 1.08


# ============================================================================
# 2. FASTAPI ENDPOINTS & MULTI-TENANT ISOLATION TESTS
# ============================================================================

def test_list_and_get_factors(client_user_a):
    """Verifies GET /api/v1/risk/factors and GET /api/v1/risk/factors/{factor_id}."""
    res = client_user_a.get("/api/v1/risk/factors")
    assert res.status_code == 200
    factors = res.json()
    assert len(factors) >= 6
    factor_ids = [f["factor_id"] for f in factors]
    assert "FACTOR_MKT" in factor_ids
    assert "FACTOR_SMB" in factor_ids
    assert "FACTOR_HML" in factor_ids

    res_single = client_user_a.get("/api/v1/risk/factors/FACTOR_MKT")
    assert res_single.status_code == 200
    f_mkt = res_single.json()
    assert f_mkt["factor_code"] == "MKT"
    assert f_mkt["family"] == "MARKET"


def test_calculate_and_get_portfolio_factors(client_user_a, risk_services):
    """Verifies POST /api/v1/risk/factor-models/calculate and GET /api/v1/risk/portfolios/{id}/factors."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Quant Multi-Asset Risk Portfolio",
            "base_currency": "USD",
            "description": "Multi-Factor Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    # 1. Post calculate
    req = {
        "portfolio_id": p_id,
        "model_id": "FAMA_FRENCH_6",
        "factor_ids": ["FACTOR_MKT", "FACTOR_SMB", "FACTOR_HML"],
    }
    res = client_user_a.post("/api/v1/risk/factor-models/calculate", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["portfolio_id"] == p_id
    assert data["total_volatility"] > 0
    assert data["is_reconciled"] is True
    assert len(data["factor_contributions"]) == 3

    # 2. Get latest factors
    res_get = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/factors")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["run_id"] == data["run_id"]

    # 3. Get security factor exposures
    res_exp = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/factors/exposures")
    assert res_exp.status_code == 200
    exposures = res_exp.json()
    assert len(exposures) >= 1

    # 4. Get factor risk contributions
    res_contrib = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/factors/contributions")
    assert res_contrib.status_code == 200
    contribs = res_contrib.json()
    assert len(contribs) == 3

    # 5. Get model diagnostics
    res_diag = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/factors/diagnostics")
    assert res_diag.status_code == 200
    diag = res_diag.json()
    assert diag["observation_count"] == 252
    assert diag["factor_count"] == 3
    assert diag["status"] in ("HEALTHY", "WARNING_COLLINEARITY")


def test_portfolio_concentration_endpoints(client_user_a, risk_services):
    """Verifies GET /api/v1/risk/portfolios/{id}/concentration and /concentration/issuers."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Concentration Test Portfolio",
            "base_currency": "USD",
            "description": "Concentration Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    # Security dimension
    res = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/concentration?dimension=SECURITY")
    assert res.status_code == 200
    data = res.json()
    assert data["dimension"] == "SECURITY"
    assert data["hhi"] > 0
    assert data["effective_number_of_holdings"] > 0
    assert data["top_1_weight"] > 0

    # Issuer dimension
    res_issuers = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/concentration/issuers")
    assert res_issuers.status_code == 200
    data_issuers = res_issuers.json()
    assert data_issuers["dimension"] == "ISSUER"


def test_portfolio_currency_endpoints(client_user_a, risk_services):
    """Verifies GET /api/v1/risk/portfolios/{id}/currencies, /exposures, and /sensitivity."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "FX Test Portfolio",
            "base_currency": "USD",
            "description": "FX Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    res = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/currencies")
    assert res.status_code == 200
    data = res.json()
    assert data["reporting_currency"] == "USD"
    assert "exposures" in data
    assert "base_local_interaction" in data

    res_exp = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/currencies/exposures")
    assert res_exp.status_code == 200
    exps = res_exp.json()
    assert len(exps) >= 1

    res_sens = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/currencies/sensitivity")
    assert res_sens.status_code == 200
    sens = res_sens.json()
    assert "base_local_interaction" in sens


def test_portfolio_sector_risk_endpoints(client_user_a, risk_services):
    """Verifies GET /api/v1/risk/portfolios/{id}/sectors and /sectors/contributions."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Sector Test Portfolio",
            "base_currency": "USD",
            "description": "Sector Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    res = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/sectors")
    assert res.status_code == 200
    data = res.json()
    assert data["portfolio_variance"] > 0
    assert data["is_reconciled"] is True
    assert len(data["sectors"]) >= 1

    res_contrib = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/sectors/contributions")
    assert res_contrib.status_code == 200
    secs = res_contrib.json()
    assert len(secs) >= 1


def test_cross_exposure_and_benchmark_endpoints(client_user_a, risk_services):
    """Verifies GET /api/v1/risk/portfolios/{id}/cross-exposures and /factor-benchmark."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Cross Exposure Portfolio",
            "base_currency": "USD",
            "description": "Cross Exposure Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    # Factor by Sector
    res_cross = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/cross-exposures?row_dimension=FACTOR&col_dimension=SECTOR")
    assert res_cross.status_code == 200
    cross = res_cross.json()
    assert cross["row_dimension"] == "FACTOR"
    assert cross["col_dimension"] == "SECTOR"
    assert len(cross["cells"]) > 0

    # Currency by Sector
    res_curr_sec = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/cross-exposures?row_dimension=CURRENCY&col_dimension=SECTOR")
    assert res_curr_sec.status_code == 200
    curr_sec = res_curr_sec.json()
    assert curr_sec["row_dimension"] == "CURRENCY"
    assert curr_sec["col_dimension"] == "SECTOR"

    # Factor benchmark comparison
    res_bench = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/factor-benchmark")
    assert res_bench.status_code == 200
    bench = res_bench.json()
    assert "portfolio_exposures" in bench
    assert "benchmark_exposures" in bench
    assert "active_factor_exposures" in bench


def test_multi_tenant_isolation(client_user_a, client_user_b, risk_services):
    """Verifies User B cannot access User A's factor risk, concentration, currency, or sector data."""
    p_service, _ = risk_services
    p_a = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "User A Proprietary Strategy",
            "base_currency": "USD",
            "description": "Private",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_a_id = p_a.id

    # User B attempting to access User A's endpoints -> HTTP 400 or 404
    res_factors = client_user_b.get(f"/api/v1/risk/portfolios/{p_a_id}/factors")
    assert res_factors.status_code in (400, 403, 404)

    res_conc = client_user_b.get(f"/api/v1/risk/portfolios/{p_a_id}/concentration")
    assert res_conc.status_code in (400, 403, 404)

    res_curr = client_user_b.get(f"/api/v1/risk/portfolios/{p_a_id}/currencies")
    assert res_curr.status_code in (400, 403, 404)

    res_sec = client_user_b.get(f"/api/v1/risk/portfolios/{p_a_id}/sectors")
    assert res_sec.status_code in (400, 403, 404)

    res_cross = client_user_b.get(f"/api/v1/risk/portfolios/{p_a_id}/cross-exposures")
    assert res_cross.status_code in (400, 403, 404)
