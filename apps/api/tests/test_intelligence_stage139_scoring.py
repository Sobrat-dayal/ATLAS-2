"""Comprehensive Institutional Test Suite for ATLAS Stage 139: Intelligence Scoring.

Verifies:
- All 19 Canonical Reference Test Fixtures (Fixtures A through S)
- Strict mathematical explainability (factor contributions sum exactly to score)
- Bitemporal known_as_of horizon (zero look-ahead leakage)
- Anti-gaming (syndicated news duplication does not inflate corroboration)
- Source conflict preservation and penalty
- Multi-tenant portfolio attention privacy isolation
- Model governance (approval gates, rollback, and audit log)
- REST API endpoints under /api/v1/intelligence/scoring/*
"""

import pytest
from fastapi.testclient import TestClient

from atlas_api.main import app
from atlas.intelligence.scoring import (
    AtlasScoringService,
    CalibrationMetrics,
    ModelEvaluator,
    ModelGovernanceManager,
    RankingMetrics,
    ScoreObjectiveId,
    ScoreStatus,
    ScoringLookAheadViolationError,
    ScoringModelValidationError,
    ScoringQuotaExceededError,
    ScoringTenantAccessDeniedError,
    ScoringUnauthorizedActivationError,
)

client = TestClient(app)
svc = AtlasScoringService()


# -------------------------------------------------------------------------
# Fixture A: Direct Relevance (Part C, Paragraph 290)
# -------------------------------------------------------------------------
def test_fixture_a_direct_relevance():
    """Event E: Verified earnings announcement. Issuer I: Directly identified by official source.

    Expected: System recognizes direct issuer relevance. Does not invent price impact.
    """
    event = {
        "event_id": "evt_aapl_q4",
        "title": "Apple Inc. Q4 Form 10-K Filed",
        "published_at": "2024-10-31T20:30:00Z",
        "entities": [{"entity_id": "COMP_AAPL", "predicate": "ISSUED_BY"}],
        "sources": [{"source_id": "src_sec", "name": "SEC EDGAR", "source_type": "OFFICIAL_REGULATORY"}],
    }
    score = svc.calculate_score(
        event_data=event,
        objective_id="EVENT_ENTITY_RELEVANCE",
        context={"selected_entity_id": "COMP_AAPL"},
    )
    assert score.score_status == ScoreStatus.AVAILABLE
    assert score.score_value is not None
    assert score.score_value >= 80.0
    # Verify no price prediction claim in interpretation
    assert "stock" not in score.score_interpretation.lower()
    assert "price" not in score.score_interpretation.lower()
    # Direct match factor contribution must be positive
    direct_factor = next(f for f in score.factor_contributions if f.factor_id == "FEAT_DIRECT_ISSUER_MATCH")
    assert direct_factor.transformed_value == 1.0
    assert direct_factor.contribution_points > 0


# -------------------------------------------------------------------------
# Fixture B: Indirect Relevance (Part CI, Paragraph 291)
# -------------------------------------------------------------------------
def test_fixture_b_indirect_relevance():
    """Event E -> Subsidiary S -> Parent P.

    Expected: Direct relation to S, qualified indirect context for P, explicit path explanation.
    """
    event = {
        "event_id": "evt_sub_plant",
        "title": "Subsidiary Factory Incident",
        "published_at": "2024-10-30T10:00:00Z",
        "entities": [{"entity_id": "COMP_ACME_SUB", "predicate": "ISSUED_BY"}],
        "sources": [{"source_id": "src_local", "name": "Regional Press", "article_fingerprint": "wire_1"}],
    }
    # Query with Parent P as selected entity
    score = svc.calculate_score(
        event_data=event,
        objective_id="EVENT_ENTITY_RELEVANCE",
        context={"selected_entity_id": "COMP_ACME_PARENT"},
    )
    # Since direct issuer match fails for Parent P, direct factor is 0.0
    direct_factor = next(f for f in score.factor_contributions if f.factor_id == "FEAT_DIRECT_ISSUER_MATCH")
    assert direct_factor.transformed_value == 0.0


