"""Canonical Knowledge Graph Seed Fixtures (Stage 136).

Provides 20 institutional validation fixtures (Fixtures A through T):
- Fixture A: Earnings Issuer Linking (ANNOUNCED_BY, no security explosion)
- Fixture B: Multiple Share Classes (issuer event does not fabricate distinct equity class edges)
- Fixture C: Sanctions Exact Match / Collision Avoidance (innocent similarly-named firms excluded)
- Fixture D: Central Bank Decision (DECIDED_BY, HAS_ISSUING_JURISDICTION)
- Fixture E: Economic Indicator Series (RELEASES_INDICATOR, statistical agency)
- Fixture F: Corporate Action Roles (Acquirer vs Target vs Regulator)
- Fixture G: Multi-Hop Subsidiary to Parent (Event -> Sub -> Parent without false relabeling)
- Fixture H: Earthquake Proximity (GEOGRAPHICALLY_NEAR with distance km, strictly NO DAMAGED edge)
- Fixture I: Geographic Precision / Missing Coordinate Protection (country-level event has no asset proximity)
- Fixture J: Commodity Mention (references Crude Oil without linking all derivatives)
- Fixture K: Historical Ownership (2022 query reflects 2022 parent, not changed 2024 status)
- Fixture L: Knowledge As-Of (T1 query excludes T2 amendment)
- Fixture M: Multi-Source Evidence Corroboration (1 logical edge, 3 evidence records)
- Fixture N: Disputed / Conflicting Identity (conflicting sources recorded under CONFLICTED status)
- Fixture O: Revoked Data Source (license loss revokes edge and invalidates query)
- Fixture P: Multi-Tenant Private Graph (Tenant A private edge invisible to Tenant B)
- Fixture Q: Graph Cycle Detection and Prevention (cross-holding cycle terminates cleanly)
- Fixture R: Stage 135 Event Retraction (dependent edges invalidated non-destructively)
- Fixture S: Reused Ticker Disambiguation (resolves correct entity valid at event epoch)
- Fixture T: Factual Path Explanation (Event -> Asset -> Operator with zero speculative loss claims)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List

from atlas.events.domain import (
    AtlasUniversalEvent,
    DatePrecision,
    EventCategory,
    EventGeographicScope,
    EventLifecycleStatus,
    EventVerificationStatus,
    GeographicScopeType,
)
from .domain import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    GraphNodeType,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)

if TYPE_CHECKING:
    from .service import EventEntityKnowledgeGraphService


def seed_knowledge_graph_fixtures(service: EventEntityKnowledgeGraphService):
    """Populates the service with canonical nodes, structural edges, and 20 test fixtures."""

    # =========================================================================
    # 1. Register Canonical Entity Nodes
    # =========================================================================

    # Companies & Issuers
    aapl = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-AAPL",
        canonical_name="Apple Inc.",
        identifier_map={"TICKER": "AAPL", "CIK": "0000320193", "LEI": "HW688K0W8P712W1S2P10"},
        country_code="US",
        sector="Information Technology",
    )
    service.register_canonical_node(aapl)

    googl = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-GOOGL",
        canonical_name="Alphabet Inc.",
        identifier_map={"TICKER": "GOOGL", "CIK": "0001652044", "LEI": "549300649000ALPHABET01"},
        country_code="US",
        sector="Communication Services",
    )
    service.register_canonical_node(googl)

    deepmind = CanonicalGraphNodeRef(
        node_type=GraphNodeType.LEGAL_ENTITY,
        entity_id="LEGAL-DEEPMIND-UK",
        canonical_name="Google DeepMind Technologies Limited",
        identifier_map={"CRN": "07386347", "LEI": "213800DEEPMIND000001"},
        country_code="GB",
        sector="Artificial Intelligence Research",
    )
    service.register_canonical_node(deepmind)

    msft = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-MSFT",
        canonical_name="Microsoft Corporation",
        identifier_map={"TICKER": "MSFT", "CIK": "0000789019", "LEI": "INR2EJN1ERAN0W5ZP974"},
        country_code="US",
        sector="Information Technology",
    )
    service.register_canonical_node(msft)

    atvi = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-ATVI",
        canonical_name="Activision Blizzard Inc.",
        identifier_map={"TICKER": "ATVI", "CIK": "0000718877", "LEI": "549300ATVIBLIZZARD01"},
        country_code="US",
        sector="Communication Services",
    )
    service.register_canonical_node(atvi)

    # Sanctions: Designated Entity vs Innocent Firm
    volga_ru = CanonicalGraphNodeRef(
        node_type=GraphNodeType.LEGAL_ENTITY,
        entity_id="LEGAL-VOLGA-PETRO-RU",
        canonical_name="Volga Petroleum Logistics LLC",
        identifier_map={"LEI": "984500984500VOLGAPET0", "OGRN": "1027700132190"},
        country_code="RU",
        sector="Energy Logistics",
    )
    service.register_canonical_node(volga_ru)

    volga_uk = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-VOLGA-PETRO-UK",
        canonical_name="Volga Petroleum Retail UK Ltd",
        identifier_map={"LEI": "213800VOLGAUK999999", "CRN": "09876543"},
        country_code="GB",
        sector="Retail Fuel",
    )
    service.register_canonical_node(volga_uk)

    # Financial Instruments
    aapl_stock = CanonicalGraphNodeRef(
        node_type=GraphNodeType.FINANCIAL_INSTRUMENT,
        entity_id="INSTR-AAPL-US",
        canonical_name="Apple Inc. Common Stock",
        identifier_map={"ISIN": "US0378331005", "FIGI": "BBG000B9XRY4"},
        country_code="US",
    )
    service.register_canonical_node(aapl_stock)

    googl_stock_a = CanonicalGraphNodeRef(
        node_type=GraphNodeType.FINANCIAL_INSTRUMENT,
        entity_id="INSTR-GOOGL-A",
        canonical_name="Alphabet Inc. Class A Common Stock",
        identifier_map={"ISIN": "US02079K3059", "TICKER": "GOOGL"},
        country_code="US",
    )
    service.register_canonical_node(googl_stock_a)

    googl_stock_c = CanonicalGraphNodeRef(
        node_type=GraphNodeType.FINANCIAL_INSTRUMENT,
        entity_id="INSTR-GOOG-C",
        canonical_name="Alphabet Inc. Class C Capital Stock",
        identifier_map={"ISIN": "US02079K1079", "TICKER": "GOOG"},
        country_code="US",
    )
    service.register_canonical_node(googl_stock_c)

    # Central Banks, Regulators & Agencies
    frb = CanonicalGraphNodeRef(
        node_type=GraphNodeType.CENTRAL_BANK,
        entity_id="CB-FRB",
        canonical_name="Board of Governors of the Federal Reserve System",
        identifier_map={"CODE": "FRB_US", "LEI": "549300FRBBOARD000001"},
        country_code="US",
    )
    service.register_canonical_node(frb)

    bls = CanonicalGraphNodeRef(
        node_type=GraphNodeType.REGULATORY_AUTHORITY,
        entity_id="AGENCY-BLS",
        canonical_name="U.S. Bureau of Labor Statistics",
        identifier_map={"CODE": "US_BLS"},
        country_code="US",
    )
    service.register_canonical_node(bls)

    ofac = CanonicalGraphNodeRef(
        node_type=GraphNodeType.REGULATORY_AUTHORITY,
        entity_id="REG-OFAC",
        canonical_name="Office of Foreign Assets Control (US Treasury)",
        identifier_map={"CODE": "US_OFAC"},
        country_code="US",
    )
    service.register_canonical_node(ofac)

    ftc = CanonicalGraphNodeRef(
        node_type=GraphNodeType.REGULATORY_AUTHORITY,
        entity_id="REG-FTC",
        canonical_name="Federal Trade Commission",
        identifier_map={"CODE": "US_FTC"},
        country_code="US",
    )
    service.register_canonical_node(ftc)

    # Countries
    us_country = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COUNTRY,
        entity_id="COUNTRY-US",
        canonical_name="United States of America",
        identifier_map={"ISO2": "US", "ISO3": "USA"},
    )
    service.register_canonical_node(us_country)

    jp_country = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COUNTRY,
        entity_id="COUNTRY-JP",
        canonical_name="Japan",
        identifier_map={"ISO2": "JP", "ISO3": "JPN"},
    )
    service.register_canonical_node(jp_country)

    de_country = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COUNTRY,
        entity_id="COUNTRY-DE",
        canonical_name="Federal Republic of Germany",
        identifier_map={"ISO2": "DE", "ISO3": "DEU"},
    )
    service.register_canonical_node(de_country)

    gb_country = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COUNTRY,
        entity_id="COUNTRY-GB",
        canonical_name="United Kingdom",
        identifier_map={"ISO2": "GB", "ISO3": "GBR"},
    )
    service.register_canonical_node(gb_country)

    # Indicators & Commodities
    cpi_us = CanonicalGraphNodeRef(
        node_type=GraphNodeType.ECONOMIC_INDICATOR,
        entity_id="IND-CPI-US",
        canonical_name="US Consumer Price Index (CPI)",
        identifier_map={"SERIES": "CPI_US_YOY", "INDICATOR_ID": "IND-CPI-US"},
        country_code="US",
    )
    service.register_canonical_node(cpi_us)

    brent_crude = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMMODITY,
        entity_id="COMM-BRENT-CRUDE",
        canonical_name="Brent Crude Oil",
        identifier_map={"SYMBOL": "BRENT", "COMMODITY_ID": "COMM-BRENT-CRUDE"},
    )
    service.register_canonical_node(brent_crude)

    # Infrastructure Assets & Facilities
    onagawa_npp = CanonicalGraphNodeRef(
        node_type=GraphNodeType.INFRASTRUCTURE_ASSET,
        entity_id="INFRA-ONAGAWA-NPP",
        canonical_name="Onagawa Nuclear Power Plant",
        identifier_map={"ASSET_ID": "INFRA-ONAGAWA-NPP"},
        country_code="JP",
        metadata={"latitude": 38.401, "longitude": 141.499, "type": "NUCLEAR_POWER_PLANT"},
    )
    service.register_canonical_node(onagawa_npp)

    tohk_ep = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-TOHOKU-EP",
        canonical_name="Tohoku Electric Power Company",
        identifier_map={"TICKER": "9506:JP", "LEI": "353800TOHOKUEP00001"},
        country_code="JP",
    )
    service.register_canonical_node(tohk_ep)

    colonial_pipe = CanonicalGraphNodeRef(
        node_type=GraphNodeType.INFRASTRUCTURE_ASSET,
        entity_id="INFRA-COLONIAL-PIPELINE",
        canonical_name="Colonial Pipeline System",
        identifier_map={"ASSET_ID": "INFRA-COLONIAL-PIPELINE"},
        country_code="US",
        metadata={"type": "REFINED_PRODUCTS_PIPELINE"},
    )
    service.register_canonical_node(colonial_pipe)

    colonial_co = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-COLONIAL-PIPELINE-CO",
        canonical_name="Colonial Pipeline Company",
        identifier_map={"LEI": "549300COLONIALPIPE01"},
        country_code="US",
    )
    service.register_canonical_node(colonial_co)

    tsmc = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-TSMC",
        canonical_name="Taiwan Semiconductor Manufacturing Company Limited",
        identifier_map={"TICKER": "TSM", "LEI": "549300TSMCFAB0000001"},
        country_code="TW",
    )
    service.register_canonical_node(tsmc)

    # Disputed Entities for Rumors
    iberdrola = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-IBERDROLA",
        canonical_name="Iberdrola S.A.",
        identifier_map={"TICKER": "IBE:SM", "LEI": "549300IBERDROLA00001"},
        country_code="ES",
    )
    service.register_canonical_node(iberdrola)

    enel = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-ENEL",
        canonical_name="Enel S.p.A.",
        identifier_map={"TICKER": "ENEL:IM", "LEI": "549300ENELITALIA00001"},
        country_code="IT",
    )
    service.register_canonical_node(enel)

    # Reused Ticker Entities (Fixture S)
    meta_fin = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-META-FINANCIAL",
        canonical_name="Meta Financial Group Inc.",
        identifier_map={"CIK": "0000907471"},
        country_code="US",
    )
    service.register_canonical_node(
        meta_fin,
        aliases=[{
            "type": "TICKER",
            "value": "META",
            "valid_from": datetime(2000, 1, 1, tzinfo=timezone.utc),
            "valid_to": datetime(2021, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        }],
    )

    meta_plat = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-META-PLATFORMS",
        canonical_name="Meta Platforms Inc.",
        identifier_map={"CIK": "0001326801"},
        country_code="US",
    )
    service.register_canonical_node(
        meta_plat,
        aliases=[{
            "type": "TICKER",
            "value": "META",
            "valid_from": datetime(2022, 6, 9, tzinfo=timezone.utc),
            "valid_to": None,
        }],
    )

    # Historical Ownership (Fixture K): ARM Holdings & SoftBank Group
    softbank = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-SOFTBANK",
        canonical_name="SoftBank Group Corp.",
        identifier_map={"TICKER": "9984:JP", "LEI": "353800SOFTBANK000001"},
        country_code="JP",
    )
    service.register_canonical_node(softbank)

    arm = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-ARM",
        canonical_name="ARM Holdings plc",
        identifier_map={"TICKER": "ARM", "LEI": "213800ARMHOLDINGS0001"},
        country_code="GB",
    )
    service.register_canonical_node(arm)

    # Structural Edge: ARM subsidiary of SoftBank in 2022
    service.add_structural_edge(
        source_node=arm,
        target_node=softbank,
        predicate=PredicateType.SUBSIDIARY_OF,
        relationship_role="WHOLLY_OWNED_SUBSIDIARY",
        temporal_valid_from=datetime(2016, 9, 1, tzinfo=timezone.utc),
        temporal_valid_to=datetime(2023, 9, 13, tzinfo=timezone.utc),
        knowledge_available_at=datetime(2016, 9, 1, tzinfo=timezone.utc),
        metadata={"ownership_pct": 100.0},
    )

    # Structural Edge: DeepMind subsidiary of Alphabet
    service.add_structural_edge(
        source_node=deepmind,
        target_node=googl,
        predicate=PredicateType.SUBSIDIARY_OF,
        relationship_role="RESEARCH_SUBSIDIARY",
        temporal_valid_from=datetime(2014, 1, 26, tzinfo=timezone.utc),
        knowledge_available_at=datetime(2014, 1, 26, tzinfo=timezone.utc),
        metadata={"ownership_pct": 100.0},
    )

    # Structural Edge: Onagawa NPP operated by Tohoku EP
    service.add_structural_edge(
        source_node=onagawa_npp,
        target_node=tohk_ep,
        predicate=PredicateType.OPERATED_BY,
        relationship_role="OPERATOR",
        temporal_valid_from=datetime(1984, 6, 1, tzinfo=timezone.utc),
        knowledge_available_at=datetime(1984, 6, 1, tzinfo=timezone.utc),
    )

    # Structural Edge: Colonial Pipeline operated by Colonial Pipeline Co
    service.add_structural_edge(
        source_node=colonial_pipe,
        target_node=colonial_co,
        predicate=PredicateType.OPERATED_BY,
        relationship_role="SYSTEM_OPERATOR",
        temporal_valid_from=datetime(1962, 1, 1, tzinfo=timezone.utc),
        knowledge_available_at=datetime(1962, 1, 1, tzinfo=timezone.utc),
    )

    # Structural Edge: GOOGL and GOOG issued by Alphabet
    service.add_structural_edge(
        source_node=googl_stock_a,
        target_node=googl,
        predicate=PredicateType.ISSUED_BY_COMPANY,
        relationship_role="CLASS_A_COMMON",
    )
    service.add_structural_edge(
        source_node=googl_stock_c,
        target_node=googl,
        predicate=PredicateType.ISSUED_BY_COMPANY,
        relationship_role="CLASS_C_CAPITAL",
    )

    # Cycle Detection nodes (Fixture Q)
    cycle_x = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-CYCLE-X",
        canonical_name="Cross-Holding Alpha Corp",
    )
    cycle_y = CanonicalGraphNodeRef(
        node_type=GraphNodeType.COMPANY,
        entity_id="COMP-CYCLE-Y",
        canonical_name="Cross-Holding Beta Corp",
    )
    service.register_canonical_node(cycle_x)
    service.register_canonical_node(cycle_y)

    service.add_structural_edge(
        source_node=cycle_x,
        target_node=cycle_y,
        predicate=PredicateType.SUBSIDIARY_OF,
        relationship_role="CROSS_HOLDING_LEG_1",
    )
    service.add_structural_edge(
        source_node=cycle_y,
        target_node=cycle_x,
        predicate=PredicateType.SUBSIDIARY_OF,
        relationship_role="CROSS_HOLDING_LEG_2",
    )

    # =========================================================================
    # 2. Ingest Events & Build Relationship Fixtures
    # =========================================================================

    # Fixture A: Apple Earnings (ANNOUNCED_BY, no security explosion)
    evt_a = AtlasUniversalEvent(
        event_id="EVT-EARNINGS-AAPL-2024Q3",
        canonical_event_key="EARNINGS:AAPL:2024Q3",
        event_type="EARNINGS_RELEASE",
        event_subtype="Q3_EARNINGS",
        event_category=EventCategory.FINANCIAL,
        title="Apple Reports Q3 FY2024 Financial Results",
        factual_summary="Apple announced quarterly revenue of $85.8 billion, up 5% year-over-year.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 8, 1, 20, 30, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 8, 1, 20, 31, tzinfo=timezone.utc),
        updated_at=datetime(2024, 8, 1, 20, 31, tzinfo=timezone.utc),
        primary_source_id="SRC-AAPL-PR-2024Q3",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "company_id": "COMP-AAPL",
            "ticker": "AAPL",
            "lei": "HW688K0W8P712W1S2P10",
            "primary_instrument_id": "US0378331005",
            "period": "2024Q3",
        },
    )
    service.link_event(evt_a, evidence_ids=["EVID-AAPL-10Q-2024Q3", "EVID-AAPL-PR-2024Q3"])

    # Fixture B: Issuer-Level Corporate Governance Update
    evt_b = AtlasUniversalEvent(
        event_id="EVT-CORP-GOOGL-GOV",
        canonical_event_key="GOV:GOOGL:202409",
        event_type="CORPORATE_GOVERNANCE",
        event_subtype="BOARD_APPOINTMENT",
        event_category=EventCategory.CORPORATE,
        title="Alphabet Appoints Anat Ashkenazi as Chief Financial Officer",
        factual_summary="Alphabet Inc. announced the appointment of Anat Ashkenazi as CFO.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 6, 5, 12, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 6, 5, 12, 5, tzinfo=timezone.utc),
        updated_at=datetime(2024, 6, 5, 12, 5, tzinfo=timezone.utc),
        primary_source_id="SRC-GOOGL-SEC-8K",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "initiator_id": "COMP-GOOGL",
        },
    )
    service.link_event(evt_b, evidence_ids=["EVID-GOOGL-8K-20240605"])

    # Fixture C: Sanctions Designation (Exact Match Only, Innocent UK firm excluded)
    evt_c = AtlasUniversalEvent(
        event_id="EVT-SANCTION-VOLGA-PETRO",
        canonical_event_key="SANCTION:US:VOLGA-PETRO:2024",
        event_type="SANCTION_DESIGNATION",
        event_subtype="OFAC_SDN_ADDITION",
        event_category=EventCategory.SANCTIONS,
        title="OFAC Designates Volga Petroleum Logistics LLC under Russia Sanctions",
        factual_summary="US Treasury OFAC added Volga Petroleum Logistics LLC to the SDN list.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 5, 1, 14, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 5, 1, 14, 2, tzinfo=timezone.utc),
        updated_at=datetime(2024, 5, 1, 14, 2, tzinfo=timezone.utc),
        primary_source_id="SRC-OFAC-NOTICE-20240501",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "authority_id": "REG-OFAC",
            "designated_entity_id": "LEGAL-VOLGA-PETRO-RU",
            "designated_lei": "984500984500VOLGAPET0",
            "program": "RUSSIA-EO14024",
        },
    )
    service.link_event(evt_c, evidence_ids=["EVID-OFAC-SDN-20240501"])

    # Fixture D: Federal Reserve Rate Decision
    evt_d = AtlasUniversalEvent(
        event_id="EVT-FOMC-20230726",
        canonical_event_key="FOMC:RATE:20230726",
        event_type="MONETARY_POLICY_DECISION",
        event_subtype="RATE_INCREASE",
        event_category=EventCategory.MONETARY_POLICY,
        title="Federal Reserve Increases Target Range for Federal Funds Rate by 25 bps",
        factual_summary="The FOMC decided to raise the target range for the federal funds rate to 5.25 to 5.50 percent.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2023, 7, 26, 18, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2023, 7, 26, 18, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 7, 26, 18, 1, tzinfo=timezone.utc),
        primary_source_id="SRC-FRB-STMT-20230726",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "central_bank_id": "CB-FRB",
            "rate_change_bps": 25,
            "decision_type": "HIKE",
        },
    )
    service.link_event(evt_d, evidence_ids=["EVID-FRB-STMT-20230726"])

    # Fixture E: US CPI Release
    evt_e = AtlasUniversalEvent(
        event_id="EVT-CPI-US-202406",
        canonical_event_key="ECON:CPI:US:202406",
        event_type="ECONOMIC_INDICATOR_RELEASE",
        event_subtype="CPI_REPORT",
        event_category=EventCategory.ECONOMIC,
        title="BLS Releases June 2024 Consumer Price Index",
        factual_summary="The Consumer Price Index for All Urban Consumers (CPI-U) was unchanged in June on a seasonally adjusted basis.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 7, 11, 12, 30, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 7, 11, 12, 31, tzinfo=timezone.utc),
        updated_at=datetime(2024, 7, 11, 12, 31, tzinfo=timezone.utc),
        primary_source_id="SRC-BLS-CPI-202406",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "indicator_id": "IND-CPI-US",
            "agency_id": "AGENCY-BLS",
            "actual_value": 3.0,
            "prior_value": 3.3,
        },
    )
    service.link_event(evt_e, evidence_ids=["EVID-BLS-CPI-202406"])

    # Fixture F: Microsoft / Activision Merger Completion
    evt_f = AtlasUniversalEvent(
        event_id="EVT-MERGER-MSFT-ATVI",
        canonical_event_key="MERGER:MSFT:ATVI:202310",
        event_type="M_AND_A_COMPLETION",
        event_subtype="ACQUISITION_CLOSED",
        event_category=EventCategory.CORPORATE,
        title="Microsoft Completes Acquisition of Activision Blizzard",
        factual_summary="Microsoft Corporation closed its $68.7 billion acquisition of Activision Blizzard Inc.",
        lifecycle_status=EventLifecycleStatus.CONFIRMED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2023, 10, 13, 13, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2023, 10, 13, 13, 5, tzinfo=timezone.utc),
        updated_at=datetime(2023, 10, 13, 13, 5, tzinfo=timezone.utc),
        primary_source_id="SRC-MSFT-SEC-8K-20231013",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "acquirer_id": "COMP-MSFT",
            "target_id": "COMP-ATVI",
            "regulator_id": "REG-FTC",
            "deal_value_usd": 68700000000,
        },
    )
    service.link_event(evt_f, evidence_ids=["EVID-MSFT-8K-20231013", "EVID-ATVI-FORM15-20231013"])

    # Fixture G: DeepMind Gemini Launch (Subsidiary release)
    evt_g = AtlasUniversalEvent(
        event_id="EVT-PRODUCT-DEEPMIND-GEMINI",
        canonical_event_key="PRODUCT:DEEPMIND:GEMINI:202312",
        event_type="PRODUCT_RELEASE",
        event_subtype="MODEL_FAMILY_ANNOUNCEMENT",
        event_category=EventCategory.CORPORATE,
        title="Google DeepMind Introduces Gemini 1.0",
        factual_summary="Google DeepMind unveiled Gemini, a new foundational multimodal model family.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2023, 12, 6, 14, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2023, 12, 6, 14, 2, tzinfo=timezone.utc),
        updated_at=datetime(2023, 12, 6, 14, 2, tzinfo=timezone.utc),
        primary_source_id="SRC-DEEPMIND-BLOG-20231206",
        geographic_scope=EventGeographicScope(country_code="GB"),
        event_payload={
            "initiator_id": "LEGAL-DEEPMIND-UK",
        },
    )
    service.link_event(evt_g, evidence_ids=["EVID-DEEPMIND-BLOG-20231206"])

    # Fixture H: Earthquake Proximity (GEOGRAPHICALLY_NEAR, strictly NO DAMAGED)
    evt_h = AtlasUniversalEvent(
        event_id="EVT-QUAKE-SENDAI-2024",
        canonical_event_key="QUAKE:USGS:SENDAI:20240408",
        event_type="NATURAL_EVENT",
        event_subtype="EARTHQUAKE",
        event_category=EventCategory.NATURAL_DISASTER,
        title="M6.8 Earthquake off the Coast of Sendai, Miyagi Prefecture",
        factual_summary="USGS recorded a magnitude 6.8 earthquake at coordinates (38.30N, 142.40E), depth 40km.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 4, 8, 9, 30, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 4, 8, 9, 32, tzinfo=timezone.utc),
        updated_at=datetime(2024, 4, 8, 9, 32, tzinfo=timezone.utc),
        primary_source_id="SRC-USGS-EQ-20240408",
        geographic_scope=EventGeographicScope(
            scope_type=GeographicScopeType.POINT,
            country_code="JP",
            latitude=38.30,
            longitude=142.40,
            coordinates=[142.40, 38.30],
        ),
        event_payload={
            "magnitude": 6.8,
            "proximity_radius_km": 150.0,
        },
    )
    service.link_event(evt_h, evidence_ids=["EVID-USGS-20240408", "EVID-JMA-20240408"])

    # Fixture I: Country-Level Coarse Event (No fabricated asset proximity)
    evt_i = AtlasUniversalEvent(
        event_id="EVT-TAX-DE-2024",
        canonical_event_key="TAX:DE:GROWTH_OPPORTUNITIES:2024",
        event_type="LEGISLATIVE_REFORM",
        event_subtype="CORPORATE_TAX_LAW",
        event_category=EventCategory.REGULATORY,
        title="German Bundestag Passes Growth Opportunities Act",
        factual_summary="Federal tax package includes corporate investment premiums and extended loss carry-forwards.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 3, 22, 11, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 3, 22, 11, 10, tzinfo=timezone.utc),
        updated_at=datetime(2024, 3, 22, 11, 10, tzinfo=timezone.utc),
        primary_source_id="SRC-BUNDESTAG-20240322",
        geographic_scope=EventGeographicScope(
            scope_type=GeographicScopeType.COUNTRY,
            country_code="DE",
        ),
        event_payload={},
    )
    service.link_event(evt_i, evidence_ids=["EVID-BUNDESTAG-20240322"])

    # Fixture J: OPEC+ Output Quota Reduction (Commodity Mention)
    evt_j = AtlasUniversalEvent(
        event_id="EVT-OPEC-2024Q2",
        canonical_event_key="OPEC:QUOTA:202406",
        event_type="COMMODITY_AGREEMENT",
        event_subtype="SUPPLY_QUOTA",
        event_category=EventCategory.GEOPOLITICAL,
        title="OPEC+ Extends Voluntary Crude Oil Output Cuts Through 2025",
        factual_summary="OPEC and non-OPEC ministerial meeting agreed to extend total crude cuts.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 6, 2, 16, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 6, 2, 16, 5, tzinfo=timezone.utc),
        updated_at=datetime(2024, 6, 2, 16, 5, tzinfo=timezone.utc),
        primary_source_id="SRC-OPEC-PR-20240602",
        geographic_scope=EventGeographicScope(country_code="AT"),
        event_payload={"commodity_id": "COMM-BRENT-CRUDE"},
    )
    evt_j_node = service._linkers[EventCategory.GEOPOLITICAL].create_event_node(evt_j)
    brent_node = service.resolver.get_node(GraphNodeType.COMMODITY, "COMM-BRENT-CRUDE")
    if brent_node:
        service.add_relationship(
            AtlasEventEntityRelationship(
                relationship_id="rel-opec-brent-01",
                event_id=evt_j.event_id,
                source_node=evt_j_node,
                target_node=brent_node,
                predicate=PredicateType.REFERENCES_COMMODITY,
                assertion_origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
                verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                evidence_ids=["EVID-OPEC-PR-20240602"],
                derivation_method="COMMODITY_MENTION",
            )
        )

    # Fixture L: Point-in-Time Knowledge As-Of (T1 vs T2 Revision)
    evt_l = AtlasUniversalEvent(
        event_id="EVT-FILING-TESLA-SEC",
        canonical_event_key="FILING:TSLA:8K:202401",
        event_type="REGULATORY_FILING",
        event_subtype="SEC_8K",
        event_category=EventCategory.REGULATORY,
        title="SEC Form 8-K Filing",
        factual_summary="Initial 8-K disclosure filed.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 1, 10, 10, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 1, 10, 10, 5, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 10, 10, 5, tzinfo=timezone.utc),
        primary_source_id="SRC-SEC-TSLA-20240110",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={"regulator_id": "REG-FTC"},
    )
    service.link_event(evt_l, evidence_ids=["EVID-TSLA-8K-INITIAL"])

    # Future amendment known only at T2
    t2_rel = AtlasEventEntityRelationship(
        relationship_id="rel-tsla-amendment-t2",
        event_id=evt_l.event_id,
        source_node=service._linkers[EventCategory.REGULATORY].create_event_node(evt_l),
        target_node=aapl,  # hypothetical amendment cross-reference
        predicate=PredicateType.EXPLICITLY_MENTIONS,
        assertion_origin=RelationshipOrigin.REGULATORY_FILING,
        verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
        knowledge_available_at=datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc),  # T2 in future
        temporal_valid_from=datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc),
        evidence_ids=["EVID-TSLA-8K-AMENDMENT"],
    )
    service.add_relationship(t2_rel)

    # Fixture M: Multi-Source Corroboration (1 logical edge, 3 evidence IDs)
    evt_m = AtlasUniversalEvent(
        event_id="EVT-TSMC-AZ-FAB",
        canonical_event_key="FACILITY:TSMC:AZ_PROD:2024",
        event_type="FACILITY_COMMISSIONING",
        event_subtype="COMMERCIAL_PRODUCTION",
        event_category=EventCategory.INFRASTRUCTURE,
        title="TSMC Completes Trial Production Runs at Arizona Fab 21",
        factual_summary="TSMC achieved production yields comparable to Taiwan facilities.",
        lifecycle_status=EventLifecycleStatus.CONFIRMED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 9, 5, 8, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 9, 5, 8, 10, tzinfo=timezone.utc),
        updated_at=datetime(2024, 9, 5, 8, 10, tzinfo=timezone.utc),
        primary_source_id="SRC-TSMC-SEC-6K",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={"company_id": "COMP-TSMC"},
    )
    service.link_event(
        evt_m,
        evidence_ids=["EVID-TSMC-6K-202409", "EVID-TSMC-PRESS-RELEASE", "EVID-NIKKEI-DISPATCH"],
    )

    # Fixture N: Disputed / Conflicting Identity Rumor
    evt_n = AtlasUniversalEvent(
        event_id="EVT-RUMOR-EU-UTIL",
        canonical_event_key="RUMOR:M_AND_A:EU_UTILITY:2024",
        event_type="UNCONFIRMED_RUMOR",
        event_subtype="TAKEOVER_SPECULATION",
        event_category=EventCategory.NEWS_REPORTED,
        title="Market Rumor: Potential Bidding War for Regional Iberian Grid Asset",
        factual_summary="Conflicting reports cite Iberdrola and Enel as rival bidders.",
        lifecycle_status=EventLifecycleStatus.REPORTED,
        verification_status=EventVerificationStatus.CONFLICTED,
        occurred_at=datetime(2024, 8, 20, 15, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 8, 20, 15, 5, tzinfo=timezone.utc),
        updated_at=datetime(2024, 8, 20, 15, 5, tzinfo=timezone.utc),
        primary_source_id="SRC-MARKET-CHATTER",
        geographic_scope=EventGeographicScope(country_code="ES"),
        event_payload={"is_rumor": True, "mentioned_entities": ["COMP-IBERDROLA", "COMP-ENEL"]},
    )
    service.link_event(evt_n, evidence_ids=["EVID-RUMOR-BLOG", "EVID-TRADER-CHAT"])

    # Fixture O: Revoked Data Source
    evt_o = AtlasUniversalEvent(
        event_id="EVT-LEAK-DEFENSE",
        canonical_event_key="LEAK:DEFENSE:PROJECT_X:2024",
        event_type="UNAUTHORIZED_LEAK",
        event_subtype="PROPRIETARY_LEAK",
        event_category=EventCategory.NEWS_REPORTED,
        title="Unauthorized Leak Regarding Advanced Aerospace Contract",
        factual_summary="Unverified document posted to message board alleging contract award.",
        lifecycle_status=EventLifecycleStatus.REPORTED,
        verification_status=EventVerificationStatus.UNVERIFIED,
        first_ingested_at=datetime(2024, 7, 1, 10, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 7, 1, 10, 0, tzinfo=timezone.utc),
        primary_source_id="SRC-UNAUTH-LEAK",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={"company_id": "COMP-MSFT"},
    )
    service.link_event(evt_o, evidence_ids=["EVID-UNAUTH-LEAK"])
    # Find that relationship and revoke it due to revoked source authorization
    o_neighbors = service.get_event_neighbors("EVT-LEAK-DEFENSE")
    if o_neighbors:
        service.revoke_relationship(
            relationship_id=o_neighbors[0].relationship_id,
            reason="Source SRC-UNAUTH-LEAK was de-authorized and license revoked.",
        )

    # Fixture P: Multi-Tenant Private Relationship
    evt_p = AtlasUniversalEvent(
        event_id="EVT-TENANT-ALPHA-NOTE",
        canonical_event_key="PRIVATE:TENANT_ALPHA:2024",
        event_type="INTERNAL_RESEARCH",
        event_subtype="ANALYST_NOTE",
        event_category=EventCategory.CORPORATE,
        title="Alpha Fund Confidential Field Assessment of Apple Supply Chain",
        factual_summary="Proprietary analyst channel check on component yields.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.SOURCE_REPORTED,
        first_ingested_at=datetime(2024, 8, 10, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 8, 10, 9, 0, tzinfo=timezone.utc),
        primary_source_id="SRC-ALPHA-INTERNAL",
        geographic_scope=EventGeographicScope(country_code="US"),
        tenant_id="tenant-alpha-fund",
        event_payload={"company_id": "COMP-AAPL"},
    )
    service.link_event(evt_p, evidence_ids=["EVID-ALPHA-RESEARCH-NOTE"])

    # Fixture R: Retracted Event Edge Invalidation
    evt_r = AtlasUniversalEvent(
        event_id="EVT-RETRACTED-TSUNAMI-FALSE",
        canonical_event_key="WARNING:TSUNAMI:FALSE_ALARM:2024",
        event_type="WEATHER_WARNING",
        event_subtype="FALSE_ALARM",
        event_category=EventCategory.NATURAL_DISASTER,
        title="False Tsunami Warning Siren Triggered in Honshu",
        factual_summary="System malfunction generated an errant advisory that was retracted within 6 minutes.",
        lifecycle_status=EventLifecycleStatus.RETRACTED,
        verification_status=EventVerificationStatus.REJECTED,
        first_ingested_at=datetime(2024, 5, 12, 4, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 5, 12, 4, 10, tzinfo=timezone.utc),
        primary_source_id="SRC-JMA-ERR-2024",
        geographic_scope=EventGeographicScope(country_code="JP"),
        is_retracted=True,
        retraction_reason="False alarm trigger issued in error by telemetry test.",
        event_payload={"country_code": "JP"},
    )
    service.link_event(evt_r, evidence_ids=["EVID-JMA-ERR-NOTICE"])
    service.handle_event_retraction(
        event_id="EVT-RETRACTED-TSUNAMI-FALSE",
        reason="Errant sensor alert retracted by national meteorological agency.",
    )

    # Fixture T: Factual Multi-Hop Path Explanation
    evt_t = AtlasUniversalEvent(
        event_id="EVT-PIPELINE-OUTAGE-COLONIAL",
        canonical_event_key="OUTAGE:COLONIAL:PIPELINE:2024",
        event_type="INFRASTRUCTURE_DISRUPTION",
        event_subtype="MAINTENANCE_SHUTDOWN",
        event_category=EventCategory.INFRASTRUCTURE,
        title="Colonial Pipeline Line 1 Precautionary Flow Curtailment",
        factual_summary="Operator Colonial Pipeline Co initiated scheduled valve inspection.",
        lifecycle_status=EventLifecycleStatus.OCCURRED,
        verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
        occurred_at=datetime(2024, 7, 18, 6, 0, tzinfo=timezone.utc),
        first_ingested_at=datetime(2024, 7, 18, 6, 5, tzinfo=timezone.utc),
        updated_at=datetime(2024, 7, 18, 6, 5, tzinfo=timezone.utc),
        primary_source_id="SRC-COLONIAL-NOTICE-20240718",
        geographic_scope=EventGeographicScope(country_code="US"),
        event_payload={
            "asset_id": "INFRA-COLONIAL-PIPELINE",
            "operator_id": "COMP-COLONIAL-PIPELINE-CO",
        },
    )
    service.link_event(evt_t, evidence_ids=["EVID-COLONIAL-NOTICE-20240718"])

