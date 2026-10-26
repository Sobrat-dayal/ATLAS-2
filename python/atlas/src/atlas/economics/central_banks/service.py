"""Domain Service for Central Bank Intelligence (Stage 91).

Orchestrates business logic, rate change basis-point calculations, deterministic policy
cycle evaluation, point-in-time filtering, and conversion to Pydantic V2 DTOs.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from .enums import PolicyRateRepresentationKind
from .errors import CentralBankIncompatibleInstrumentError, CentralBankRateRangeInvalidError
from .models import (
    CentralBankOverview,
    RateChangeMetric,
)
from .repository import CentralBanksRepository
from .schemas import (
    CentralBankBalanceSheetSummaryDTO,
    CentralBankCoverageResponseDTO,
    CentralBankInstitutionDTO,
    CentralBankOverviewDTO,
    CentralBankPolicyProgramDTO,
    CommitteeVotingRecordDTO,
    MonetaryPolicyDecisionDTO,
    MonetaryPolicyFrameworkDTO,
    MonetaryPolicyMeetingDTO,
    OfficialForwardGuidanceDTO,
    OfficialPublicationDTO,
    OfficialSpeechDTO,
    PolicyInstrumentDTO,
    PolicyTimelineEventDTO,
    CommitteeMetadataDTO,
    HistoricalRatePointDTO,
    InflationTargetDTO,
    SourceProvenanceDTO,
)


class CentralBankService:
    """Service orchestrating Central Bank Intelligence queries and transformations."""

    def __init__(self, repo: Optional[CentralBanksRepository] = None):
        self.repo = repo or CentralBanksRepository()

    # -------------------------------------------------------------------------
    # Rate Arithmetic & Validation
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_rate_change(
        instrument_code: str,
        representation: PolicyRateRepresentationKind,
        previous_rate: Optional[Decimal] = None,
        new_rate: Optional[Decimal] = None,
        previous_lower_bound: Optional[Decimal] = None,
        previous_upper_bound: Optional[Decimal] = None,
        new_lower_bound: Optional[Decimal] = None,
        new_upper_bound: Optional[Decimal] = None,
    ) -> RateChangeMetric:
        """Calculate basis-point change according to exact Stage 91 arithmetic: (New - Previous) * 100."""
        if representation == PolicyRateRepresentationKind.SINGLE_RATE:
            if previous_rate is None or new_rate is None:
                raise CentralBankIncompatibleInstrumentError("Single rate calculation requires previous_rate and new_rate.")
            change_bps = (new_rate - previous_rate) * Decimal("100")
            return RateChangeMetric(
                instrument_code=instrument_code,
                previous_rate=previous_rate,
                new_rate=new_rate,
                change_bps=change_bps,
            )

        if representation == PolicyRateRepresentationKind.TARGET_RANGE:
            if None in (previous_lower_bound, previous_upper_bound, new_lower_bound, new_upper_bound):
                raise CentralBankRateRangeInvalidError("Target range calculation requires all 4 bound endpoints.")
            if previous_lower_bound >= previous_upper_bound or new_lower_bound >= new_upper_bound:
                raise CentralBankRateRangeInvalidError("Lower bound must be strictly less than upper bound.")

            chg_lower = (new_lower_bound - previous_lower_bound) * Decimal("100")
            chg_upper = (new_upper_bound - previous_upper_bound) * Decimal("100")
            # For uniform ranges, primary change_bps matches
            avg_change = chg_lower if chg_lower == chg_upper else (chg_lower + chg_upper) / Decimal("2")

            return RateChangeMetric(
                instrument_code=instrument_code,
                previous_lower_bound=previous_lower_bound,
                previous_upper_bound=previous_upper_bound,
                new_lower_bound=new_lower_bound,
                new_upper_bound=new_upper_bound,
                change_lower_bps=chg_lower,
                change_upper_bps=chg_upper,
                change_bps=avg_change,
            )

        raise CentralBankIncompatibleInstrumentError(f"Unsupported rate representation kind: {representation}")

    # -------------------------------------------------------------------------
    # Institution & Overview
    # -------------------------------------------------------------------------

    def list_institutions(self) -> List[CentralBankInstitutionDTO]:
        institutions = self.repo.list_institutions()
        return [CentralBankInstitutionDTO.model_validate(inst) for inst in institutions]

    def get_institution(self, central_bank_id: str) -> CentralBankInstitutionDTO:
        inst = self.repo.get_institution(central_bank_id)
        return CentralBankInstitutionDTO.model_validate(inst)

    def get_overview(self, central_bank_id: str) -> CentralBankOverviewDTO:
        overview: CentralBankOverview = self.repo.get_overview(central_bank_id)
        return CentralBankOverviewDTO.model_validate(overview)

    def get_framework(self, central_bank_id: str) -> MonetaryPolicyFrameworkDTO:
        framework = self.repo.get_framework(central_bank_id)
        return MonetaryPolicyFrameworkDTO.model_validate(framework)

    def get_instruments(self, central_bank_id: str) -> List[PolicyInstrumentDTO]:
        instruments = self.repo.get_instruments(central_bank_id)
        return [PolicyInstrumentDTO.model_validate(inst) for inst in instruments]

    def get_instrument(self, central_bank_id: str, instrument_code: str) -> PolicyInstrumentDTO:
        inst = self.repo.get_instrument(central_bank_id, instrument_code)
        return PolicyInstrumentDTO.model_validate(inst)

    # -------------------------------------------------------------------------
    # Decisions & Meetings
    # -------------------------------------------------------------------------

    def get_decisions(self, central_bank_id: str) -> List[MonetaryPolicyDecisionDTO]:
        decisions = self.repo.get_decisions(central_bank_id)
        return [MonetaryPolicyDecisionDTO.model_validate(dec) for dec in decisions]

    def get_decision(self, decision_id: str) -> MonetaryPolicyDecisionDTO:
        dec = self.repo.get_decision(decision_id)
        return MonetaryPolicyDecisionDTO.model_validate(dec)

    def get_meetings(self, central_bank_id: str) -> List[MonetaryPolicyMeetingDTO]:
        meetings = self.repo.get_meetings(central_bank_id)
        return [MonetaryPolicyMeetingDTO.model_validate(meet) for meet in meetings]

    def get_meeting(self, meeting_id: str) -> MonetaryPolicyMeetingDTO:
        meet = self.repo.get_meeting(meeting_id)
        return MonetaryPolicyMeetingDTO.model_validate(meet)

    def get_voting_record(self, meeting_id: str) -> Optional[CommitteeVotingRecordDTO]:
        record = self.repo.get_voting_record(meeting_id)
        if record is None:
            return None
        return CommitteeVotingRecordDTO.model_validate(record)

    # -------------------------------------------------------------------------
    # Publications, Speeches & Guidance
    # -------------------------------------------------------------------------

    def get_publications(self, central_bank_id: str) -> List[OfficialPublicationDTO]:
        publications = self.repo.get_publications(central_bank_id)
        return [OfficialPublicationDTO.model_validate(pub) for pub in publications]

    def get_publication(self, document_id: str) -> OfficialPublicationDTO:
        pub = self.repo.get_publication(document_id)
        return OfficialPublicationDTO.model_validate(pub)

    def get_speeches(self, central_bank_id: str) -> List[OfficialSpeechDTO]:
        speeches = self.repo.get_speeches(central_bank_id)
        return [OfficialSpeechDTO.model_validate(sp) for sp in speeches]

    def get_guidance(self, central_bank_id: str) -> List[OfficialForwardGuidanceDTO]:
        guidances = self.repo.get_guidance(central_bank_id)
        return [OfficialForwardGuidanceDTO.model_validate(g) for g in guidances]

    # -------------------------------------------------------------------------
    # Balance Sheets & Programs
    # -------------------------------------------------------------------------

    def get_balance_sheet(self, central_bank_id: str) -> Optional[CentralBankBalanceSheetSummaryDTO]:
        bs = self.repo.get_balance_sheet(central_bank_id)
        if bs is None:
            return None
        return CentralBankBalanceSheetSummaryDTO.model_validate(bs)

    def get_programs(self, central_bank_id: str) -> List[CentralBankPolicyProgramDTO]:
        programs = self.repo.get_programs(central_bank_id)
        return [CentralBankPolicyProgramDTO.model_validate(prog) for prog in programs]

    def get_timeline(self, central_bank_id: str) -> List[PolicyTimelineEventDTO]:
        events = self.repo.get_timeline(central_bank_id)
        return [PolicyTimelineEventDTO.model_validate(ev) for ev in events]

    # -------------------------------------------------------------------------
    # Temporal Point-in-Time Qualification
    # -------------------------------------------------------------------------

    def filter_decisions_point_in_time(
        self, central_bank_id: str, as_of: datetime
    ) -> List[MonetaryPolicyDecisionDTO]:
        """Strict point-in-time filtering: return only decisions announced at or before `as_of`."""
        all_decisions = self.repo.get_decisions(central_bank_id)
        filtered = [d for d in all_decisions if d.announced_at <= as_of]
        return [MonetaryPolicyDecisionDTO.model_validate(d) for d in filtered]

    # -------------------------------------------------------------------------
    # Coverage Matrix
    # -------------------------------------------------------------------------

    def get_coverage(self, central_bank_id: str) -> CentralBankCoverageResponseDTO:
        cid = self.repo.resolve_institution_id(central_bank_id)
        inst = self.repo.get_institution(cid)
        instruments = self.repo.get_instruments(cid)
        decisions = self.repo.get_decisions(cid)
        meetings = self.repo.get_meetings(cid)
        publications = self.repo.get_publications(cid)
        speeches = self.repo.get_speeches(cid)
        guidances = self.repo.get_guidance(cid)
        bs = self.repo.get_balance_sheet(cid)
        programs = self.repo.get_programs(cid)

        has_target_range = any(i.representation == PolicyRateRepresentationKind.TARGET_RANGE for i in instruments)
        has_voting_records = any(self.repo.get_voting_record(m.meeting_id) is not None for m in meetings)

        return CentralBankCoverageResponseDTO(
            central_bank_id=cid,
            institution=CentralBankInstitutionDTO.model_validate(inst),
            has_policy_rate_series=len(instruments) > 0,
            has_target_range=has_target_range,
            has_decision_history=len(decisions) > 0,
            has_meeting_minutes=any(m.minutes_document_id is not None for m in meetings),
            has_voting_records=has_voting_records,
            has_official_statements=len(publications) > 0,
            has_official_speeches=len(speeches) > 0,
            has_forward_guidance=len(guidances) > 0,
            has_balance_sheet=bs is not None,
            has_policy_programs=len(programs) > 0,
        )

    # -------------------------------------------------------------------------
    # Inflation Targets, Committee, Sources & Rate History
    # -------------------------------------------------------------------------

    def get_targets(self, central_bank_id: str) -> InflationTargetDTO:
        framework = self.repo.get_framework(central_bank_id)
        return InflationTargetDTO(
            central_bank_id=framework.central_bank_id,
            inflation_target_metric=framework.inflation_target_metric,
            inflation_target_pct=float(framework.inflation_target_pct) if framework.inflation_target_pct is not None else None,
            target_lower_bound_pct=float(framework.target_lower_bound_pct) if framework.target_lower_bound_pct is not None else None,
            target_upper_bound_pct=float(framework.target_upper_bound_pct) if framework.target_upper_bound_pct is not None else None,
            target_tolerance_band=framework.target_tolerance_band,
            target_horizon=framework.target_horizon,
            effective_since=framework.effective_since,
            source_citation=framework.source_citation,
        )

    def get_committee_metadata(self, central_bank_id: str) -> CommitteeMetadataDTO:
        cid = self.repo.resolve_institution_id(central_bank_id)
        inst = self.repo.get_institution(cid)
        framework = self.repo.get_framework(cid)
        meetings = self.repo.get_meetings(cid)
        has_voting = any(self.repo.get_voting_record(m.meeting_id) is not None for m in meetings)
        member_counts = {
            "cb-fed": 12,
            "cb-ecb": 26,
            "cb-boe": 9,
            "cb-boj": 9,
            "cb-rbi": 6,
            "cb-pboc": 14,
        }
        return CommitteeMetadataDTO(
            central_bank_id=cid,
            committee_name=inst.primary_policy_committee,
            mandate=framework.mandate_summary,
            total_members=member_counts.get(cid, 9),
            discloses_individual_votes=has_voting,
            official_charter_url=inst.official_website_url,
        )

    def get_sources(self, central_bank_id: str) -> SourceProvenanceDTO:
        cid = self.repo.resolve_institution_id(central_bank_id)
        inst = self.repo.get_institution(cid)
        return SourceProvenanceDTO(
            central_bank_id=cid,
            official_institution_name=inst.canonical_name,
            official_website_url=inst.official_website_url,
            data_authority=f"OFFICIAL_{inst.acronym}_AUTHORITY",
            source_tier="OFFICIAL_CENTRAL_BANK",
            provenance_id=f"prov-{cid}-official",
            reporting_currency=inst.currency_code,
            is_point_in_time_verified=True,
        )

    def get_rate_history(self, central_bank_id: str) -> List[HistoricalRatePointDTO]:
        cid = self.repo.resolve_institution_id(central_bank_id)
        decisions = self.repo.get_decisions(cid)
        instruments = self.repo.get_instruments(cid)
        history: List[HistoricalRatePointDTO] = []

        # Populate from decisions
        for dec in decisions:
            for chg in dec.rate_changes:
                history.append(
                    HistoricalRatePointDTO(
                        observation_date=dec.announced_at.strftime("%Y-%m-%d"),
                        instrument_code=chg.instrument_code,
                        rate=float(chg.new_rate) if chg.new_rate is not None else None,
                        lower_bound=float(chg.new_lower_bound) if chg.new_lower_bound is not None else None,
                        upper_bound=float(chg.new_upper_bound) if chg.new_upper_bound is not None else None,
                        effective_date=dec.effective_at.strftime("%Y-%m-%d"),
                        source_decision_id=dec.decision_id,
                    )
                )

        # Include current instrument observations if not present
        for inst in instruments:
            already_has = any(h.instrument_code == inst.code for h in history)
            if not already_has:
                history.append(
                    HistoricalRatePointDTO(
                        observation_date=inst.effective_date,
                        instrument_code=inst.code,
                        rate=float(inst.current_rate) if inst.current_rate is not None else None,
                        lower_bound=float(inst.current_lower_bound) if inst.current_lower_bound is not None else None,
                        upper_bound=float(inst.current_upper_bound) if inst.current_upper_bound is not None else None,
                        effective_date=inst.effective_date,
                        source_decision_id=None,
                    )
                )

        return sorted(history, key=lambda x: x.effective_date, reverse=True)
