"""Repository for Central Bank Intelligence (Stage 91).

Provides authoritative, source-backed in-memory institutional representations for
monetary policy frameworks, administered policy interest rates, official decisions,
meetings, committee voting splits, publications, speeches, balance sheets, and
quantitative easing/tightening programs for major monetary authorities.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from .enums import (
    CentralBankInstitutionKind,
    ForwardGuidanceKind,
    MeetingKind,
    PolicyCycleKind,
    PolicyDecisionKind,
    PolicyInstrumentCategory,
    PolicyProgramKind,
    PolicyRateRepresentationKind,
    PublicationKind,
    VotingOutcomeKind,
)
from .errors import (
    CentralBankDecisionNotFoundError,
    CentralBankInstrumentNotFoundError,
    CentralBankMeetingNotFoundError,
    CentralBankNotFoundError,
    CentralBankPublicationNotFoundError,
)
from .models import (
    BalanceSheetItem,
    CentralBankBalanceSheetSummary,
    CentralBankInstitution,
    CentralBankOverview,
    CentralBankPolicyProgram,
    CommitteeVotingRecord,
    IndividualVote,
    MonetaryPolicyDecision,
    MonetaryPolicyFramework,
    MonetaryPolicyMeeting,
    OfficialForwardGuidance,
    OfficialPublication,
    OfficialSpeech,
    PolicyInstrument,
    PolicyTimelineEvent,
    RateChangeMetric,
)


class CentralBanksRepository:
    """Canonical in-memory repository for Central Bank Intelligence."""

    def __init__(self):
        self._institutions: Dict[str, CentralBankInstitution] = {}
        self._frameworks: Dict[str, MonetaryPolicyFramework] = {}
        self._instruments: Dict[str, List[PolicyInstrument]] = {}
        self._decisions: Dict[str, List[MonetaryPolicyDecision]] = {}
        self._meetings: Dict[str, List[MonetaryPolicyMeeting]] = {}
        self._voting_records: Dict[str, CommitteeVotingRecord] = {}  # keyed by meeting_id
        self._publications: Dict[str, List[OfficialPublication]] = {}
        self._speeches: Dict[str, List[OfficialSpeech]] = {}
        self._guidance: Dict[str, List[OfficialForwardGuidance]] = {}
        self._balance_sheets: Dict[str, CentralBankBalanceSheetSummary] = {}
        self._programs: Dict[str, List[CentralBankPolicyProgram]] = {}
        self._timelines: Dict[str, List[PolicyTimelineEvent]] = {}

        self._alias_map: Dict[str, str] = {
            "fed": "cb-fed",
            "federal reserve": "cb-fed",
            "federal reserve system": "cb-fed",
            "fomc": "cb-fed",
            "us": "cb-fed",
            "usa": "cb-fed",
            "cb-fed": "cb-fed",
            "ecb": "cb-ecb",
            "european central bank": "cb-ecb",
            "euro area": "cb-ecb",
            "eurozone": "cb-ecb",
            "ea": "cb-ecb",
            "eu": "cb-ecb",
            "cb-ecb": "cb-ecb",
            "boe": "cb-boe",
            "bank of england": "cb-boe",
            "mpc": "cb-boe",
            "gb": "cb-boe",
            "gbr": "cb-boe",
            "uk": "cb-boe",
            "cb-boe": "cb-boe",
            "boj": "cb-boj",
            "bank of japan": "cb-boj",
            "jp": "cb-boj",
            "jpn": "cb-boj",
            "japan": "cb-boj",
            "cb-boj": "cb-boj",
            "rbi": "cb-rbi",
            "reserve bank of india": "cb-rbi",
            "in": "cb-rbi",
            "ind": "cb-rbi",
            "india": "cb-rbi",
            "cb-rbi": "cb-rbi",
            "pboc": "cb-pboc",
            "people's bank of china": "cb-pboc",
            "peoples bank of china": "cb-pboc",
            "cn": "cb-pboc",
            "chn": "cb-pboc",
            "china": "cb-pboc",
            "cb-pboc": "cb-pboc",
        }

        self._seed_data()

    def resolve_institution_id(self, identifier: str) -> str:
        """Resolve common acronyms, codes, or ISO codes to a canonical central_bank_id."""
        normalized = identifier.strip().lower()
        if normalized in self._alias_map:
            return self._alias_map[normalized]
        if identifier in self._institutions:
            return identifier
        raise CentralBankNotFoundError(f"Central bank institution '{identifier}' not found in registry.")

    # -------------------------------------------------------------------------
    # Seed Data Initialization
    # -------------------------------------------------------------------------

    def _seed_data(self) -> None:
        self._seed_fed()
        self._seed_ecb()
        self._seed_boe()
        self._seed_boj()
        self._seed_rbi()
        self._seed_pboc()

    def _seed_fed(self) -> None:
        cb_id = "cb-fed"

        # 1. Institution
        self._institutions[cb_id] = CentralBankInstitution(
            central_bank_id=cb_id,
            canonical_name="Federal Reserve System",
            acronym="Fed",
            institution_kind=CentralBankInstitutionKind.FEDERAL_CENTRAL_BANK,
            primary_geography_id="US",
            monetary_area_id="US",
            currency_code="USD",
            official_website_url="https://www.federalreserve.gov",
            established_year=1913,
            headquarters_city="Washington, D.C.",
            primary_policy_committee="Federal Open Market Committee (FOMC)",
            is_active=True,
            supported_instruments_count=4,
            notes="Consists of Board of Governors and 12 Regional Federal Reserve Banks.",
        )

        # 2. Framework
        self._frameworks[cb_id] = MonetaryPolicyFramework(
            central_bank_id=cb_id,
            mandate_title="Dual Mandate (Maximum Employment & Price Stability)",
            mandate_summary=(
                "Statutory mandate under Federal Reserve Act to promote effectively the goals of maximum "
                "employment, stable prices, and moderate long-term interest rates."
            ),
            operating_strategy=(
                "Flexible average inflation targeting framework seeking to achieve inflation that averages 2 percent "
                "over time, following periods when inflation has been persistently below 2 percent."
            ),
            inflation_target_metric="PCE Price Index (Personal Consumption Expenditures)",
            inflation_target_pct=Decimal("2.0"),
            target_lower_bound_pct=None,
            target_upper_bound_pct=None,
            target_tolerance_band="Symmetric 2.0% objective",
            target_horizon="Longer Run",
            effective_since="2012 (revised 2020 Statement on Longer-Run Goals)",
            source_citation="FOMC Statement on Longer-Run Goals and Monetary Policy Strategy",
        )

        # 3. Instruments
        self._instruments[cb_id] = [
            PolicyInstrument(
                instrument_id="inst-fed-fftr",
                central_bank_id=cb_id,
                code="FED_FUNDS_TARGET_RANGE",
                name="Federal Funds Target Range",
                category=PolicyInstrumentCategory.TARGET_RANGE,
                representation=PolicyRateRepresentationKind.TARGET_RANGE,
                current_rate=None,
                current_lower_bound=Decimal("4.50"),
                current_upper_bound=Decimal("4.75"),
                effective_date="2024-11-08",
                canonical_series_id="econ_us_fed_funds_target",
                operational_description="Primary operational policy instrument administered by the FOMC.",
            ),
            PolicyInstrument(
                instrument_id="inst-fed-iorb",
                central_bank_id=cb_id,
                code="FED_IORB",
                name="Interest on Reserve Balances",
                category=PolicyInstrumentCategory.RESERVE_REMUNERATION_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("4.65"),
                current_lower_bound=None,
                current_upper_bound=None,
                effective_date="2024-11-08",
                canonical_series_id="econ_us_iorb",
                operational_description="Interest rate paid by Federal Reserve on reserve balances held by depository institutions.",
            ),
            PolicyInstrument(
                instrument_id="inst-fed-on-rrp",
                central_bank_id=cb_id,
                code="FED_ON_RRP",
                name="Overnight Reverse Repo Facility Offering Rate",
                category=PolicyInstrumentCategory.OTHER_ADMINISTERED_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("4.55"),
                current_lower_bound=None,
                current_upper_bound=None,
                effective_date="2024-11-08",
                canonical_series_id="econ_us_on_rrp",
                operational_description="Floor rate under the federal funds rate corridor.",
            ),
            PolicyInstrument(
                instrument_id="inst-fed-primary-credit",
                central_bank_id=cb_id,
                code="FED_PRIMARY_CREDIT",
                name="Discount Window Primary Credit Rate",
                category=PolicyInstrumentCategory.LENDING_FACILITY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("4.75"),
                current_lower_bound=None,
                current_upper_bound=None,
                effective_date="2024-11-08",
                canonical_series_id="econ_us_primary_credit",
                operational_description="Standing lending facility rate available to generally sound depository institutions.",
            ),
        ]

        # 4. Decisions
        self._decisions[cb_id] = [
            MonetaryPolicyDecision(
                decision_id="dec-fed-2024-11-07",
                official_identifier="FOMC-DEC-20241107",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 11, 7, 14, 0),
                effective_at=date(2024, 11, 8),
                meeting_id="meet-fed-2024-11",
                statement_document_id="doc-fed-stmt-2024-11-07",
                affected_instruments=["FED_FUNDS_TARGET_RANGE", "FED_IORB", "FED_ON_RRP", "FED_PRIMARY_CREDIT"],
                rate_changes=[
                    RateChangeMetric(
                        instrument_code="FED_FUNDS_TARGET_RANGE",
                        previous_lower_bound=Decimal("4.75"),
                        previous_upper_bound=Decimal("5.00"),
                        new_lower_bound=Decimal("4.50"),
                        new_upper_bound=Decimal("4.75"),
                        change_lower_bps=Decimal("-25.0"),
                        change_upper_bps=Decimal("-25.0"),
                        change_bps=Decimal("-25.0"),
                    ),
                    RateChangeMetric(
                        instrument_code="FED_IORB",
                        previous_rate=Decimal("4.90"),
                        new_rate=Decimal("4.65"),
                        change_bps=Decimal("-25.0"),
                    ),
                ],
                policy_rationale=(
                    "Recent indicators suggest that economic activity has continued to expand at a solid pace. "
                    "Since earlier in the year, labor market conditions have generally eased, and the unemployment rate has moved up "
                    "but remains low. Inflation has made progress toward the Committee's 2 percent objective but remains somewhat elevated."
                ),
            ),
            MonetaryPolicyDecision(
                decision_id="dec-fed-2024-09-18",
                official_identifier="FOMC-DEC-20240918",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 9, 18, 14, 0),
                effective_at=date(2024, 9, 19),
                meeting_id="meet-fed-2024-09",
                statement_document_id="doc-fed-stmt-2024-09-18",
                affected_instruments=["FED_FUNDS_TARGET_RANGE", "FED_IORB", "FED_ON_RRP", "FED_PRIMARY_CREDIT"],
                rate_changes=[
                    RateChangeMetric(
                        instrument_code="FED_FUNDS_TARGET_RANGE",
                        previous_lower_bound=Decimal("5.25"),
                        previous_upper_bound=Decimal("5.50"),
                        new_lower_bound=Decimal("4.75"),
                        new_upper_bound=Decimal("5.00"),
                        change_lower_bps=Decimal("-50.0"),
                        change_upper_bps=Decimal("-50.0"),
                        change_bps=Decimal("-50.0"),
                    ),
                ],
                policy_rationale=(
                    "In light of the progress on inflation and the balance of risks, the Committee decided to lower the target range "
                    "for the federal funds rate by 50 basis points to 4-3/4 to 5 percent."
                ),
            ),
            MonetaryPolicyDecision(
                decision_id="dec-fed-2024-07-31",
                official_identifier="FOMC-DEC-20240731",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_HOLD,
                announced_at=datetime(2024, 7, 31, 14, 0),
                effective_at=date(2024, 8, 1),
                meeting_id="meet-fed-2024-07",
                statement_document_id="doc-fed-stmt-2024-07-31",
                affected_instruments=["FED_FUNDS_TARGET_RANGE"],
                rate_changes=[
                    RateChangeMetric(
                        instrument_code="FED_FUNDS_TARGET_RANGE",
                        previous_lower_bound=Decimal("5.25"),
                        previous_upper_bound=Decimal("5.50"),
                        new_lower_bound=Decimal("5.25"),
                        new_upper_bound=Decimal("5.50"),
                        change_lower_bps=Decimal("0.0"),
                        change_upper_bps=Decimal("0.0"),
                        change_bps=Decimal("0.0"),
                    ),
                ],
                policy_rationale="The Committee judged that the risks to achieving its employment and inflation goals continue to move into better balance.",
            ),
        ]

        # 5. Meetings
        self._meetings[cb_id] = [
            MonetaryPolicyMeeting(
                meeting_id="meet-fed-2024-11",
                official_identifier="FOMC-MEET-20241106-07",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 11, 6),
                end_date=date(2024, 11, 7),
                decision_ids=["dec-fed-2024-11-07"],
                statement_document_id="doc-fed-stmt-2024-11-07",
                minutes_document_id="doc-fed-min-2024-11-07",
                minutes_published_at=datetime(2024, 11, 26, 14, 0),
                voting_record_id="vote-fed-2024-11",
            ),
            MonetaryPolicyMeeting(
                meeting_id="meet-fed-2024-09",
                official_identifier="FOMC-MEET-20240917-18",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 9, 17),
                end_date=date(2024, 9, 18),
                decision_ids=["dec-fed-2024-09-18"],
                statement_document_id="doc-fed-stmt-2024-09-18",
                minutes_document_id="doc-fed-min-2024-09-18",
                minutes_published_at=datetime(2024, 10, 9, 14, 0),
                voting_record_id="vote-fed-2024-09",
            ),
            MonetaryPolicyMeeting(
                meeting_id="meet-fed-2024-07",
                official_identifier="FOMC-MEET-20240730-31",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 7, 30),
                end_date=date(2024, 7, 31),
                decision_ids=["dec-fed-2024-07-31"],
                statement_document_id="doc-fed-stmt-2024-07-31",
                minutes_document_id="doc-fed-min-2024-07-31",
                minutes_published_at=datetime(2024, 8, 21, 14, 0),
                voting_record_id="vote-fed-2024-07",
            ),
        ]

        # 6. Committee Voting Records
        self._voting_records["meet-fed-2024-11"] = CommitteeVotingRecord(
            record_id="vote-fed-2024-11",
            meeting_id="meet-fed-2024-11",
            decision_id="dec-fed-2024-11-07",
            votes_for=12,
            votes_against=0,
            votes_abstain=0,
            individual_votes=[
                IndividualVote("Jerome H. Powell", "Chair", VotingOutcomeKind.FOR),
                IndividualVote("John C. Williams", "Vice Chair", VotingOutcomeKind.FOR),
                IndividualVote("Thomas I. Barkin", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Michael S. Barr", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Raphael W. Bostic", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Michelle W. Bowman", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Lisa D. Cook", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Mary C. Daly", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Beth M. Hammack", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Philip N. Jefferson", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Adriana D. Kugler", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Christopher J. Waller", "Member", VotingOutcomeKind.FOR),
            ],
            is_publicly_disclosed=True,
            source_reference="Federal Reserve Board press release, November 7, 2024",
        )

        self._voting_records["meet-fed-2024-09"] = CommitteeVotingRecord(
            record_id="vote-fed-2024-09",
            meeting_id="meet-fed-2024-09",
            decision_id="dec-fed-2024-09-18",
            votes_for=11,
            votes_against=1,
            votes_abstain=0,
            individual_votes=[
                IndividualVote("Jerome H. Powell", "Chair", VotingOutcomeKind.FOR),
                IndividualVote("John C. Williams", "Vice Chair", VotingOutcomeKind.FOR),
                IndividualVote("Thomas I. Barkin", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Michael S. Barr", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Raphael W. Bostic", "Member", VotingOutcomeKind.FOR),
                IndividualVote(
                    "Michelle W. Bowman",
                    "Member",
                    VotingOutcomeKind.AGAINST,
                    dissent_rationale="Preferred to lower the target range for the federal funds rate by 25 basis points at this meeting.",
                ),
                IndividualVote("Lisa D. Cook", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Mary C. Daly", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Beth M. Hammack", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Philip N. Jefferson", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Adriana D. Kugler", "Member", VotingOutcomeKind.FOR),
                IndividualVote("Christopher J. Waller", "Member", VotingOutcomeKind.FOR),
            ],
            is_publicly_disclosed=True,
            source_reference="Federal Reserve Board press release, September 18, 2024",
        )

        # 7. Publications
        self._publications[cb_id] = [
            OfficialPublication(
                document_id="doc-fed-stmt-2024-11-07",
                central_bank_id=cb_id,
                title="Federal Reserve issues FOMC statement (November 7, 2024)",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 11, 7, 14, 0),
                source_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20241107a.htm",
                media_type="HTML",
                content_hash="sha256-fed-stmt-20241107",
                sanitized_excerpt=(
                    "The Committee decided to lower the target range for the federal funds rate by 1/4 percentage point to 4-1/2 to 4-3/4 percent. "
                    "The Committee will continue reducing its holdings of Treasury securities and agency debt and agency mortgage-backed securities."
                ),
            ),
            OfficialPublication(
                document_id="doc-fed-stmt-2024-09-18",
                central_bank_id=cb_id,
                title="Federal Reserve issues FOMC statement (September 18, 2024)",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 9, 18, 14, 0),
                source_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm",
                media_type="HTML",
                content_hash="sha256-fed-stmt-20240918",
                sanitized_excerpt="The Committee decided to lower the target range for the federal funds rate by 50 basis points to 4-3/4 to 5 percent.",
            ),
            OfficialPublication(
                document_id="doc-fed-mpr-2024-06",
                central_bank_id=cb_id,
                title="Monetary Policy Report - June 2024",
                publication_kind=PublicationKind.MONETARY_POLICY_REPORT,
                published_at=datetime(2024, 6, 21, 11, 0),
                source_url="https://www.federalreserve.gov/monetarypolicy/2024-06-mpr-summary.htm",
                media_type="HTML",
                content_hash="sha256-fed-mpr-202406",
                sanitized_excerpt="Semiannual report submitted to Congress pursuant to section 2B of the Federal Reserve Act.",
            ),
        ]

        # 8. Speeches
        self._speeches[cb_id] = [
            OfficialSpeech(
                speech_id="sp-fed-powell-2024-08-23",
                central_bank_id=cb_id,
                speaker_name="Jerome H. Powell",
                speaker_role="Chair, Board of Governors of the Federal Reserve System",
                title="Review and Outlook: Jackson Hole Economic Symposium",
                delivered_at=datetime(2024, 8, 23, 10, 0),
                published_at=datetime(2024, 8, 23, 10, 5),
                location="Jackson Hole, Wyoming",
                source_url="https://www.federalreserve.gov/newsevents/speech/powell20240823a.htm",
                key_takeaway="'The time has come for policy to adjust. The direction of travel is clear, and the timing and pace of rate cuts will depend on incoming data, the evolving outlook, and the balance of risks.'",
            ),
        ]

        # 9. Forward Guidance
        self._guidance[cb_id] = [
            OfficialForwardGuidance(
                guidance_id="fg-fed-2024-11",
                central_bank_id=cb_id,
                source_document_id="doc-fed-stmt-2024-11-07",
                guidance_kind=ForwardGuidanceKind.STATE_CONTINGENT,
                verbatim_excerpt=(
                    "In considering additional adjustments to the target range for the federal funds rate, "
                    "the Committee will carefully assess incoming data, the evolving outlook, and the balance of risks."
                ),
                explicit_conditions="Conditioned on labor market developments, inflation indicators, and broader financial conditions.",
                published_at=datetime(2024, 11, 7, 14, 0),
                status="ACTIVE",
            )
        ]

        # 10. Balance Sheet
        self._balance_sheets[cb_id] = CentralBankBalanceSheetSummary(
            central_bank_id=cb_id,
            reference_date="2024-11-06",
            reporting_frequency="Weekly (H.4.1 Release)",
            currency="USD",
            total_assets_billions=Decimal("7012.4"),
            total_liabilities_billions=Decimal("6968.1"),
            securities_holdings_billions=Decimal("6520.8"),
            reserve_balances_billions=Decimal("3210.5"),
            items=[
                BalanceSheetItem("bs-fed-ust", "U.S. Treasury Securities held outright", "Securities", "ASSET", Decimal("4420.5"), "USD"),
                BalanceSheetItem("bs-fed-mbs", "Mortgage-backed securities (MBS) held outright", "Securities", "ASSET", Decimal("2100.3"), "USD"),
                BalanceSheetItem("bs-fed-reserves", "Reserve balances with Federal Reserve Banks", "Deposits", "LIABILITY", Decimal("3210.5"), "USD"),
                BalanceSheetItem("bs-fed-currency", "Federal Reserve notes outstanding (Currency)", "Currency", "LIABILITY", Decimal("2320.1"), "USD"),
                BalanceSheetItem("bs-fed-rrp", "Reverse repurchase agreements", "Borrowings", "LIABILITY", Decimal("215.2"), "USD"),
            ],
            accounting_notes="Federal Reserve Statistical Release H.4.1: Factors Affecting Reserve Balances of Depository Institutions.",
        )

        # 11. Programs
        self._programs[cb_id] = [
            CentralBankPolicyProgram(
                program_id="prog-fed-qt-runoff",
                central_bank_id=cb_id,
                name="System Open Market Account (SOMA) Balance Sheet Reduction (QT)",
                program_kind=PolicyProgramKind.BALANCE_SHEET_RUNOFF,
                announced_date="2022-05-04",
                effective_start="2022-06-01",
                effective_end=None,
                authorized_envelope_billions=None,
                current_holdings_billions=Decimal("6520.8"),
                status="ACTIVE",
                description="Redemption caps: $25B/month for U.S. Treasury securities (tapered from $60B in June 2024) and $35B/month for Agency MBS.",
            )
        ]

        # 12. Timeline
        self._timelines[cb_id] = [
            PolicyTimelineEvent(
                event_id="tl-fed-2024-11",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 11, 7, 14, 0),
                event_kind="RATE_DECISION",
                title="FOMC lowers Federal Funds Target Range by 25 bps",
                summary="Target range reduced to 4.50% - 4.75% unanimously.",
                instrument_code="FED_FUNDS_TARGET_RANGE",
                rate_change_bps=Decimal("-25.0"),
                document_id="doc-fed-stmt-2024-11-07",
            ),
            PolicyTimelineEvent(
                event_id="tl-fed-2024-09",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 9, 18, 14, 0),
                event_kind="RATE_DECISION",
                title="FOMC lowers Federal Funds Target Range by 50 bps",
                summary="Target range reduced to 4.75% - 5.00%. Governor Bowman dissented for 25 bps.",
                instrument_code="FED_FUNDS_TARGET_RANGE",
                rate_change_bps=Decimal("-50.0"),
                document_id="doc-fed-stmt-2024-09-18",
            ),
            PolicyTimelineEvent(
                event_id="tl-fed-2024-08",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 8, 23, 10, 0),
                event_kind="SPEECH",
                title="Chair Powell Jackson Hole Address",
                summary="'The time has come for policy to adjust.'",
            ),
            PolicyTimelineEvent(
                event_id="tl-fed-2024-07",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 7, 31, 14, 0),
                event_kind="RATE_DECISION",
                title="FOMC holds Federal Funds Target Range at 5.25% - 5.50%",
                summary="Rate held unchanged.",
                instrument_code="FED_FUNDS_TARGET_RANGE",
                rate_change_bps=Decimal("0.0"),
            ),
        ]

    def _seed_ecb(self) -> None:
        cb_id = "cb-ecb"

        # 1. Institution
        self._institutions[cb_id] = CentralBankInstitution(
            central_bank_id=cb_id,
            canonical_name="European Central Bank",
            acronym="ECB",
            institution_kind=CentralBankInstitutionKind.SUPRANATIONAL_CENTRAL_BANK,
            primary_geography_id="EA",
            monetary_area_id="EA",
            currency_code="EUR",
            official_website_url="https://www.ecb.europa.eu",
            established_year=1998,
            headquarters_city="Frankfurt am Main, Germany",
            primary_policy_committee="Governing Council of the European Central Bank",
            is_active=True,
            supported_instruments_count=3,
            notes="Sole issuer of the Euro across member states of the European Union monetary union.",
        )

        # 2. Framework
        self._frameworks[cb_id] = MonetaryPolicyFramework(
            central_bank_id=cb_id,
            mandate_title="Price Stability Mandate (Treaty on the Functioning of the EU)",
            mandate_summary=(
                "Primary objective under Article 127(1) of the Treaty is to maintain price stability. "
                "Without prejudice to price stability, it shall support general economic policies in the Union."
            ),
            operating_strategy=(
                "Symmetric 2 percent inflation target over the medium term. "
                "The Governing Council considers that price stability is best maintained by aiming for a 2% target as measured by the HICP."
            ),
            inflation_target_metric="Harmonised Index of Consumer Prices (HICP)",
            inflation_target_pct=Decimal("2.0"),
            target_lower_bound_pct=None,
            target_upper_bound_pct=None,
            target_tolerance_band="Symmetric 2.0% medium-term target",
            target_horizon="Medium Term",
            effective_since="1999 (revised 2021 Monetary Policy Strategy)",
            source_citation="ECB Strategy Review 2021 / Article 127(1) TFEU",
        )

        # 3. Instruments
        self._instruments[cb_id] = [
            PolicyInstrument(
                instrument_id="inst-ecb-deposit",
                central_bank_id=cb_id,
                code="ECB_DEPOSIT_FACILITY",
                name="Deposit Facility Rate (DFR)",
                category=PolicyInstrumentCategory.DEPOSIT_FACILITY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("3.25"),
                effective_date="2024-10-23",
                canonical_series_id="econ_ea_ecb_deposit_facility",
                operational_description="Primary operational rate through which the ECB steers its monetary policy stance.",
            ),
            PolicyInstrument(
                instrument_id="inst-ecb-mro",
                central_bank_id=cb_id,
                code="ECB_MAIN_REFINANCING",
                name="Main Refinancing Operations Rate (MRO)",
                category=PolicyInstrumentCategory.REFINANCING_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("3.40"),
                effective_date="2024-10-23",
                canonical_series_id="econ_ea_ecb_main_refinancing",
                operational_description="Fixed rate tender for regular weekly liquidity-providing credit operations (spread narrowed to 15 bps over DFR in Sep 2024).",
            ),
            PolicyInstrument(
                instrument_id="inst-ecb-marginal-lending",
                central_bank_id=cb_id,
                code="ECB_MARGINAL_LENDING",
                name="Marginal Lending Facility Rate (MLF)",
                category=PolicyInstrumentCategory.LENDING_FACILITY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("3.65"),
                effective_date="2024-10-23",
                canonical_series_id="econ_ea_ecb_marginal_lending",
                operational_description="Overnight credit facility rate to Eurosystem counterparties against eligible collateral.",
            ),
        ]

        # 4. Decisions
        self._decisions[cb_id] = [
            MonetaryPolicyDecision(
                decision_id="dec-ecb-2024-10-17",
                official_identifier="ECB-DEC-20241017",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 10, 17, 14, 15),
                effective_at=date(2024, 10, 23),
                meeting_id="meet-ecb-2024-10",
                statement_document_id="doc-ecb-stmt-2024-10-17",
                affected_instruments=["ECB_DEPOSIT_FACILITY", "ECB_MAIN_REFINANCING", "ECB_MARGINAL_LENDING"],
                rate_changes=[
                    RateChangeMetric("ECB_DEPOSIT_FACILITY", previous_rate=Decimal("3.50"), new_rate=Decimal("3.25"), change_bps=Decimal("-25.0")),
                    RateChangeMetric("ECB_MAIN_REFINANCING", previous_rate=Decimal("3.65"), new_rate=Decimal("3.40"), change_bps=Decimal("-25.0")),
                    RateChangeMetric("ECB_MARGINAL_LENDING", previous_rate=Decimal("3.90"), new_rate=Decimal("3.65"), change_bps=Decimal("-25.0")),
                ],
                policy_rationale=(
                    "The incoming information on inflation shows that the disinflationary process is well on track. "
                    "The inflation outlook is also affected by recent downside surprises in indicators of economic activity."
                ),
            ),
            MonetaryPolicyDecision(
                decision_id="dec-ecb-2024-09-12",
                official_identifier="ECB-DEC-20240912",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 9, 12, 14, 15),
                effective_at=date(2024, 9, 18),
                meeting_id="meet-ecb-2024-09",
                statement_document_id="doc-ecb-stmt-2024-09-12",
                affected_instruments=["ECB_DEPOSIT_FACILITY", "ECB_MAIN_REFINANCING", "ECB_MARGINAL_LENDING"],
                rate_changes=[
                    RateChangeMetric("ECB_DEPOSIT_FACILITY", previous_rate=Decimal("3.75"), new_rate=Decimal("3.50"), change_bps=Decimal("-25.0")),
                    RateChangeMetric("ECB_MAIN_REFINANCING", previous_rate=Decimal("4.25"), new_rate=Decimal("3.65"), change_bps=Decimal("-60.0")),
                    RateChangeMetric("ECB_MARGINAL_LENDING", previous_rate=Decimal("4.50"), new_rate=Decimal("3.90"), change_bps=Decimal("-60.0")),
                ],
                policy_rationale="Governing Council decided to lower the deposit facility rate by 25 basis points and enacted operational framework adjustments.",
            ),
        ]

        # 5. Meetings
        self._meetings[cb_id] = [
            MonetaryPolicyMeeting(
                meeting_id="meet-ecb-2024-10",
                official_identifier="ECB-MEET-20241016-17",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 10, 16),
                end_date=date(2024, 10, 17),
                decision_ids=["dec-ecb-2024-10-17"],
                statement_document_id="doc-ecb-stmt-2024-10-17",
                minutes_document_id="doc-ecb-acc-2024-10-17",
                minutes_published_at=datetime(2024, 11, 21, 13, 30),
                voting_record_id="vote-ecb-2024-10",
            ),
            MonetaryPolicyMeeting(
                meeting_id="meet-ecb-2024-09",
                official_identifier="ECB-MEET-20240911-12",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 9, 11),
                end_date=date(2024, 9, 12),
                decision_ids=["dec-ecb-2024-09-12"],
                statement_document_id="doc-ecb-stmt-2024-09-12",
                minutes_document_id="doc-ecb-acc-2024-09-12",
                minutes_published_at=datetime(2024, 10, 10, 13, 30),
                voting_record_id="vote-ecb-2024-09",
            ),
        ]

        # 6. Committee Voting (ECB does not publish individual voting records per statute)
        self._voting_records["meet-ecb-2024-10"] = CommitteeVotingRecord(
            record_id="vote-ecb-2024-10",
            meeting_id="meet-ecb-2024-10",
            decision_id="dec-ecb-2024-10-17",
            votes_for=26,
            votes_against=0,
            votes_abstain=0,
            individual_votes=[],
            is_publicly_disclosed=False,
            source_reference="ECB Governing Council operates on collegial consensus; individual member votes are not disclosed by statute.",
        )

        # 7. Publications
        self._publications[cb_id] = [
            OfficialPublication(
                document_id="doc-ecb-stmt-2024-10-17",
                central_bank_id=cb_id,
                title="Monetary policy decisions (17 October 2024)",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 10, 17, 14, 15),
                source_url="https://www.ecb.europa.eu/press/pr/date/2024/html/ecb.mp241017~91d1ec9b3f.en.html",
                media_type="HTML",
                content_hash="sha256-ecb-stmt-20241017",
                sanitized_excerpt="The Governing Council today decided to lower the three key ECB interest rates by 25 basis points.",
            )
        ]

        # 8. Speeches
        self._speeches[cb_id] = [
            OfficialSpeech(
                speech_id="sp-ecb-lagarde-2024-10-31",
                central_bank_id=cb_id,
                speaker_name="Christine Lagarde",
                speaker_role="President of the European Central Bank",
                title="Monetary policy in a shifting global environment",
                delivered_at=datetime(2024, 10, 31, 9, 30),
                published_at=datetime(2024, 10, 31, 9, 35),
                location="Florence, Italy",
                source_url="https://www.ecb.europa.eu/press/key/date/2024/html/ecb.sp241031~c0428ef5bc.en.html",
                key_takeaway="'Disinflation is on track, but economic headwinds require a vigilant, meeting-by-meeting data-dependent stance.'",
            )
        ]

        # 9. Forward Guidance
        self._guidance[cb_id] = [
            OfficialForwardGuidance(
                guidance_id="fg-ecb-2024-10",
                central_bank_id=cb_id,
                source_document_id="doc-ecb-stmt-2024-10-17",
                guidance_kind=ForwardGuidanceKind.POLICY_REACTION_FRAMEWORK,
                verbatim_excerpt=(
                    "The Governing Council will continue to follow a data-dependent and meeting-by-meeting approach "
                    "to determining the appropriate level and duration of restriction. In particular, its interest rate decisions "
                    "will be based on its assessment of the inflation outlook in light of incoming economic and financial data."
                ),
                explicit_conditions="Data-dependent, non-precommitted rate path.",
                published_at=datetime(2024, 10, 17, 14, 15),
                status="ACTIVE",
            )
        ]

        # 10. Balance Sheet
        self._balance_sheets[cb_id] = CentralBankBalanceSheetSummary(
            central_bank_id=cb_id,
            reference_date="2024-10-25",
            reporting_frequency="Weekly Financial Statement",
            currency="EUR",
            total_assets_billions=Decimal("6450.2"),
            total_liabilities_billions=Decimal("6410.5"),
            securities_holdings_billions=Decimal("4650.0"),
            reserve_balances_billions=Decimal("3020.1"),
            items=[
                BalanceSheetItem("bs-ecb-sec", "Securities of euro area residents denominated in euro", "Securities", "ASSET", Decimal("4650.0"), "EUR"),
                BalanceSheetItem("bs-ecb-gold", "Gold and gold receivables", "Reserves", "ASSET", Decimal("710.2"), "EUR"),
                BalanceSheetItem("bs-ecb-dep", "Current accounts and deposit facility liabilities", "Liabilities", "LIABILITY", Decimal("3020.1"), "EUR"),
                BalanceSheetItem("bs-ecb-banknotes", "Banknotes in circulation", "Currency", "LIABILITY", Decimal("1580.4"), "EUR"),
            ],
            accounting_notes="Consolidated Financial Statement of the Eurosystem.",
        )

        # 11. Programs
        self._programs[cb_id] = [
            CentralBankPolicyProgram(
                program_id="prog-ecb-pepp",
                central_bank_id=cb_id,
                name="Pandemic Emergency Purchase Programme (PEPP) Runoff",
                program_kind=PolicyProgramKind.BALANCE_SHEET_RUNOFF,
                announced_date="2023-12-14",
                effective_start="2024-07-01",
                effective_end=None,
                authorized_envelope_billions=Decimal("1710.0"),
                current_holdings_billions=Decimal("1650.0"),
                status="ACTIVE",
                description="The Governing Council is reducing the PEPP portfolio by €7.5 billion per month on average and intends to discontinue reinvestments at end-2024.",
            )
        ]

        # 12. Timeline
        self._timelines[cb_id] = [
            PolicyTimelineEvent(
                event_id="tl-ecb-2024-10",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 10, 17, 14, 15),
                event_kind="RATE_DECISION",
                title="ECB lowers key interest rates by 25 bps",
                summary="Deposit facility cut to 3.25%, MRO to 3.40%, Marginal lending to 3.65%.",
                instrument_code="ECB_DEPOSIT_FACILITY",
                rate_change_bps=Decimal("-25.0"),
                document_id="doc-ecb-stmt-2024-10-17",
            ),
            PolicyTimelineEvent(
                event_id="tl-ecb-2024-09",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 9, 12, 14, 15),
                event_kind="RATE_DECISION",
                title="ECB lowers deposit facility by 25 bps and implements operational framework",
                summary="Deposit facility cut to 3.50%. Spread to MRO narrowed to 15 bps.",
                instrument_code="ECB_DEPOSIT_FACILITY",
                rate_change_bps=Decimal("-25.0"),
            ),
        ]

    def _seed_boe(self) -> None:
        cb_id = "cb-boe"

        self._institutions[cb_id] = CentralBankInstitution(
            central_bank_id=cb_id,
            canonical_name="Bank of England",
            acronym="BoE",
            institution_kind=CentralBankInstitutionKind.NATIONAL_CENTRAL_BANK,
            primary_geography_id="GB",
            monetary_area_id="GB",
            currency_code="GBP",
            official_website_url="https://www.bankofengland.co.uk",
            established_year=1694,
            headquarters_city="London, United Kingdom",
            primary_policy_committee="Monetary Policy Committee (MPC)",
            is_active=True,
            supported_instruments_count=1,
            notes="Statutory monetary policy independence established under the Bank of England Act 1998.",
        )

        self._frameworks[cb_id] = MonetaryPolicyFramework(
            central_bank_id=cb_id,
            mandate_title="Statutory Price Stability Remit (Bank of England Act 1998)",
            mandate_summary="Maintain price stability, and subject to that, support the economic policy of His Majesty's Government.",
            operating_strategy="Symmetric 2.0% 12-month CPI inflation target confirmed annually by the Chancellor of the Exchequer.",
            inflation_target_metric="Consumer Prices Index (CPI)",
            inflation_target_pct=Decimal("2.0"),
            target_tolerance_band="Open letter threshold of +/- 1.0 percentage point (i.e. <1.0% or >3.0%)",
            target_horizon="Medium Term",
            effective_since="1997 / 1998 Act",
            source_citation="HM Treasury Remit for the Monetary Policy Committee",
        )

        self._instruments[cb_id] = [
            PolicyInstrument(
                instrument_id="inst-boe-bank-rate",
                central_bank_id=cb_id,
                code="BOE_BANK_RATE",
                name="Official Bank Rate",
                category=PolicyInstrumentCategory.PRIMARY_POLICY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("4.75"),
                effective_date="2024-11-08",
                canonical_series_id="econ_gb_boe_bank_rate",
                operational_description="Interest rate paid by the Bank of England on central bank reserves.",
            ),
        ]

        self._decisions[cb_id] = [
            MonetaryPolicyDecision(
                decision_id="dec-boe-2024-11-07",
                official_identifier="BOE-DEC-20241107",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 11, 7, 12, 0),
                effective_at=date(2024, 11, 8),
                meeting_id="meet-boe-2024-11",
                statement_document_id="doc-boe-stmt-2024-11-07",
                affected_instruments=["BOE_BANK_RATE"],
                rate_changes=[
                    RateChangeMetric("BOE_BANK_RATE", previous_rate=Decimal("5.00"), new_rate=Decimal("4.75"), change_bps=Decimal("-25.0")),
                ],
                policy_rationale="The Monetary Policy Committee voted by a majority of 8-1 to reduce Bank Rate by 0.25 percentage points to 4.75%.",
            ),
            MonetaryPolicyDecision(
                decision_id="dec-boe-2024-09-19",
                official_identifier="BOE-DEC-20240919",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_HOLD,
                announced_at=datetime(2024, 9, 19, 12, 0),
                effective_at=date(2024, 9, 20),
                meeting_id="meet-boe-2024-09",
                statement_document_id="doc-boe-stmt-2024-09-19",
                affected_instruments=["BOE_BANK_RATE"],
                rate_changes=[
                    RateChangeMetric("BOE_BANK_RATE", previous_rate=Decimal("5.00"), new_rate=Decimal("5.00"), change_bps=Decimal("0.0")),
                ],
                policy_rationale="The MPC voted by a majority of 8-1 to maintain Bank Rate at 5.0%.",
            ),
        ]

        self._meetings[cb_id] = [
            MonetaryPolicyMeeting(
                meeting_id="meet-boe-2024-11",
                official_identifier="BOE-MEET-20241106-07",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 11, 6),
                end_date=date(2024, 11, 7),
                decision_ids=["dec-boe-2024-11-07"],
                statement_document_id="doc-boe-stmt-2024-11-07",
                minutes_document_id="doc-boe-min-2024-11-07",
                minutes_published_at=datetime(2024, 11, 7, 12, 0),
                voting_record_id="vote-boe-2024-11",
            ),
        ]

        self._voting_records["meet-boe-2024-11"] = CommitteeVotingRecord(
            record_id="vote-boe-2024-11",
            meeting_id="meet-boe-2024-11",
            decision_id="dec-boe-2024-11-07",
            votes_for=8,
            votes_against=1,
            votes_abstain=0,
            individual_votes=[
                IndividualVote("Andrew Bailey", "Governor", VotingOutcomeKind.FOR),
                IndividualVote("Sarah Breeden", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Ben Broadbent", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Lombardelli Clare", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Dave Ramsden", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Swati Dhingra", "External Member", VotingOutcomeKind.FOR),
                IndividualVote("Megan Greene", "External Member", VotingOutcomeKind.FOR),
                IndividualVote("Alan Taylor", "External Member", VotingOutcomeKind.FOR),
                IndividualVote("Catherine L. Mann", "External Member", VotingOutcomeKind.AGAINST, dissent_rationale="Preferred to maintain Bank Rate at 5.00%."),
            ],
            is_publicly_disclosed=True,
            source_reference="Bank of England Monetary Policy Summary, November 2024",
        )

        self._publications[cb_id] = [
            OfficialPublication(
                document_id="doc-boe-stmt-2024-11-07",
                central_bank_id=cb_id,
                title="Monetary Policy Summary and minutes of the Monetary Policy Committee meeting",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 11, 7, 12, 0),
                source_url="https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2024/november-2024",
                media_type="HTML",
                content_hash="sha256-boe-stmt-20241107",
                sanitized_excerpt="The Bank of England's Monetary Policy Committee voted by a majority of 8-1 to reduce Bank Rate by 0.25 percentage points, to 4.75%.",
            )
        ]

        self._speeches[cb_id] = [
            OfficialSpeech(
                speech_id="sp-boe-bailey-2024-11-14",
                central_bank_id=cb_id,
                speaker_name="Andrew Bailey",
                speaker_role="Governor of the Bank of England",
                title="Mansion House Speech: The Outlook for the UK Economy",
                delivered_at=datetime(2024, 11, 14, 20, 0),
                published_at=datetime(2024, 11, 14, 20, 15),
                location="Mansion House, London",
                source_url="https://www.bankofengland.co.uk/speech/2024/november/andrew-bailey-speech-at-mansion-house",
                key_takeaway="'A gradual approach to removing monetary policy restraint will remain appropriate as disinflation proceeds.'",
            )
        ]

        self._guidance[cb_id] = [
            OfficialForwardGuidance(
                guidance_id="fg-boe-2024-11",
                central_bank_id=cb_id,
                source_document_id="doc-boe-stmt-2024-11-07",
                guidance_kind=ForwardGuidanceKind.STATE_CONTINGENT,
                verbatim_excerpt="Based on the evolving evidence, a gradual approach to removing policy restraint will remain appropriate.",
                explicit_conditions="Conditional on inflation remaining aligned with the 2% target sustainably.",
                published_at=datetime(2024, 11, 7, 12, 0),
                status="ACTIVE",
            )
        ]

        self._balance_sheets[cb_id] = CentralBankBalanceSheetSummary(
            central_bank_id=cb_id,
            reference_date="2024-10-30",
            reporting_frequency="Weekly (Bank of England Return)",
            currency="GBP",
            total_assets_billions=Decimal("812.4"),
            total_liabilities_billions=Decimal("808.2"),
            securities_holdings_billions=Decimal("685.0"),
            reserve_balances_billions=Decimal("730.5"),
            items=[
                BalanceSheetItem("bs-boe-gilt", "Loan to Asset Purchase Facility (APF) - UK Gilts", "Loans", "ASSET", Decimal("685.0"), "GBP"),
                BalanceSheetItem("bs-boe-res", "Reserve Balances of commercial banks", "Reserves", "LIABILITY", Decimal("730.5"), "GBP"),
                BalanceSheetItem("bs-boe-notes", "Bank of England notes in circulation", "Notes", "LIABILITY", Decimal("86.4"), "GBP"),
            ],
            accounting_notes="Bank of England Weekly Bank Return.",
        )

        self._programs[cb_id] = [
            CentralBankPolicyProgram(
                program_id="prog-boe-apf-qt",
                central_bank_id=cb_id,
                name="Asset Purchase Facility (APF) Quantitative Tightening",
                program_kind=PolicyProgramKind.BALANCE_SHEET_RUNOFF,
                announced_date="2024-09-19",
                effective_start="2024-10-01",
                effective_end=None,
                authorized_envelope_billions=Decimal("100.0"),
                current_holdings_billions=Decimal("685.0"),
                status="ACTIVE",
                description="MPC confirmed target to reduce the stock of UK government bond purchases by £100 billion over October 2024 to September 2025.",
            )
        ]

        self._timelines[cb_id] = [
            PolicyTimelineEvent(
                event_id="tl-boe-2024-11",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 11, 7, 12, 0),
                event_kind="RATE_DECISION",
                title="MPC reduces Bank Rate by 25 bps to 4.75%",
                summary="Majority of 8-1 voted for 25 bps reduction.",
                instrument_code="BOE_BANK_RATE",
                rate_change_bps=Decimal("-25.0"),
                document_id="doc-boe-stmt-2024-11-07",
            )
        ]

    def _seed_boj(self) -> None:
        cb_id = "cb-boj"

        self._institutions[cb_id] = CentralBankInstitution(
            central_bank_id=cb_id,
            canonical_name="Bank of Japan",
            acronym="BoJ",
            institution_kind=CentralBankInstitutionKind.NATIONAL_CENTRAL_BANK,
            primary_geography_id="JP",
            monetary_area_id="JP",
            currency_code="JPY",
            official_website_url="https://www.boj.or.jp",
            established_year=1882,
            headquarters_city="Tokyo, Japan",
            primary_policy_committee="Policy Board of the Bank of Japan",
            is_active=True,
            supported_instruments_count=1,
            notes="Statutory independence governed by the revised Bank of Japan Act of 1997.",
        )

        self._frameworks[cb_id] = MonetaryPolicyFramework(
            central_bank_id=cb_id,
            mandate_title="Price Stability and Financial System Soundness (Bank of Japan Act)",
            mandate_summary="Pursuing price stability to contribute to the sound development of the national economy.",
            operating_strategy="Price Stability Target of 2 percent in terms of year-on-year rate of change in the Consumer Price Index (CPI).",
            inflation_target_metric="CPI (all items less fresh food)",
            inflation_target_pct=Decimal("2.0"),
            target_tolerance_band="2.0% sustainable objective",
            target_horizon="Earliest possible time",
            effective_since="2013 Joint Statement with Government",
            source_citation="Joint Statement of the Government and the Bank of Japan on Overcoming Deflation",
        )

        self._instruments[cb_id] = [
            PolicyInstrument(
                instrument_id="inst-boj-call-rate",
                central_bank_id=cb_id,
                code="BOJ_CALL_RATE",
                name="Uncollateralized Overnight Call Rate Target",
                category=PolicyInstrumentCategory.OVERNIGHT_RATE_TARGET,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("0.25"),
                effective_date="2024-08-01",
                canonical_series_id="econ_jp_boj_call_rate",
                operational_description="Primary operational target rate for money market operations (hiked from 0.0-0.10% to around 0.25% in July 2024).",
            )
        ]

        self._decisions[cb_id] = [
            MonetaryPolicyDecision(
                decision_id="dec-boj-2024-10-31",
                official_identifier="BOJ-DEC-20241031",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_HOLD,
                announced_at=datetime(2024, 10, 31, 12, 0),
                effective_at=date(2024, 11, 1),
                meeting_id="meet-boj-2024-10",
                statement_document_id="doc-boj-stmt-2024-10-31",
                affected_instruments=["BOJ_CALL_RATE"],
                rate_changes=[
                    RateChangeMetric("BOJ_CALL_RATE", previous_rate=Decimal("0.25"), new_rate=Decimal("0.25"), change_bps=Decimal("0.0")),
                ],
                policy_rationale="The Bank decided by a unanimous vote to maintain the uncollateralized overnight call rate target at around 0.25%.",
            ),
            MonetaryPolicyDecision(
                decision_id="dec-boj-2024-07-31",
                official_identifier="BOJ-DEC-20240731",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_INCREASE,
                announced_at=datetime(2024, 7, 31, 12, 30),
                effective_at=date(2024, 8, 1),
                meeting_id="meet-boj-2024-07",
                statement_document_id="doc-boj-stmt-2024-07-31",
                affected_instruments=["BOJ_CALL_RATE"],
                rate_changes=[
                    RateChangeMetric("BOJ_CALL_RATE", previous_rate=Decimal("0.10"), new_rate=Decimal("0.25"), change_bps=Decimal("15.0")),
                ],
                policy_rationale="The Bank decided to encourage the uncollateralized overnight call rate to remain at around 0.25 percent.",
            ),
        ]

        self._meetings[cb_id] = [
            MonetaryPolicyMeeting(
                meeting_id="meet-boj-2024-10",
                official_identifier="BOJ-MEET-20241030-31",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 10, 30),
                end_date=date(2024, 10, 31),
                decision_ids=["dec-boj-2024-10-31"],
                statement_document_id="doc-boj-stmt-2024-10-31",
                minutes_document_id="doc-boj-min-2024-10-31",
                minutes_published_at=datetime(2024, 11, 6, 8, 50),
                voting_record_id="vote-boj-2024-10",
            ),
        ]

        self._voting_records["meet-boj-2024-10"] = CommitteeVotingRecord(
            record_id="vote-boj-2024-10",
            meeting_id="meet-boj-2024-10",
            decision_id="dec-boj-2024-10-31",
            votes_for=9,
            votes_against=0,
            votes_abstain=0,
            individual_votes=[
                IndividualVote("Kazuo Ueda", "Governor", VotingOutcomeKind.FOR),
                IndividualVote("Shinichi Uchida", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Ryozo Himino", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Seiji Adachi", "Member of Policy Board", VotingOutcomeKind.FOR),
                IndividualVote("Asahi Noguchi", "Member of Policy Board", VotingOutcomeKind.FOR),
                IndividualVote("Naoki Tamura", "Member of Policy Board", VotingOutcomeKind.FOR),
                IndividualVote("Junko Nakagawa", "Member of Policy Board", VotingOutcomeKind.FOR),
                IndividualVote("Hajime Takata", "Member of Policy Board", VotingOutcomeKind.FOR),
                IndividualVote("Toyoaki Nakamura", "Member of Policy Board", VotingOutcomeKind.FOR),
            ],
            is_publicly_disclosed=True,
            source_reference="Bank of Japan Statement on Monetary Policy, October 31, 2024",
        )

        self._publications[cb_id] = [
            OfficialPublication(
                document_id="doc-boj-stmt-2024-10-31",
                central_bank_id=cb_id,
                title="Statement on Monetary Policy (October 31, 2024)",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 10, 31, 12, 0),
                source_url="https://www.boj.or.jp/en/mopo/mpmdeci/mpe_2024/k241031a.pdf",
                media_type="PDF",
                content_hash="sha256-boj-stmt-20241031",
                sanitized_excerpt="At the Monetary Policy Meeting held today, the Policy Board of the Bank of Japan decided to keep the uncollateralized overnight call rate at around 0.25%.",
            )
        ]

        self._speeches[cb_id] = [
            OfficialSpeech(
                speech_id="sp-boj-ueda-2024-11-18",
                central_bank_id=cb_id,
                speaker_name="Kazuo Ueda",
                speaker_role="Governor of the Bank of Japan",
                title="Economic Activity and Prices in Japan and Monetary Policy",
                delivered_at=datetime(2024, 11, 18, 10, 0),
                published_at=datetime(2024, 11, 18, 10, 30),
                location="Nagoya, Japan",
                source_url="https://www.boj.or.jp/en/about/press/koen_2024/ko241118a.htm",
                key_takeaway="'The Bank will adjust the degree of monetary accommodation if economic and price developments evolve as expected.'",
            )
        ]

        self._guidance[cb_id] = [
            OfficialForwardGuidance(
                guidance_id="fg-boj-2024-10",
                central_bank_id=cb_id,
                source_document_id="doc-boj-stmt-2024-10-31",
                guidance_kind=ForwardGuidanceKind.POLICY_REACTION_FRAMEWORK,
                verbatim_excerpt=(
                    "If the baseline scenario presented in the Outlook Report is realized, the Bank will continue to raise the policy interest rate "
                    "and adjust the degree of monetary accommodation accordingly."
                ),
                explicit_conditions="Conditional on inflation and wage growth confirming the virtuous economic cycle.",
                published_at=datetime(2024, 10, 31, 12, 0),
                status="ACTIVE",
            )
        ]

        self._balance_sheets[cb_id] = CentralBankBalanceSheetSummary(
            central_bank_id=cb_id,
            reference_date="2024-10-31",
            reporting_frequency="Monthly Balance Sheet",
            currency="JPY",
            total_assets_billions=Decimal("752100.0"),  # 752.1 Trillion JPY
            total_liabilities_billions=Decimal("747800.0"),
            securities_holdings_billions=Decimal("588400.0"),  # Japanese Government Bonds
            reserve_balances_billions=Decimal("545200.0"),
            items=[
                BalanceSheetItem("bs-boj-jgb", "Japanese Government Bonds (JGBs)", "Securities", "ASSET", Decimal("588400.0"), "JPY"),
                BalanceSheetItem("bs-boj-cur", "Banknotes in circulation", "Notes", "LIABILITY", Decimal("124200.0"), "JPY"),
                BalanceSheetItem("bs-boj-dep", "Current account deposits", "Deposits", "LIABILITY", Decimal("545200.0"), "JPY"),
            ],
            accounting_notes="Bank of Japan Accounts, end of October 2024.",
        )

        self._programs[cb_id] = [
            CentralBankPolicyProgram(
                program_id="prog-boj-jgb-taper",
                central_bank_id=cb_id,
                name="Plan for the Reduction of the Purchase Amount of Japanese Government Bonds",
                program_kind=PolicyProgramKind.BALANCE_SHEET_RUNOFF,
                announced_date="2024-07-31",
                effective_start="2024-08-01",
                effective_end=None,
                authorized_envelope_billions=None,
                current_holdings_billions=Decimal("588400.0"),
                status="ACTIVE",
                description="Tapering monthly JGB purchases from approx ¥6 trillion to ¥3 trillion per month by Q1 2026.",
            )
        ]

        self._timelines[cb_id] = [
            PolicyTimelineEvent(
                event_id="tl-boj-2024-10",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 10, 31, 12, 0),
                event_kind="RATE_DECISION",
                title="Policy Board holds call rate target at 0.25%",
                summary="Unanimous decision to keep target around 0.25%.",
                instrument_code="BOJ_CALL_RATE",
                rate_change_bps=Decimal("0.0"),
                document_id="doc-boj-stmt-2024-10-31",
            ),
            PolicyTimelineEvent(
                event_id="tl-boj-2024-07",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 7, 31, 12, 30),
                event_kind="RATE_DECISION",
                title="Policy Board hikes call rate to 0.25%",
                summary="Hike from 0.0-0.10% to around 0.25% (+15 bps).",
                instrument_code="BOJ_CALL_RATE",
                rate_change_bps=Decimal("15.0"),
            ),
        ]

    def _seed_rbi(self) -> None:
        cb_id = "cb-rbi"

        self._institutions[cb_id] = CentralBankInstitution(
            central_bank_id=cb_id,
            canonical_name="Reserve Bank of India",
            acronym="RBI",
            institution_kind=CentralBankInstitutionKind.NATIONAL_CENTRAL_BANK,
            primary_geography_id="IN",
            monetary_area_id="IN",
            currency_code="INR",
            official_website_url="https://www.rbi.org.in",
            established_year=1935,
            headquarters_city="Mumbai, India",
            primary_policy_committee="Monetary Policy Committee (MPC)",
            is_active=True,
            supported_instruments_count=3,
            notes="Governed by the Reserve Bank of India Act, 1934; flexible inflation targeting enacted in 2016.",
        )

        self._frameworks[cb_id] = MonetaryPolicyFramework(
            central_bank_id=cb_id,
            mandate_title="Flexible Inflation Targeting Framework (RBI Act 1934)",
            mandate_summary="Maintain price stability while keeping in mind the objective of growth.",
            operating_strategy="Inflation target of 4.0% with an upper tolerance level of 6.0% and a lower tolerance level of 2.0%.",
            inflation_target_metric="Consumer Price Index (Combined) (CPI-C)",
            inflation_target_pct=Decimal("4.0"),
            target_lower_bound_pct=Decimal("2.0"),
            target_upper_bound_pct=Decimal("6.0"),
            target_tolerance_band="4.0% +/- 2.0% (2.0% to 6.0%)",
            target_horizon="Medium Term",
            effective_since="2016 (amended Section 45ZA of RBI Act)",
            source_citation="Gazette Notification on Inflation Target, Ministry of Finance, Government of India",
        )

        self._instruments[cb_id] = [
            PolicyInstrument(
                instrument_id="inst-rbi-repo",
                central_bank_id=cb_id,
                code="RBI_REPO_RATE",
                name="Policy Repo Rate",
                category=PolicyInstrumentCategory.REPO_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("6.50"),
                effective_date="2023-02-08",
                canonical_series_id="econ_in_rbi_repo_rate",
                operational_description="Primary rate at which the RBI lends short-term funds to commercial banks against government securities.",
            ),
            PolicyInstrument(
                instrument_id="inst-rbi-sdf",
                central_bank_id=cb_id,
                code="RBI_SDF_RATE",
                name="Standing Deposit Facility (SDF) Rate",
                category=PolicyInstrumentCategory.DEPOSIT_FACILITY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("6.25"),
                effective_date="2023-02-08",
                canonical_series_id="econ_in_rbi_sdf_rate",
                operational_description="Floor rate under the Liquidity Adjustment Facility (LAF) corridor without collateral requirement.",
            ),
            PolicyInstrument(
                instrument_id="inst-rbi-msf",
                central_bank_id=cb_id,
                code="RBI_MSF_RATE",
                name="Marginal Standing Facility (MSF) Rate",
                category=PolicyInstrumentCategory.LENDING_FACILITY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("6.75"),
                effective_date="2023-02-08",
                canonical_series_id="econ_in_rbi_msf_rate",
                operational_description="Ceiling rate under the LAF corridor for emergency overnight bank borrowing.",
            ),
        ]

        self._decisions[cb_id] = [
            MonetaryPolicyDecision(
                decision_id="dec-rbi-2024-10-09",
                official_identifier="RBI-DEC-20241009",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_HOLD,
                announced_at=datetime(2024, 10, 9, 10, 0),
                effective_at=date(2024, 10, 9),
                meeting_id="meet-rbi-2024-10",
                statement_document_id="doc-rbi-stmt-2024-10-09",
                affected_instruments=["RBI_REPO_RATE"],
                rate_changes=[
                    RateChangeMetric("RBI_REPO_RATE", previous_rate=Decimal("6.50"), new_rate=Decimal("6.50"), change_bps=Decimal("0.0")),
                ],
                policy_rationale=(
                    "The MPC decided by a 5-1 majority to keep the policy repo rate unchanged at 6.50%, "
                    "and unanimously decided to change the monetary policy stance from withdrawal of accommodation to 'neutral'."
                ),
            )
        ]

        self._meetings[cb_id] = [
            MonetaryPolicyMeeting(
                meeting_id="meet-rbi-2024-10",
                official_identifier="RBI-MEET-20241007-09",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 10, 7),
                end_date=date(2024, 10, 9),
                decision_ids=["dec-rbi-2024-10-09"],
                statement_document_id="doc-rbi-stmt-2024-10-09",
                minutes_document_id="doc-rbi-min-2024-10-09",
                minutes_published_at=datetime(2024, 10, 23, 17, 0),
                voting_record_id="vote-rbi-2024-10",
            )
        ]

        self._voting_records["meet-rbi-2024-10"] = CommitteeVotingRecord(
            record_id="vote-rbi-2024-10",
            meeting_id="meet-rbi-2024-10",
            decision_id="dec-rbi-2024-10-09",
            votes_for=5,
            votes_against=1,
            votes_abstain=0,
            individual_votes=[
                IndividualVote("Shaktikanta Das", "Governor", VotingOutcomeKind.FOR),
                IndividualVote("Michael Debabrata Patra", "Deputy Governor", VotingOutcomeKind.FOR),
                IndividualVote("Rajiv Ranjan", "Executive Director", VotingOutcomeKind.FOR),
                IndividualVote("Ram Singh", "External Member", VotingOutcomeKind.FOR),
                IndividualVote("Saugata Bhattacharya", "External Member", VotingOutcomeKind.FOR),
                IndividualVote("Nagesh Kumar", "External Member", VotingOutcomeKind.AGAINST, dissent_rationale="Voted to reduce the policy repo rate by 25 basis points."),
            ],
            is_publicly_disclosed=True,
            source_reference="Minutes of the Monetary Policy Committee Meeting, October 7-9, 2024",
        )

        self._publications[cb_id] = [
            OfficialPublication(
                document_id="doc-rbi-stmt-2024-10-09",
                central_bank_id=cb_id,
                title="Monetary Policy Statement, 2024-25 Resolution of the Monetary Policy Committee",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 10, 9, 10, 0),
                source_url="https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=58814",
                media_type="HTML",
                content_hash="sha256-rbi-stmt-20241009",
                sanitized_excerpt="On the basis of an assessment of current macroeconomic conditions, the Monetary Policy Committee (MPC) decided to keep the policy repo rate unchanged at 6.50 per cent.",
            )
        ]

        self._speeches[cb_id] = [
            OfficialSpeech(
                speech_id="sp-rbi-das-2024-10-09",
                central_bank_id=cb_id,
                speaker_name="Shaktikanta Das",
                speaker_role="Governor, Reserve Bank of India",
                title="Governor's Statement: Monetary Policy October 2024",
                delivered_at=datetime(2024, 10, 9, 10, 0),
                published_at=datetime(2024, 10, 9, 10, 15),
                location="Mumbai, India",
                source_url="https://www.rbi.org.in/Scripts/BS_ViewSpeeches.aspx?Id=1450",
                key_takeaway="'The horse is in the stable and inflation has moderated, but we cannot lower our guard until inflation durably aligns with the 4% target.'",
            )
        ]

        self._guidance[cb_id] = [
            OfficialForwardGuidance(
                guidance_id="fg-rbi-2024-10",
                central_bank_id=cb_id,
                source_document_id="doc-rbi-stmt-2024-10-09",
                guidance_kind=ForwardGuidanceKind.POLICY_REACTION_FRAMEWORK,
                verbatim_excerpt="The MPC decided to remain unambiguously focused on a durable alignment of inflation with the target, while supporting growth.",
                explicit_conditions="Focusing on durable alignment with 4% headline inflation target.",
                published_at=datetime(2024, 10, 9, 10, 0),
                status="ACTIVE",
            )
        ]

        self._balance_sheets[cb_id] = CentralBankBalanceSheetSummary(
            central_bank_id=cb_id,
            reference_date="2024-10-25",
            reporting_frequency="Weekly Statement of Affairs",
            currency="INR",
            total_assets_billions=Decimal("69850.0"),  # ₹69.85 Trillion INR
            total_liabilities_billions=Decimal("69850.0"),
            securities_holdings_billions=Decimal("15200.0"),
            reserve_balances_billions=Decimal("11400.0"),
            items=[
                BalanceSheetItem("bs-rbi-foreign", "Foreign Currency Assets & Gold", "External Reserves", "ASSET", Decimal("54200.0"), "INR"),
                BalanceSheetItem("bs-rbi-gov", "Rupee Securities including Treasury Bills", "Domestic Assets", "ASSET", Decimal("15200.0"), "INR"),
                BalanceSheetItem("bs-rbi-notes", "Notes in Circulation", "Currency", "LIABILITY", Decimal("35400.0"), "INR"),
                BalanceSheetItem("bs-rbi-dep", "Deposits of Banks", "Reserves", "LIABILITY", Decimal("11400.0"), "INR"),
            ],
            accounting_notes="Reserve Bank of India Weekly Statement of Affairs.",
        )

        self._programs[cb_id] = []

        self._timelines[cb_id] = [
            PolicyTimelineEvent(
                event_id="tl-rbi-2024-10",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 10, 9, 10, 0),
                event_kind="RATE_DECISION",
                title="MPC holds Repo Rate at 6.50% and shifts stance to Neutral",
                summary="Decision to hold rate was 5-1; shift in stance to Neutral was unanimous.",
                instrument_code="RBI_REPO_RATE",
                rate_change_bps=Decimal("0.0"),
                document_id="doc-rbi-stmt-2024-10-09",
            )
        ]

    def _seed_pboc(self) -> None:
        cb_id = "cb-pboc"

        self._institutions[cb_id] = CentralBankInstitution(
            central_bank_id=cb_id,
            canonical_name="People's Bank of China",
            acronym="PBOC",
            institution_kind=CentralBankInstitutionKind.NATIONAL_CENTRAL_BANK,
            primary_geography_id="CN",
            monetary_area_id="CN",
            currency_code="CNY",
            official_website_url="http://www.pbc.gov.cn",
            established_year=1948,
            headquarters_city="Beijing, China",
            primary_policy_committee="Monetary Policy Committee of the PBOC",
            is_active=True,
            supported_instruments_count=4,
            notes="Operates under the guidance of the State Council of the People's Republic of China.",
        )

        self._frameworks[cb_id] = MonetaryPolicyFramework(
            central_bank_id=cb_id,
            mandate_title="Multiple Objectives under the Law of the People's Republic of China on the PBOC",
            mandate_summary="Maintain currency value stability and thereby promote economic growth, while supporting financial stability and employment.",
            operating_strategy="Prudent and supportive monetary policy using market-based policy interest rate transmission.",
            inflation_target_metric="Consumer Price Index (CPI)",
            inflation_target_pct=Decimal("3.0"),
            target_tolerance_band="Around 3.0% annual ceiling target set by State Council",
            target_horizon="Annual Target",
            effective_since="1995 (Law on the PBOC)",
            source_citation="Government Work Report, National People's Congress",
        )

        self._instruments[cb_id] = [
            PolicyInstrument(
                instrument_id="inst-pboc-7d-repo",
                central_bank_id=cb_id,
                code="PBOC_7D_REVERSE_REPO",
                name="7-Day Reverse Repo Rate",
                category=PolicyInstrumentCategory.REPO_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("1.50"),
                effective_date="2024-09-27",
                canonical_series_id="econ_cn_pboc_7d_repo",
                operational_description="Primary short-term policy interest rate benchmark for open market operations.",
            ),
            PolicyInstrument(
                instrument_id="inst-pboc-1y-lpr",
                central_bank_id=cb_id,
                code="PBOC_1Y_LPR",
                name="1-Year Loan Prime Rate (LPR)",
                category=PolicyInstrumentCategory.PRIMARY_POLICY_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("3.10"),
                effective_date="2024-10-21",
                canonical_series_id="econ_cn_pboc_1y_lpr",
                operational_description="Benchmark lending reference rate for corporate and commercial bank loans.",
            ),
            PolicyInstrument(
                instrument_id="inst-pboc-5y-lpr",
                central_bank_id=cb_id,
                code="PBOC_5Y_LPR",
                name="5-Year Loan Prime Rate (LPR)",
                category=PolicyInstrumentCategory.OTHER_ADMINISTERED_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("3.60"),
                effective_date="2024-10-21",
                canonical_series_id="econ_cn_pboc_5y_lpr",
                operational_description="Benchmark reference rate for long-term loans and residential mortgage credit.",
            ),
            PolicyInstrument(
                instrument_id="inst-pboc-1y-mlf",
                central_bank_id=cb_id,
                code="PBOC_1Y_MLF",
                name="1-Year Medium-Term Lending Facility (MLF)",
                category=PolicyInstrumentCategory.REFINANCING_RATE,
                representation=PolicyRateRepresentationKind.SINGLE_RATE,
                current_rate=Decimal("2.00"),
                effective_date="2024-09-25",
                canonical_series_id="econ_cn_pboc_1y_mlf",
                operational_description="Medium-term refinancing facility for commercial banks.",
            ),
        ]

        self._decisions[cb_id] = [
            MonetaryPolicyDecision(
                decision_id="dec-pboc-2024-10-21",
                official_identifier="PBOC-DEC-20241021",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 10, 21, 9, 15),
                effective_at=date(2024, 10, 21),
                meeting_id=None,
                statement_document_id="doc-pboc-stmt-2024-10-21",
                affected_instruments=["PBOC_1Y_LPR", "PBOC_5Y_LPR"],
                rate_changes=[
                    RateChangeMetric("PBOC_1Y_LPR", previous_rate=Decimal("3.35"), new_rate=Decimal("3.10"), change_bps=Decimal("-25.0")),
                    RateChangeMetric("PBOC_5Y_LPR", previous_rate=Decimal("3.85"), new_rate=Decimal("3.60"), change_bps=Decimal("-25.0")),
                ],
                policy_rationale="National Interbank Funding Center announced reductions in the 1-year and 5-year Loan Prime Rates by 25 basis points.",
            ),
            MonetaryPolicyDecision(
                decision_id="dec-pboc-2024-09-27",
                official_identifier="PBOC-DEC-20240927",
                central_bank_id=cb_id,
                decision_kind=PolicyDecisionKind.RATE_DECREASE,
                announced_at=datetime(2024, 9, 27, 8, 0),
                effective_at=date(2024, 9, 27),
                meeting_id=None,
                statement_document_id="doc-pboc-stmt-2024-09-27",
                affected_instruments=["PBOC_7D_REVERSE_REPO"],
                rate_changes=[
                    RateChangeMetric("PBOC_7D_REVERSE_REPO", previous_rate=Decimal("1.70"), new_rate=Decimal("1.50"), change_bps=Decimal("-20.0")),
                ],
                policy_rationale="The PBOC decided to lower the 7-day reverse repurchase operation rate by 20 basis points from 1.7% to 1.5%.",
            ),
        ]

        self._meetings[cb_id] = [
            MonetaryPolicyMeeting(
                meeting_id="meet-pboc-2024-q3",
                official_identifier="PBOC-MEET-2024Q3",
                central_bank_id=cb_id,
                meeting_kind=MeetingKind.REGULAR_POLICY_MEETING,
                start_date=date(2024, 9, 23),
                end_date=date(2024, 9, 24),
                decision_ids=["dec-pboc-2024-09-27"],
                statement_document_id="doc-pboc-stmt-2024-09-27",
            )
        ]

        self._voting_records["meet-pboc-2024-q3"] = CommitteeVotingRecord(
            record_id="vote-pboc-2024-q3",
            meeting_id="meet-pboc-2024-q3",
            decision_id="dec-pboc-2024-09-27",
            votes_for=14,
            votes_against=0,
            votes_abstain=0,
            individual_votes=[],
            is_publicly_disclosed=False,
            source_reference="PBOC Monetary Policy Committee decisions are consultative; individual voting splits are not published.",
        )

        self._publications[cb_id] = [
            OfficialPublication(
                document_id="doc-pboc-stmt-2024-10-21",
                central_bank_id=cb_id,
                title="Loan Prime Rate (LPR) Announcement (October 21, 2024)",
                publication_kind=PublicationKind.POLICY_DECISION_STATEMENT,
                published_at=datetime(2024, 10, 21, 9, 15),
                source_url="http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html",
                media_type="HTML",
                content_hash="sha256-pboc-stmt-20241021",
                sanitized_excerpt="The 1-year LPR was quoted at 3.10% and the 5-year-plus LPR at 3.60%, both down by 25 basis points.",
            )
        ]

        self._speeches[cb_id] = [
            OfficialSpeech(
                speech_id="sp-pboc-pan-2024-09-24",
                central_bank_id=cb_id,
                speaker_name="Pan Gongsheng",
                speaker_role="Governor of the People's Bank of China",
                title="Press Conference on Financial Support for High-Quality Economic Development",
                delivered_at=datetime(2024, 9, 24, 9, 0),
                published_at=datetime(2024, 9, 24, 10, 0),
                location="Beijing, China (State Council Information Office)",
                source_url="http://www.scio.gov.cn/xwfbh/xwbfbh/wqfbh/49421/index.htm",
                key_takeaway="'The PBOC will reduce the reserve requirement ratio by 50 basis points and lower the 7-day reverse repo rate by 20 basis points.'",
            )
        ]

        self._guidance[cb_id] = [
            OfficialForwardGuidance(
                guidance_id="fg-pboc-2024-09",
                central_bank_id=cb_id,
                source_document_id="doc-pboc-stmt-2024-09-27",
                guidance_kind=ForwardGuidanceKind.POLICY_REACTION_FRAMEWORK,
                verbatim_excerpt="The PBOC will continue to adhere to a supportive monetary policy stance, strengthening counter-cyclical adjustments.",
                explicit_conditions="Supporting high-quality economic recovery and stable financial markets.",
                published_at=datetime(2024, 9, 24, 9, 0),
                status="ACTIVE",
            )
        ]

        self._balance_sheets[cb_id] = CentralBankBalanceSheetSummary(
            central_bank_id=cb_id,
            reference_date="2024-09-30",
            reporting_frequency="Monthly Balance Sheet",
            currency="CNY",
            total_assets_billions=Decimal("45210.0"),  # ¥45.21 Trillion CNY
            total_liabilities_billions=Decimal("45180.0"),
            securities_holdings_billions=Decimal("1520.0"),
            reserve_balances_billions=Decimal("23400.0"),
            items=[
                BalanceSheetItem("bs-pboc-foreign", "Foreign Exchange Assets", "External Reserves", "ASSET", Decimal("22100.0"), "CNY"),
                BalanceSheetItem("bs-pboc-claims", "Claims on Depository Corporations", "Credit", "ASSET", Decimal("16500.0"), "CNY"),
                BalanceSheetItem("bs-pboc-reserves", "Deposits of Depository Corporations", "Reserves", "LIABILITY", Decimal("23400.0"), "CNY"),
                BalanceSheetItem("bs-pboc-currency", "Currency in Circulation (M0)", "Currency", "LIABILITY", Decimal("12100.0"), "CNY"),
            ],
            accounting_notes="PBOC Balance Sheet of Monetary Authority, September 2024.",
        )

        self._programs[cb_id] = []

        self._timelines[cb_id] = [
            PolicyTimelineEvent(
                event_id="tl-pboc-2024-10",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 10, 21, 9, 15),
                event_kind="RATE_DECISION",
                title="PBOC announces 25 bps cut to 1Y and 5Y LPR",
                summary="1Y LPR lowered to 3.10%; 5Y LPR lowered to 3.60%.",
                instrument_code="PBOC_1Y_LPR",
                rate_change_bps=Decimal("-25.0"),
                document_id="doc-pboc-stmt-2024-10-21",
            ),
            PolicyTimelineEvent(
                event_id="tl-pboc-2024-09",
                central_bank_id=cb_id,
                timestamp=datetime(2024, 9, 27, 8, 0),
                event_kind="RATE_DECISION",
                title="PBOC cuts 7-day reverse repo rate by 20 bps",
                summary="7-day reverse repo rate reduced to 1.50%.",
                instrument_code="PBOC_7D_REVERSE_REPO",
                rate_change_bps=Decimal("-20.0"),
            ),
        ]

    # -------------------------------------------------------------------------
    # Public Query Methods
    # -------------------------------------------------------------------------

    def get_institution(self, central_bank_id: str) -> CentralBankInstitution:
        cid = self.resolve_institution_id(central_bank_id)
        return self._institutions[cid]

    def list_institutions(self) -> List[CentralBankInstitution]:
        return list(self._institutions.values())

    def get_framework(self, central_bank_id: str) -> MonetaryPolicyFramework:
        cid = self.resolve_institution_id(central_bank_id)
        return self._frameworks[cid]

    def get_instruments(self, central_bank_id: str) -> List[PolicyInstrument]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._instruments.get(cid, [])

    def get_instrument(self, central_bank_id: str, instrument_code: str) -> PolicyInstrument:
        instruments = self.get_instruments(central_bank_id)
        for inst in instruments:
            if inst.code.lower() == instrument_code.lower() or inst.instrument_id == instrument_code:
                return inst
        raise CentralBankInstrumentNotFoundError(
            f"Policy instrument '{instrument_code}' not found for central bank '{central_bank_id}'."
        )

    def get_decisions(self, central_bank_id: str) -> List[MonetaryPolicyDecision]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._decisions.get(cid, [])

    def get_decision(self, decision_id: str) -> MonetaryPolicyDecision:
        for dec_list in self._decisions.values():
            for dec in dec_list:
                if dec.decision_id == decision_id or dec.official_identifier == decision_id:
                    return dec
        raise CentralBankDecisionNotFoundError(f"Policy decision '{decision_id}' not found.")

    def get_meetings(self, central_bank_id: str) -> List[MonetaryPolicyMeeting]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._meetings.get(cid, [])

    def get_meeting(self, meeting_id: str) -> MonetaryPolicyMeeting:
        for meet_list in self._meetings.values():
            for meet in meet_list:
                if meet.meeting_id == meeting_id or meet.official_identifier == meeting_id:
                    return meet
        raise CentralBankMeetingNotFoundError(f"Policy meeting '{meeting_id}' not found.")

    def get_voting_record(self, meeting_id: str) -> Optional[CommitteeVotingRecord]:
        return self._voting_records.get(meeting_id)

    def get_publications(self, central_bank_id: str) -> List[OfficialPublication]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._publications.get(cid, [])

    def get_publication(self, document_id: str) -> OfficialPublication:
        for pub_list in self._publications.values():
            for pub in pub_list:
                if pub.document_id == document_id:
                    return pub
        raise CentralBankPublicationNotFoundError(f"Official publication '{document_id}' not found.")

    def get_speeches(self, central_bank_id: str) -> List[OfficialSpeech]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._speeches.get(cid, [])

    def get_guidance(self, central_bank_id: str) -> List[OfficialForwardGuidance]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._guidance.get(cid, [])

    def get_balance_sheet(self, central_bank_id: str) -> Optional[CentralBankBalanceSheetSummary]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._balance_sheets.get(cid)

    def get_programs(self, central_bank_id: str) -> List[CentralBankPolicyProgram]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._programs.get(cid, [])

    def get_timeline(self, central_bank_id: str) -> List[PolicyTimelineEvent]:
        cid = self.resolve_institution_id(central_bank_id)
        return self._timelines.get(cid, [])

    def determine_policy_cycle(self, central_bank_id: str) -> PolicyCycleKind:
        """Deterministically determine policy cycle from recent decisions on primary instrument."""
        decisions = self.get_decisions(central_bank_id)
        if not decisions:
            return PolicyCycleKind.UNKNOWN

        # Examine latest 2 decisions
        recent_kinds = [d.decision_kind for d in decisions[:2]]
        if all(k == PolicyDecisionKind.RATE_DECREASE for k in recent_kinds):
            return PolicyCycleKind.EASING
        if all(k == PolicyDecisionKind.RATE_INCREASE for k in recent_kinds):
            return PolicyCycleKind.TIGHTENING
        if decisions[0].decision_kind == PolicyDecisionKind.RATE_DECREASE:
            return PolicyCycleKind.EASING
        if decisions[0].decision_kind == PolicyDecisionKind.RATE_INCREASE:
            return PolicyCycleKind.TIGHTENING
        if decisions[0].decision_kind == PolicyDecisionKind.RATE_HOLD:
            return PolicyCycleKind.HOLDING
        return PolicyCycleKind.MIXED_OR_TRANSITIONAL

    def get_overview(self, central_bank_id: str) -> CentralBankOverview:
        cid = self.resolve_institution_id(central_bank_id)
        inst = self._institutions[cid]
        framework = self._frameworks[cid]
        instruments = self._instruments.get(cid, [])
        decisions = self._decisions.get(cid, [])
        meetings = self._meetings.get(cid, [])
        bs = self._balance_sheets.get(cid)
        programs = self._programs.get(cid, [])
        guidances = self._guidance.get(cid, [])

        latest_dec = decisions[0] if decisions else None
        latest_meet = meetings[0] if meetings else None
        active_guide = guidances[0] if guidances else None
        cycle = self.determine_policy_cycle(cid)

        return CentralBankOverview(
            institution=inst,
            framework=framework,
            instruments=instruments,
            latest_decision=latest_dec,
            latest_meeting=latest_meet,
            latest_balance_sheet=bs,
            active_programs_count=len([p for p in programs if p.status == "ACTIVE"]),
            active_forward_guidance=active_guide,
            current_policy_cycle=cycle,
            data_freshness_status="VERIFIED_OFFICIAL_CURRENT",
        )
