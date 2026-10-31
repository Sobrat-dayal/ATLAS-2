"""Unit and Regression Test Suite for ATLAS Stage 132 - Corporate Geography and Facility Mapping.

Validates all 15 Canonical Reference Fixtures (Fixtures A through O):
- Fixture A: Headquarters (Corporate Headquarters != Manufacturing)
- Fixture B: Registered Address (Registered Office != Operating HQ)
- Fixture C: Owned vs Operated (Distinct owner and operator entities)
- Fixture D: Subsidiary Rollup (Group footprint vs Direct ownership)
- Fixture E: Historical Ownership (Point-in-time relationship validity)
- Fixture F: Approximate Coordinates (Locality centroid != exact site point)
- Fixture G: Candidate Deduplication (Fuzzy address/coordinate matching)
- Fixture H: Shared Address (Unrelated companies at same location do not merge)
- Fixture I: Unknown Status (Lack of evidence -> STATUS_UNKNOWN)
- Fixture J: Multiple Securities (Multiple share classes resolve to same entity)
- Fixture K: Company Comparison (Side-by-side factual comparison)
- Fixture L: Restricted Source / Tenant Isolation (403 on private facility)
- Fixture M: Revenue Misattribution (No fabricated facility revenue allocation)
- Fixture N: Announced Facility (ANNOUNCED != OPERATIONAL)
- Fixture O: Source Conflict (Preserves conflicting historical evidence)
"""

from __future__ import annotations

import datetime
from typing import Any

import pytest
from atlas.maps.corporate.analytics.comparison import compare_company_footprints
from atlas.maps.corporate.analytics.concentration import compute_facility_concentration
from atlas.maps.corporate.analytics.footprint import compute_company_footprint_summary
from atlas.maps.corporate.analytics.h3_aggregation import aggregate_facilities_to_h3
from atlas.maps.corporate.domain import (
    CorporateFacility,
    CorporateFacilityStatus,
    CorporateFacilityType,
    FacilityEntityLink,
    FacilityEvidenceClaim,
    FacilityRelationshipType,
    FacilityStatusHistory,
    GeographicPrecisionClass,
    VerificationStatus,
)
from atlas.maps.corporate.entities.graph_traversal import traverse_subsidiaries
from atlas.maps.corporate.entities.identifiers import validate_cik, validate_isin, validate_lei
from atlas.maps.corporate.entities.resolver import CanonicalEntityResolver
from atlas.maps.corporate.errors import (
    CycleDetectedInCorporateGraphError,
    FacilityAccessDeniedError,
    InvalidHistoricalAsOfError,
    InvalidPrecisionClassError,
)
from atlas.maps.corporate.facilities.history import get_status_as_of, parse_as_of_timestamp
from atlas.maps.corporate.facilities.locations import enforce_precision_rules, validate_coordinates
from atlas.maps.corporate.facilities.operators import get_facility_operators, get_facility_owners
from atlas.maps.corporate.facilities.registry import CorporateFacilityRegistry
from atlas.maps.corporate.facilities.types import verify_type_claims
from atlas.maps.corporate.ingestion.deduplication import find_matching_facility, haversine_distance_meters
from atlas.maps.corporate.seed import create_reference_test_service
from atlas.maps.corporate.service import AtlasCorporateGeoService
from atlas_api.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def test_service() -> AtlasCorporateGeoService:
    return create_reference_test_service()


# ============================================================================
# PART LXXXV — TEST FIXTURE A: HEADQUARTERS
# ============================================================================


def test_fixture_a_headquarters_classification():
    """Fixture A: Validates headquarters classification is not conflated with manufacturing."""
    evidence = "Principal executive offices and global headquarters located at One Apple Park Way."
    is_hq = verify_type_claims(CorporateFacilityType.CORPORATE_HEADQUARTERS, evidence)
    is_mfg = verify_type_claims(CorporateFacilityType.MANUFACTURING_FACILITY, evidence)

    assert is_hq is True
    # Headquarters disclosure alone must NOT verify as manufacturing
    assert is_mfg is False


# ============================================================================
# PART LXXXVI — TEST FIXTURE B: REGISTERED ADDRESS
# ============================================================================


