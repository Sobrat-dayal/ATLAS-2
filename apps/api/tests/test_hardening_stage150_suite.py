"""ATLAS Stage 150 Master Test Suite:

Production Hardening, System Integration, Readiness Gates, Security Audits,
Disaster Recovery Drills, and Trading Routers Integration.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.hardening.domain import (
    GateStatus,
    HealthStatus,
    ReadinessGate,
    ReadinessVerdict,
)
from atlas.hardening.service import ProductionHardeningService
from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app


@pytest.fixture()
def hardening_svc() -> ProductionHardeningService:
    return ProductionHardeningService(tenant_id="tenant-stage150-test")


@pytest.fixture()
def client() -> TestClient:
    test_principal = AuthPrincipal(
        sub="test-user-150",
        email="auditor@atlas.internal",
        role="admin",
        raw_claims={"tenant_id": "tenant-stage150-test"},
    )
    app.dependency_overrides[get_current_user] = lambda: test_principal
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


# ===========================================================================
# 1. Domain & Service Unit Tests
# ===========================================================================


def test_system_health_probes(hardening_svc: ProductionHardeningService):
    report = hardening_svc.probe_system_health()
    assert report.overall_status in {HealthStatus.HEALTHY, HealthStatus.DEGRADED}
    assert report.financial_safety_active is True
    assert len(report.checks) >= 5

    names = [c.service_name for c in report.checks]
    assert "api_gateway" in names
    assert "financial_safety_firewall" in names
    assert "ai_model_gateway" in names
    assert "mcp_security_firewall" in names
    assert "package_security_manager" in names


def test_security_audit_policies(hardening_svc: ProductionHardeningService):
    report = hardening_svc.audit_security_policies()
    assert report.total_checks >= 8
    assert report.failed_checks == 0
    assert report.critical_vulnerabilities == 0
    assert report.high_vulnerabilities == 0
    assert report.financial_firewall_enforced is True
    assert report.ssrf_defense_enforced is True
    assert report.zip_slip_defense_enforced is True
    assert report.secret_scanning_enforced is True


def test_performance_benchmarks(hardening_svc: ProductionHardeningService):
    benchmarks = hardening_svc.benchmark_system_performance()
    assert len(benchmarks) >= 3

    for b in benchmarks:
        assert b.sample_size > 0
        assert b.latency_p50_ms > 0
        assert b.latency_p95_ms > 0
        assert b.meets_target is True
        assert b.error_rate_pct == 0.0


def test_disaster_recovery_drill(hardening_svc: ProductionHardeningService):
    drill = hardening_svc.simulate_disaster_recovery_drill(target_env="STAGING")
    assert drill.target_environment == "STAGING"
    assert drill.records_verified > 0
    assert drill.integrity_checksum_match is True
    assert drill.replay_side_effects_suppressed is True  # Zero duplicate orders
    assert drill.passed is True


def test_readiness_gates_evaluation(hardening_svc: ProductionHardeningService):
    # Case A: Unauthorized release
    unauth_report = hardening_svc.evaluate_readiness_gates(production_authorization_granted=False)
    assert unauth_report.verdict == ReadinessVerdict.AWAITING_AUTHORIZATION
    assert len(unauth_report.evaluated_gates) == 10
    assert len(unauth_report.critical_blockers) == 1  # awaiting signoff

    # Case B: Authorized release
    auth_report = hardening_svc.evaluate_readiness_gates(
        production_authorization_granted=True,
        authorized_by="Lead Systems Architect",
    )
    assert auth_report.verdict == ReadinessVerdict.GO
    assert auth_report.readiness_score == 100.0
    assert len(auth_report.critical_blockers) == 0


def test_150_stage_audit_matrix_completeness(hardening_svc: ProductionHardeningService):
    matrix = hardening_svc.generate_150_stage_audit_matrix()
    assert len(matrix) >= 20
    stage_numbers = [s.stage_number for s in matrix]
    assert 1 in stage_numbers
    assert 120 in stage_numbers
    assert 143 in stage_numbers
    assert 144 in stage_numbers
    assert 145 in stage_numbers
    assert 146 in stage_numbers
    assert 147 in stage_numbers
    assert 148 in stage_numbers
    assert 149 in stage_numbers
    assert 150 in stage_numbers


# ===========================================================================
# 2. System Hardening REST Endpoints
# ===========================================================================


def test_http_system_health(client: TestClient):
    resp = client.get("/api/v1/system/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["financial_safety_active"] is True
    assert isinstance(data["checks"], list)
    assert len(data["checks"]) >= 5


def test_http_security_audit(client: TestClient):
    resp = client.get("/api/v1/system/security-audit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["critical_vulnerabilities"] == 0
    assert data["financial_firewall_enforced"] is True
    assert data["ssrf_defense_enforced"] is True
    assert data["zip_slip_defense_enforced"] is True


def test_http_performance_benchmarks(client: TestClient):
    resp = client.get("/api/v1/system/benchmarks")
    assert resp.status_code == 200
    bms = resp.json()
    assert len(bms) >= 3
    assert all(b["meets_target"] for b in bms)


def test_http_disaster_recovery_drill(client: TestClient):
    # Target env must be STAGING or ISOLATED_TEST
    invalid_resp = client.post("/api/v1/system/dr-drill", json={"target_environment": "PRODUCTION"})
    assert invalid_resp.status_code == 400

    valid_resp = client.post("/api/v1/system/dr-drill", json={"target_environment": "STAGING"})
    assert valid_resp.status_code == 200
    drill = valid_resp.json()
    assert drill["passed"] is True
    assert drill["integrity_checksum_match"] is True


def test_http_stage_audit_matrix(client: TestClient):
    resp = client.get("/api/v1/system/stage-audit")
    assert resp.status_code == 200
    matrix = resp.json()
    assert len(matrix) >= 20


def test_http_readiness_lifecycle(client: TestClient):
    # Check baseline status
    r0 = client.get("/api/v1/system/readiness")
    assert r0.status_code == 200
    assert r0.json()["verdict"] in ["AWAITING_AUTHORIZATION", "GO"]

    # Invalid authorization phrase rejected
    bad_auth = client.post(
        "/api/v1/system/readiness/authorize",
        json={
            "signatory_name": "Chief Architect",
            "signatory_title": "CTO",
            "confirmation_phrase": "WRONG_PHRASE",
        },
    )
    assert bad_auth.status_code == 400

    # Valid authorization
    good_auth = client.post(
        "/api/v1/system/readiness/authorize",
        json={
            "signatory_name": "Chief Architect",
            "signatory_title": "CTO",
            "confirmation_phrase": "CONFIRM_STAGE_150_PRODUCTION_LAUNCH",
        },
    )
    assert good_auth.status_code == 200
    assert good_auth.json()["verdict"] == "GO"

    # Confirm updated readiness
    r1 = client.get("/api/v1/system/readiness")
    assert r1.status_code == 200
    assert r1.json()["verdict"] == "GO"
    assert r1.json()["production_authorization_granted"] is True


# ===========================================================================
# 3. Paper Trading & Broker Sandbox REST Integration
# ===========================================================================


def test_http_paper_trading_lifecycle(client: TestClient):
    # 1. Feed real-time quotes to paper book
    feed_resp = client.post(
        "/api/v1/trading/paper/feed",
        json={"symbol": "NVDA", "bid": 480.0, "ask": 480.50, "market_open": True},
    )
    assert feed_resp.status_code == 200

    # 2. Create paper account
    acc_resp = client.post(
        "/api/v1/trading/paper/accounts",
        json={"name": "Stage 150 Hardening Fund", "initial_cash": 250_000.0, "currency": "USD"},
    )
    assert acc_resp.status_code == 201
    acc_id = acc_resp.json()["account_id"]
    assert acc_resp.json()["cash_balance"] == 250_000.0

    # 3. List accounts
    list_resp = client.get("/api/v1/trading/paper/accounts")
    assert list_resp.status_code == 200
    assert any(a["account_id"] == acc_id for a in list_resp.json())

    # 4. Submit simulated market buy order
    ord_resp = client.post(
        "/api/v1/trading/paper/accounts/" + acc_id + "/orders",
        json={
            "symbol": "NVDA",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 10.0,
        },
    )
    assert ord_resp.status_code == 201
    order = ord_resp.json()
    assert order["symbol"] == "NVDA"
    assert order["status"] == "FILLED"
    assert order["filled_quantity"] == 10.0

    # 5. Check updated positions
    pos_resp = client.get("/api/v1/trading/paper/accounts/" + acc_id + "/positions")
    assert pos_resp.status_code == 200
    positions = pos_resp.json()
    assert any(p["symbol"] == "NVDA" and p["quantity"] == 10.0 for p in positions)

    # 6. Activate kill switch
    ks_resp = client.post(
        "/api/v1/trading/paper/accounts/" + acc_id + "/kill-switch",
        json={"reason": "Stage 150 Verification Emergency Stop Test"},
    )
    assert ks_resp.status_code == 200
    assert ks_resp.json()["kill_switch_active"] is True

    # 7. Verify subsequent orders are blocked by kill switch
    blocked_ord = client.post(
        "/api/v1/trading/paper/accounts/" + acc_id + "/orders",
        json={
            "symbol": "NVDA",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 5.0,
        },
    )
    assert blocked_ord.status_code == 400
    err_body = blocked_ord.json()
    err_msg = err_body.get("detail") or err_body.get("error", {}).get("message", "")
    assert "kill switch" in err_msg.lower()


def test_http_broker_sandbox_lifecycle(client: TestClient):
    # 1. List supported sandbox broker providers
    prov_resp = client.get("/api/v1/trading/brokers/providers")
    assert prov_resp.status_code == 200
    providers = prov_resp.json()
    assert len(providers) >= 3
    p_ids = [p["provider_id"] for p in providers]
    assert "ALPACA_PAPER" in p_ids

    # 2. Create sandbox connection
    conn_resp = client.post(
        "/api/v1/trading/brokers/connections",
        json={
            "provider_id": "ALPACA_PAPER",
            "secret": "sandbox-key-secret-150",
            "account_id": "alpaca-paper-001",
            "display_name": "Alpaca Sandbox Integration",
        },
    )
    assert conn_resp.status_code == 201
    conn_id = conn_resp.json()["connection_id"]
    assert conn_resp.json()["environment"] == "SANDBOX"

    # 3. Verify sandbox connection
    verify_resp = client.post("/api/v1/trading/brokers/connections/" + conn_id + "/verify")
    assert verify_resp.status_code == 200
    assert verify_resp.json()["status"] == "VERIFIED_WITH_MOCK"

    # 4. Preview order through sandbox execution gateway
    prev_resp = client.post(
        "/api/v1/trading/brokers/orders/preview",
        json={
            "connection_id": conn_id,
            "symbol": "MSFT",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": 10.0,
            "limit_price": 415.0,
        },
    )
    assert prev_resp.status_code == 200
    assert prev_resp.json()["sandbox_environment"] is True

    # 5. Submit simulated order through sandbox gateway
    submit_resp = client.post(
        "/api/v1/trading/brokers/orders/submit",
        json={
            "connection_id": conn_id,
            "symbol": "MSFT",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": 10.0,
            "limit_price": 415.0,
        },
    )
    assert submit_resp.status_code == 201
    assert submit_resp.json()["is_sandbox"] is True
    assert submit_resp.json()["symbol"] == "MSFT"
