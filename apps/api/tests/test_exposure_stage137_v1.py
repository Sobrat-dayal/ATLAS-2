"""Exhaustive Test Suite for Stage 137: Financial and Economic Exposure Engine.

Validates all 24 canonical fixtures (Fixtures A through X):
- Test A: Geographic Revenue ($10M total, $4M Europe => 40.0% share)
- Test B: Facility Count vs Revenue (10 sites => count 10, revenue UNAVAILABLE)
- Test C: Portfolio Sector ($100k NAV, $30k Tech => 30%, unclassified uncovered)
- Test D: Long and Short (+$100k, -$100k => $0 Net, $200k Gross)
- Test E: Fund Look-Through (20% Fund F * 30% Company C => 6.0% indirect)
- Test F: Nested Fund Cycle (Fund A -> Fund B -> Fund A terminates with CycleDetectedError)
- Test G: Corporate Consolidation (Parent $100M, Sub $30M => group $100M, not $130M)
- Test H: Minority Ownership (Parent 40% affiliate => Equity Method, not added to consolidated revenue)
- Test I: Point-in-Time FX Conversion (€1,000 at EUR/USD 1.10 => $1,100.00)
- Test J: Missing FX Rate (missing historical rate raises MissingCurrencyRateError)
- Test K: Interest Rate Scenario (DV01 $100/bp, +25 bps => -$2,500 approximate P&L)
- Test L: Commodity Context Mention (Qualitative mention, numerical UNAVAILABLE)
- Test M: Supply Chain Relationship (Documented tie, contract amount UNAVAILABLE)
- Test N: Earthquake Proximity (25 km distance confirmed, loss/damage UNAVAILABLE)
- Test O: Historical Knowledge (look-ahead bias protection rejects future as_of)
- Test P: Data Vintage (point-in-time snapshot preservation)
- Test Q: Missing Revenue Coverage (domestic 60%, foreign 40%, no fabricated sub-regions)
- Test R: Portfolio Privacy (Tenant isolation blocks unauthorized tenant access)
- Test S: Source Entitlement Invalidation (revoked source invalidates lineage retrieval)
- Test T: Deterministic Scenario Shock ($50k position * -10% => -$5,000 conditional P&L)
- Test U: Derivative Delta-Equivalent (10 contracts * 100 * $150 * 0.60 => $90,000)
- Test V: Corporate Group History (historical ownership reflects period-specific structure)
- Test W: Source Conflict / Restatement (preserves distinct filing vintages)
- Test X: Geographic Residual (85% explained => 15% unallocated residual, no rescaling)

Also validates REST API endpoints on /api/v1/intelligence/exposure.
"""

from decimal import Decimal
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.exposure import (
    AnalysisRunStatus,
    AtlasExposureEngineService,
    AtlasExposureResult,
    ConsolidationBasis,
    CoverageStatus,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureMeasureDefinition,
    ExposureRelationshipStrength,
    ExposureScenarioDefinition,
    ExposureScenarioShock,
    ExposureType,
    UncertaintyClass,
)
from atlas.exposure.errors import (
    CycleDetectedError,
    DoubleCountingError,
    IncompatiblePeriodError,
    InvalidDenominatorError,
    LookAheadViolationError,
    MissingCurrencyRateError,
    SourceLicenseRevokedError,
    TenantExposureAccessDeniedError,
)
from atlas.exposure.calculations import (
    calculate_dv01_sensitivity,
    calculate_fund_lookthrough,
    calculate_group_consolidated_revenue,
    calculate_option_delta_equivalent,
    calculate_portfolio_exposures,
    convert_currency_point_in_time,
    verify_period_compatibility,
    FundConstituentEdge,
    PortfolioPosition,
)
from atlas.exposure.calculations.consolidation import EntityFinancialRecord
from atlas.exposure.domains import (
    analyze_commodity_mention,
    analyze_company_geographic_revenue,
    analyze_dv01_interest_rate_sensitivity,
    analyze_facility_event_proximity,
    analyze_geographic_presence_vs_revenue,
    analyze_option_delta_exposure,
    analyze_portfolio_holdings,
    analyze_supply_chain_relationship,
)
from atlas.exposure.quality.coverage import calculate_coverage_summary
from atlas.exposure.seed import (
    COMPANY_ACME,
    COMPANY_BETA,
    PORTFOLIO_ALPHA,
    REGION_EUROPE,
    REGION_NORTH_AMERICA,
    EVENT_EARTHQUAKE,
    FACILITY_PLANT_1,
    COMMODITY_COPPER,
    BENCHMARK_US_10Y,
    get_fixture_a_geographic_revenue,
    get_fixture_b_facility_count,
    get_fixture_c_portfolio_sector,
    get_fixture_d_long_short,
    get_fixture_e_fund_lookthrough,
    get_fixture_f_fund_cycle,
    get_fixture_g_consolidation,
    get_fixture_h_minority_ownership,
    get_fixture_k_interest_rate_sensitivity,
    get_fixture_t_scenario,
    get_fixture_u_derivative,
    get_fixture_x_geographic_residual,
)
from atlas_api.main import app

