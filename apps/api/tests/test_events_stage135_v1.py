"""Exhaustive Test Suite for Stage 135: Universal Event Model and Global Financial Event Foundation.

Validates all 18 standard validation scenarios (Fixtures A through R):
- Fixture A: Duplicate earnings reports -> 1 canonical event, 3 evidence records.
- Fixture B: Earnings scheduled vs reported results.
- Fixture C: Economic indicator revision with bitemporal as-of verification.
- Fixture D: Rate decision +25 bps math.
- Fixture E: Rate target range (5.25% - 5.50%).
- Fixture F: Sanctions exact match without fuzzy false positives.
- Fixture G: Sanctions amendment without duplicate designation.
- Fixture H: Merger announced vs approved vs completed.
- Fixture I: USGS earthquake revision (M5.2 -> M5.4 in-place).
- Fixture J: Separate distinct earthquakes.
- Fixture K: News rumor qualified as unverified candidate.
- Fixture L: Date-only event precision.
- Fixture M: Historical as-of query excluding future corrections (Zero Look-Ahead Bias).
- Fixture N: Conflicting source claims preserved without fabricated averages.
- Fixture O: Event retraction and tombstoning.
- Fixture P: Unlicensed source retention enforcement.
- Fixture Q: Multi-tenant isolation.
- Fixture R: Stage 134 physical-world observation bridge.

And verifies all FastAPI REST endpoints under /api/v1/events.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from atlas.events import (
    AtlasUniversalEvent,
    AtlasUniversalEventService,
    ClaimConflictStatus,
    DatePrecision,
    EventCategory,
    EventLifecycleStatus,
    EventSourceRecord,
    EventVerificationStatus,
    EvidenceRole,
)
from atlas.events.errors import EventLookAheadViolationError, EventNotFoundError
from atlas.events.identity.canonical import generate_canonical_event_key
from atlas.events.identity.deduplication import MatchConfidence
from atlas.events.search.query import EventSearchParams
from atlas.events.taxonomy.payloads import CentralBankEventPayload, EarningsEventPayload
from atlas_api.main import app

client = TestClient(app)


@pytest.fixture
def event_service() -> AtlasUniversalEventService:
    """Fresh event service with reference seed fixtures."""
    return AtlasUniversalEventService(populate_seed_data=True)


# ==============================================================================
# 1. CORE TAXONOMY & CLASSIFICATION TESTS
# ==============================================================================
def test_taxonomy_registry(event_service: AtlasUniversalEventService):
    categories = event_service.taxonomy.list_categories_with_subtypes()
    assert "FINANCIAL" in categories
    assert "ECONOMIC" in categories
    assert "MONETARY_POLICY" in categories
    assert "SANCTIONS" in categories
    assert "CORPORATE" in categories
    assert "NATURAL_DISASTER" in categories
    assert "INFRASTRUCTURE" in categories

    assert event_service.taxonomy.validate_subtype("FINANCIAL.EARNINGS_RELEASE")
    assert event_service.taxonomy.validate_subtype("MONETARY_POLICY.RATE_DECISION")
    assert not event_service.taxonomy.validate_subtype("INVALID.FAKE.SUBTYPE")


# ==============================================================================
# 2. FIXTURE A: DUPLICATE EARNINGS DEDUPLICATION (1 CANONICAL, 3 EVIDENCE)
# ==============================================================================
def test_fixture_a_duplicate_earnings_deduplication(event_service: AtlasUniversalEventService):
    evt = event_service.get_event("evt-aapl-2026-q3-earnings")
    assert evt is not None
    assert evt.canonical_event_key == "FINANCIAL.EARNINGS:AAPL:2026:3"
    assert evt.event_category == EventCategory.FINANCIAL
    assert evt.source_count >= 3

    evidence = event_service.get_evidence(evt.event_id)
    assert len(evidence) == 3

    roles = {ev.evidence_role for ev in evidence}
    assert EvidenceRole.PRIMARY_SOURCE in roles
    assert EvidenceRole.OFFICIAL_CONFIRMATION in roles
    assert EvidenceRole.CORROBORATING_SOURCE in roles


# ==============================================================================
# 3. FIXTURE B: SCHEDULED VS REPORTED EARNINGS
# ==============================================================================
def test_fixture_b_scheduled_vs_reported(event_service: AtlasUniversalEventService):
    evt_scheduled = event_service.get_event("evt-msft-2026-q4-earnings")
    assert evt_scheduled.lifecycle_status == EventLifecycleStatus.SCHEDULED
    assert evt_scheduled.scheduled_for is not None
    assert evt_scheduled.occurred_at is None

    # Now ingest actual results for MSFT Q4 2026 via earnings adapter
    payload = {
        "issuer_reference": "MSFT",
        "fiscal_year": 2026,
        "fiscal_quarter": 4,
        "is_scheduled": False,
        "reported_metrics": {"eps": 3.10, "revenue": 64700000000.0},
        "consensus_metrics": {"eps": 2.95, "revenue": 64000000000.0},
    }
    src_record = EventSourceRecord(
        source_record_id="src-msft-pr",
        source_id="sec_edgar",
        publisher="Microsoft IR",
        title="Microsoft Q4 2026 Release",
        retrieved_at=datetime.now(timezone.utc),
    )

    result_evt, is_new, confidence = event_service.ingest_source_event(
        adapter_name="earnings",
        raw_payload=payload,
        source_record=src_record,
    )
    # Dedup matches the scheduled event key!
    assert not is_new
    assert confidence == MatchConfidence.EXACT_CANONICAL_KEY
    assert result_evt.event_id == evt_scheduled.event_id


# ==============================================================================
# 4. FIXTURE C & M: BITEMPORAL HISTORY & ZERO LOOK-AHEAD AS-OF QUERIES
# ==============================================================================
def test_fixture_c_and_m_bitemporal_as_of_lookahead(event_service: AtlasUniversalEventService):
    evt_nfp = event_service.get_event("evt-nfp-2026-12")
    assert evt_nfp.current_revision_number == 2
    assert evt_nfp.event_payload["actual_value"] == 230000.0

    # Query as of 2026-01-10 (after initial release of 250k, but BEFORE revision of 230k on Feb 2)
    as_of_jan10 = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    historical_jan = event_service.as_of_query(as_of_time=as_of_jan10, event_id="evt-nfp-2026-12")
    assert len(historical_jan) == 1
    # MUST see initial 250k value, NOT the revised 230k value!
    assert historical_jan[0].event_payload["actual_value"] == 250000.0

    # Query as of 2026-02-15 (after Feb 2 revision)
    as_of_feb15 = datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc)
    historical_feb = event_service.as_of_query(as_of_time=as_of_feb15, event_id="evt-nfp-2026-12")
    assert len(historical_feb) == 1
    assert historical_feb[0].event_payload["actual_value"] == 230000.0

    # Query as of 2025-12-01 (before event occurred) -> must return empty list (was not known yet)
    as_of_pre = datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc)
    historical_pre = event_service.as_of_query(as_of_time=as_of_pre, event_id="evt-nfp-2026-12")
    assert len(historical_pre) == 0


# ==============================================================================
# 5. FIXTURE D: MONETARY POLICY BASIS POINTS MATH
# ==============================================================================
def test_fixture_d_basis_points_math(event_service: AtlasUniversalEventService):
    evt = event_service.get_event("evt-ecb-rate-20260910")
    payload = evt.event_payload
    assert payload["previous_rate"] == 3.75
    assert payload["new_rate"] == 4.00
    assert payload["change_bps"] == 25.0

    # Custom calculation test
    cb_test = CentralBankEventPayload(
        central_bank_reference="TEST_CB",
        jurisdiction="TEST",
        policy_instrument="RATE",
        decision_time=datetime.now(timezone.utc),
        previous_rate=5.50,
        new_rate=5.00,
    )
    cb_test.compute_change_bps()
    assert cb_test.change_bps == -50.0


# ==============================================================================
# 6. FIXTURE E: RATE TARGET RANGE BOUNDS
# ==============================================================================
def test_fixture_e_rate_target_range(event_service: AtlasUniversalEventService):
    evt = event_service.get_event("evt-fomc-range-20260916")
    payload = evt.event_payload
    assert payload["target_range_lower"] == 5.25
    assert payload["target_range_upper"] == 5.50
    assert "5.25%" in evt.title
    assert "5.50%" in evt.title


# ==============================================================================
# 7. FIXTURE F & G: SANCTIONS EXACT MATCH & AMENDMENT
# ==============================================================================
def test_fixture_f_and_g_sanctions(event_service: AtlasUniversalEventService):
    evt_f = event_service.get_event("evt-ofac-sovzvezda-av")
    assert evt_f.event_category == EventCategory.SANCTIONS
    assert evt_f.event_payload["designated_subject_reference"] == "SOVZVEZDA AVIATION LLC"
    assert evt_f.event_payload["action_type"] == "DESIGNATION"

    evt_g = event_service.get_event("evt-ofac-sovzvezda-amend")
    assert evt_g.event_payload["action_type"] == "AMENDMENT"
    assert evt_g.event_id != evt_f.event_id

    # Deduplication test: An unrelated entity "SOVZVEZDA LOGISTICS CJSC"
    # must NOT match or collide with SOVZVEZDA AVIATION LLC
    candidate_key = generate_canonical_event_key(
        "SANCTIONS.DESIGNATION",
        {
            "authority_id": "US_OFAC",
            "designated_subject_reference": "SOVZVEZDA LOGISTICS CJSC",
            "action_type": "DESIGNATION",
        },
        occurred_or_scheduled_date="2026-08-10",
    )
    assert candidate_key != evt_f.canonical_event_key


# ==============================================================================
# 8. FIXTURE H: CORPORATE MERGER DISTINCT MILESTONES
# ==============================================================================
def test_fixture_h_merger_milestones(event_service: AtlasUniversalEventService):
    evt_ann = event_service.get_event("evt-merger-acme-beta-ann")
    evt_comp = event_service.get_event("evt-merger-acme-beta-comp")

    assert evt_ann.lifecycle_status == EventLifecycleStatus.ANNOUNCED
    assert evt_comp.lifecycle_status == EventLifecycleStatus.OCCURRED
    assert evt_ann.canonical_event_key != evt_comp.canonical_event_key
    assert evt_ann.event_payload["action_type"] == "MERGER_ANNOUNCED"
    assert evt_comp.event_payload["action_type"] == "MERGER_COMPLETED"


# ==============================================================================
# 9. FIXTURES I & J: EARTHQUAKE REVISION VS SEPARATE DISTINCT EARTHQUAKES
# ==============================================================================
def test_fixtures_i_and_j_earthquakes(event_service: AtlasUniversalEventService):
    # Fixture I: USGS Earthquake us7000m4wz updated from 5.2 to 5.4 in-place
    evt_i = event_service.get_event("evt-usgs-us7000m4wz")
    assert evt_i.event_payload["magnitude_or_severity"] == "5.4"
    assert evt_i.current_revision_number == 2
    assert evt_i.canonical_event_key == "NATURAL_DISASTER.EARTHQUAKE:US7000M4WZ"

    revisions = event_service.get_revisions(evt_i.event_id)
    assert len(revisions) == 2
    assert revisions[0].changed_fields["magnitude_or_severity"] == "5.2"
    assert revisions[1].changed_fields["magnitude_or_severity"] == "5.4"

    # Fixture J: Separate distinct earthquake us7000m4x1 must NOT merge with us7000m4wz
    evt_j = event_service.get_event("evt-usgs-us7000m4x1")
    assert evt_j.canonical_event_key == "NATURAL_DISASTER.EARTHQUAKE:US7000M4X1"
    assert evt_j.event_id != evt_i.event_id
    assert evt_j.canonical_event_key != evt_i.canonical_event_key


# ==============================================================================
# 10. FIXTURE K: NEWS RUMOR QUALIFIED AS UNVERIFIED CANDIDATE
# ==============================================================================
def test_fixture_k_news_rumor(event_service: AtlasUniversalEventService):
    evt_k = event_service.get_event("evt-news-rumor-orcl")
    assert evt_k.verification_status == EventVerificationStatus.UNVERIFIED
    assert evt_k.lifecycle_status == EventLifecycleStatus.REPORTED
    assert "rumor" in evt_k.tags
    assert evt_k.verification_status != EventVerificationStatus.OFFICIALLY_CONFIRMED


# ==============================================================================
# 11. FIXTURE L: DATE-ONLY PRECISION
# ==============================================================================
def test_fixture_l_date_only_precision(event_service: AtlasUniversalEventService):
    evt_l = event_service.get_event("evt-amzn-shareholder-meeting-2026")
    assert evt_l.date_precision == DatePrecision.DATE_ONLY
    assert evt_l.scheduled_for is not None


# ==============================================================================
# 12. FIXTURE N: CONFLICTING SOURCE CLAIMS PRESERVED
# ==============================================================================
def test_fixture_n_conflicting_claims(event_service: AtlasUniversalEventService):
    evt_n = event_service.get_event("evt-port-explosion-2026")
    assert evt_n.claim_conflict_status == ClaimConflictStatus.CONFLICT_DETECTED

    claims = event_service.get_claims(evt_n.event_id)
    assert len(claims) == 2

    claim_values = {c.claim_value for c in claims}
    assert 12 in claim_values
    assert 25 in claim_values
    # Zero fabrication check: the system stores both 12 and 25, never averaging them to 18.5
    assert 18.5 not in claim_values


# ==============================================================================
# 13. FIXTURE O: EVENT RETRACTION AND TOMBSTONING
# ==============================================================================
def test_fixture_o_retraction_and_tombstone(event_service: AtlasUniversalEventService):
    evt_o = event_service.get_event("evt-false-hoax-20260401")
    assert evt_o.is_retracted is True
    assert evt_o.lifecycle_status == EventLifecycleStatus.RETRACTED
    assert evt_o.verification_status == EventVerificationStatus.REJECTED
    assert "Confirmed fraudulent release" in str(evt_o.retraction_reason)

    # Standard search must omit retracted events by default
    res = event_service.search_events(EventSearchParams(query="HoaxCo", include_retracted=False))
    assert res.total_count == 0

    # Explicit search with include_retracted=True surfaces the tombstoned record
    res_retracted = event_service.search_events(EventSearchParams(query="HoaxCo", include_retracted=True))
    assert res_retracted.total_count == 1
    assert res_retracted.events[0].event_id == evt_o.event_id


# ==============================================================================
# 14. FIXTURE P: UNLICENSED SOURCE RETENTION POLICY
# ==============================================================================
def test_fixture_p_unlicensed_source_policy(event_service: AtlasUniversalEventService):
    assert event_service.sources.is_source_authorized("sec_edgar") is True
    assert event_service.sources.is_source_authorized("unlicensed_wire") is False
    assert event_service.sources.verify_retention_compliance("sec_edgar") is True
    assert event_service.sources.verify_retention_compliance("reuters_wire") is False


# ==============================================================================
# 15. FIXTURE Q: MULTI-TENANT ISOLATION
# ==============================================================================
def test_fixture_q_multi_tenant_isolation(event_service: AtlasUniversalEventService):
    evt_q = event_service.get_event("evt-tenant-fund-alpha-001", tenant_id="tenant-hedgefund-alpha")
    assert evt_q.tenant_id == "tenant-hedgefund-alpha"

    # Other tenant attempting to access must receive NotFound
    with pytest.raises(EventNotFoundError):
        event_service.get_event("evt-tenant-fund-alpha-001", tenant_id="tenant-other-fund")


# ==============================================================================
# 16. FIXTURE R: STAGE 134 PHYSICAL-WORLD OBSERVATION BRIDGE
# ==============================================================================
def test_fixture_r_stage134_observation_bridge(event_service: AtlasUniversalEventService):
    evt_r = event_service.get_event("evt-fire-firms-20260904-098")
    assert evt_r.event_payload["stage134_observation_id"] == "obs-fire-20260904-098"
    assert evt_r.event_payload["frp_mw"] == 142.6
    assert "stage134_bridge" in evt_r.tags


# ==============================================================================
# 17. SEARCH & TIMELINE SUBSYSTEM TESTS
# ==============================================================================
def test_search_and_timeline_filtering(event_service: AtlasUniversalEventService):
    # Free-text search
    res = event_service.search_events(EventSearchParams(query="Apple"))
    assert res.total_count >= 1
    assert any(e.event_id == "evt-aapl-2026-q3-earnings" for e in res.events)

    # Category search
    res_monetary = event_service.search_events(EventSearchParams(categories=[EventCategory.MONETARY_POLICY]))
    assert res_monetary.total_count >= 2

    # Timeline streaming
    timeline = event_service.get_timeline(clock="occurred_at", ascending=False, limit=20)
    assert timeline.total_events > 0
    assert len(timeline.buckets) > 0

    # Upcoming schedule
    upcoming = event_service.get_upcoming_schedule(limit=10)
    assert len(upcoming) >= 1
    assert any(u.lifecycle_status == EventLifecycleStatus.SCHEDULED for u in upcoming)

    # Recent verified events
    recent = event_service.get_recent_events(limit=10)
    assert len(recent) >= 1


# ==============================================================================
# 18. FASTAPI REST ROUTE INTEGRATION TESTS
# ==============================================================================
def test_rest_capabilities_and_types():
    resp = client.get("/api/v1/events/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == 135
    assert data["bitemporal_support"] is True
    assert "occurred_at" in data["supported_clocks"]

    resp_types = client.get("/api/v1/events/types")
    assert resp_types.status_code == 200
    types_data = resp_types.json()
    assert "FINANCIAL" in types_data["categories"]


def test_rest_search_and_timeline():
    resp = client.get("/api/v1/events/search?q=Apple")
    assert resp.status_code == 200
    res = resp.json()
    assert res["total_count"] >= 1

    resp_tl = client.get("/api/v1/events/timeline?clock=occurred_at&limit=10")
    assert resp_tl.status_code == 200
    tl = resp_tl.json()
    assert "buckets" in tl
    assert tl["total_events"] > 0

    resp_up = client.get("/api/v1/events/upcoming")
    assert resp_up.status_code == 200
    assert isinstance(resp_up.json(), list)

    resp_rec = client.get("/api/v1/events/recent")
    assert resp_rec.status_code == 200
    assert isinstance(resp_rec.json(), list)


def test_rest_event_subresources():
    # Single event
    resp = client.get("/api/v1/events/evt-aapl-2026-q3-earnings")
    assert resp.status_code == 200
    evt = resp.json()
    assert evt["canonical_event_key"] == "FINANCIAL.EARNINGS:AAPL:2026:3"

    # Evidence subresource
    resp_ev = client.get("/api/v1/events/evt-aapl-2026-q3-earnings/evidence")
    assert resp_ev.status_code == 200
    assert len(resp_ev.json()) == 3

    # Claims subresource
    resp_clm = client.get("/api/v1/events/evt-port-explosion-2026/claims")
    assert resp_clm.status_code == 200
    assert len(resp_clm.json()) == 2

    # Revisions subresource
    resp_rev = client.get("/api/v1/events/evt-nfp-2026-12/revisions")
    assert resp_rev.status_code == 200
    assert len(resp_rev.json()) == 2

    # Sources subresource
    resp_src = client.get("/api/v1/events/evt-aapl-2026-q3-earnings/sources")
    assert resp_src.status_code == 200
    assert len(resp_src.json()) >= 1


def test_rest_as_of_historical_query():
    # As of Jan 10, NFP Dec 2026 actual_value must be 250k
    resp = client.post(
        "/api/v1/events/as-of",
        json={
            "as_of_time": "2026-01-10T12:00:00Z",
            "event_id": "evt-nfp-2026-12",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["event_payload"]["actual_value"] == 250000.0


def test_rest_deduplicate_check():
    resp = client.post(
        "/api/v1/events/deduplicate",
        json={
            "event_type": "FINANCIAL.EARNINGS",
            "payload": {"issuer_reference": "AAPL", "fiscal_year": 2026, "fiscal_quarter": 3},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_found"] is True
    assert data["confidence"] == "EXACT_CANONICAL_KEY"
    assert data["matched_event_id"] == "evt-aapl-2026-q3-earnings"
