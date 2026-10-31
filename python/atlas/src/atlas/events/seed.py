"""Canonical Test and Seed Fixtures A through R for Stage 135.

Implements all 18 standard validation scenarios required by the institutional specification:
- Fixture A: Duplicate earnings reports -> 1 canonical event, 3 evidence records.
- Fixture B: Earnings scheduled vs reported results.
- Fixture C: Economic indicator revision with bitemporal as-of verification.
- Fixture D: Rate decision +25 bps math.
- Fixture E: Rate target range (5.25% - 5.50%).
- Fixture F: Sanctions exact match without fuzzy false positives.
- Fixture G: Sanctions amendment without duplicate designation.
- Fixture H: Merger announced vs approved vs completed.
- Fixture I: USGS earthquake revision (M5.2 -> M5.4 in-place).
- Fixture J: Separate distinct earthquakes (different USGS IDs).
- Fixture K: News rumor qualified as unverified candidate.
- Fixture L: Date-only event precision.
- Fixture M: Historical as-of query excluding future corrections.
- Fixture N: Conflicting source claims preserved without fabricated averages.
- Fixture O: Event retraction and tombstoning.
- Fixture P: Unlicensed source retention enforcement.
- Fixture Q: Multi-tenant isolation.
- Fixture R: Stage 134 physical-world observation bridge.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .domain import (
    AtlasUniversalEvent,
    ClaimConflictStatus,
    DatePrecision,
    EventCategory,
    EventClaim,
    EventEvidence,
    EventGeographicScope,
    EventLifecycleStatus,
    EventRevision,
    EventSourceRecord,
    EventVerificationStatus,
    EvidenceRole,
    GeographicScopeType,
)
from .identity.canonical import generate_canonical_event_key
from .taxonomy.payloads import (
    CentralBankEventPayload,
    CorporateActionEventPayload,
    EarningsEventPayload,
    EconomicReleasePayload,
    PhysicalDisasterEventPayload,
    SanctionsEventPayload,
)


def build_stage135_fixtures() -> Tuple[
    List[AtlasUniversalEvent],
    List[EventSourceRecord],
    List[EventEvidence],
    List[EventClaim],
    List[EventRevision],
]:
    """Generate the complete reference seed dataset covering Fixtures A through R."""
    now_utc = datetime(2026, 10, 31, 8, 0, 0, tzinfo=timezone.utc)

    events: List[AtlasUniversalEvent] = []
    sources: List[EventSourceRecord] = []
    evidence_list: List[EventEvidence] = []
    claims_list: List[EventClaim] = []
    revisions: List[EventRevision] = []

    # -------------------------------------------------------------
    # FIXTURE A: Duplicate earnings reports -> 1 canonical event, 3 evidence records
    # -------------------------------------------------------------
    src_pr = EventSourceRecord(
        source_record_id="src-prn-aapl-q3",
        source_id="pr_newswire",
        publisher="Cision / PR Newswire",
        title="Apple Reports Third Quarter Results",
        published_at=datetime(2026, 7, 25, 20, 30, tzinfo=timezone.utc),
        retrieved_at=datetime(2026, 7, 25, 20, 31, tzinfo=timezone.utc),
        attribution="PR Newswire Official Wire",
    )
    src_edgar = EventSourceRecord(
        source_record_id="src-sec-aapl-10q",
        source_id="sec_edgar",
        publisher="US SEC",
        title="AAPL Form 10-Q for Period Ending 2026-06-27",
        published_at=datetime(2026, 7, 25, 20, 35, tzinfo=timezone.utc),
        retrieved_at=datetime(2026, 7, 25, 20, 36, tzinfo=timezone.utc),
        attribution="US SEC EDGAR",
    )
    src_reuters = EventSourceRecord(
        source_record_id="src-reuters-aapl",
        source_id="reuters",
        publisher="Thomson Reuters",
        title="Apple beats revenue targets in Q3 driven by Services growth",
        published_at=datetime(2026, 7, 25, 20, 32, tzinfo=timezone.utc),
        retrieved_at=datetime(2026, 7, 25, 20, 33, tzinfo=timezone.utc),
        attribution="Reuters News",
    )
    sources.extend([src_pr, src_edgar, src_reuters])

    payload_a = EarningsEventPayload(
        issuer_reference="AAPL",
        fiscal_period="2026-Q3",
        fiscal_year=2026,
        fiscal_quarter=3,
        period_end="2026-06-27",
        reporting_currency="USD",
        reported_metrics={"eps": 1.40, "revenue": 85800000000.0},
        consensus_metrics={"eps": 1.35, "revenue": 84500000000.0},
        surprise_metrics={"eps_surprise_pct": 3.7, "revenue_surprise_pct": 1.54},
    )

    key_a = generate_canonical_event_key("FINANCIAL.EARNINGS", payload_a.model_dump())
    evt_a = AtlasUniversalEvent(
        event_id="evt-aapl-2026-q3-earnings",
        canonical_event_key=key_a,
        event_type="FINANCIAL.EARNINGS",
        event_subtype="FINANCIAL.EARNINGS.REPORTED",
        event_category=EventCategory.FINANCIAL,
        title="Apple Inc Q3 2026 Earnings Release",
        factual_summary="Apple Inc reported Q3 2026 EPS of $1.40 (vs $1.35 consensus) and Revenue of $85.80B.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 7, 25, 20, 30, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 7, 25, 20, 30, tzinfo=timezone.utc),
        announced_at=datetime(2026, 7, 25, 20, 30, tzinfo=timezone.utc),
        first_public_at=datetime(2026, 7, 25, 20, 30, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 7, 25, 20, 31, tzinfo=timezone.utc),
        updated_at=datetime(2026, 7, 25, 20, 36, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="sec_edgar",
        event_payload=payload_a.model_dump(),
        source_count=3,
        current_revision_number=1,
        aliases=["AAPL", "Apple Inc."],
        tags=["earnings", "aapl", "q3-2026"],
    )
    events.append(evt_a)

    evidence_list.extend([
        EventEvidence(
            evidence_id="evi-a-1",
            event_id=evt_a.event_id,
            source_record_id=src_pr.source_record_id,
            evidence_role=EvidenceRole.PRIMARY_SOURCE,
            verification_status=EventVerificationStatus.SOURCE_REPORTED,
            snippet="Apple today announced financial results for its fiscal 2026 third quarter...",
            recorded_at=datetime(2026, 7, 25, 20, 31, tzinfo=timezone.utc),
        ),
        EventEvidence(
            evidence_id="evi-a-2",
            event_id=evt_a.event_id,
            source_record_id=src_edgar.source_record_id,
            evidence_role=EvidenceRole.OFFICIAL_CONFIRMATION,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
            snippet="Form 10-Q Apple Inc. For the quarterly period ended June 27, 2026...",
            recorded_at=datetime(2026, 7, 25, 20, 36, tzinfo=timezone.utc),
        ),
        EventEvidence(
            evidence_id="evi-a-3",
            event_id=evt_a.event_id,
            source_record_id=src_reuters.source_record_id,
            evidence_role=EvidenceRole.CORROBORATING_SOURCE,
            verification_status=EventVerificationStatus.INDEPENDENTLY_CORROBORATED,
            snippet="Reuters - Apple reports quarterly beat led by strong iPad and Services revenue...",
            recorded_at=datetime(2026, 7, 25, 20, 33, tzinfo=timezone.utc),
        ),
    ])

    # -------------------------------------------------------------
    # FIXTURE B: Earnings scheduled vs reported results
    # -------------------------------------------------------------
    evt_b = AtlasUniversalEvent(
        event_id="evt-msft-2026-q4-earnings",
        canonical_event_key="FINANCIAL.EARNINGS:MSFT:2026:4",
        event_type="FINANCIAL.EARNINGS",
        event_subtype="FINANCIAL.EARNINGS.SCHEDULED",
        event_category=EventCategory.FINANCIAL,
        title="Microsoft Corp Q4 2026 Earnings Announcement (Scheduled)",
        factual_summary="Microsoft scheduled to announce Q4 fiscal 2026 financial results after market close on 2026-11-12.",
        lifecycle_status=EventLifecycleStatus.SCHEDULED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        scheduled_for=datetime(2026, 11, 12, 21, 0, tzinfo=timezone.utc),
        announced_at=datetime(2026, 10, 15, 14, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 10, 15, 14, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 15, 14, 5, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="msft_ir",
        event_payload={"issuer_reference": "MSFT", "fiscal_year": 2026, "fiscal_quarter": 4, "status": "SCHEDULED"},
        aliases=["MSFT", "Microsoft"],
        tags=["earnings", "upcoming", "msft"],
    )
    events.append(evt_b)

    # -------------------------------------------------------------
    # FIXTURE C & M: Economic indicator revision with bitemporal as-of verification
    # Nonfarm Payrolls: Initial vintage 250k on Jan 5; Revised vintage 230k on Feb 2
    # -------------------------------------------------------------
    evt_c = AtlasUniversalEvent(
        event_id="evt-nfp-2026-12",
        canonical_event_key="ECONOMIC:US_NFP:US:2026-12:INITIAL",
        event_type="ECONOMIC.INDICATOR",
        event_subtype="ECONOMIC.EMPLOYMENT.NFP",
        event_category=EventCategory.ECONOMIC,
        title="US Nonfarm Payrolls - Dec 2026",
        factual_summary="US Bureau of Labor Statistics reported Dec 2026 Nonfarm Payrolls changed by 230k (revised from initial 250k).",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 1, 5, 13, 30, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 1, 5, 13, 30, tzinfo=timezone.utc),
        effective_at=datetime(2026, 1, 5, 13, 30, tzinfo=timezone.utc),
        first_public_at=datetime(2026, 1, 5, 13, 30, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 1, 5, 13, 31, tzinfo=timezone.utc),
        updated_at=datetime(2026, 2, 2, 13, 31, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="us_bls",
        event_payload={
            "indicator_id": "US_NFP",
            "indicator_name": "Nonfarm Payroll Employment",
            "country_region": "US",
            "reporting_period": "2026-12",
            "actual_value": 230000.0,
            "previous_value": 250000.0,
            "consensus_value": 200000.0,
            "revision_vintage": "REVISED_1",
            "unit": "PERSONS",
        },
        source_count=1,
        current_revision_number=2,
        aliases=["US_NFP", "Payrolls", "BLS NFP"],
        tags=["economic", "employment", "nfp", "us"],
    )
    events.append(evt_c)

    rev_c_1 = EventRevision(
        event_revision_id="rev-c-1",
        event_id=evt_c.event_id,
        revision_number=1,
        changed_fields={
            "event_payload": {
                "indicator_id": "US_NFP",
                "reporting_period": "2026-12",
                "actual_value": 250000.0,
                "revision_vintage": "INITIAL",
            }
        },
        reason="Initial employment situation release",
        recorded_at=datetime(2026, 1, 5, 13, 31, tzinfo=timezone.utc),
        published_at=datetime(2026, 1, 5, 13, 30, tzinfo=timezone.utc),
    )
    rev_c_2 = EventRevision(
        event_revision_id="rev-c-2",
        event_id=evt_c.event_id,
        revision_number=2,
        previous_revision_id=rev_c_1.event_revision_id,
        changed_fields={
            "event_payload": {
                "actual_value": 230000.0,
                "previous_value": 250000.0,
                "revision_vintage": "REVISED_1",
            }
        },
        reason="First regular benchmark revision by BLS",
        recorded_at=datetime(2026, 2, 2, 13, 31, tzinfo=timezone.utc),
        published_at=datetime(2026, 2, 2, 13, 30, tzinfo=timezone.utc),
    )
    revisions.extend([rev_c_1, rev_c_2])

    # -------------------------------------------------------------
    # FIXTURE D: Rate decision +25 bps math
    # -------------------------------------------------------------
    cb_d = CentralBankEventPayload(
        central_bank_reference="ECB",
        jurisdiction="EZ",
        policy_instrument="MAIN_REFINANCING_RATE",
        decision_time=datetime(2026, 9, 10, 12, 15, tzinfo=timezone.utc),
        previous_rate=3.75,
        new_rate=4.00,
        rate_unit="PERCENT",
    )
    cb_d.compute_change_bps()

    evt_d = AtlasUniversalEvent(
        event_id="evt-ecb-rate-20260910",
        canonical_event_key=generate_canonical_event_key("MONETARY_POLICY.RATE_DECISION", cb_d.model_dump()),
        event_type="MONETARY_POLICY.RATE_DECISION",
        event_subtype="MONETARY_POLICY.RATE_DECISION",
        event_category=EventCategory.MONETARY_POLICY,
        title="ECB Policy Rate Hike +25 bps to 4.00%",
        factual_summary="European Central Bank raised its main refinancing rate by +25 bps from 3.75% to 4.00%.",
        lifecycle_status=EventLifecycleStatus.CONFIRMED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=cb_d.decision_time,
        source_published_at=cb_d.decision_time,
        announced_at=cb_d.decision_time,
        first_public_at=cb_d.decision_time,
        first_ingested_at=cb_d.decision_time,
        updated_at=cb_d.decision_time,
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.CONTINENT, country_code="EU"),
        primary_source_id="ecb_press",
        event_payload=cb_d.model_dump(),
        tags=["ecb", "rates", "monetary_policy"],
        aliases=["ECB"],
    )
    events.append(evt_d)

    # -------------------------------------------------------------
    # FIXTURE E: Rate target range (5.25% - 5.50%)
    # -------------------------------------------------------------
    cb_e = CentralBankEventPayload(
        central_bank_reference="US_FED",
        jurisdiction="US",
        policy_instrument="FED_FUNDS_TARGET_RANGE",
        decision_time=datetime(2026, 9, 16, 18, 0, tzinfo=timezone.utc),
        target_range_lower=5.25,
        target_range_upper=5.50,
        rate_unit="PERCENT",
    )
    evt_e = AtlasUniversalEvent(
        event_id="evt-fomc-range-20260916",
        canonical_event_key=generate_canonical_event_key("MONETARY_POLICY.RATE_DECISION", cb_e.model_dump()),
        event_type="MONETARY_POLICY.RATE_DECISION",
        event_subtype="MONETARY_POLICY.RATE_DECISION",
        event_category=EventCategory.MONETARY_POLICY,
        title="FOMC Maintained Federal Funds Rate Target Range at 5.25% - 5.50%",
        factual_summary="Federal Open Market Committee maintained federal funds target range at 5.25% to 5.50%.",
        lifecycle_status=EventLifecycleStatus.CONFIRMED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=cb_e.decision_time,
        source_published_at=cb_e.decision_time,
        announced_at=cb_e.decision_time,
        first_public_at=cb_e.decision_time,
        first_ingested_at=cb_e.decision_time,
        updated_at=cb_e.decision_time,
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="us_fed",
        event_payload=cb_e.model_dump(),
        tags=["fomc", "fed", "interest_rates"],
        aliases=["US_FED", "FOMC"],
    )
    events.append(evt_e)

    # -------------------------------------------------------------
    # FIXTURE F: Sanctions exact match without fuzzy false positives
    # Designated subject: "SOVZVEZDA AVIATION LLC"
    # Unrelated entity: "SOVZVEZDA LOGISTICS CJSC" (must NOT be matched)
    # -------------------------------------------------------------
    sanc_f = SanctionsEventPayload(
        authority_id="US_OFAC",
        jurisdiction="US",
        program_id="RUSSIA-EO14024",
        official_action_id="OFAC-SDN-20260810-01",
        action_type="DESIGNATION",
        designated_subject_reference="SOVZVEZDA AVIATION LLC",
        subject_kind="ENTITY",
        publication_date="2026-08-10",
        effective_date="2026-08-10",
    )
    evt_f = AtlasUniversalEvent(
        event_id="evt-ofac-sovzvezda-av",
        canonical_event_key=generate_canonical_event_key("SANCTIONS.DESIGNATION", sanc_f.model_dump()),
        event_type="SANCTIONS.DESIGNATION",
        event_subtype="SANCTIONS.DESIGNATION",
        event_category=EventCategory.SANCTIONS,
        title="US OFAC Sanctions Designation: SOVZVEZDA AVIATION LLC",
        factual_summary="US OFAC added SOVZVEZDA AVIATION LLC to SDN list under program RUSSIA-EO14024.",
        lifecycle_status=EventLifecycleStatus.CONFIRMED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 8, 10, 15, 0, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 8, 10, 15, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 8, 10, 15, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 8, 10, 15, 5, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="us_ofac",
        event_payload=sanc_f.model_dump(),
        aliases=["SOVZVEZDA AVIATION LLC"],
        tags=["sanctions", "ofac", "sdn"],
    )
    events.append(evt_f)

    # -------------------------------------------------------------
    # FIXTURE G: Sanctions amendment without duplicate designation
    # Updating existing SDN entry with new maritime identifier
    # -------------------------------------------------------------
    sanc_g = SanctionsEventPayload(
        authority_id="US_OFAC",
        jurisdiction="US",
        program_id="RUSSIA-EO14024",
        official_action_id="OFAC-SDN-20260810-01",
        action_type="AMENDMENT",
        designated_subject_reference="SOVZVEZDA AVIATION LLC",
        subject_kind="ENTITY",
        publication_date="2026-09-01",
        effective_date="2026-09-01",
    )
    evt_g = AtlasUniversalEvent(
        event_id="evt-ofac-sovzvezda-amend",
        canonical_event_key=generate_canonical_event_key("SANCTIONS.AMENDMENT", sanc_g.model_dump()),
        event_type="SANCTIONS.AMENDMENT",
        event_subtype="SANCTIONS.AMENDMENT",
        event_category=EventCategory.SANCTIONS,
        title="US OFAC Sanctions Amendment: SOVZVEZDA AVIATION LLC",
        factual_summary="US OFAC amended SDN record for SOVZVEZDA AVIATION LLC updating identifier details.",
        lifecycle_status=EventLifecycleStatus.CONFIRMED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 9, 1, 14, 0, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 9, 1, 14, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 9, 1, 14, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, 14, 5, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="us_ofac",
        event_payload=sanc_g.model_dump(),
        aliases=["SOVZVEZDA AVIATION LLC"],
        tags=["sanctions", "ofac", "amendment"],
    )
    events.append(evt_g)

    # -------------------------------------------------------------
    # FIXTURE H: Merger announced vs approved vs completed
    # Acme acquiring Beta: distinct lifecycle events
    # -------------------------------------------------------------
    corp_h_ann = CorporateActionEventPayload(
        issuer_reference="ACME_CORP",
        action_type="MERGER_ANNOUNCED",
        target_reference="BETA_TECH",
        deal_value_currency="USD",
        deal_value_amount=1500000000.0,
        declaration_date="2026-04-10",
    )
    evt_h_ann = AtlasUniversalEvent(
        event_id="evt-merger-acme-beta-ann",
        canonical_event_key=generate_canonical_event_key("CORPORATE.MERGER_ANNOUNCED", corp_h_ann.model_dump()),
        event_type="CORPORATE.ACTION",
        event_subtype="CORPORATE.M_AND_A.ANNOUNCED",
        event_category=EventCategory.CORPORATE,
        title="Acme Corp Announces Agreement to Acquire Beta Tech for $1.5B",
        factual_summary="Acme Corp announced definitive agreement to acquire Beta Tech for $1.50B in cash and stock.",
        lifecycle_status=EventLifecycleStatus.ANNOUNCED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 4, 10, 10, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 10, 10, 5, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="sec_edgar",
        event_payload=corp_h_ann.model_dump(),
        aliases=["ACME_CORP", "BETA_TECH"],
        tags=["merger", "m_and_a", "announced"],
    )

    corp_h_comp = CorporateActionEventPayload(
        issuer_reference="ACME_CORP",
        action_type="MERGER_COMPLETED",
        target_reference="BETA_TECH",
        deal_value_currency="USD",
        deal_value_amount=1500000000.0,
        declaration_date="2026-09-30",
    )
    evt_h_comp = AtlasUniversalEvent(
        event_id="evt-merger-acme-beta-comp",
        canonical_event_key=generate_canonical_event_key("CORPORATE.MERGER_COMPLETED", corp_h_comp.model_dump()),
        event_type="CORPORATE.ACTION",
        event_subtype="CORPORATE.M_AND_A.COMPLETED",
        event_category=EventCategory.CORPORATE,
        title="Acme Corp Completes Acquisition of Beta Tech",
        factual_summary="Acme Corp completed the closing of its $1.50B acquisition of Beta Tech.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 9, 30, 18, 0, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 9, 30, 18, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 9, 30, 18, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 30, 18, 5, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="sec_edgar",
        event_payload=corp_h_comp.model_dump(),
        aliases=["ACME_CORP", "BETA_TECH"],
        tags=["merger", "m_and_a", "completed"],
    )
    events.extend([evt_h_ann, evt_h_comp])

    # -------------------------------------------------------------
    # FIXTURE I: USGS earthquake revision (M5.2 -> M5.4 in-place)
    # Same USGS event ID: "us7000m4wz"
    # -------------------------------------------------------------
    disaster_i = PhysicalDisasterEventPayload(
        disaster_type="EARTHQUAKE",
        magnitude_or_severity="5.4",
        depth_km=12.5,
        source_event_id="us7000m4wz",
    )
    evt_i = AtlasUniversalEvent(
        event_id="evt-usgs-us7000m4wz",
        canonical_event_key="NATURAL_DISASTER.EARTHQUAKE:US7000M4WZ",
        event_type="NATURAL_DISASTER.OBSERVED",
        event_subtype="NATURAL_DISASTER.EARTHQUAKE",
        event_category=EventCategory.NATURAL_DISASTER,
        title="M5.4 Earthquake - 15km SE of Ridgecrest, CA",
        factual_summary="USGS Earthquake us7000m4wz revised from M5.2 to M5.4 at depth 12.5 km.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 6, 14, 4, 12, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 6, 14, 4, 15, tzinfo=timezone.utc),
        first_public_at=datetime(2026, 6, 14, 4, 15, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 6, 14, 4, 16, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 14, 4, 45, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(
            scope_type=GeographicScopeType.COORDINATES,
            country_code="US",
            latitude=35.58,
            longitude=-117.52,
            location_name="Ridgecrest, CA",
        ),
        primary_source_id="usgs_earthquakes",
        event_payload=disaster_i.model_dump(),
        current_revision_number=2,
        aliases=["us7000m4wz"],
        tags=["earthquake", "california", "usgs"],
    )
    events.append(evt_i)

    rev_i_1 = EventRevision(
        event_revision_id="rev-i-1",
        event_id=evt_i.event_id,
        revision_number=1,
        changed_fields={"magnitude_or_severity": "5.2", "depth_km": 10.0},
        reason="Initial automatic alert",
        recorded_at=datetime(2026, 6, 14, 4, 16, tzinfo=timezone.utc),
    )
    rev_i_2 = EventRevision(
        event_revision_id="rev-i-2",
        event_id=evt_i.event_id,
        revision_number=2,
        previous_revision_id=rev_i_1.event_revision_id,
        changed_fields={"magnitude_or_severity": "5.4", "depth_km": 12.5},
        reason="Seismologist manual review and magnitude upgrade",
        recorded_at=datetime(2026, 6, 14, 4, 45, tzinfo=timezone.utc),
    )
    revisions.extend([rev_i_1, rev_i_2])

    # -------------------------------------------------------------
    # FIXTURE J: Separate distinct earthquakes
    # Different USGS event ID: "us7000m4x1" occurring in same region
    # -------------------------------------------------------------
    disaster_j = PhysicalDisasterEventPayload(
        disaster_type="EARTHQUAKE",
        magnitude_or_severity="4.8",
        depth_km=8.2,
        source_event_id="us7000m4x1",
    )
    evt_j = AtlasUniversalEvent(
        event_id="evt-usgs-us7000m4x1",
        canonical_event_key="NATURAL_DISASTER.EARTHQUAKE:US7000M4X1",
        event_type="NATURAL_DISASTER.OBSERVED",
        event_subtype="NATURAL_DISASTER.EARTHQUAKE",
        event_category=EventCategory.NATURAL_DISASTER,
        title="M4.8 Earthquake - 12km E of Ridgecrest, CA",
        factual_summary="USGS Earthquake us7000m4x1 of magnitude 4.8 occurred at depth 8.2 km.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 6, 14, 5, 30, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 6, 14, 5, 32, tzinfo=timezone.utc),
        first_public_at=datetime(2026, 6, 14, 5, 32, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 6, 14, 5, 33, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 14, 5, 33, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(
            scope_type=GeographicScopeType.COORDINATES,
            country_code="US",
            latitude=35.61,
            longitude=-117.48,
            location_name="Ridgecrest, CA",
        ),
        primary_source_id="usgs_earthquakes",
        event_payload=disaster_j.model_dump(),
        aliases=["us7000m4x1"],
        tags=["earthquake", "aftershock", "usgs"],
    )
    events.append(evt_j)

    # -------------------------------------------------------------
    # FIXTURE K: News rumor qualified as unverified candidate
    # Rumored merger talks
    # -------------------------------------------------------------
    evt_k = AtlasUniversalEvent(
        event_id="evt-news-rumor-orcl",
        canonical_event_key="NEWS.REPORTED:RUMOR:ORCL:2026-05-18",
        event_type="NEWS.REPORTED",
        event_subtype="NEWS.CANDIDATE_RUMOR",
        event_category=EventCategory.NEWS_REPORTED,
        title="Reported: Sources Say Oracle Considering Acquisition of Cloud AI Startup",
        factual_summary="Market media reports indicate Oracle may be exploring an acquisition; unverified candidate.",
        lifecycle_status=EventLifecycleStatus.REPORTED,
        verification_status=EventVerificationStatus.UNVERIFIED,
        occurred_at=datetime(2026, 5, 18, 12, 0, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 5, 18, 12, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 5, 18, 12, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 18, 12, 5, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="financial_rumor_feed",
        event_payload={"subject_entity": "ORCL", "is_rumor": True},
        aliases=["ORCL"],
        tags=["rumor", "unverified", "orcl", "m_and_a"],
    )
    events.append(evt_k)

    # -------------------------------------------------------------
    # FIXTURE L: Date-only event precision
    # Annual shareholder meeting with no exact minute specified
    # -------------------------------------------------------------
    evt_l = AtlasUniversalEvent(
        event_id="evt-amzn-shareholder-meeting-2026",
        canonical_event_key="CORPORATE.MEETING:AMZN:2026-05-20",
        event_type="CORPORATE.ANNUAL_MEETING",
        event_subtype="CORPORATE.ANNUAL_MEETING",
        event_category=EventCategory.CORPORATE,
        title="Amazon.com Inc 2026 Annual Meeting of Shareholders",
        factual_summary="Amazon.com Inc scheduled its Annual Meeting of Shareholders for May 20, 2026.",
        lifecycle_status=EventLifecycleStatus.SCHEDULED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc),
        scheduled_for=datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc),
        date_precision=DatePrecision.DATE_ONLY,
        first_ingested_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="sec_edgar",
        event_payload={"issuer_reference": "AMZN", "meeting_date": "2026-05-20"},
        aliases=["AMZN"],
        tags=["meeting", "shareholders", "amzn"],
    )
    events.append(evt_l)

    # -------------------------------------------------------------
    # FIXTURE N: Conflicting source claims preserved
    # Two wire reports conflicting on initial casualty/impact figure
    # -------------------------------------------------------------
    evt_n = AtlasUniversalEvent(
        event_id="evt-port-explosion-2026",
        canonical_event_key="INFRASTRUCTURE.INCIDENT:ROTTERDAM:2026-07-02",
        event_type="INFRASTRUCTURE.INCIDENT",
        event_subtype="INFRASTRUCTURE.INCIDENT.EXPLOSION",
        event_category=EventCategory.INFRASTRUCTURE,
        title="Industrial Storage Explosion at Port of Rotterdam Facility",
        factual_summary="Industrial explosion occurred at a bulk chemical terminal in Port of Rotterdam; source claims conflict on reported injuries.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.CONFLICTED,
        claim_conflict_status=ClaimConflictStatus.CONFLICT_DETECTED,
        occurred_at=datetime(2026, 7, 2, 8, 30, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 7, 2, 8, 45, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 7, 2, 8, 50, tzinfo=timezone.utc),
        updated_at=datetime(2026, 7, 2, 9, 15, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(
            scope_type=GeographicScopeType.COORDINATES,
            country_code="NL",
            latitude=51.92,
            longitude=4.48,
            location_name="Port of Rotterdam",
        ),
        primary_source_id="local_police_wire",
        source_count=2,
        aliases=["Port of Rotterdam"],
        tags=["infrastructure", "rotterdam", "conflicted"],
    )
    events.append(evt_n)

    claim_n_1 = EventClaim(
        claim_id="clm-rotterdam-1",
        event_id=evt_n.event_id,
        source_record_id="src-wire-a",
        predicate="REPORTED_INJURIES",
        claim_value=12,
        value_type="INTEGER",
        units="PERSONS",
        extracted_at=datetime(2026, 7, 2, 8, 50, tzinfo=timezone.utc),
        verification_status=EventVerificationStatus.SOURCE_REPORTED,
    )
    claim_n_2 = EventClaim(
        claim_id="clm-rotterdam-2",
        event_id=evt_n.event_id,
        source_record_id="src-wire-b",
        predicate="REPORTED_INJURIES",
        claim_value=25,
        value_type="INTEGER",
        units="PERSONS",
        extracted_at=datetime(2026, 7, 2, 9, 10, tzinfo=timezone.utc),
        verification_status=EventVerificationStatus.SOURCE_REPORTED,
    )
    claims_list.extend([claim_n_1, claim_n_2])

    # -------------------------------------------------------------
    # FIXTURE O: Event retraction and tombstoning
    # False press release that was retracted by the wire
    # -------------------------------------------------------------
    evt_o = AtlasUniversalEvent(
        event_id="evt-false-hoax-20260401",
        canonical_event_key="CORPORATE.HOAX:HOAXCO:2026-04-01",
        event_type="CORPORATE.ANNOUNCEMENT",
        event_subtype="CORPORATE.RETRACTED",
        event_category=EventCategory.CORPORATE,
        title="[RETRACTED] Purported Takeover Bid of HoaxCo",
        factual_summary="This event was retracted after wire service confirmed unauthorized dissemination.",
        lifecycle_status=EventLifecycleStatus.RETRACTED,
        verification_status=EventVerificationStatus.REJECTED,
        is_retracted=True,
        retraction_reason="Confirmed fraudulent release issued via compromised account; formally retracted by wire.",
        occurred_at=datetime(2026, 4, 1, 13, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 4, 1, 13, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 1, 13, 40, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="pr_newswire",
        tags=["retracted", "tombstone", "fraud"],
    )
    events.append(evt_o)

    # -------------------------------------------------------------
    # FIXTURE P: Unlicensed source retention enforcement
    # Demonstrating source policy
    # -------------------------------------------------------------
    src_unlicensed = EventSourceRecord(
        source_record_id="src-unlicensed-feed-01",
        source_id="unlicensed_wire",
        publisher="ScrapeVendor Inc",
        title="Unauthorized feed item",
        published_at=datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc),
        retrieved_at=datetime(2026, 8, 1, 10, 5, tzinfo=timezone.utc),
        license_name="UNLICENSED_TEST",
        retention_policy="TRANSIENT_PROHIBITED",
        access_policy="RESTRICTED",
        attribution="Restricted Unlicensed Data",
    )
    sources.append(src_unlicensed)

    # -------------------------------------------------------------
    # FIXTURE Q: Multi-tenant isolation
    # Tenant-specific internal event
    # -------------------------------------------------------------
    evt_q = AtlasUniversalEvent(
        event_id="evt-tenant-fund-alpha-001",
        canonical_event_key="INTERNAL.REBALANCE:FUND_ALPHA:2026-10-15",
        event_type="FINANCIAL.INTERNAL_REBALANCE",
        event_subtype="FINANCIAL.INTERNAL_REBALANCE",
        event_category=EventCategory.FINANCIAL,
        title="Fund Alpha Q4 Internal Rebalance Execution",
        factual_summary="Internal tenant portfolio rebalance completed across sovereign debt sleeves.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 10, 15, 16, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 10, 15, 16, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 15, 16, 1, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(scope_type=GeographicScopeType.COUNTRY, country_code="US"),
        primary_source_id="internal_oms",
        tenant_id="tenant-hedgefund-alpha",
        tags=["tenant_private", "rebalance"],
    )
    events.append(evt_q)

    # -------------------------------------------------------------
    # FIXTURE R: Stage 134 physical-world observation bridge
    # Connected directly to Stage 134 wildfire observation
    # -------------------------------------------------------------
    disaster_r = PhysicalDisasterEventPayload(
        disaster_type="WILDFIRE",
        magnitude_or_severity="MODERATE_FRP",
        frp_mw=142.6,
        source_event_id="firms-modis-20260904-098",
        stage134_observation_id="obs-fire-20260904-098",
    )
    evt_r = AtlasUniversalEvent(
        event_id="evt-fire-firms-20260904-098",
        canonical_event_key="NATURAL_DISASTER.WILDFIRE:FIRMS-MODIS-20260904-098",
        event_type="NATURAL_DISASTER.OBSERVED",
        event_subtype="NATURAL_DISASTER.WILDFIRE",
        event_category=EventCategory.NATURAL_DISASTER,
        title="Thermal Anomaly / Active Wildfire - Mendocino County, CA",
        factual_summary="Satellite-detected MODIS thermal hotspot observed with 142.6 MW Fire Radiative Power (bridged from Stage 134 observation obs-fire-20260904-098).",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2026, 9, 4, 19, 20, tzinfo=timezone.utc),
        source_published_at=datetime(2026, 9, 4, 19, 25, tzinfo=timezone.utc),
        first_ingested_at=datetime(2026, 9, 4, 19, 30, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 4, 19, 30, tzinfo=timezone.utc),
        geographic_scope=EventGeographicScope(
            scope_type=GeographicScopeType.COORDINATES,
            country_code="US",
            latitude=39.15,
            longitude=-123.21,
            location_name="Mendocino County, CA",
        ),
        primary_source_id="nasa_firms",
        event_payload=disaster_r.model_dump(),
        aliases=["firms-modis-20260904-098", "obs-fire-20260904-098"],
        tags=["wildfire", "firms", "stage134_bridge", "physical_world"],
    )
    events.append(evt_r)

    return events, sources, evidence_list, claims_list, revisions