def test_fixture_b_registered_office_vs_operating_hq():
    """Fixture B: Registered office address does not prove operating headquarters or factory."""
    fac = CorporateFacility(
        facility_id="TEST_REG_OFFICE_B",
        canonical_name="Test Registered Office",
        facility_type=CorporateFacilityType.REGISTERED_OFFICE,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_STREET_ADDRESS,
        country_code="GB",
        locality="London",
        address_text="123 Statutory Way, London, UK",
        primary_entity_id="TEST_ENTITY_B",
        links=[
            FacilityEntityLink(
                link_id="link_reg_1",
                facility_id="TEST_REG_OFFICE_B",
                legal_entity_id="TEST_ENTITY_B",
                company_id="TEST_ENTITY_B",
                relationship_type=FacilityRelationshipType.REGISTERED_ADDRESS_OF,
                role_description="Statutory legal registered office",
            )
        ],
    )
    assert fac.facility_type == CorporateFacilityType.REGISTERED_OFFICE
    assert fac.facility_type != CorporateFacilityType.CORPORATE_HEADQUARTERS
    assert fac.links[0].relationship_type == FacilityRelationshipType.REGISTERED_ADDRESS_OF


# ============================================================================
# PART LXXXVII — TEST FIXTURE C: OWNED VS OPERATED
# ============================================================================


def test_fixture_c_owned_vs_operated_separation():
    """Fixture C: Entity A owns Facility X, Entity B operates Facility X. Roles remain distinct."""
    link_owner = FacilityEntityLink(
        link_id="l_own_1",
        facility_id="TEST_FAC_X",
        legal_entity_id="ENTITY_A",
        company_id="ENTITY_A",
        relationship_type=FacilityRelationshipType.OWNED_BY,
        role_description="Property owner",
    )
    link_operator = FacilityEntityLink(
        link_id="l_op_1",
        facility_id="TEST_FAC_X",
        legal_entity_id="ENTITY_B",
        company_id="ENTITY_B",
        relationship_type=FacilityRelationshipType.OPERATED_BY,
        role_description="Plant operator",
    )
    links = [link_owner, link_operator]

    owners = get_facility_owners(links)
    operators = get_facility_operators(links)

    assert len(owners) == 1
    assert owners[0].legal_entity_id == "ENTITY_A"
    assert len(operators) == 1
    assert operators[0].legal_entity_id == "ENTITY_B"
    assert operators[0].legal_entity_id != "ENTITY_A"


# ============================================================================
# PART LXXXVIII — TEST FIXTURE D: SUBSIDIARY
# ============================================================================


def test_fixture_d_subsidiary_footprint_rollup(test_service: AtlasCorporateGeoService):
    """Fixture D: Parent P, Subsidiary S, Facility F operated by S. Group footprint includes F."""
    # Register facility operated by S
    fac_s = CorporateFacility(
        facility_id="TEST_FAC_SUBSIDIARY",
        canonical_name="Subsidiary S Plant",
        facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
        country_code="DE",
        locality="Munich",
        longitude=11.58,
        latitude=48.15,
        primary_entity_id="TEST_SUBSIDIARY_S",
        links=[
            FacilityEntityLink(
                link_id="l_sub_1",
                facility_id="TEST_FAC_SUBSIDIARY",
                legal_entity_id="TEST_SUBSIDIARY_S",
                company_id="TEST_SUBSIDIARY_S",
                relationship_type=FacilityRelationshipType.OPERATED_BY,
            )
        ],
    )
    test_service.registry.register_facility(fac_s)

    # 1. Direct query for Parent P -> Should NOT include F (0 facilities)
    direct_resp = test_service.get_company_footprint("TEST_PARENT_P", include_subsidiaries=False)
    assert direct_resp.summary.total_facilities == 0
    assert direct_resp.summary.direct_facilities_count == 0

    # 2. Subsidiary-inclusive query for Parent P -> Includes F (1 facility, classified as subsidiary)
    group_resp = test_service.get_company_footprint("TEST_PARENT_P", include_subsidiaries=True)
    assert group_resp.summary.total_facilities == 1
    assert group_resp.summary.subsidiary_facilities_count == 1
    assert group_resp.facilities[0].facility_id == "TEST_FAC_SUBSIDIARY"


