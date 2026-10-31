"""Canonical seed data and reference fixtures for Corporate Geography (Stage 132)."""

from __future__ import annotations

import datetime

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


def get_canonical_seed_entities() -> list[dict]:
    """Return canonical company entities for resolution and testing."""
    return [
        {
            "entity_id": "cmp_apple",
            "company_id": "cmp_apple",
            "canonical_name": "Apple Inc.",
            "legal_name": "Apple Inc.",
            "tickers": ["AAPL"],
            "lei": "HW68UGV4U3M805199327",
            "cik": "0000320193",
            "primary_country_code": "US",
            "organization_type": "public_company",
            "status": "active",
        },
        {
            "entity_id": "cmp_alphabet",
            "company_id": "cmp_alphabet",
            "canonical_name": "Alphabet Inc.",
            "legal_name": "Alphabet Inc.",
            "tickers": ["GOOG", "GOOGL"],
            "lei": "5493006MHB84DD0ZWV18",
            "cik": "0001652044",
            "primary_country_code": "US",
            "organization_type": "public_company",
            "status": "active",
        },
        {
            "entity_id": "cmp_bmw",
            "company_id": "cmp_bmw",
            "canonical_name": "Bayerische Motoren Werke AG",
            "legal_name": "Bayerische Motoren Werke Aktiengesellschaft",
            "tickers": ["BMW", "BMW.DE", "BMWYY"],
            "lei": "YE52UQUSBQL2P82UN568",
            "cik": "0000014277",
            "primary_country_code": "DE",
            "organization_type": "public_company",
            "status": "active",
        },
        # Subsidiaries
        {
            "entity_id": "cmp_apple_europe",
            "company_id": "cmp_apple_europe",
            "canonical_name": "Apple Operations Europe",
            "legal_name": "Apple Operations Europe Limited",
            "primary_country_code": "IE",
            "organization_type": "subsidiary",
            "status": "active",
        },
        {
            "entity_id": "cmp_bmw_us",
            "company_id": "cmp_bmw_us",
            "canonical_name": "BMW Manufacturing Co., LLC",
            "legal_name": "BMW Manufacturing Corporation",
            "primary_country_code": "US",
            "organization_type": "subsidiary",
            "status": "active",
        },
        {
            "entity_id": "cmp_bmw_motoren",
            "company_id": "cmp_bmw_motoren",
            "canonical_name": "BMW Motoren GmbH",
            "legal_name": "BMW Motoren GmbH",
            "primary_country_code": "AT",
            "organization_type": "subsidiary",
            "status": "active",
        },
        # Canonical Test Entities for Reference Fixtures (Fixtures A - O)
        {
            "entity_id": "TEST_COMPANY_A",
            "company_id": "TEST_COMPANY_A",
            "canonical_name": "Test Company Alpha",
            "legal_name": "Test Company Alpha Corp",
            "tickers": ["TCMA"],
            "primary_country_code": "US",
            "organization_type": "public_company",
            "status": "active",
        },
        {
            "entity_id": "TEST_ENTITY_B",
            "company_id": "TEST_ENTITY_B",
            "canonical_name": "Test Entity Beta",
            "legal_name": "Test Entity Beta LLC",
            "primary_country_code": "GB",
            "organization_type": "private_company",
            "status": "active",
        },
        {
            "entity_id": "TEST_PARENT_P",
            "company_id": "TEST_PARENT_P",
            "canonical_name": "Test Parent P",
            "legal_name": "Test Parent P Holdings",
            "primary_country_code": "US",
            "organization_type": "public_company",
            "status": "active",
        },
        {
            "entity_id": "TEST_SUBSIDIARY_S",
            "company_id": "TEST_SUBSIDIARY_S",
            "canonical_name": "Test Subsidiary S",
            "legal_name": "Test Subsidiary S Inc.",
            "primary_country_code": "DE",
            "organization_type": "subsidiary",
            "status": "active",
        },
        {
            "entity_id": "TEST_COMPARE_A",
            "company_id": "TEST_COMPARE_A",
            "canonical_name": "Compare Corp Alpha",
            "tickers": ["CCPA"],
            "primary_country_code": "US",
            "organization_type": "public_company",
            "status": "active",
        },
        {
            "entity_id": "TEST_COMPARE_B",
            "company_id": "TEST_COMPARE_B",
            "canonical_name": "Compare Corp Beta",
            "tickers": ["CCPB"],
            "primary_country_code": "DE",
            "organization_type": "public_company",
            "status": "active",
        },
        {
            "entity_id": "TEST_MULTI_SEC_ISSUER",
            "company_id": "TEST_MULTI_SEC_ISSUER",
            "canonical_name": "Multi Security Issuer",
            "tickers": ["MSIA", "MSIB"],
            "primary_country_code": "US",
            "organization_type": "public_company",
            "status": "active",
        },
    ]