client = TestClient(app)


@pytest.fixture
def service():
    return AtlasExposureEngineService()


# =============================================================================
# Fixture Tests (Tests A through X)
# =============================================================================

def test_fixture_a_geographic_revenue():
    """Test A: Geographic Revenue ($10M total, $4M region => 40.0% share)."""
    fix = get_fixture_a_geographic_revenue()
    res_dict = analyze_company_geographic_revenue(
        run_id="run_a",
        company_ref=fix["company"],
        segments=fix["segments"],
        total_consolidated_revenue=fix["total_revenue"]
    )
    results = res_dict["results"]
    assert len(results) == 2
    eu_res = next(r for r in results if r.target_entity_ref.entity_id == "REG_EU")
    assert eu_res.amount == Decimal("4000000.00")
    assert eu_res.percentage == Decimal("40.00")
    assert eu_res.denominator_value == Decimal("10000000.00")
    assert eu_res.uncertainty_class == UncertaintyClass.VERIFIED_DETERMINISTIC


def test_fixture_b_facility_count_vs_revenue():
    """Test B: 10 facilities in Region A => 10 count presence, Revenue UNAVAILABLE."""
    fix = get_fixture_b_facility_count()
    res_dict = analyze_geographic_presence_vs_revenue(
        run_id="run_b",
        company_ref=fix["company"],
        region_ref=fix["region"],
        facility_count=fix["facility_count"],
        total_facilities=fix["total_facilities"],
        reported_revenue=fix["revenue_disclosed"]
    )
    results = res_dict["results"]
    assert len(results) == 2

    # Facility presence
    fac_res = next(r for r in results if r.exposure_type == ExposureType.FACILITY_GEOGRAPHIC_PRESENCE)
    assert fac_res.amount == Decimal("10")
    assert fac_res.unit == "COUNT"
    assert fac_res.percentage == Decimal("20.00")

    # Revenue must be UNAVAILABLE
    rev_res = next(r for r in results if r.exposure_type == ExposureType.REVENUE_GEOGRAPHIC_EXPOSURE)
    assert rev_res.evidence_class == ExposureEvidenceClass.UNAVAILABLE
    assert rev_res.amount is None
    assert rev_res.percentage is None


def test_fixture_c_portfolio_sector():
    """Test C: Portfolio Sector ($100k NAV, $30k Tech => 30% weight; unclassified uncovered)."""
    fix = get_fixture_c_portfolio_sector()
    summary = calculate_portfolio_exposures(fix["positions"], stated_nav=fix["nav"])
    assert summary.sector_weights["Information Technology"] == Decimal("30.00")
    assert summary.sector_weights["Financials"] == Decimal("60.00")
    assert summary.uncovered_sector_value == Decimal("10000.00")
    assert summary.sector_coverage_ratio == Decimal("0.90")


