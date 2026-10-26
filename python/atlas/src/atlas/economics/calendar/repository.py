"""Canonical In-Memory Repository for Global Economic Calendar (Stage 92)."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List

from .enums import (
    AlertStatus,
    EconomicEventCategory,
    EconomicEventImportance,
    EconomicEventKind,
    EconomicEventStatus,
    ForecastAggregationMethod,
    ReleaseStage,
    SchedulePrecision,
)
from .errors import EconomicEventAlertNotFoundError, EconomicEventNotFoundError
from .models import (
    AlertDeliveryIntent,
    ConsensusSnapshot,
    EconomicCalendarEvent,
    EconomicEventObservation,
    EconomicReleaseFamily,
    ScheduleRevision,
    UserEventAlert,
)


class EconomicCalendarRepository:
    """In-memory canonical storage for economic calendar events, families, and alerts."""

    def __init__(self):
        self._families: Dict[str, EconomicReleaseFamily] = {}
        self._events: Dict[str, EconomicCalendarEvent] = {}
        self._alerts: Dict[str, UserEventAlert] = {}
        self._intents: List[AlertDeliveryIntent] = []
        self._seed_canonical_data()

    # -------------------------------------------------------------------------
    # Event Queries
    # -------------------------------------------------------------------------

    def list_events(self) -> List[EconomicCalendarEvent]:
        return list(self._events.values())

    def get_event(self, event_id: str) -> EconomicCalendarEvent:
        event = self._events.get(event_id)
        if not event:
            # Try finding by official_event_identifier
            for e in self._events.values():
                if e.official_event_identifier == event_id:
                    return e
            raise EconomicEventNotFoundError(event_id)
        return event

    def list_families(self) -> List[EconomicReleaseFamily]:
        return list(self._families.values())

    # -------------------------------------------------------------------------
    # Alert Management
    # -------------------------------------------------------------------------

    def list_user_alerts(self, user_id: str) -> List[UserEventAlert]:
        return [a for a in self._alerts.values() if a.owner_user_id == user_id]

    def get_alert(self, alert_id: str, user_id: str) -> UserEventAlert:
        alert = self._alerts.get(alert_id)
        if not alert or alert.owner_user_id != user_id:
            raise EconomicEventAlertNotFoundError(alert_id)
        return alert

    def save_alert(self, alert: UserEventAlert) -> UserEventAlert:
        self._alerts[alert.alert_id] = alert
        return alert

    def delete_alert(self, alert_id: str, user_id: str) -> bool:
        alert = self.get_alert(alert_id, user_id)
        alert.status = AlertStatus.CANCELLED
        alert.is_enabled = False
        del self._alerts[alert_id]
        return True

    def list_delivery_intents(self, user_id: str) -> List[AlertDeliveryIntent]:
        return [i for i in self._intents if i.owner_user_id == user_id]

    def record_delivery_intent(self, intent: AlertDeliveryIntent):
        self._intents.append(intent)

    # -------------------------------------------------------------------------
    # Canonical Seed Data across G6 Economies
    # -------------------------------------------------------------------------

    def _seed_canonical_data(self):
        # 1. Release Families
        fam_us_cpi = EconomicReleaseFamily(
            family_id="fam-us-cpi",
            name="US Consumer Price Index",
            category=EconomicEventCategory.INFLATION,
            geography_id="US",
            agency_name="U.S. Bureau of Labor Statistics (BLS)",
            default_importance=EconomicEventImportance.HIGH,
            description="Measures monthly changes in the prices paid by urban consumers for a market basket of goods and services.",
        )
        fam_us_payrolls = EconomicReleaseFamily(
            family_id="fam-us-nfp",
            name="US Employment Situation",
            category=EconomicEventCategory.LABOR_MARKET,
            geography_id="US",
            agency_name="U.S. Bureau of Labor Statistics (BLS)",
            default_importance=EconomicEventImportance.HIGH,
            description="Comprehensive monthly estimate of employment, hours worked, earnings, and the unemployment rate.",
        )
        fam_us_gdp = EconomicReleaseFamily(
            family_id="fam-us-gdp",
            name="US Gross Domestic Product",
            category=EconomicEventCategory.GDP,
            geography_id="US",
            agency_name="U.S. Bureau of Economic Analysis (BEA)",
            default_importance=EconomicEventImportance.HIGH,
            description="Quarterly estimate of the value of all goods and services produced in the United States economy.",
        )
        fam_us_fomc = EconomicReleaseFamily(
            family_id="fam-us-fomc",
            name="FOMC Monetary Policy Decision",
            category=EconomicEventCategory.CENTRAL_BANK,
            geography_id="US",
            agency_name="Federal Reserve Board of Governors",
            default_importance=EconomicEventImportance.HIGH,
            description="Official monetary policy target rate decision and statement by the Federal Open Market Committee.",
        )

        fam_eu_hicp = EconomicReleaseFamily(
            family_id="fam-eu-hicp",
            name="Euro Area Harmonised Index of Consumer Prices",
            category=EconomicEventCategory.INFLATION,
            geography_id="EU",
            agency_name="Eurostat",
            default_importance=EconomicEventImportance.HIGH,
            description="Consumer price inflation index compiled according to a harmonised methodology across Euro Area member states.",
        )
        fam_eu_ecb = EconomicReleaseFamily(
            family_id="fam-eu-ecb",
            name="ECB Governing Council Policy Decision",
            category=EconomicEventCategory.CENTRAL_BANK,
            geography_id="EU",
            agency_name="European Central Bank",
            default_importance=EconomicEventImportance.HIGH,
            description="Key policy interest rate decision announced by the ECB Governing Council.",
        )

        fam_gb_cpi = EconomicReleaseFamily(
            family_id="fam-gb-cpi",
            name="UK Consumer Prices Index",
            category=EconomicEventCategory.INFLATION,
            geography_id="GB",
            agency_name="Office for National Statistics (ONS)",
            default_importance=EconomicEventImportance.HIGH,
            description="Headline 12-month rate of consumer price inflation targeted by the Bank of England MPC.",
        )
        fam_gb_boe = EconomicReleaseFamily(
            family_id="fam-gb-boe",
            name="Bank of England MPC Rate Decision",
            category=EconomicEventCategory.CENTRAL_BANK,
            geography_id="GB",
            agency_name="Bank of England",
            default_importance=EconomicEventImportance.HIGH,
            description="Official Bank Rate decision and minutes released by the Monetary Policy Committee.",
        )

        fam_jp_cpi = EconomicReleaseFamily(
            family_id="fam-jp-cpi",
            name="Japan National Consumer Price Index",
            category=EconomicEventCategory.INFLATION,
            geography_id="JP",
            agency_name="Statistics Bureau of Japan",
            default_importance=EconomicEventImportance.HIGH,
            description="Year-on-year nationwide consumer price change excluding fresh food and energy.",
        )
        fam_jp_boj = EconomicReleaseFamily(
            family_id="fam-jp-boj",
            name="Bank of Japan Monetary Policy Decision",
            category=EconomicEventCategory.CENTRAL_BANK,
            geography_id="JP",
            agency_name="Bank of Japan",
            default_importance=EconomicEventImportance.HIGH,
            description="Policy rate decision and Outlook Report released by the Bank of Japan Policy Board.",
        )

        fam_in_cpi = EconomicReleaseFamily(
            family_id="fam-in-cpi",
            name="India Consumer Price Index Combined",
            category=EconomicEventCategory.INFLATION,
            geography_id="IN",
            agency_name="Ministry of Statistics and Programme Implementation (MoSPI)",
            default_importance=EconomicEventImportance.HIGH,
            description="Retail inflation index targeted by the Reserve Bank of India Monetary Policy Committee.",
        )
        fam_in_rbi = EconomicReleaseFamily(
            family_id="fam-in-rbi",
            name="RBI Monetary Policy Decision",
            category=EconomicEventCategory.CENTRAL_BANK,
            geography_id="IN",
            agency_name="Reserve Bank of India",
            default_importance=EconomicEventImportance.HIGH,
            description="Bimonthly Policy Repo Rate decision and stance announced by the RBI MPC.",
        )

        fam_cn_cpi = EconomicReleaseFamily(
            family_id="fam-cn-cpi",
            name="China Consumer Price Index",
            category=EconomicEventCategory.INFLATION,
            geography_id="CN",
            agency_name="National Bureau of Statistics of China (NBS)",
            default_importance=EconomicEventImportance.HIGH,
            description="Year-on-year headline consumer price inflation rate across urban and rural China.",
        )
        fam_cn_lpr = EconomicReleaseFamily(
            family_id="fam-cn-lpr",
            name="China Loan Prime Rate Fixing",
            category=EconomicEventCategory.CENTRAL_BANK,
            geography_id="CN",
            agency_name="People's Bank of China (PBOC)",
            default_importance=EconomicEventImportance.HIGH,
            description="Monthly benchmark lending rates announced by the National Interbank Funding Center under PBOC mandate.",
        )

        for fam in [
            fam_us_cpi, fam_us_payrolls, fam_us_gdp, fam_us_fomc,
            fam_eu_hicp, fam_eu_ecb,
            fam_gb_cpi, fam_gb_boe,
            fam_jp_cpi, fam_jp_boj,
            fam_in_cpi, fam_in_rbi,
            fam_cn_cpi, fam_cn_lpr,
        ]:
            self._families[fam.family_id] = fam

        # 2. Canonical Events (2024 Oct, Nov, Dec & Q3/Q4 cycles)

        # Event 1: US CPI (Oct 2024 release on Nov 13, 2024 at 13:30 UTC / 08:30 EST)
        ev_us_cpi_oct = EconomicCalendarEvent(
            event_id="ev-us-cpi-202410",
            official_event_identifier="US-BLS-CPI-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-us-cpi",
            title="US Consumer Price Index (YoY)",
            geographic_entity_ids=["US"],
            institution_entity_id="agency-bls",
            scheduled_start=datetime(2024, 11, 13, 13, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-10",
            release_stage=ReleaseStage.SINGLE_ESTIMATE,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["US_CPI_YOY", "US_CORE_CPI_YOY"],
            official_source_id="bls-us",
            official_source_name="U.S. Bureau of Labor Statistics",
            official_source_url="https://www.bls.gov/cpi/",
            published_at=datetime(2024, 11, 13, 13, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-cpi-yoy-202410",
                    event_id="ev-us-cpi-202410",
                    economic_series_id="US_CPI_YOY",
                    indicator_name="Consumer Price Index for All Urban Consumers (YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("2.6"),
                    previous_value=Decimal("2.4"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
                EconomicEventObservation(
                    observation_id="obs-us-core-cpi-yoy-202410",
                    event_id="ev-us-cpi-202410",
                    economic_series_id="US_CORE_CPI_YOY",
                    indicator_name="Core CPI (Ex Food & Energy YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("3.3"),
                    previous_value=Decimal("3.3"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-cpi-202410",
                    event_id="ev-us-cpi-202410",
                    economic_series_id="US_CPI_YOY",
                    consensus_value=Decimal("2.6"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=64,
                    snapshot_timestamp=datetime(2024, 11, 13, 12, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
                ConsensusSnapshot(
                    snapshot_id="cs-us-core-cpi-202410",
                    event_id="ev-us-cpi-202410",
                    economic_series_id="US_CORE_CPI_YOY",
                    consensus_value=Decimal("3.3"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=61,
                    snapshot_timestamp=datetime(2024, 11, 13, 12, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="In line with consensus at 2.6% YoY.",
        )

        # Event 2: US Employment Situation (NFP Oct 2024 released Nov 1, 2024)
        ev_us_nfp_oct = EconomicCalendarEvent(
            event_id="ev-us-nfp-202410",
            official_event_identifier="US-BLS-NFP-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.LABOR_MARKET,
            release_family_id="fam-us-nfp",
            title="US Nonfarm Payrolls & Unemployment Rate",
            geographic_entity_ids=["US"],
            institution_entity_id="agency-bls",
            scheduled_start=datetime(2024, 11, 1, 12, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-10",
            release_stage=ReleaseStage.PRELIMINARY,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["US_NFP_CHANGE", "US_UNEMPLOYMENT_RATE"],
            official_source_id="bls-us",
            official_source_name="U.S. Bureau of Labor Statistics",
            official_source_url="https://www.bls.gov/news.release/empsit.nr0.htm",
            published_at=datetime(2024, 11, 1, 12, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-nfp-202410",
                    event_id="ev-us-nfp-202410",
                    economic_series_id="US_NFP_CHANGE",
                    indicator_name="Nonfarm Payroll Employment Net Monthly Change",
                    reference_period="2024-10",
                    actual_value=Decimal("12"),
                    previous_value=Decimal("254"),
                    revised_previous_value=Decimal("223"),
                    unit="k jobs",
                    release_stage=ReleaseStage.PRELIMINARY,
                ),
                EconomicEventObservation(
                    observation_id="obs-us-ur-202410",
                    event_id="ev-us-nfp-202410",
                    economic_series_id="US_UNEMPLOYMENT_RATE",
                    indicator_name="Civilian Unemployment Rate",
                    reference_period="2024-10",
                    actual_value=Decimal("4.1"),
                    previous_value=Decimal("4.1"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.PRELIMINARY,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-nfp-202410",
                    event_id="ev-us-nfp-202410",
                    economic_series_id="US_NFP_CHANGE",
                    consensus_value=Decimal("113"),
                    unit="k jobs",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=70,
                    snapshot_timestamp=datetime(2024, 11, 1, 11, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Affected by severe hurricane weather events and major aerospace manufacturing labor strike.",
        )

        # Event 3: US GDP Advance Estimate (Q3 2024 released Oct 30, 2024)
        ev_us_gdp_q3 = EconomicCalendarEvent(
            event_id="ev-us-gdp-2024q3",
            official_event_identifier="US-BEA-GDP-2024Q3-ADV",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.GDP,
            release_family_id="fam-us-gdp",
            title="US Gross Domestic Product (Annualized QoQ)",
            geographic_entity_ids=["US"],
            institution_entity_id="agency-bea",
            scheduled_start=datetime(2024, 10, 30, 12, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-Q3",
            release_stage=ReleaseStage.ADVANCE,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["US_GDP_QOQ_ANN"],
            official_source_id="bea-us",
            official_source_name="U.S. Bureau of Economic Analysis",
            official_source_url="https://www.bea.gov/data/gdp/gross-domestic-product",
            published_at=datetime(2024, 10, 30, 12, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-gdp-2024q3",
                    event_id="ev-us-gdp-2024q3",
                    economic_series_id="US_GDP_QOQ_ANN",
                    indicator_name="Real Gross Domestic Product (Annualized QoQ)",
                    reference_period="2024-Q3",
                    actual_value=Decimal("2.8"),
                    previous_value=Decimal("3.0"),
                    revised_previous_value=None,
                    unit="% Ann QoQ",
                    release_stage=ReleaseStage.ADVANCE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-gdp-2024q3",
                    event_id="ev-us-gdp-2024q3",
                    economic_series_id="US_GDP_QOQ_ANN",
                    consensus_value=Decimal("3.0"),
                    unit="% Ann QoQ",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=55,
                    snapshot_timestamp=datetime(2024, 10, 30, 10, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Advance estimate showed 2.8% annualized growth.",
        )

        # Event 4: FOMC Rate Decision (Nov 7, 2024 at 19:00 UTC / 14:00 EST)
        ev_us_fomc_nov = EconomicCalendarEvent(
            event_id="ev-us-fomc-202411",
            official_event_identifier="US-FRB-FOMC-202411",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-us-fomc",
            title="Federal Reserve FOMC Interest Rate Decision",
            geographic_entity_ids=["US"],
            institution_entity_id="cb-fed",
            scheduled_start=datetime(2024, 11, 7, 19, 0, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-11-07",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["FED_FUNDS_TARGET_RANGE"],
            official_source_id="fed-us",
            official_source_name="Federal Reserve Board of Governors",
            official_source_url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            published_at=datetime(2024, 11, 7, 19, 0, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-fed-rate-202411",
                    event_id="ev-us-fomc-202411",
                    economic_series_id="FED_FUNDS_TARGET_RANGE",
                    indicator_name="Federal Funds Target Range (Upper Bound)",
                    reference_period="2024-11-07",
                    actual_value=Decimal("4.75"),
                    previous_value=Decimal("5.00"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-fed-rate-202411",
                    event_id="ev-us-fomc-202411",
                    economic_series_id="FED_FUNDS_TARGET_RANGE",
                    consensus_value=Decimal("4.75"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=98,
                    snapshot_timestamp=datetime(2024, 11, 7, 15, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="FOMC reduced target range by 25 basis points to 4.50% - 4.75%.",
        )

        # Event 5: Euro Area HICP Flash (Oct 2024 released Oct 31, 2024 at 10:00 UTC)
        ev_eu_hicp_oct = EconomicCalendarEvent(
            event_id="ev-eu-hicp-202410",
            official_event_identifier="EU-ESTAT-HICP-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-eu-hicp",
            title="Euro Area Harmonised Index of Consumer Prices Flash (YoY)",
            geographic_entity_ids=["EU"],
            institution_entity_id="eurostat-eu",
            scheduled_start=datetime(2024, 10, 31, 10, 0, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Europe/Frankfurt",
            reference_period="2024-10",
            release_stage=ReleaseStage.PRELIMINARY,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["EU_HICP_YOY"],
            official_source_id="eurostat-eu",
            official_source_name="Eurostat",
            official_source_url="https://ec.europa.eu/eurostat",
            published_at=datetime(2024, 10, 31, 10, 0, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-eu-hicp-202410",
                    event_id="ev-eu-hicp-202410",
                    economic_series_id="EU_HICP_YOY",
                    indicator_name="Euro Area HICP Flash (YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("2.0"),
                    previous_value=Decimal("1.7"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.PRELIMINARY,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-eu-hicp-202410",
                    event_id="ev-eu-hicp-202410",
                    economic_series_id="EU_HICP_YOY",
                    consensus_value=Decimal("1.9"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=42,
                    snapshot_timestamp=datetime(2024, 10, 31, 8, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Flash estimate came in at 2.0% YoY vs 1.9% forecast.",
        )

        # Event 6: ECB Policy Decision (Oct 17, 2024 at 12:15 UTC)
        ev_eu_ecb_oct = EconomicCalendarEvent(
            event_id="ev-eu-ecb-202410",
            official_event_identifier="EU-ECB-DEC-202410",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-eu-ecb",
            title="European Central Bank Interest Rate Decision",
            geographic_entity_ids=["EU"],
            institution_entity_id="cb-ecb",
            scheduled_start=datetime(2024, 10, 17, 12, 15, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Europe/Frankfurt",
            reference_period="2024-10-17",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["ECB_DFR"],
            official_source_id="ecb-eu",
            official_source_name="European Central Bank",
            official_source_url="https://www.ecb.europa.eu/press/pr/date/2024/html/index.en.html",
            published_at=datetime(2024, 10, 17, 12, 15, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-eu-ecb-dfr-202410",
                    event_id="ev-eu-ecb-202410",
                    economic_series_id="ECB_DFR",
                    indicator_name="ECB Deposit Facility Rate",
                    reference_period="2024-10-17",
                    actual_value=Decimal("3.25"),
                    previous_value=Decimal("3.50"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-eu-ecb-dfr-202410",
                    event_id="ev-eu-ecb-202410",
                    economic_series_id="ECB_DFR",
                    consensus_value=Decimal("3.25"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=65,
                    snapshot_timestamp=datetime(2024, 10, 17, 10, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Governing Council cut key policy rates by 25 basis points.",
        )

        # Event 7: UK CPI (Oct 2024 released Nov 20, 2024 at 07:00 UTC)
        ev_gb_cpi_oct = EconomicCalendarEvent(
            event_id="ev-gb-cpi-202410",
            official_event_identifier="GB-ONS-CPI-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-gb-cpi",
            title="UK Consumer Prices Index (12-Month YoY)",
            geographic_entity_ids=["GB"],
            institution_entity_id="agency-ons",
            scheduled_start=datetime(2024, 11, 20, 7, 0, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Europe/London",
            reference_period="2024-10",
            release_stage=ReleaseStage.SINGLE_ESTIMATE,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["GB_CPI_YOY"],
            official_source_id="ons-gb",
            official_source_name="Office for National Statistics",
            official_source_url="https://www.ons.gov.uk/economy/inflationandpriceindices",
            published_at=datetime(2024, 11, 20, 7, 0, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-gb-cpi-202410",
                    event_id="ev-gb-cpi-202410",
                    economic_series_id="GB_CPI_YOY",
                    indicator_name="UK CPI 12-Month Rate (YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("2.3"),
                    previous_value=Decimal("1.7"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-gb-cpi-202410",
                    event_id="ev-gb-cpi-202410",
                    economic_series_id="GB_CPI_YOY",
                    consensus_value=Decimal("2.2"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=36,
                    snapshot_timestamp=datetime(2024, 11, 20, 6, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="UK inflation rose to 2.3% YoY driven by energy price cap changes.",
        )

        # Event 8: Bank of England MPC Rate Decision (Nov 7, 2024 at 12:00 UTC)
        ev_gb_boe_nov = EconomicCalendarEvent(
            event_id="ev-gb-boe-202411",
            official_event_identifier="GB-BOE-MPC-202411",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-gb-boe",
            title="Bank of England Official Bank Rate Decision",
            geographic_entity_ids=["GB"],
            institution_entity_id="cb-boe",
            scheduled_start=datetime(2024, 11, 7, 12, 0, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Europe/London",
            reference_period="2024-11-07",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["BOE_BANK_RATE"],
            official_source_id="boe-gb",
            official_source_name="Bank of England",
            official_source_url="https://www.bankofengland.co.uk/monetary-policy",
            published_at=datetime(2024, 11, 7, 12, 0, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-gb-boe-202411",
                    event_id="ev-gb-boe-202411",
                    economic_series_id="BOE_BANK_RATE",
                    indicator_name="Bank of England Bank Rate",
                    reference_period="2024-11-07",
                    actual_value=Decimal("4.75"),
                    previous_value=Decimal("5.00"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-gb-boe-202411",
                    event_id="ev-gb-boe-202411",
                    economic_series_id="BOE_BANK_RATE",
                    consensus_value=Decimal("4.75"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=48,
                    snapshot_timestamp=datetime(2024, 11, 7, 10, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="MPC voted 8-1 to reduce Bank Rate by 0.25 percentage points to 4.75%.",
        )

        # Event 9: Japan National CPI (Oct 2024 released Nov 21, 2024 at 23:30 UTC / Nov 22 08:30 JST)
        ev_jp_cpi_oct = EconomicCalendarEvent(
            event_id="ev-jp-cpi-202410",
            official_event_identifier="JP-STAT-CPI-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-jp-cpi",
            title="Japan National Consumer Price Index (YoY)",
            geographic_entity_ids=["JP"],
            institution_entity_id="agency-sbj",
            scheduled_start=datetime(2024, 11, 21, 23, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Asia/Tokyo",
            reference_period="2024-10",
            release_stage=ReleaseStage.SINGLE_ESTIMATE,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["JP_CPI_YOY"],
            official_source_id="stat-jp",
            official_source_name="Statistics Bureau of Japan",
            official_source_url="https://www.stat.go.jp/english/data/cpi/index.html",
            published_at=datetime(2024, 11, 21, 23, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-jp-cpi-202410",
                    event_id="ev-jp-cpi-202410",
                    economic_series_id="JP_CPI_YOY",
                    indicator_name="Japan All Items CPI (YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("2.3"),
                    previous_value=Decimal("2.5"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-jp-cpi-202410",
                    event_id="ev-jp-cpi-202410",
                    economic_series_id="JP_CPI_YOY",
                    consensus_value=Decimal("2.2"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=29,
                    snapshot_timestamp=datetime(2024, 11, 21, 20, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Headline inflation at 2.3% YoY above BoJ 2.0% target.",
        )

        # Event 10: Bank of Japan Policy Decision (Oct 31, 2024 around 03:30 UTC / 12:30 JST)
        ev_jp_boj_oct = EconomicCalendarEvent(
            event_id="ev-jp-boj-202410",
            official_event_identifier="JP-BOJ-MPM-202410",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-jp-boj",
            title="Bank of Japan Policy Rate Decision & Outlook",
            geographic_entity_ids=["JP"],
            institution_entity_id="cb-boj",
            scheduled_start=datetime(2024, 10, 31, 3, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.LOCAL_DATE_TIME,
            source_timezone="Asia/Tokyo",
            reference_period="2024-10-31",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["BOJ_CALL_RATE"],
            official_source_id="boj-jp",
            official_source_name="Bank of Japan",
            official_source_url="https://www.boj.or.jp/en/mopo/index.htm",
            published_at=datetime(2024, 10, 31, 3, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-jp-boj-202410",
                    event_id="ev-jp-boj-202410",
                    economic_series_id="BOJ_CALL_RATE",
                    indicator_name="Uncollateralized Overnight Call Rate Target",
                    reference_period="2024-10-31",
                    actual_value=Decimal("0.25"),
                    previous_value=Decimal("0.25"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-jp-boj-202410",
                    event_id="ev-jp-boj-202410",
                    economic_series_id="BOJ_CALL_RATE",
                    consensus_value=Decimal("0.25"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=45,
                    snapshot_timestamp=datetime(2024, 10, 30, 20, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Policy Board maintained rate at 0.25% in unanimous vote.",
        )

        # Event 10: India CPI Inflation (Oct 2024 released Nov 12, 2024 at 12:00 UTC / 17:30 IST)
        ev_in_cpi_oct = EconomicCalendarEvent(
            event_id="ev-in-cpi-202410",
            official_event_identifier="IN-MOSPI-CPI-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-in-cpi",
            title="India Consumer Price Index Combined (YoY)",
            geographic_entity_ids=["IN"],
            institution_entity_id="agency-mospi",
            scheduled_start=datetime(2024, 11, 12, 12, 0, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Asia/Kolkata",
            reference_period="2024-10",
            release_stage=ReleaseStage.SINGLE_ESTIMATE,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["IN_CPI_YOY"],
            official_source_id="mospi-in",
            official_source_name="Ministry of Statistics and Programme Implementation",
            official_source_url="https://mospi.gov.in",
            published_at=datetime(2024, 11, 12, 12, 0, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-in-cpi-202410",
                    event_id="ev-in-cpi-202410",
                    economic_series_id="IN_CPI_YOY",
                    indicator_name="Consumer Price Index Combined (YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("6.21"),
                    previous_value=Decimal("5.49"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-in-cpi-202410",
                    event_id="ev-in-cpi-202410",
                    economic_series_id="IN_CPI_YOY",
                    consensus_value=Decimal("5.81"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=32,
                    snapshot_timestamp=datetime(2024, 11, 12, 10, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Retail inflation accelerated to 6.21% breached RBI upper tolerance band of 6.0%.",
        )

        # Event 11: RBI MPC Decision (Oct 9, 2024 at 04:30 UTC / 10:00 IST)
        ev_in_rbi_oct = EconomicCalendarEvent(
            event_id="ev-in-rbi-202410",
            official_event_identifier="IN-RBI-MPC-202410",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-in-rbi",
            title="Reserve Bank of India Monetary Policy Decision",
            geographic_entity_ids=["IN"],
            institution_entity_id="cb-rbi",
            scheduled_start=datetime(2024, 10, 9, 4, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Asia/Kolkata",
            reference_period="2024-10-09",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["RBI_REPO_RATE"],
            official_source_id="rbi-in",
            official_source_name="Reserve Bank of India",
            official_source_url="https://rbi.org.in",
            published_at=datetime(2024, 10, 9, 4, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-in-rbi-repo-202410",
                    event_id="ev-in-rbi-202410",
                    economic_series_id="RBI_REPO_RATE",
                    indicator_name="RBI Policy Repo Rate",
                    reference_period="2024-10-09",
                    actual_value=Decimal("6.50"),
                    previous_value=Decimal("6.50"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-in-rbi-repo-202410",
                    event_id="ev-in-rbi-202410",
                    economic_series_id="RBI_REPO_RATE",
                    consensus_value=Decimal("6.50"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=40,
                    snapshot_timestamp=datetime(2024, 10, 9, 2, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="MPC held repo rate at 6.50% and shifted policy stance to Neutral.",
        )

        # Event 12: China CPI (Oct 2024 released Nov 9, 2024 at 01:30 UTC / 09:30 CST)
        ev_cn_cpi_oct = EconomicCalendarEvent(
            event_id="ev-cn-cpi-202410",
            official_event_identifier="CN-NBS-CPI-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-cn-cpi",
            title="China Consumer Price Index (YoY)",
            geographic_entity_ids=["CN"],
            institution_entity_id="agency-nbs",
            scheduled_start=datetime(2024, 11, 9, 1, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Asia/Shanghai",
            reference_period="2024-10",
            release_stage=ReleaseStage.SINGLE_ESTIMATE,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["CN_CPI_YOY"],
            official_source_id="stats-cn",
            official_source_name="National Bureau of Statistics of China",
            official_source_url="http://www.stats.gov.cn",
            published_at=datetime(2024, 11, 9, 1, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-cn-cpi-202410",
                    event_id="ev-cn-cpi-202410",
                    economic_series_id="CN_CPI_YOY",
                    indicator_name="China Headline CPI (YoY)",
                    reference_period="2024-10",
                    actual_value=Decimal("0.3"),
                    previous_value=Decimal("0.4"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-cn-cpi-202410",
                    event_id="ev-cn-cpi-202410",
                    economic_series_id="CN_CPI_YOY",
                    consensus_value=Decimal("0.4"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=28,
                    snapshot_timestamp=datetime(2024, 11, 8, 20, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="CPI slowed slightly to 0.3% YoY in October.",
        )

        # Event 13: China Loan Prime Rate (Oct 21, 2024 at 01:15 UTC / 09:15 CST)
        ev_cn_lpr_oct = EconomicCalendarEvent(
            event_id="ev-cn-lpr-202410",
            official_event_identifier="CN-PBOC-LPR-202410",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-cn-lpr",
            title="People's Bank of China 1-Year & 5-Year LPR Fixing",
            geographic_entity_ids=["CN"],
            institution_entity_id="cb-pboc",
            scheduled_start=datetime(2024, 10, 21, 1, 15, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="Asia/Shanghai",
            reference_period="2024-10-21",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.RELEASE_VERIFIED,
            importance=EconomicEventImportance.HIGH,
            indicators=["PBOC_1Y_LPR", "PBOC_5Y_LPR"],
            official_source_id="pboc-cn",
            official_source_name="People's Bank of China",
            official_source_url="http://www.pbc.gov.cn",
            published_at=datetime(2024, 10, 21, 1, 15, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-cn-lpr1-202410",
                    event_id="ev-cn-lpr-202410",
                    economic_series_id="PBOC_1Y_LPR",
                    indicator_name="1-Year Loan Prime Rate (LPR)",
                    reference_period="2024-10-21",
                    actual_value=Decimal("3.10"),
                    previous_value=Decimal("3.35"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
                EconomicEventObservation(
                    observation_id="obs-cn-lpr5-202410",
                    event_id="ev-cn-lpr-202410",
                    economic_series_id="PBOC_5Y_LPR",
                    indicator_name="5-Year Loan Prime Rate (LPR)",
                    reference_period="2024-10-21",
                    actual_value=Decimal("3.60"),
                    previous_value=Decimal("3.85"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-cn-lpr-202410",
                    event_id="ev-cn-lpr-202410",
                    economic_series_id="PBOC_1Y_LPR",
                    consensus_value=Decimal("3.10"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=35,
                    snapshot_timestamp=datetime(2024, 10, 20, 20, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="PBOC lowered 1Y and 5Y LPR by 25 bps following policy package announcement.",
        )

        # Event 14: US CPI Nov 2024 (Scheduled Upcoming Event: Dec 11, 2024 at 13:30 UTC / 08:30 EST)
        ev_us_cpi_nov = EconomicCalendarEvent(
            event_id="ev-us-cpi-202411",
            official_event_identifier="US-BLS-CPI-202411",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.INFLATION,
            release_family_id="fam-us-cpi",
            title="US Consumer Price Index (YoY)",
            geographic_entity_ids=["US"],
            institution_entity_id="agency-bls",
            scheduled_start=datetime(2024, 12, 11, 13, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-11",
            release_stage=ReleaseStage.SINGLE_ESTIMATE,
            event_status=EconomicEventStatus.SCHEDULED,
            importance=EconomicEventImportance.HIGH,
            indicators=["US_CPI_YOY"],
            official_source_id="bls-us",
            official_source_name="U.S. Bureau of Labor Statistics",
            official_source_url="https://www.bls.gov/cpi/",
            published_at=None,
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-cpi-yoy-202411",
                    event_id="ev-us-cpi-202411",
                    economic_series_id="US_CPI_YOY",
                    indicator_name="Consumer Price Index for All Urban Consumers (YoY)",
                    reference_period="2024-11",
                    actual_value=None,
                    previous_value=Decimal("2.6"),
                    revised_previous_value=None,
                    unit="% YoY",
                    release_stage=ReleaseStage.SINGLE_ESTIMATE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-cpi-202411",
                    event_id="ev-us-cpi-202411",
                    economic_series_id="US_CPI_YOY",
                    consensus_value=Decimal("2.7"),
                    unit="% YoY",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=58,
                    snapshot_timestamp=datetime(2024, 12, 10, 18, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Upcoming release schedule verified on official BLS calendar.",
        )

        # Event 15: US FOMC Dec 2024 Decision (Scheduled Upcoming: Dec 18, 2024 at 19:00 UTC)
        ev_us_fomc_dec = EconomicCalendarEvent(
            event_id="ev-us-fomc-202412",
            official_event_identifier="US-FRB-FOMC-202412",
            event_kind=EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            category=EconomicEventCategory.CENTRAL_BANK,
            release_family_id="fam-us-fomc",
            title="Federal Reserve FOMC Interest Rate Decision & SEP",
            geographic_entity_ids=["US"],
            institution_entity_id="cb-fed",
            scheduled_start=datetime(2024, 12, 18, 19, 0, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-12-18",
            release_stage=ReleaseStage.FINAL,
            event_status=EconomicEventStatus.SCHEDULED,
            importance=EconomicEventImportance.HIGH,
            indicators=["FED_FUNDS_TARGET_RANGE"],
            official_source_id="fed-us",
            official_source_name="Federal Reserve Board of Governors",
            official_source_url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            published_at=None,
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-fed-rate-202412",
                    event_id="ev-us-fomc-202412",
                    economic_series_id="FED_FUNDS_TARGET_RANGE",
                    indicator_name="Federal Funds Target Range (Upper Bound)",
                    reference_period="2024-12-18",
                    actual_value=None,
                    previous_value=Decimal("4.75"),
                    revised_previous_value=None,
                    unit="%",
                    release_stage=ReleaseStage.FINAL,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-fed-rate-202412",
                    event_id="ev-us-fomc-202412",
                    economic_series_id="FED_FUNDS_TARGET_RANGE",
                    consensus_value=Decimal("4.50"),
                    unit="%",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=92,
                    snapshot_timestamp=datetime(2024, 12, 17, 18, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            notes="Scheduled meeting with updated Summary of Economic Projections (SEP).",
        )

        # Event 16: Rescheduled Event Example (e.g., US Census Retail Sales Reschedule Test Case)
        ev_us_retail_rescheduled = EconomicCalendarEvent(
            event_id="ev-us-retail-202410",
            official_event_identifier="US-CENSUS-RET-202410",
            event_kind=EconomicEventKind.ECONOMIC_STATISTICS_RELEASE,
            category=EconomicEventCategory.RETAIL_SALES,
            release_family_id="fam-us-cpi",
            title="US Advance Monthly Sales for Retail and Food Services (MoM)",
            geographic_entity_ids=["US"],
            institution_entity_id="agency-census",
            scheduled_start=datetime(2024, 11, 15, 13, 30, tzinfo=timezone.utc),
            scheduled_end=None,
            schedule_precision=SchedulePrecision.EXACT_INSTANT,
            source_timezone="America/New_York",
            reference_period="2024-10",
            release_stage=ReleaseStage.ADVANCE,
            event_status=EconomicEventStatus.RESCHEDULED,
            importance=EconomicEventImportance.MEDIUM,
            indicators=["US_RETAIL_SALES_MOM"],
            official_source_id="census-us",
            official_source_name="U.S. Census Bureau",
            official_source_url="https://www.census.gov/retail/",
            published_at=datetime(2024, 11, 15, 13, 30, tzinfo=timezone.utc),
            is_verified=True,
            observations=[
                EconomicEventObservation(
                    observation_id="obs-us-ret-202410",
                    event_id="ev-us-retail-202410",
                    economic_series_id="US_RETAIL_SALES_MOM",
                    indicator_name="Retail and Food Services Sales (MoM)",
                    reference_period="2024-10",
                    actual_value=Decimal("0.4"),
                    previous_value=Decimal("0.4"),
                    revised_previous_value=Decimal("0.8"),
                    unit="% MoM",
                    release_stage=ReleaseStage.ADVANCE,
                ),
            ],
            consensus_snapshots=[
                ConsensusSnapshot(
                    snapshot_id="cs-us-ret-202410",
                    event_id="ev-us-retail-202410",
                    economic_series_id="US_RETAIL_SALES_MOM",
                    consensus_value=Decimal("0.3"),
                    unit="% MoM",
                    aggregation_method=ForecastAggregationMethod.MEDIAN,
                    contributor_count=48,
                    snapshot_timestamp=datetime(2024, 11, 15, 10, 0, tzinfo=timezone.utc),
                    provider_name="Authorized Consensus Median",
                ),
            ],
            schedule_revisions=[
                ScheduleRevision(
                    revision_id="rev-us-ret-1",
                    event_id="ev-us-retail-202410",
                    previous_scheduled_time=datetime(2024, 11, 14, 13, 30, tzinfo=timezone.utc),
                    new_scheduled_time=datetime(2024, 11, 15, 13, 30, tzinfo=timezone.utc),
                    reason="Official statistical agency processing schedule calendar adjustment.",
                    revised_at=datetime(2024, 11, 1, 14, 0, tzinfo=timezone.utc),
                ),
            ],
            notes="Postponed by 24 hours per Census Bureau schedule revision notice.",
        )

        for ev in [
            ev_us_cpi_oct, ev_us_nfp_oct, ev_us_gdp_q3, ev_us_fomc_nov,
            ev_eu_hicp_oct, ev_eu_ecb_oct,
            ev_gb_cpi_oct, ev_gb_boe_nov,
            ev_jp_cpi_oct, ev_jp_boj_oct,
            ev_in_cpi_oct, ev_in_rbi_oct,
            ev_cn_cpi_oct, ev_cn_lpr_oct,
            ev_us_cpi_nov, ev_us_fomc_dec,
            ev_us_retail_rescheduled,
        ]:
            self._events[ev.event_id] = ev