# -------------------------------------------------------------------------
# Fixture C: Portfolio Attention (Part CII, Paragraph 292)
# -------------------------------------------------------------------------
def test_fixture_c_portfolio_attention():
    """Portfolio P contains verified 20% NAV weight in Issuer I. Event E directly concerns Issuer I.

    Expected: Eligible for portfolio attention with holding weight factor. Does NOT infer 20% loss.
    """
    event = {
        "event_id": "evt_fed_hike",
        "title": "Federal Reserve Rate Increase",
        "published_at": "2024-11-01T18:00:00Z",
        "entities": [{"entity_id": "COMP_MSFT", "predicate": "ISSUED_BY"}],
        "sources": [{"source_id": "src_fed", "name": "Federal Reserve Bulletin", "source_type": "CENTRAL_BANK_BULLETIN"}],
    }
    score = svc.calculate_score(
        event_data=event,
        objective_id="PORTFOLIO_EVENT_ATTENTION",
        context={
            "selected_entity_id": "COMP_MSFT",
            "portfolio_context": {
                "portfolio_id": "PORT_TECH_ALPHA",
                "holding_weight_pct": 20.0,
                "tenant_id": "tenant_quant",
            },
        },
        tenant_id="tenant_quant",
    )
    assert score.score_status == ScoreStatus.AVAILABLE
    assert score.score_value is not None
    assert score.score_value >= 70.0
    # Explicit disclaimer check: must not mention loss probability
    assert "loss" not in score.score_interpretation.lower()


# -------------------------------------------------------------------------
# Fixture D: Portfolio Privacy (Part CIII, Paragraph 293)
# -------------------------------------------------------------------------
def test_fixture_d_portfolio_privacy():
    """User A owns Portfolio P. User B can view public Event E.

    Expected: User B cannot see Portfolio P attention score or private weights (raises access error).
    """
    event = {
        "event_id": "evt_public_news",
        "title": "Earnings Announcement",
        "published_at": "2024-11-01T12:00:00Z",
        "entities": [{"entity_id": "COMP_AAPL"}],
    }
    # Tenant B tries to compute attention for Tenant A's portfolio
    with pytest.raises(ScoringTenantAccessDeniedError):
        svc.calculate_score(
            event_data=event,
            objective_id="PORTFOLIO_EVENT_ATTENTION",
            context={
                "portfolio_context": {
                    "portfolio_id": "PORT_PRIVATE_USER_A",
                    "tenant_id": "tenant_user_a",
                    "holding_weight_pct": 15.0,
                }
            },
            tenant_id="tenant_user_b",
        )


# -------------------------------------------------------------------------
# Fixture E: Article Duplication / Anti-Gaming (Part CIV, Paragraph 294)
# -------------------------------------------------------------------------
def test_fixture_e_article_duplication_anti_gaming():
    """Ten news records syndicate one original article.

    Expected: Deduplicates syndicated copies; does NOT count 10 independent corroborations.
    """
    # 10 syndicated wire articles with identical fingerprint
    sources = [
        {"source_id": f"wire_{i}", "name": f"Syndicated Outlet {i}", "article_fingerprint": "syndicated_story_xyz"}
        for i in range(10)
    ]
    event = {
        "event_id": "evt_syndicated",
        "title": "Syndicated Press Release",
        "published_at": "2024-11-02T10:00:00Z",
        "sources": sources,
    }
    score = svc.calculate_score(
        event_data=event,
        objective_id="EVENT_REVIEW_PRIORITY",
        known_as_of="2024-11-02T12:00:00Z",
    )
    src_factor = next(f for f in score.factor_contributions if f.factor_id == "FEAT_INDEPENDENT_SOURCE_COUNT")
    # Independent count must be 1, NOT 10!
    assert src_factor.raw_value == 1
    assert src_factor.transformed_value == 0.2  # 1 / 5 saturation cap = 0.2