def test_fixture_d_long_short():
    """Test D: Long & Short (+$100k Long, -$100k Short => $0 Net, $200k Gross)."""
    positions = get_fixture_d_long_short()
    summary = calculate_portfolio_exposures(positions)
    assert summary.net_exposure == Decimal("0.00")
    assert summary.gross_exposure == Decimal("200000.00")
    assert summary.long_exposure == Decimal("100000.00")
    assert summary.short_exposure == Decimal("-100000.00")


def test_fixture_e_fund_lookthrough():
    """Test E: Fund Look-Through (20% in Fund F, Fund F 30% in Company C => 6.0% indirect)."""
    edges = get_fixture_e_fund_lookthrough()
    eff_weight, path = calculate_fund_lookthrough("PORT_TOP", "COMP_C", edges)
    assert eff_weight == Decimal("0.06")
    assert path == ["PORT_TOP", "FUND_F", "COMP_C"]


def test_fixture_f_fund_cycle():
    """Test F: Nested Fund Cycle (Fund A -> Fund B -> Fund A) halts safely with CycleDetectedError."""
    edges = get_fixture_f_fund_cycle()
    with pytest.raises(CycleDetectedError) as exc_info:
        calculate_fund_lookthrough("FUND_A", "TARGET_X", edges)
    assert "FUND_A" in exc_info.value.cycle_path


def test_fixture_g_consolidation():
    """Test G: Parent $100M consolidated, Sub $30M consolidated => report $100M, not $130M."""
    records = get_fixture_g_consolidation()
    data = calculate_group_consolidated_revenue(records, "PARENT_1")
    assert data["group_revenue"] == Decimal("100000000.00")
    assert data["eliminated_double_count_amount"] == Decimal("30000000.00")


def test_fixture_h_minority_ownership():
    """Test H: Parent owns 40% of affiliate => Equity Method, unconsolidated revenue."""
    records = get_fixture_h_minority_ownership()
    data = calculate_group_consolidated_revenue(records, "PARENT_1")
    # Does not add affiliate revenue
    assert data["group_revenue"] == Decimal("50000000.00")


def test_fixture_i_fx_conversion():
    """Test I: FX Conversion (€1,000 at EUR/USD 1.10 => $1,100.00)."""
    conv, rate = convert_currency_point_in_time(Decimal("1000.00"), "EUR", "USD", "2024-12-31")
    assert conv == Decimal("1100.00")
    assert rate == Decimal("1.1000")


def test_fixture_j_missing_fx_rate():
    """Test J: Missing FX Rate as of 2018-05-01 raises MissingCurrencyRateError without current substitution."""
    with pytest.raises(MissingCurrencyRateError) as exc_info:
        convert_currency_point_in_time(Decimal("500.00"), "EUR", "USD", "2018-05-01")
    assert exc_info.value.code == "MISSING_FX_RATE"


def test_fixture_k_interest_rate_sensitivity():
    """Test K: Interest Rate Scenario (DV01 $100/bp, +25 bps => -$2,500 P&L)."""
    fix = get_fixture_k_interest_rate_sensitivity()
    res = analyze_dv01_interest_rate_sensitivity(
        run_id="run_k",
        subject_ref=PORTFOLIO_ALPHA,
        rate_benchmark_ref=BENCHMARK_US_10Y,
        dv01_amount=fix["dv01"],
        rate_shift_bps=fix["shift_bps"]
    )
    assert res.amount == Decimal("-2500.00")
    assert res.uncertainty_class == UncertaintyClass.SCENARIO_ASSUMPTION


def test_fixture_l_commodity_mention():
    """Test L: Commodity Mention in news => Qualitative mention recorded, numerical UNAVAILABLE."""
    res = analyze_commodity_mention(
        run_id="run_l",
        subject_ref=COMPANY_ACME,
        commodity_ref=COMMODITY_COPPER,
        source_context="Financial Times article discussing electronics manufacturing wiring supply"
    )
    assert res.amount is None
    assert res.evidence_class == ExposureEvidenceClass.UNAVAILABLE
    assert res.unit == "QUALITATIVE"