def get_canonical_corporate_edges() -> list[dict]:
    """Return corporate relationships connecting parents to subsidiaries."""
    return [
        {
            "source_entity_id": "cmp_apple",
            "target_entity_id": "cmp_apple_europe",
            "relationship_type": "PARENT_OF",
            "is_current": True,
        },
        {
            "source_entity_id": "cmp_bmw",
            "target_entity_id": "cmp_bmw_us",
            "relationship_type": "PARENT_OF",
            "is_current": True,
        },
        {
            "source_entity_id": "cmp_bmw",
            "target_entity_id": "cmp_bmw_motoren",
            "relationship_type": "PARENT_OF",
            "is_current": True,
        },
        {
            "source_entity_id": "TEST_PARENT_P",
            "target_entity_id": "TEST_SUBSIDIARY_S",
            "relationship_type": "PARENT_OF",
            "is_current": True,
        },
    ]


def get_canonical_seed_facilities() -> list[CorporateFacility]:
    """Return verified canonical corporate facilities with grounded sources."""
    base_date = datetime.datetime(2024, 1, 15, tzinfo=datetime.timezone.utc)

    return [
        # --- Apple Facilities ---
        CorporateFacility(
            facility_id="fac_appl_apple_park",
            canonical_name="Apple Park",
            facility_type=CorporateFacilityType.CORPORATE_HEADQUARTERS,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POLYGON,
            country_code="US",
            administrative_region="California",
            locality="Cupertino",
            address_text="One Apple Park Way, Cupertino, CA 95014",
            longitude=-122.0090,
            latitude=37.3349,
            geometry_type="POLYGON",
            coordinates=[[
                [-122.0120, 37.3325],
                [-122.0060, 37.3325],
                [-122.0060, 37.3375],
                [-122.0120, 37.3375],
                [-122.0120, 37.3325],
            ]],
            primary_entity_id="cmp_apple",
            source_manifest_id="src_sec_edgar_10k",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_appl_hq_1",
                    facility_id="fac_appl_apple_park",
                    legal_entity_id="cmp_apple",
                    company_id="cmp_apple",
                    relationship_type=FacilityRelationshipType.HEADQUARTERS_OF,
                    role_description="Principal Executive Office and Corporate Headquarters",
                    valid_from=base_date,
                    verification_status=VerificationStatus.VERIFIED,
                ),
                FacilityEntityLink(
                    link_id="link_appl_own_1",
                    facility_id="fac_appl_apple_park",
                    legal_entity_id="cmp_apple",
                    company_id="cmp_apple",
                    relationship_type=FacilityRelationshipType.OWNED_BY,
                    role_description="Campus owned and occupied by Apple Inc.",
                    valid_from=base_date,
                    verification_status=VerificationStatus.VERIFIED,
                ),
            ],
            evidence_claims=[
                FacilityEvidenceClaim(
                    claim_id="clm_appl_hq_1",
                    facility_id="fac_appl_apple_park",
                    subject_entity_id="cmp_apple",
                    predicate="headquartered_at",
                    source_title="Apple Inc. Form 10-K for Fiscal Year Ended September 30, 2023",
                    source_document_id="sec_edgar_0000320193_23_000106",
                    publisher="U.S. Securities and Exchange Commission",
                    publication_date=datetime.datetime(2023, 11, 3, tzinfo=datetime.timezone.utc),
                    exact_evidence_span="The Company's principal executive offices are located at One Apple Park Way, Cupertino, California 95014.",
                    document_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019323000106/aapl-20230930.htm",
                )
            ],
            status_history=[
                FacilityStatusHistory(
                    history_id="hist_appl_hq_1",
                    facility_id="fac_appl_apple_park",
                    status=CorporateFacilityStatus.OPERATIONAL,
                    valid_from=datetime.datetime(2017, 4, 1, tzinfo=datetime.timezone.utc),
                    verification_status=VerificationStatus.VERIFIED,
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_appl_infinite_loop",
            canonical_name="Apple Infinite Loop",
            facility_type=CorporateFacilityType.CORPORATE_OFFICE,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="US",
            administrative_region="California",
            locality="Cupertino",
            address_text="1 Infinite Loop, Cupertino, CA 95014",
            longitude=-122.0322,
            latitude=37.3318,
            primary_entity_id="cmp_apple",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_appl_inf_1",
                    facility_id="fac_appl_infinite_loop",
                    legal_entity_id="cmp_apple",
                    company_id="cmp_apple",
                    relationship_type=FacilityRelationshipType.OCCUPIED_BY,
                    role_description="Engineering and Corporate Offices",
                    valid_from=datetime.datetime(1993, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_appl_austin",
            canonical_name="Apple Austin Campus",
            facility_type=CorporateFacilityType.REGIONAL_HEADQUARTERS,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="US",
            administrative_region="Texas",
            locality="Austin",
            address_text="12545 Riata Vista Circle, Austin, TX 78727",
            longitude=-97.7431,
            latitude=30.4015,
            primary_entity_id="cmp_apple",
            source_manifest_id="src_sec_edgar_10k",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_appl_tx_1",
                    facility_id="fac_appl_austin",
                    legal_entity_id="cmp_apple",
                    company_id="cmp_apple",
                    relationship_type=FacilityRelationshipType.OPERATED_BY,
                    role_description="Americas Operations and Engineering Center",
                    valid_from=datetime.datetime(2014, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_appl_cork",
            canonical_name="Apple European Operations (Hollyhill)",
            facility_type=CorporateFacilityType.REGIONAL_HEADQUARTERS,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="IE",
            administrative_region="Munster",
            locality="Cork",
            address_text="Hollyhill Industrial Estate, Cork, Ireland",
            longitude=-8.4958,
            latitude=51.9036,
            primary_entity_id="cmp_apple_europe",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_appl_cork_1",
                    facility_id="fac_appl_cork",
                    legal_entity_id="cmp_apple_europe",
                    company_id="cmp_apple",
                    relationship_type=FacilityRelationshipType.OPERATED_BY,
                    role_description="European Operations and Manufacturing Center",
                    valid_from=datetime.datetime(1980, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_appl_munich",
            canonical_name="Apple European Silicon Design Center",
            facility_type=CorporateFacilityType.RESEARCH_AND_DEVELOPMENT,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="DE",
            administrative_region="Bavaria",
            locality="Munich",
            address_text="Karlstrasse 28, 80333 Munich, Germany",
            longitude=11.5580,
            latitude=48.1402,
            primary_entity_id="cmp_apple",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_appl_mun_1",
                    facility_id="fac_appl_munich",
                    legal_entity_id="cmp_apple",
                    company_id="cmp_apple",
                    relationship_type=FacilityRelationshipType.OCCUPIED_BY,
                    role_description="Silicon design, power management, and cellular engineering hub",
                    valid_from=datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        # --- Alphabet Facilities ---
        CorporateFacility(
            facility_id="fac_goog_plex",
            canonical_name="Googleplex",
            facility_type=CorporateFacilityType.CORPORATE_HEADQUARTERS,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POLYGON,
            country_code="US",
            administrative_region="California",
            locality="Mountain View",
            address_text="1600 Amphitheatre Parkway, Mountain View, CA 94043",
            longitude=-122.0842,
            latitude=37.4220,
            geometry_type="POLYGON",
            coordinates=[[
                [-122.0880, 37.4200],
                [-122.0800, 37.4200],
                [-122.0800, 37.4250],
                [-122.0880, 37.4250],
                [-122.0880, 37.4200],
            ]],
            primary_entity_id="cmp_alphabet",
            source_manifest_id="src_sec_edgar_10k",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_goog_hq_1",
                    facility_id="fac_goog_plex",
                    legal_entity_id="cmp_alphabet",
                    company_id="cmp_alphabet",
                    relationship_type=FacilityRelationshipType.HEADQUARTERS_OF,
                    role_description="Principal Executive Offices and Global Headquarters",
                    valid_from=datetime.datetime(2004, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_goog_pier57",
            canonical_name="Google Pier 57",
            facility_type=CorporateFacilityType.CORPORATE_OFFICE,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="US",
            administrative_region="New York",
            locality="New York",
            address_text="25 11th Ave, New York, NY 10011",
            longitude=-74.0094,
            latitude=40.7433,
            primary_entity_id="cmp_alphabet",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_goog_ny_1",
                    facility_id="fac_goog_pier57",
                    legal_entity_id="cmp_alphabet",
                    company_id="cmp_alphabet",
                    relationship_type=FacilityRelationshipType.LEASED_BY,
                    role_description="New York Engineering & Business Office",
                    valid_from=datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_goog_london",
            canonical_name="Google Kings Cross Hub",
            facility_type=CorporateFacilityType.REGIONAL_HEADQUARTERS,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="GB",
            administrative_region="Greater London",
            locality="London",
            address_text="6 Pancras Square, London N1C 4AG, United Kingdom",
            longitude=-0.1246,
            latitude=51.5348,
            primary_entity_id="cmp_alphabet",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_goog_lon_1",
                    facility_id="fac_goog_london",
                    legal_entity_id="cmp_alphabet",
                    company_id="cmp_alphabet",
                    relationship_type=FacilityRelationshipType.OPERATED_BY,
                    role_description="UK & EMEA Engineering Headquarters",
                    valid_from=datetime.datetime(2016, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_goog_zurich",
            canonical_name="Google Zurich Engineering Hub",
            facility_type=CorporateFacilityType.RESEARCH_AND_DEVELOPMENT,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="CH",
            administrative_region="Zurich",
            locality="Zurich",
            address_text="Brandschenkestrasse 110, 8002 Zurich, Switzerland",
            longitude=8.5287,
            latitude=47.3667,
            primary_entity_id="cmp_alphabet",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_goog_zh_1",
                    facility_id="fac_goog_zurich",
                    legal_entity_id="cmp_alphabet",
                    company_id="cmp_alphabet",
                    relationship_type=FacilityRelationshipType.OCCUPIED_BY,
                    role_description="AI, Search and Cloud Engineering Center",
                    valid_from=datetime.datetime(2008, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        # --- BMW Facilities ---
        CorporateFacility(
            facility_id="fac_bmw_hq",
            canonical_name="BMW Vierzylder Headquarters",
            facility_type=CorporateFacilityType.CORPORATE_HEADQUARTERS,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="DE",
            administrative_region="Bavaria",
            locality="Munich",
            address_text="Petuelring 130, 80809 Munich, Germany",
            longitude=11.5597,
            latitude=48.1772,
            primary_entity_id="cmp_bmw",
            source_manifest_id="src_gleif_lei",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_bmw_hq_1",
                    facility_id="fac_bmw_hq",
                    legal_entity_id="cmp_bmw",
                    company_id="cmp_bmw",
                    relationship_type=FacilityRelationshipType.HEADQUARTERS_OF,
                    role_description="Global Corporate Headquarters and Executive Seat",
                    valid_from=datetime.datetime(1973, 5, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_bmw_munich_plant",
            canonical_name="BMW Group Plant Munich",
            facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="DE",
            administrative_region="Bavaria",
            locality="Munich",
            address_text="Dossenhain 1, 80809 Munich, Germany",
            longitude=11.5721,
            latitude=48.1798,
            primary_entity_id="cmp_bmw",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_bmw_mun_pl_1",
                    facility_id="fac_bmw_munich_plant",
                    legal_entity_id="cmp_bmw",
                    company_id="cmp_bmw",
                    relationship_type=FacilityRelationshipType.OPERATED_BY,
                    role_description="Automotive assembly and electric drive manufacturing",
                    valid_from=datetime.datetime(1922, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_bmw_spartanburg",
            canonical_name="BMW Plant Spartanburg",
            facility_type=CorporateFacilityType.ASSEMBLY_FACILITY,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="US",
            administrative_region="South Carolina",
            locality="Greer",
            address_text="1400 Highway 101 S, Greer, SC 29651",
            longitude=-82.1936,
            latitude=34.8967,
            primary_entity_id="cmp_bmw_us",
            source_manifest_id="src_sec_edgar_10k",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_bmw_spart_1",
                    facility_id="fac_bmw_spartanburg",
                    legal_entity_id="cmp_bmw_us",
                    company_id="cmp_bmw",
                    relationship_type=FacilityRelationshipType.OPERATED_BY,
                    role_description="Global production hub for BMW X models",
                    valid_from=datetime.datetime(1994, 9, 8, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
        CorporateFacility(
            facility_id="fac_bmw_steyr",
            canonical_name="BMW Group Plant Steyr",
            facility_type=CorporateFacilityType.MANUFACTURING_FACILITY,
            facility_status=CorporateFacilityStatus.OPERATIONAL,
            precision_class=GeographicPrecisionClass.VERIFIED_SITE_POINT,
            country_code="AT",
            administrative_region="Upper Austria",
            locality="Steyr",
            address_text="Hinterbergstrasse 2, 4400 Steyr, Austria",
            longitude=14.4175,
            latitude=48.0538,
            primary_entity_id="cmp_bmw_motoren",
            source_manifest_id="src_company_ir_disclosures",
            verification_status=VerificationStatus.VERIFIED,
            links=[
                FacilityEntityLink(
                    link_id="link_bmw_steyr_1",
                    facility_id="fac_bmw_steyr",
                    legal_entity_id="cmp_bmw_motoren",
                    company_id="cmp_bmw",
                    relationship_type=FacilityRelationshipType.OPERATED_BY,
                    role_description="Engine and e-mobility drive unit development and production",
                    valid_from=datetime.datetime(1979, 1, 1, tzinfo=datetime.timezone.utc),
                )
            ],
        ),
    ]


def create_reference_test_service() -> Any:
    """Create a fully initialized AtlasCorporateGeoService with canonical seed data and test fixtures."""
    from atlas.maps.corporate.entities.resolver import CanonicalEntityResolver
    from atlas.maps.corporate.facilities.registry import CorporateFacilityRegistry
    from atlas.maps.corporate.service import AtlasCorporateGeoService

    resolver = CanonicalEntityResolver(get_canonical_seed_entities())
    registry = CorporateFacilityRegistry(get_canonical_seed_facilities())
    edges = get_canonical_corporate_edges()

    return AtlasCorporateGeoService(
        resolver=resolver,
        registry=registry,
        corporate_edges=edges,
    )