# -------------------------------------------------------------------------
# Fixture F: Source Conflict (Part CV, Paragraph 295)
# -------------------------------------------------------------------------
def test_fixture_f_source_conflict():
    """Two valid sources report conflicting figures.

    Expected: Conflict preserved, conflict flag raised, no false high-confidence consensus.
    """
    event = {
        "event_id": "evt_conflicted",
        "title": "Disputed Revenue Restatement",
        "published_at": "2024-11-01T14:00:00Z",
        "has_conflicts": True,
        "sources": [
            {"source_id": "src_1", "name": "Agency A", "published_at": "2024-11-01T14:00:00Z"},
            {"source_id": "src_2", "name": "Agency B", "published_at": "2024-11-01T14:05:00Z"},
        ],
    }
    score = svc.calculate_score(event_data=event, objective_id="SOURCE_EVIDENCE_ASSESSMENT")
    assert score.uncertainty.has_source_conflicts is True
    assert len(score.uncertainty.conflict_notes) > 0


# -------------------------------------------------------------------------
# Fixture G: Data Coverage / Missing Features (Part CVI, Paragraph 296)
# -------------------------------------------------------------------------
def test_fixture_g_data_coverage_missing_features():
    """A policy requires multiple features. Some are missing.

    Expected: Explicit coverage ratio reported; never silently imputes 0 or synthetic mean.
    """
    # Event lacking proximity km and portfolio context
    event = {
        "event_id": "evt_sparse",
        "title": "Sparse Event Record",
        "published_at": "2024-11-01T10:00:00Z",
        "sources": [{"source_id": "s1", "name": "Feed"}],
    }
    score = svc.calculate_score(event_data=event, objective_id="GEOGRAPHIC_EVENT_RELEVANCE")
    # Distance is missing -> status should be PARTIAL or INSUFFICIENT_DATA
    assert score.uncertainty.coverage_ratio < 1.0
    assert "FEAT_PROXIMITY_KM" in score.uncertainty.missing_features


# -------------------------------------------------------------------------
# Fixture H: Future Information / Look-Ahead Bias (Part CVII, Paragraph 297)
# -------------------------------------------------------------------------
def test_fixture_h_look_ahead_bias_prevention():
    """Historical As-of: Jan 10. Source published: Jan 15.

    Expected: Future source rejected with LookAheadViolationError if event published after as-of.
    """
    event = {
        "event_id": "evt_future",
        "title": "Q4 Results Announced",
        "published_at": "2024-01-15T10:00:00Z",
    }
    with pytest.raises(ScoringLookAheadViolationError):
        svc.calculate_score(
            event_data=event,
            objective_id="EVENT_REVIEW_PRIORITY",
            known_as_of="2024-01-10T00:00:00Z",
        )


# -------------------------------------------------------------------------
# Fixture I: Model Revision & Versioning (Part CVIII, Paragraph 298)
# -------------------------------------------------------------------------
def test_fixture_i_model_versioning_and_comparison():
    """Scoring policy v1 and v2 have different factor weights.

    Expected: Different versioned scores with explicit factor contribution deltas.
    """
    event = {
        "event_id": "evt_version_test",
        "title": "SEC Regulatory Action",
        "published_at": "2024-11-01T08:00:00Z",
        "entities": [{"entity_id": "COMP_AAPL", "predicate": "TARGET_OF"}],
        "sources": [{"source_id": "sec_1", "name": "SEC EDGAR", "source_type": "OFFICIAL_REGULATORY"}],
    }
    comparison = svc.compare_models(
        event_data=event,
        version_a="v1.0.0",
        version_b="v2.0.0",
        objective_id="EVENT_REVIEW_PRIORITY",
        context={"selected_entity_id": "COMP_AAPL"},
        known_as_of="2024-11-01T12:00:00Z",
    )
    assert comparison.score_a.model_version == "v1.0.0"
    assert comparison.score_b.model_version == "v2.0.0"
    assert len(comparison.explanation_differences) >= 3


# -------------------------------------------------------------------------
# Fixture J: Model Rollback & Governance (Part CIX, Paragraph 299)
# -------------------------------------------------------------------------
def test_fixture_j_model_rollback():
    """Candidate policy v2 fails validation or unauthorized activation.

    Expected: Unauthorized user blocked; rollback restores approved version.
    """
    # Unauthorized activation attempt
    with pytest.raises(ScoringUnauthorizedActivationError):
        svc.activate_model_version(
            model_id="MOD_EVENT_PRIORITY",
            version="v2.0.0",
            user_id="junior_trader",
            user_roles=["GUEST"],
        )

    # Rollback execution by authorized RISK_ADMIN
    audit = svc.rollback_model_version(
        model_id="MOD_EVENT_PRIORITY",
        rollback_to_version="v1.0.0",
        user_id="risk_officer_1",
        user_roles=["RISK_ADMIN"],
    )
    assert audit.action == "ROLLBACK"
    assert audit.version == "v1.0.0"