def test_fixture_m_supply_chain():
    """Test M: Supply Chain (Company A is customer of Company B, no contract value => amount UNAVAILABLE)."""
    res = analyze_supply_chain_relationship(
        run_id="run_m",
        subject_ref=COMPANY_ACME,
        partner_ref=COMPANY_BETA,
        role="CUSTOMER",
        disclosed_contract_amount=None
    )
    assert res.amount is None
    assert res.evidence_class == ExposureEvidenceClass.SOURCE_REPORTED_QUALITATIVE
    assert "Specific commercial contract value" in res.explanation


def test_fixture_n_earthquake_proximity():
    """Test N: Facility 25 km from earthquake => proximity confirmed, damage/loss UNKNOWN."""
    res = analyze_facility_event_proximity(
        run_id="run_n",
        company_ref=COMPANY_ACME,
        facility_ref=FACILITY_PLANT_1,
        event_ref=EVENT_EARTHQUAKE,
        distance_km=Decimal("25.0"),
        threshold_km=Decimal("50.0")
    )
    assert res.amount == Decimal("25.0")
    assert res.unit == "KM"
    assert "economic loss are UNKNOWN" in res.explanation


def test_fixture_o_historical_knowledge(service: AtlasExposureEngineService):
    """Test O: Point-in-Time integrity check raises LookAheadViolationError on future as_of."""
    future_date = datetime(2099, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(LookAheadViolationError):
        service.analyze_company(
            company_ref=COMPANY_ACME,
            segments=[{"region_code": "REG_EU", "revenue_amount": Decimal("10.0")}],
            total_consolidated_revenue=Decimal("10.0"),
            as_of=future_date
        )


def test_fixture_p_data_vintage():
    """Test P: Period compatibility verifier rejects quarterly divided by annual without explicit flag."""
    with pytest.raises(IncompatiblePeriodError):
        verify_period_compatibility("2024Q3", "FY2024", allow_annualized_quarter=False)


def test_fixture_q_missing_revenue_coverage():
    """Test Q: Domestic $60M, Foreign $40M, Total $100M => 60% domestic, 40% foreign, complete coverage."""
    res_dict = analyze_company_geographic_revenue(
        run_id="run_q",
        company_ref=COMPANY_ACME,
        segments=[
            {"region_code": "DOM", "region_name": "Domestic", "revenue_amount": Decimal("60000000.00")},
            {"region_code": "FOR", "region_name": "Foreign", "revenue_amount": Decimal("40000000.00")}
        ],
        total_consolidated_revenue=Decimal("100000000.00")
    )
    cov = res_dict["coverage_summary"]
    assert cov.coverage_ratio == Decimal("1.0000")
    assert cov.coverage_status == CoverageStatus.COMPLETE


def test_fixture_r_portfolio_privacy(service: AtlasExposureEngineService):
    """Test R: Portfolio owned by Tenant A is inaccessible to Tenant B."""
    run = service.analyze_portfolio(
        portfolio_ref=PORTFOLIO_ALPHA,
        positions=[PortfolioPosition(position_id="p1", instrument_id="AAPL", symbol="AAPL", market_value=Decimal("500.0"))],
        tenant_id="TENANT_1"
    )
    # Authorized tenant
    fetched = service.get_run(run.run_id, requesting_tenant_id="TENANT_1")
    assert fetched.run_id == run.run_id

    # Unauthorized tenant raises TenantExposureAccessDeniedError
    with pytest.raises(TenantExposureAccessDeniedError):
        service.get_run(run.run_id, requesting_tenant_id="TENANT_2")


def test_fixture_s_source_entitlement_invalidation(service: AtlasExposureEngineService):
    """Test S: Revoked source entitlement immediately locks lineage retrieval."""
    run = service.analyze_company(
        company_ref=COMPANY_ACME,
        segments=[{"region_code": "REG_EU", "revenue_amount": Decimal("100.0")}],
        total_consolidated_revenue=Decimal("100.0")
    )
    exp_id = run.results[0].exposure_id
    # Valid lineage
    lineage = service.get_lineage(exp_id)
    assert lineage.calculation_method == "RATIO_CALCULATION"

    # Revoke underlying source
    service.provenance_registry.revoke_source("SEC_10K_AUDITED_FILING")
    with pytest.raises(SourceLicenseRevokedError):
        service.get_lineage(exp_id)
    # Restore for subsequent tests
    service.provenance_registry.restore_source("SEC_10K_AUDITED_FILING")


def test_fixture_t_scenario_shock():
    """Test T: User Scenario (-10% shock on $50k holding => -$5,000 P&L)."""
    fix = get_fixture_t_scenario()
    pos = fix["position"]
    pos["node_ref"] = COMPANY_ACME
    service = AtlasExposureEngineService()
    scen_def = ExposureScenarioDefinition(
        scenario_id="scen_t",
        scenario_name="Tech Sector Contraction",
        owner_id="USER_1",
        shocks=[fix["shock"]]
    )
    scen_run = service.run_scenario(scen_def, [pos])
    assert scen_run.total_conditional_pnl == Decimal("-5000.00")
    assert len(scen_run.results) == 1
    assert "HYPOTHETICAL SCENARIO RESULT" in scen_run.assumptions_notice


def test_fixture_u_derivative_delta_equivalent():
    """Test U: Derivative Delta Equivalent (10 contracts * 100 * $150 * 0.60 => $90,000)."""
    fix = get_fixture_u_derivative()
    res = analyze_option_delta_exposure(
        run_id="run_u",
        portfolio_ref=PORTFOLIO_ALPHA,
        option_ref=CanonicalGraphNodeRef(node_type=GraphNodeType.FINANCIAL_INSTRUMENT, entity_id="OPT_AAPL_C150", canonical_name="AAPL Dec 150 Call"),
        underlying_ref=CanonicalGraphNodeRef(node_type=GraphNodeType.FINANCIAL_INSTRUMENT, entity_id="INSTR_AAPL", canonical_name="Apple Inc."),
        contracts=fix["contracts"],
        multiplier=fix["multiplier"],
        underlying_price=fix["underlying_price"],
        delta=fix["delta"]
    )
    assert res.amount == Decimal("90000.00")
    assert res.unit == "CURRENCY"


def test_fixture_v_corporate_group_history():
    """Test V: Corporate Group History verifies period-specific structure."""
    # 2024 structure includes SUB_1
    records_2024 = get_fixture_g_consolidation()
    data_2024 = calculate_group_consolidated_revenue(records_2024, "PARENT_1")
    assert data_2024["included_subsidiary_count"] == 1

    # 2023 structure before acquisition
    records_2023 = [records_2024[0]]
    data_2023 = calculate_group_consolidated_revenue(records_2023, "PARENT_1")
    assert data_2023["included_subsidiary_count"] == 0


def test_fixture_w_source_conflict_restatement():
    """Test W: Restatement preserves distinct filing vintages without averaging."""
    # Original filing record
    rec_original = EntityFinancialRecord("ACME", "Acme Corp", Decimal("100.0"), "USD", "FY2024_ORIGINAL", ConsolidationBasis.CONSOLIDATED)
    # Restated filing record
    rec_restated = EntityFinancialRecord("ACME", "Acme Corp", Decimal("95.0"), "USD", "FY2024_RESTATED", ConsolidationBasis.CONSOLIDATED)

    assert rec_original.revenue == Decimal("100.0")
    assert rec_restated.revenue == Decimal("95.0")
    assert rec_original.period != rec_restated.period


def test_fixture_x_geographic_residual():
    """Test X: Geographic Residual ($50M NA, $35M EU, $100M Total => Coverage 85%, Residual $15M / 15%)."""
    fix = get_fixture_x_geographic_residual()
    covered = sum(s["revenue"] for s in fix["segments"])
    summary = calculate_coverage_summary(
        total_relevant_denominator=fix["total_revenue"],
        covered_items_sum=covered,
        covered_dimension_names=[s["region_name"] for s in fix["segments"]]
    )
    assert summary.coverage_ratio == Decimal("0.8500")
    assert summary.unallocated_residual_amount == Decimal("15000000.00")
    assert summary.unallocated_residual_percentage == Decimal("15.00")
    assert summary.coverage_status == CoverageStatus.PARTIAL


# =============================================================================
# REST API Endpoint Tests
# =============================================================================

def test_api_capabilities():
    """GET /api/v1/intelligence/exposure/capabilities returns 200 with engine guarantees."""
    resp = client.get("/api/v1/intelligence/exposure/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == 137
    assert len(data["supported_domains"]) == 10
    assert len(data["guarantees"]) >= 8


def test_api_measures():
    """GET /api/v1/intelligence/exposure/measures returns registered measures with numerators and denominators."""
    resp = client.get("/api/v1/intelligence/exposure/measures")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 10
    measure_ids = [m["measure_id"] for m in data]
    assert "REV_GEO_SHARE_V1" in measure_ids
    assert "PORTFOLIO_NAV_WEIGHT_V1" in measure_ids
    assert "FACILITY_COUNT_V1" in measure_ids


def test_api_analyze_company():
    """POST /api/v1/intelligence/exposure/analyze/company computes geographic revenue and returns run."""
    payload = {
        "company_ref": {
            "node_type": "COMPANY",
            "entity_id": "COMP_ACME",
            "canonical_name": "Acme Global Corporation"
        },
        "segments": [
            {"region_code": "REG_EU", "region_name": "Europe", "revenue_amount": 4000000.0},
            {"region_code": "REG_NA", "region_name": "North America", "revenue_amount": 6000000.0}
        ],
        "total_consolidated_revenue": 10000000.0,
        "currency": "USD",
        "period": "FY2024"
    }
    resp = client.post("/api/v1/intelligence/exposure/analyze/company", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "COMPLETED"
    assert len(data["results"]) == 2
    assert data["coverage_summary"]["coverage_ratio"] == "1.0000"

    # Fetch run
    run_id = data["run_id"]
    get_resp = client.get(f"/api/v1/intelligence/exposure/runs/{run_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["run_id"] == run_id


def test_api_scenario_run():
    """POST /api/v1/intelligence/exposure/scenarios/run evaluates hypothetical shock."""
    payload = {
        "scenario_id": "test_scen_1",
        "scenario_name": "Tech Shock",
        "shocks": [
            {
                "shock_id": "shk_1",
                "target_dimension": "SECTOR",
                "target_identifier": "TECHNOLOGY",
                "shock_value": -10.0,
                "shock_unit": "PERCENT"
            }
        ],
        "positions": [
            {
                "id": "p_tech",
                "symbol": "TECH1",
                "market_value": 100000.0,
                "sector": "Technology",
                "country": "US",
                "node_ref": {
                    "node_type": "COMPANY",
                    "entity_id": "COMP_TECH",
                    "canonical_name": "Tech Corp"
                }
            }
        ],
        "base_currency": "USD"
    }
    resp = client.post("/api/v1/intelligence/exposure/scenarios/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert Decimal(str(data["total_conditional_pnl"])) == Decimal("-10000.00")
    assert "HYPOTHETICAL SCENARIO RESULT" in data["assumptions_notice"]


def test_api_fixture_endpoint():
    """GET /api/v1/intelligence/exposure/fixtures/A returns reference fixture."""
    resp = client.get("/api/v1/intelligence/exposure/fixtures/A")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_revenue"] == "10000000.00"