# ============================================================================
# PART LXXXIX — TEST FIXTURE E: HISTORICAL OWNERSHIP
# ============================================================================


def test_fixture_e_historical_ownership_transition():
    """Fixture E: Facility associated with Entity A until 2023-01-01, then Entity B."""
    t_split = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)
    fac = CorporateFacility(
        facility_id="TEST_HIST_FAC",
        canonical_name="Historical Plant",
        facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
        country_code="US",
        links=[
            FacilityEntityLink(
                link_id="l_hist_a",
                facility_id="TEST_HIST_FAC",
                legal_entity_id="ENTITY_A",
                company_id="ENTITY_A",
                relationship_type=FacilityRelationshipType.OWNED_BY,
                valid_from=datetime.datetime(2015, 1, 1, tzinfo=datetime.timezone.utc),
                valid_to=t_split,
            ),
            FacilityEntityLink(
                link_id="l_hist_b",
                facility_id="TEST_HIST_FAC",
                legal_entity_id="ENTITY_B",
                company_id="ENTITY_B",
                relationship_type=FacilityRelationshipType.OWNED_BY,
                valid_from=t_split,
                valid_to=None,
            ),
        ],
    )
    reg = CorporateFacilityRegistry([fac])

    # As of 2022-06-01: Entity A owns it, Entity B does NOT
    facs_a = reg.query_facilities(company_id="ENTITY_A", as_of="2022-06-01T00:00:00Z")
    facs_b = reg.query_facilities(company_id="ENTITY_B", as_of="2022-06-01T00:00:00Z")
    assert len(facs_a) == 1
    assert len(facs_b) == 0

    # As of 2024-01-01: Entity B owns it, Entity A does NOT
    facs_a_2024 = reg.query_facilities(company_id="ENTITY_A", as_of="2024-01-01T00:00:00Z")
    facs_b_2024 = reg.query_facilities(company_id="ENTITY_B", as_of="2024-01-01T00:00:00Z")
    assert len(facs_a_2024) == 0
    assert len(facs_b_2024) == 1


# ============================================================================
# PART XC — TEST FIXTURE F: APPROXIMATE COORDINATES
# ============================================================================


def test_fixture_f_locality_centroid_precision():
    """Fixture F: Corporate document with only city name cannot be elevated to verified site point."""
    with pytest.raises(InvalidPrecisionClassError):
        enforce_precision_rules(
            precision=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            has_street_address=False,
            has_exact_site_point=False,
            is_city_only=True,
        )

    # City-only data correctly resolves to LOCALITY_CENTROID
    eval_precision = enforce_precision_rules(
        precision=GeographicPrecisionClass.LOCALITY_CENTROID,
        has_street_address=False,
        has_exact_site_point=False,
        is_city_only=True,
    )
    assert eval_precision == GeographicPrecisionClass.LOCALITY_CENTROID

    # Excluded from high-resolution H3 aggregation (res >= 6)
    fac_approx = CorporateFacility(
        facility_id="TEST_CITY_FAC",
        canonical_name="Approximate City Office",
        facility_type=CorporateFacilityType.CORPORATE_OFFICE,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.LOCALITY_CENTROID,
        country_code="US",
        longitude=-122.08,
        latitude=37.42,
    )
    agg_res_7 = aggregate_facilities_to_h3([fac_approx], resolution=7)
    assert agg_res_7["suppressed_approximate_count"] == 1
    assert len(agg_res_7["aggregates"]) == 0


# ============================================================================
# PART XCI — TEST FIXTURE G: DUPLICATES
# ============================================================================


def test_fixture_g_duplicate_candidate_matching():
    """Fixture G: Two source records with different address formatting match as candidate duplicate."""
    fac1 = CorporateFacility(
        facility_id="TEST_DEDUP_1",
        canonical_name="Plant Alpha",
        facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_STREET_ADDRESS,
        country_code="US",
        locality="Springfield",
        address_text="100 Industrial Boulevard, Suite 200",
        longitude=-89.6500,
        latitude=39.7800,
        primary_entity_id="CMP_SAME",
    )
    fac2 = CorporateFacility(
        facility_id="TEST_DEDUP_2",
        canonical_name="Plant Alpha",
        facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_STREET_ADDRESS,
        country_code="US",
        locality="Springfield",
        address_text="100 Industrial Blvd #200",
        longitude=-89.6501,
        latitude=39.7801,
        primary_entity_id="CMP_SAME",
    )

    match = find_matching_facility(fac2, [fac1])
    assert match is not None
    assert match.facility_id == "TEST_DEDUP_1"