# -------------------------------------------------------------------------
# Fixture K: Historical Portfolio Snapshot (Part CX, Paragraph 300)
# -------------------------------------------------------------------------
def test_fixture_k_historical_portfolio_holdings():
    """Portfolio holdings change after date T.

    Expected: Historical Portfolio Attention uses holdings snapshot valid at T.
    """
    event = {
        "event_id": "evt_holdings_test",
        "title": "Corporate Reorganization",
        "published_at": "2024-06-01T10:00:00Z",
        "entities": [{"entity_id": "COMP_AAPL"}],
    }
    # Score as of historical date T (holding weight was 25% at T, vs 5% today)
    score_hist = svc.calculate_score(
        event_data=event,
        objective_id="PORTFOLIO_EVENT_ATTENTION",
        context={
            "selected_entity_id": "COMP_AAPL",
            "portfolio_context": {
                "portfolio_id": "PORT_GROWTH",
                "holding_weight_pct": 25.0,
                "as_of": "2024-06-01T10:00:00Z",
            },
        },
        known_as_of="2024-06-01T12:00:00Z",
    )
    weight_factor = next(f for f in score_hist.factor_contributions if f.factor_id == "FEAT_PORTFOLIO_WEIGHT")
    assert weight_factor.raw_value == 25.0
    assert weight_factor.transformed_value == 1.0


# -------------------------------------------------------------------------
# Fixture L: Geographic Proximity (Part CXI, Paragraph 301)
# -------------------------------------------------------------------------
def test_fixture_l_geographic_proximity():
    """An earthquake occurs near a verified power plant (distance 12 km).

    Expected: Spatial relevance calculated; must NOT imply confirmed plant damage or company loss.
    """
    event = {
        "event_id": "evt_quake_fukushima",
        "title": "Magnitude 5.8 Seismic Activity",
        "published_at": "2024-11-01T04:00:00Z",
        "proximity_km": 12.0,
        "sources": [{"source_id": "usgs_1", "name": "USGS Seismic", "source_type": "OFFICIAL_GOVERNMENT"}],
    }
    score = svc.calculate_score(event_data=event, objective_id="GEOGRAPHIC_EVENT_RELEVANCE")
    assert score.score_status == ScoreStatus.AVAILABLE
    assert score.score_value is not None
    # Verify proximity step function: 12 km maps to 0.70
    prox_factor = next(f for f in score.factor_contributions if f.factor_id == "FEAT_PROXIMITY_KM")
    assert prox_factor.transformed_value == 0.70
    # Mandatory disclaimer verification
    assert any("not measure" in lim.lower() for lim in score.uncertainty.limitations)


# -------------------------------------------------------------------------
# Fixture M: Category Comparability (Part CXII, Paragraph 302)
# -------------------------------------------------------------------------
def test_fixture_m_category_comparability():
    """Earnings announcement and earthquake have different category policies.

    Expected: Distinct objectives, no misleading raw magnitude collapse.
    """
    obj_earnings = svc.get_objective("EVENT_REVIEW_PRIORITY")
    obj_geo = svc.get_objective("GEOGRAPHIC_EVENT_RELEVANCE")
    assert obj_earnings.target_construct != obj_geo.target_construct
    assert obj_geo.required_features != obj_earnings.required_features


# -------------------------------------------------------------------------
# Fixture N: Probabilistic Calibration Limits (Part CXIII, Paragraph 303)
# -------------------------------------------------------------------------
def test_fixture_n_probabilistic_calibration():
    """When evaluated against true binary labels, compute Brier score & ECE.

    If non-probabilistic ranking, mark calibration not applicable.
    """
    preds = [85.0, 70.0, 40.0, 20.0, 10.0]
    true_rel = [3.0, 2.0, 1.0, 0.0, 0.0]
    binary_labels = [1, 1, 0, 0, 0]

    manifest = ModelEvaluator.evaluate_model(
        model_id="MOD_EVENT_PRIORITY",
        model_version="v1.0.0",
        predicted_scores=preds,
        ground_truth_relevance=true_rel,
        binary_labels=binary_labels,
    )
    assert manifest.ndcg_at_10 is not None
    assert manifest.ndcg_at_10 >= 0.85
    assert manifest.brier_score is not None
    assert manifest.brier_score <= 0.15
    assert manifest.expected_calibration_error is not None