# ============================================================================
# PART XCII — TEST FIXTURE H: SHARED ADDRESS
# ============================================================================


def test_fixture_h_shared_address_no_entity_merge():
    """Fixture H: Two unrelated companies in the same commercial building are NOT merged."""
    fac_firm_1 = CorporateFacility(
        facility_id="TEST_SHARED_1",
        canonical_name="Firm One Office",
        facility_type=CorporateFacilityType.CORPORATE_OFFICE,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_STREET_ADDRESS,
        country_code="US",
        locality="New York",
        address_text="350 Fifth Ave, New York, NY",
        longitude=-73.9857,
        latitude=40.7484,
        primary_entity_id="CMP_FIRM_1",
    )
    fac_firm_2 = CorporateFacility(
        facility_id="TEST_SHARED_2",
        canonical_name="Firm Two Office",
        facility_type=CorporateFacilityType.CORPORATE_OFFICE,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_STREET_ADDRESS,
        country_code="US",
        locality="New York",
        address_text="350 Fifth Ave, New York, NY",
        longitude=-73.9857,
        latitude=40.7484,
        primary_entity_id="CMP_FIRM_2",
    )

    # find_matching_facility must return None because entities are distinct and unrelated
    match = find_matching_facility(fac_firm_2, [fac_firm_1])
    assert match is None


# ============================================================================
# PART XCIII — TEST FIXTURE I: UNKNOWN STATUS
# ============================================================================


def test_fixture_i_status_unknown():
    """Fixture I: Missing recent operational evidence retains STATUS_UNKNOWN rather than guessing."""
    fac_unknown = CorporateFacility(
        facility_id="TEST_UNKNOWN_FAC",
        canonical_name="Historical Site",
        facility_type=CorporateFacilityType.OTHER_VERIFIED_FACILITY,
        facility_status=CorporateFacilityStatus.STATUS_UNKNOWN,
        precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
        country_code="US",
    )
    assert fac_unknown.facility_status == CorporateFacilityStatus.STATUS_UNKNOWN
    assert fac_unknown.facility_status != CorporateFacilityStatus.OPERATIONAL
    assert fac_unknown.facility_status != CorporateFacilityStatus.PERMANENTLY_CLOSED


# ============================================================================
# PART XCIV — TEST FIXTURE J: MULTIPLE SECURITIES
# ============================================================================


def test_fixture_j_multiple_securities_resolution(test_service: AtlasCorporateGeoService):
    """Fixture J: One issuer with two listed share classes (GOOG and GOOGL) resolves to same company."""
    ent_goog = test_service.resolver.resolve("GOOG")
    ent_googl = test_service.resolver.resolve("GOOGL")

    assert ent_goog["entity_id"] == "cmp_alphabet"
    assert ent_googl["entity_id"] == "cmp_alphabet"

    # Facility counts are not doubled
    footprint_goog = test_service.get_company_footprint("GOOG")
    footprint_googl = test_service.get_company_footprint("GOOGL")

    assert footprint_goog.summary.distinct_facilities == footprint_googl.summary.distinct_facilities
    assert footprint_goog.company_id == "cmp_alphabet"


# ============================================================================
# PART XCV — TEST FIXTURE K: COMPANY COMPARISON
# ============================================================================


def test_fixture_k_company_comparison(test_service: AtlasCorporateGeoService):
    """Fixture K: Compare Company A and Company B side-by-side with genuine metrics."""
    res = test_service.compare_companies("cmp_apple", "cmp_alphabet")

    assert res.company_a.company_id == "cmp_apple"
    assert res.company_b.company_id == "cmp_alphabet"
    assert isinstance(res.shared_countries, list)
    assert "US" in res.shared_countries
    assert "CORPORATE_HEADQUARTERS" in res.type_comparison


# ============================================================================
# PART XCVI — TEST FIXTURE L: RESTRICTED SOURCE / TENANT ISOLATION
# ============================================================================


def test_fixture_l_tenant_isolation_private_facility(test_service: AtlasCorporateGeoService):
    """Fixture L: User B cannot access private facility owned by Tenant A."""
    private_fac = CorporateFacility(
        facility_id="TEST_PRIVATE_FAC",
        canonical_name="Confidential Secure Facility",
        facility_type=CorporateFacilityType.CORPORATE_OFFICE,
        facility_status=CorporateFacilityStatus.OPERATIONAL,
        precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
        country_code="US",
        is_public=False,
        tenant_id="tenant_alpha",
    )
    test_service.registry.register_facility(private_fac)

    # Tenant Alpha can access
    fac = test_service.get_facility_details("TEST_PRIVATE_FAC", tenant_id="tenant_alpha")
    assert fac.facility_id == "TEST_PRIVATE_FAC"

    # Tenant Beta is denied access
    with pytest.raises(FacilityAccessDeniedError):
        test_service.get_facility_details("TEST_PRIVATE_FAC", tenant_id="tenant_beta")


# ============================================================================
# PART XCVII — TEST FIXTURE M: REVENUE MISATTRIBUTION
# ============================================================================


def test_fixture_m_revenue_misattribution_boundary():
    """Fixture M: Verifies system calculates facility count concentration without fabricating revenue."""
    fac1 = CorporateFacility("F1", "Site 1", CorporateFacilityType.CORPORATE_OFFICE, CorporateFacilityStatus.OPERATIONAL, GeographicPrecisionClass.VERIFIED_SITE_POINT, "US")
    fac2 = CorporateFacility("F2", "Site 2", CorporateFacilityType.CORPORATE_OFFICE, CorporateFacilityStatus.OPERATIONAL, GeographicPrecisionClass.VERIFIED_SITE_POINT, "US")
    fac3 = CorporateFacility("F3", "Site 3", CorporateFacilityType.CORPORATE_OFFICE, CorporateFacilityStatus.OPERATIONAL, GeographicPrecisionClass.VERIFIED_SITE_POINT, "DE")

    conc = compute_facility_concentration([fac1, fac2, fac3])
    # Must report facility share (66.67% US, 33.33% DE)
    assert conc["top_countries"][0]["country_code"] == "US"
    assert conc["top_countries"][0]["share_pct"] == 66.67

    # Concentration output strictly does NOT contain financial revenue estimates
    assert "revenue_exposure" not in conc
    assert "revenue_allocation" not in conc


# ============================================================================
# PART XCVIII — TEST FIXTURE N: ANNOUNCED FACILITY
# ============================================================================


def test_fixture_n_announced_facility_not_operational():
    """Fixture N: Announced proposed factory is labeled ANNOUNCED and excluded from operational count."""
    fac_announced = CorporateFacility(
        facility_id="TEST_ANNOUNCED_FAC",
        canonical_name="Proposed Mega Factory",
        facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
        facility_status=CorporateFacilityStatus.ANNOUNCED,
        precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
        country_code="US",
        primary_entity_id="TEST_ANNOUNCED_CMP",
    )
    assert fac_announced.facility_status == CorporateFacilityStatus.ANNOUNCED
    assert fac_announced.facility_status != CorporateFacilityStatus.OPERATIONAL

    summary = compute_company_footprint_summary(
        company_id="TEST_ANNOUNCED_CMP",
        canonical_name="Announced Corp",
        ticker="ANNC",
        facilities=[fac_announced],
        root_entity_id="TEST_ANNOUNCED_CMP",
    )
    assert summary.status_breakdown.get("ANNOUNCED") == 1
    assert summary.status_breakdown.get("OPERATIONAL", 0) == 0


# ============================================================================
# PART XCIX — TEST FIXTURE O: SOURCE CONFLICT
# ============================================================================