# -------------------------------------------------------------------------
# Fixture O: Source Retraction (Part CXIV, Paragraph 304)
# -------------------------------------------------------------------------
def test_fixture_o_source_retraction():
    """An official event is retracted.

    Expected: Relevant scores invalidated (NOT_APPLICABLE), score value is None.
    """
    event = {
        "event_id": "evt_rumour_retracted",
        "title": "Retracted Acquisition Claim",
        "status": "RETRACTED",
        "published_at": "2024-11-01T09:00:00Z",
    }
    score = svc.calculate_score(event_data=event, objective_id="EVENT_REVIEW_PRIORITY")
    assert score.score_status == ScoreStatus.NOT_APPLICABLE
    assert score.score_value is None
    assert "retracted" in score.score_interpretation.lower()


# -------------------------------------------------------------------------
# Fixture P: Quota & Resource Protection (Part CXV, Paragraph 305)
# -------------------------------------------------------------------------
def test_fixture_p_quota_protection():
    """User requests scoring of an excessive number of events (> 500).

    Expected: Bounded request raises ScoringQuotaExceededError.
    """
    excessive_events = [{"event_id": f"evt_{i}", "published_at": "2024-11-01T00:00:00Z"} for i in range(505)]
    with pytest.raises(ScoringQuotaExceededError):
        svc.rank_events(candidate_events=excessive_events, objective_id="EVENT_REVIEW_PRIORITY")


# -------------------------------------------------------------------------
# Fixture Q: Ranking Stability & Deterministic Tie-Breaking (Part CXVI, Paragraph 306)
# -------------------------------------------------------------------------
def test_fixture_q_deterministic_ranking_stability():
    """Identical candidate set, inputs, and model version.

    Expected: Deterministic scores, stable pagination, deterministic secondary tie-breaking.
    """
    candidates = [
        {
            "event_id": "evt_tie_b",
            "title": "Event B",
            "published_at": "2024-11-01T12:00:00Z",
            "valid_at": "2024-11-01T12:00:00Z",
            "entities": [{"entity_id": "COMP_AAPL", "predicate": "ISSUED_BY"}],
            "sources": [{"source_id": "s1", "name": "Newswire"}],
        },
        {
            "event_id": "evt_tie_a",
            "title": "Event A",
            "published_at": "2024-11-01T12:00:00Z",
            "valid_at": "2024-11-01T12:00:00Z",
            "entities": [{"entity_id": "COMP_AAPL", "predicate": "ISSUED_BY"}],
            "sources": [{"source_id": "s1", "name": "Newswire"}],
        },
    ]
    rank_run_1 = svc.rank_events(
        candidate_events=candidates,
        objective_id="EVENT_REVIEW_PRIORITY",
        context={"selected_entity_id": "COMP_AAPL"},
        known_as_of="2024-11-01T15:00:00Z",
    )
    rank_run_2 = svc.rank_events(
        candidate_events=candidates,
        objective_id="EVENT_REVIEW_PRIORITY",
        context={"selected_entity_id": "COMP_AAPL"},
        known_as_of="2024-11-01T15:00:00Z",
    )
    # Order must be strictly identical across runs (evt_tie_a before evt_tie_b by canonical tie-breaker)
    assert [r.score.event_id for r in rank_run_1] == [r.score.event_id for r in rank_run_2]
    assert rank_run_1[0].score.event_id == "evt_tie_a"
    assert rank_run_1[1].score.event_id == "evt_tie_b"


# -------------------------------------------------------------------------
# Fixture R: Missing Source License / Entitlement (Part CXVII, Paragraph 307)
# -------------------------------------------------------------------------
def test_fixture_r_missing_source_license():
    """Feature depends on data tenant cannot access.

    Expected: Restricted feature is omitted or marked without data leakage.
    """
    event = {
        "event_id": "evt_licensed",
        "title": "Licensed Data Feed Event",
        "published_at": "2024-11-01T10:00:00Z",
        "sources": [{"source_id": "premium_terminal_wire", "name": "Premium Source"}],
    }
    score = svc.calculate_score(event_data=event, objective_id="EVENT_REVIEW_PRIORITY")
    assert score.score_status in (ScoreStatus.AVAILABLE, ScoreStatus.PARTIAL)


# -------------------------------------------------------------------------
# Fixture S: Scoring Semantics (Part CXVIII, Paragraph 308)
# -------------------------------------------------------------------------
def test_fixture_s_scoring_semantics():
    """A high priority event has no validated financial impact prediction.

    Expected: Described as operational review priority, NOT probability of loss or price forecast.
    """
    event = {
        "event_id": "evt_urgent",
        "title": "Major Regulatory Investigation",
        "published_at": "2024-11-01T12:00:00Z",
        "entities": [{"entity_id": "COMP_AAPL", "predicate": "TARGET_OF"}],
        "sources": [
            {"source_id": "s1", "name": "Regulatory Agency", "source_type": "OFFICIAL_REGULATORY"},
            {"source_id": "s2", "name": "Global News", "article_fingerprint": "wire_reg_1"},
            {"source_id": "s3", "name": "Financial Times", "article_fingerprint": "wire_reg_2"},
        ],
    }
    score = svc.calculate_score(
        event_data=event,
        objective_id="EVENT_REVIEW_PRIORITY",
        context={"selected_entity_id": "COMP_AAPL"},
        known_as_of="2024-11-01T13:00:00Z",
    )
    assert score.score_value is not None
    assert score.score_value >= 80.0
    assert "URGENT_REVIEW" in score.score_interpretation
    assert "return" not in score.score_interpretation.lower()
    assert "drawdown" not in score.score_interpretation.lower()


# -------------------------------------------------------------------------
# REST API Endpoint Tests
# -------------------------------------------------------------------------
def test_api_capabilities():
    resp = client.get("/api/v1/intelligence/scoring/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert "EVENT_REVIEW_PRIORITY" in data["supported_objectives"]
    assert len(data["compliance_guarantees"]) >= 4


def test_api_objectives_and_policies():
    resp = client.get("/api/v1/intelligence/scoring/objectives")
    assert resp.status_code == 200
    assert len(resp.json()) >= 5

    resp_pol = client.get("/api/v1/intelligence/scoring/policies")
    assert resp_pol.status_code == 200
    assert len(resp_pol.json()) >= 4


def test_api_calculate_score():
    payload = {
        "event_data": {
            "event_id": "evt_api_test",
            "title": "Central Bank Policy Statement",
            "published_at": "2024-11-01T14:00:00Z",
            "entities": [{"entity_id": "CB_FED", "predicate": "ISSUED_BY"}],
            "sources": [{"source_id": "src_fed", "name": "Fed Bulletin", "source_type": "CENTRAL_BANK_BULLETIN"}],
        },
        "objective_id": "EVENT_REVIEW_PRIORITY",
        "known_as_of": "2024-11-01T15:00:00Z",
    }
    resp = client.post("/api/v1/intelligence/scoring/scores/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score_value"] is not None
    assert len(data["factor_contributions"]) > 0


def test_api_rank_events():
    payload = {
        "candidate_events": [
            {
                "event_id": f"evt_{i}",
                "title": f"Candidate Event {i}",
                "published_at": "2024-11-01T10:00:00Z",
                "valid_at": "2024-11-01T10:00:00Z",
                "sources": [{"source_id": f"s_{i}", "name": "Newswire"}],
            }
            for i in range(5)
        ],
        "objective_id": "EVENT_REVIEW_PRIORITY",
        "limit": 10,
    }
    resp = client.post("/api/v1/intelligence/scoring/rankings/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    assert data[0]["rank"] == 1


def test_api_telemetry_and_governance():
    resp = client.get("/api/v1/intelligence/scoring/telemetry")
    assert resp.status_code == 200
    assert resp.json()["drift_status"] == "HEALTHY"

    # Governance audit
    resp_gov = client.get("/api/v1/intelligence/scoring/governance/audit")
    assert resp_gov.status_code == 200