def test_fixture_o_source_conflict_temporal_revisions():
    """Fixture O: Source A reports operating in 2021; Source B reports closure in 2023. Both preserved."""
    fac_conflict = CorporateFacility(
        facility_id="TEST_CONFLICT_FAC",
        canonical_name="Conflicted Plant",
        facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
        facility_status=CorporateFacilityStatus.PERMANENTLY_CLOSED,
        precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
        country_code="US",
        status_history=[
            FacilityStatusHistory(
                history_id="sh_1",
                facility_id="TEST_CONFLICT_FAC",
                status=CorporateFacilityStatus.OPERATIONAL,
                valid_from=datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
                valid_to=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
                source_manifest_id="src_a",
            ),
            FacilityStatusHistory(
                history_id="sh_2",
                facility_id="TEST_CONFLICT_FAC",
                status=CorporateFacilityStatus.PERMANENTLY_CLOSED,
                valid_from=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
                valid_to=None,
                source_manifest_id="src_b",
            ),
        ],
        evidence_claims=[
            FacilityEvidenceClaim(
                claim_id="clm_1",
                facility_id="TEST_CONFLICT_FAC",
                subject_entity_id="CMP_X",
                predicate="operates_plant",
                source_title="2021 Annual Report",
                source_document_id="doc_2021",
                publisher="Company X",
                publication_date=datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc),
                exact_evidence_span="Operating plant in Cleveland.",
            ),
            FacilityEvidenceClaim(
                claim_id="clm_2",
                facility_id="TEST_CONFLICT_FAC",
                subject_entity_id="CMP_X",
                predicate="closed_plant",
                source_title="2023 Form 8-K Closure Notice",
                source_document_id="doc_2023",
                publisher="SEC EDGAR",
                publication_date=datetime.datetime(2023, 1, 15, tzinfo=datetime.timezone.utc),
                exact_evidence_span="Ceased operations and closed Cleveland facility on January 1, 2023.",
            ),
        ],
    )
    # Both evidence claims are preserved
    assert len(fac_conflict.evidence_claims) == 2

    # Point-in-time status
    status_2022 = get_status_as_of(fac_conflict, datetime.datetime(2022, 6, 1, tzinfo=datetime.timezone.utc))
    status_2024 = get_status_as_of(fac_conflict, datetime.datetime(2024, 6, 1, tzinfo=datetime.timezone.utc))

    assert status_2022 == CorporateFacilityStatus.OPERATIONAL
    assert status_2024 == CorporateFacilityStatus.PERMANENTLY_CLOSED


# ============================================================================
# API Integration Tests via TestClient
# ============================================================================


def test_api_company_search(client: TestClient):
    """API: GET /api/v1/maps/companies/search."""
    response = client.get("/api/v1/maps/companies/search?q=Apple")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["canonical_name"] == "Apple Inc."


def test_api_company_footprint(client: TestClient):
    """API: GET /api/v1/maps/companies/{id}/footprint."""
    response = client.get("/api/v1/maps/companies/cmp_apple/footprint?include_subsidiaries=true")
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == "cmp_apple"
    assert data["summary"]["total_facilities"] >= 3
    assert len(data["facilities"]) >= 3


def test_api_facility_details_and_sources(client: TestClient):
    """API: GET /api/v1/maps/facilities/{id} and /sources."""
    # 1. Details
    res_detail = client.get("/api/v1/maps/facilities/fac_appl_apple_park")
    assert res_detail.status_code == 200
    fac = res_detail.json()
    assert fac["canonical_name"] == "Apple Park"
    assert fac["facility_type"] == "CORPORATE_HEADQUARTERS"

    # 2. Sources
    res_sources = client.get("/api/v1/maps/facilities/fac_appl_apple_park/sources")
    assert res_sources.status_code == 200
    claims = res_sources.json()
    assert len(claims) >= 1
    assert "principal executive offices" in claims[0]["exact_evidence_span"].lower()


def test_api_spatial_query_and_aggregation(client: TestClient):
    """API: POST /api/v1/maps/facilities/spatial-query and /aggregate."""
    # Spatial query
    query_payload = {"country_code": "US", "limit": 50}
    res_query = client.post("/api/v1/maps/facilities/spatial-query", json=query_payload)
    assert res_query.status_code == 200
    facs = res_query.json()
    assert len(facs) >= 1
    assert all(f["country_code"] == "US" for f in facs)

    # H3 aggregation
    agg_payload = {"company_id": "cmp_apple", "resolution": 4}
    res_agg = client.post("/api/v1/maps/facilities/aggregate", json=agg_payload)
    assert res_agg.status_code == 200
    agg = res_agg.json()
    assert agg["resolution"] == 4
    assert len(agg["aggregates"]) >= 1

