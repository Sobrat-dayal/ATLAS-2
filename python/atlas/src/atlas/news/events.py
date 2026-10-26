"""Canonical Financial News Event Classification & Evidence Tracking (Stage 101)."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from atlas.news.articles import NewsArticle
from atlas.news.enums import (
    EventAmountApproximation,
    EventAmountType,
    EventParticipantRole,
    EventTimePrecision,
    FinancialEventType,
    NewsCategory,
    NewsEventAssertionStatus,
    NewsEventLifecycleStatus,
    NewsEvidenceType,
)


class EventParticipant(BaseModel):
    """Specific entity participating in a corporate, market, or legal event."""

    entity_id: str = Field(..., description="Canonical entity ID (e.g., 'comp-aapl-001').")
    canonical_name: str = Field(..., description="Official name of participant.")
    role: EventParticipantRole = Field(
        default=EventParticipantRole.PRIMARY_SUBJECT,
        description="Functional role in transaction or event.",
    )
    resolution_status: str = Field(
        default="CONFIRMED", description="Verification confidence of association."
    )


class EventAmount(BaseModel):
    """Source-evidenced monetary or numerical figure associated with an event."""

    amount_type: EventAmountType = Field(..., description="Classification of financial figure.")
    amount_value: float = Field(..., description="Numerical magnitude.")
    currency: str = Field(default="USD", description="ISO 4217 currency code or percentage.")
    period: Optional[str] = Field(None, description="Fiscal period or tenure (e.g., 'Q3 2026').")
    approximation_status: EventAmountApproximation = Field(
        default=EventAmountApproximation.EXACT,
        description="Whether figure is exact, approximate, or a range boundary.",
    )
    source_text: Optional[str] = Field(
        None, description="Verbatim textual representation from source excerpt."
    )


class NewsEventEvidence(BaseModel):
    """Concrete, auditable source publication citation grounding a financial event."""

    evidence_id: str = Field(..., description="Unique evidence citation ID.")
    event_id: str = Field(..., description="ID of associated Financial Event.")
    article_id: str = Field(..., description="ID of source NewsArticle.")
    publisher_id: str = Field(..., description="Verified publisher identity.")
    publisher_name: str = Field(..., description="Display name of publisher.")
    source_provider_id: str = Field(..., description="Upstream ingestion provider identity.")
    evidence_type: NewsEvidenceType = Field(..., description="Document / publication category.")
    headline: str = Field(..., description="Source headline supporting event.")
    permitted_excerpt: Optional[str] = Field(
        None, description="Copyright-licensed excerpt or statement fragment."
    )
    source_published_at: datetime = Field(..., description="Publisher publication timestamp.")
    first_observed_at: datetime = Field(..., description="When ATLAS first observed evidence.")
    is_verified_by_filing: bool = Field(
        default=False, description="Whether corroborating regulatory filing exists."
    )
    filing_id: Optional[str] = Field(
        None, description="Associated Stage 86 Company Filing identifier if verified."
    )


class NewsEventRevision(BaseModel):
    """Audit record capturing status updates, corrections, and lifecycle changes."""

    revision_id: str = Field(..., description="Unique revision record ID.")
    event_id: str = Field(..., description="Target event ID.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When status transition was persisted.",
    )
    previous_lifecycle_status: Optional[NewsEventLifecycleStatus] = None
    new_lifecycle_status: NewsEventLifecycleStatus
    previous_assertion_status: Optional[NewsEventAssertionStatus] = None
    new_assertion_status: NewsEventAssertionStatus
    change_reason: str = Field(..., description="Explanation or source correction reference.")
    evidence_id: Optional[str] = Field(None, description="Evidence triggering the update.")


class NewsFinancialEvent(BaseModel):
    """
    Canonical, source-evidenced Financial Event record representing an identifiable
    corporate announcement, transaction milestone, regulatory mandate, or policy decision.
    """

    event_id: str = Field(..., description="Stable canonical Financial Event ID.")
    event_type: FinancialEventType = Field(..., description="Classified financial event type.")
    event_title: str = Field(..., description="Concise, source-backed display summary.")
    primary_entity_id: str = Field(..., description="Primary subject canonical entity ID.")
    primary_entity_name: str = Field(..., description="Primary subject entity display name.")
    lifecycle_status: NewsEventLifecycleStatus = Field(
        default=NewsEventLifecycleStatus.ANNOUNCED,
        description="Factual lifecycle state of occurrence.",
    )
    assertion_status: NewsEventAssertionStatus = Field(
        default=NewsEventAssertionStatus.OFFICIALLY_REPORTED,
        description="Evidentiary assertion level of report.",
    )
    event_date: Optional[datetime] = Field(
        None, description="Reported calendar date/time of event occurrence."
    )
    event_time_precision: EventTimePrecision = Field(
        default=EventTimePrecision.CALENDAR_DAY,
        description="Granularity of event date (exact, day, month, year).",
    )
    announcement_time: Optional[datetime] = Field(
        None, description="First public or official announcement timestamp."
    )
    first_seen_at: datetime = Field(
        ..., description="When ATLAS first indexed/observed event evidence."
    )
    last_evidence_updated_at: datetime = Field(
        ..., description="Timestamp of most recent supporting evidence."
    )
    participants: list[EventParticipant] = Field(
        default_factory=list, description="All verified entity participants and roles."
    )
    amounts: list[EventAmount] = Field(
        default_factory=list, description="Source-reported monetary values or quantities."
    )
    supporting_article_ids: list[str] = Field(
        default_factory=list, description="IDs of articles containing evidence for event."
    )
    evidence_records: list[NewsEventEvidence] = Field(
        default_factory=list, description="Structured citation records."
    )
    linked_story_ids: list[str] = Field(
        default_factory=list, description="Associated Story Threads."
    )
    revisions: list[NewsEventRevision] = Field(
        default_factory=list, description="Full audit trail of lifecycle updates."
    )
    is_disputed: bool = Field(default=False, description="True if contested by credible sources.")
    is_corrected: bool = Field(default=False, description="True if source revised claims.")
    source_revision_watermark: int = Field(default=1, description="Watermark for cache invalidation.")


class FinancialEventTypeDefinition(BaseModel):
    """Metadata specification for a supported financial event type."""

    event_type_id: FinancialEventType
    canonical_label: str
    event_family: str
    description: str
    supported_roles: list[EventParticipantRole]
    supported_amount_types: list[EventAmountType]


# ---------------------------------------------------------------------------
# Canonical Event Taxonomy Registry
# ---------------------------------------------------------------------------

EVENT_TYPE_CATALOG: list[FinancialEventTypeDefinition] = [
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.EARNINGS_RELEASE,
        canonical_label="Earnings Release",
        event_family="CORPORATE_ANNOUNCEMENT",
        description="Official publication of quarterly or annual revenue, profits, and operating metrics.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT, EventParticipantRole.ISSUER],
        supported_amount_types=[EventAmountType.QUARTERLY_REVENUE, EventAmountType.NET_INCOME],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.EARNINGS_GUIDANCE,
        canonical_label="Earnings Guidance",
        event_family="CORPORATE_ANNOUNCEMENT",
        description="Management forward-looking financial outlook and guidance updates.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT, EventParticipantRole.ISSUER],
        supported_amount_types=[EventAmountType.QUARTERLY_REVENUE, EventAmountType.NET_INCOME],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.DIVIDEND_DECLARATION,
        canonical_label="Dividend Declaration",
        event_family="CAPITAL_RETURN",
        description="Board declaration of cash dividends, special payouts, or bonus share distributions.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT, EventParticipantRole.ISSUER],
        supported_amount_types=[EventAmountType.DIVIDEND_PER_SHARE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.SHARE_REPURCHASE,
        canonical_label="Share Repurchase Authorization",
        event_family="CAPITAL_RETURN",
        description="Board authorization or programmatic execution of common stock buybacks.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT, EventParticipantRole.ISSUER],
        supported_amount_types=[EventAmountType.BUYBACK_AUTHORIZATION],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.MERGER_ACQUISITION_AGREEMENT,
        canonical_label="Merger / Acquisition Agreement",
        event_family="M_AND_A",
        description="Definitive agreement, demerger arrangement, or buyout contract between corporate entities.",
        supported_roles=[
            EventParticipantRole.PRIMARY_SUBJECT,
            EventParticipantRole.ACQUIRER,
            EventParticipantRole.TARGET,
            EventParticipantRole.SELLER,
        ],
        supported_amount_types=[EventAmountType.TRANSACTION_VALUE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.MERGER_ACQUISITION_PROPOSAL,
        canonical_label="Merger / Acquisition Proposal",
        event_family="M_AND_A",
        description="Unsolicited or preliminary takeover offer, acquisition approach, or buyout proposal.",
        supported_roles=[EventParticipantRole.ACQUIRER, EventParticipantRole.TARGET],
        supported_amount_types=[EventAmountType.TRANSACTION_VALUE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.MERGER_ACQUISITION_COMPLETION,
        canonical_label="Merger / Acquisition Completion",
        event_family="M_AND_A",
        description="Formal consummation, closing, and transfer of acquired business or merged entities.",
        supported_roles=[EventParticipantRole.ACQUIRER, EventParticipantRole.TARGET],
        supported_amount_types=[EventAmountType.TRANSACTION_VALUE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.EQUITY_FINANCING,
        canonical_label="Equity Financing",
        event_family="CAPITAL_RAISING",
        description="Secondary public equity offering, private placement, or rights issue announcement.",
        supported_roles=[EventParticipantRole.ISSUER, EventParticipantRole.UNDERWRITER, EventParticipantRole.INVESTOR],
        supported_amount_types=[EventAmountType.FINANCING_PROCEEDS],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.DEBT_FINANCING,
        canonical_label="Debt Financing",
        event_family="CAPITAL_RAISING",
        description="Senior note issuance, syndicated loan facility, or corporate bond offering.",
        supported_roles=[EventParticipantRole.ISSUER, EventParticipantRole.LENDER, EventParticipantRole.UNDERWRITER],
        supported_amount_types=[EventAmountType.FINANCING_PROCEEDS],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.MANAGEMENT_APPOINTMENT,
        canonical_label="Executive / Board Appointment",
        event_family="MANAGEMENT_GOVERNANCE",
        description="Appointment of CEO, CFO, key executive officers, or board directors.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT, EventParticipantRole.OFFICER],
        supported_amount_types=[],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.MANAGEMENT_DEPARTURE,
        canonical_label="Executive / Board Departure",
        event_family="MANAGEMENT_GOVERNANCE",
        description="Resignation, retirement, or removal of chief executive officers or board members.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT, EventParticipantRole.OFFICER],
        supported_amount_types=[],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.REGULATORY_ACTION,
        canonical_label="Regulatory Action / Enforcement",
        event_family="REGULATORY_LEGAL",
        description="Regulatory agency rulemaking, compliance directive, investigation, or fine.",
        supported_roles=[EventParticipantRole.REGULATOR, EventParticipantRole.SUBJECT, EventParticipantRole.RESPONDENT],
        supported_amount_types=[EventAmountType.REGULATORY_FINE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.LITIGATION_FILING,
        canonical_label="Litigation Filing",
        event_family="REGULATORY_LEGAL",
        description="Material lawsuit, civil antitrust complaint, or commercial arbitration filing.",
        supported_roles=[EventParticipantRole.SUBJECT, EventParticipantRole.RESPONDENT],
        supported_amount_types=[EventAmountType.TRANSACTION_VALUE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.BANKRUPTCY_FILING,
        canonical_label="Bankruptcy / Restructuring Filing",
        event_family="DISTRESSED",
        description="Chapter 11 or insolvency petition, debt standstill, or restructuring agreement.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT],
        supported_amount_types=[],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.PRODUCT_LAUNCH,
        canonical_label="Product Launch / Strategic Delivery",
        event_family="BUSINESS_OPERATION",
        description="Commercial launch or customer delivery of major product or technology architecture.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT],
        supported_amount_types=[],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.FACILITY_EXPANSION,
        canonical_label="Facility / Capacity Expansion",
        event_family="BUSINESS_OPERATION",
        description="Groundbreaking or commissioning of manufacturing fabs, data centers, or assembly facilities.",
        supported_roles=[EventParticipantRole.PRIMARY_SUBJECT],
        supported_amount_types=[EventAmountType.TRANSACTION_VALUE],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.CENTRAL_BANK_POLICY_DECISION,
        canonical_label="Central Bank Policy Decision",
        event_family="MACRO_POLICY",
        description="Monetary policy rate decision, target range hold, policy hike, or easing announcement.",
        supported_roles=[EventParticipantRole.REGULATOR],
        supported_amount_types=[EventAmountType.INTEREST_RATE_TARGET],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.ECONOMIC_RELEASE,
        canonical_label="Economic Data Release",
        event_family="MACRO_POLICY",
        description="Statistical release of macro indicators (CPI inflation, GDP, employment, trade balance).",
        supported_roles=[EventParticipantRole.REGULATOR],
        supported_amount_types=[],
    ),
    FinancialEventTypeDefinition(
        event_type_id=FinancialEventType.GOVERNMENT_POLICY,
        canonical_label="Government Policy Announcement",
        event_family="MACRO_POLICY",
        description="Executive order, sovereign fiscal legislation, tariff, or strategic subsidy policy.",
        supported_roles=[EventParticipantRole.REGULATOR],
        supported_amount_types=[],
    ),
]


class EventClassificationEngine:
    """
    Deterministic Financial Event Classifier and Evidence Extractor.
    Extracts structured, evidenced events from article metadata, categories,
    and headlines with strict assertion and lifecycle qualification.
    """

    def __init__(self, version: str = "1.0.0") -> None:
        self.version = version

    def classify_article(
        self,
        article: NewsArticle,
        linked_story_id: Optional[str] = None,
    ) -> list[NewsFinancialEvent]:
        """
        Extracts source-evidenced Financial Events from a NewsArticle.
        Returns empty list if no canonical event matches evidence standards.
        """
        text = f"{article.headline} {article.permitted_excerpt or ''}".lower()

        # 1. Classify Event Type
        event_type = self._detect_event_type(article, text)
        if not event_type:
            return []

        # 2. Determine Primary Entity
        entities = list(article.linked_entities)
        if not entities:
            from atlas.news.entity_resolution import resolve_entities_in_text
            entities = resolve_entities_in_text(article.headline, article.permitted_excerpt or "", list(article.tags))

        if not entities:
            if event_type in (
                FinancialEventType.CENTRAL_BANK_POLICY_DECISION,
                FinancialEventType.ECONOMIC_RELEASE,
                FinancialEventType.GOVERNMENT_POLICY,
            ):
                primary_id = article.publisher_id or "central_bank"
                primary_name = article.publisher_name or "Central Bank"
            else:
                words = article.headline.split()
                primary_name = " ".join(words[:2]) if len(words) >= 2 else (words[0] if words else "Corporate Entity")
                primary_id = f"entity-{primary_name.lower().replace(' ', '-')}"
        else:
            primary_ent = entities[0]
            primary_id = primary_ent.entity_id or "entity-unknown"
            primary_name = primary_ent.canonical_name or "Unknown Entity"

        # 3. Classify Assertion Status (Distinguish Rumor vs Confirmed vs Allegation)
        assertion_status = self._detect_assertion_status(article, text)

        # 4. Classify Lifecycle Status (Distinguish Proposed vs Announced vs Completed)
        lifecycle_status = self._detect_lifecycle_status(text, assertion_status)

        # 5. Extract Financial Amounts (without fabrication)
        amounts = self._extract_amounts(text, event_type)

        # 6. Extract Participants
        participants = self._resolve_participants(article, primary_id, primary_name, event_type)

        # 7. Generate deterministic Event ID
        event_id = self._generate_event_id(primary_id, event_type, article.published_at)

        # 8. Create structured Evidence Record
        clean_evidence_seed = f"{article.article_id}:{event_id}"
        ev_digest = hashlib.sha256(clean_evidence_seed.encode("utf-8")).hexdigest()[:12]
        evidence_id = f"evd-{ev_digest}"

        evidence_record = NewsEventEvidence(
            evidence_id=evidence_id,
            event_id=event_id,
            article_id=article.article_id,
            publisher_id=article.publisher_id,
            publisher_name=article.publisher_name or article.publisher,
            source_provider_id=article.source_provider_id,
            evidence_type=self._resolve_evidence_type(article),
            headline=article.headline,
            permitted_excerpt=article.permitted_excerpt,
            source_published_at=article.published_at,
            first_observed_at=article.first_seen_at or article.published_at,
            is_verified_by_filing=False,
            filing_id=None,
        )

        initial_revision = NewsEventRevision(
            revision_id=f"rev-{ev_digest}",
            event_id=event_id,
            timestamp=article.published_at,
            previous_lifecycle_status=None,
            new_lifecycle_status=lifecycle_status,
            previous_assertion_status=None,
            new_assertion_status=assertion_status,
            change_reason="Initial source publication",
            evidence_id=evidence_id,
        )

        event = NewsFinancialEvent(
            event_id=event_id,
            event_type=event_type,
            event_title=article.headline,
            primary_entity_id=primary_id,
            primary_entity_name=primary_name,
            lifecycle_status=lifecycle_status,
            assertion_status=assertion_status,
            event_date=article.published_at,
            event_time_precision=EventTimePrecision.CALENDAR_DAY,
            announcement_time=article.published_at,
            first_seen_at=article.first_seen_at or article.published_at,
            last_evidence_updated_at=article.published_at,
            participants=participants,
            amounts=amounts,
            supporting_article_ids=[article.article_id],
            evidence_records=[evidence_record],
            linked_story_ids=[linked_story_id] if linked_story_id else [],
            revisions=[initial_revision],
            is_disputed=(assertion_status == NewsEventAssertionStatus.DISPUTED),
            is_corrected=article.is_corrected,
            source_revision_watermark=1,
        )

        return [event]

    def _detect_event_type(
        self,
        article: NewsArticle,
        text: str,
    ) -> Optional[FinancialEventType]:
        """Maps article categories, topics, and headline keywords to canonical event types."""
        cats = set(article.categories)
        topics = set(article.topic_ids)

        # Central Bank
        if NewsCategory.CENTRAL_BANKS in cats or "INTEREST_RATES_MONETARY_POLICY" in topics:
            if any(w in text for w in ("target rate", "repo", "interest rate", "rate cut", "holds policy", "fomc")):
                return FinancialEventType.CENTRAL_BANK_POLICY_DECISION

        # M&A / Demerger / Buyout
        if "MERGERS_ACQUISITIONS" in topics or any(w in text for w in ("demerger", "acquire", "merger", "buyout", "takeover", "split-off")):
            if any(w in text for w in ("completed", "closed deal")):
                return FinancialEventType.MERGER_ACQUISITION_COMPLETION
            if any(w in text for w in ("considering", "weighs", "rumored", "explores", "preliminary")):
                return FinancialEventType.MERGER_ACQUISITION_PROPOSAL
            return FinancialEventType.MERGER_ACQUISITION_AGREEMENT

        # Dividends & Bonus Distributions
        if "DIVIDENDS_DISTRIBUTIONS" in topics or any(w in text for w in ("bonus issue", "dividend", "special payout", "dividend per share")):
            return FinancialEventType.DIVIDEND_DECLARATION

        # Buybacks
        if "SHARE_BUYBACKS" in topics or any(w in text for w in ("buyback", "share repurchase")):
            return FinancialEventType.SHARE_REPURCHASE

        # Earnings
        if "EARNINGS_RELEASES" in topics or any(w in text for w in ("quarterly results", "revenue growth", "reports services revenue", "q3 revenue", "q4 net income")):
            if any(w in text for w in ("forecasts", "guidance", "outlook")):
                return FinancialEventType.EARNINGS_GUIDANCE
            return FinancialEventType.EARNINGS_RELEASE

        # Regulatory Action
        if NewsCategory.REGULATION in cats or "FINANCIAL_REGULATION_COMPLIANCE" in topics or any(w in text for w in ("sec adopts", "climate disclosure", "antitrust lawsuit", "regulator fine")):
            return FinancialEventType.REGULATORY_ACTION

        # Capital Financing
        if "CAPITAL_RAISING" in topics or any(w in text for w in ("notes offering", "equity financing", "senior notes", "loan facility")):
            if "debt" in text or "notes" in text or "bond" in text:
                return FinancialEventType.DEBT_FINANCING
            return FinancialEventType.EQUITY_FINANCING

        # Strategic Delivery / Launch
        if any(w in text for w in ("delivers high-na", "scanner shipments", "launches enterprise generative ai", "product launch")):
            return FinancialEventType.PRODUCT_LAUNCH

        return None

    def _detect_assertion_status(
        self,
        article: NewsArticle,
        text: str,
    ) -> NewsEventAssertionStatus:
        """Determines factual reporting assertion level."""
        if any(w in text for w in ("rumored", "rumours", "people familiar", "considering", "weighing")):
            return NewsEventAssertionStatus.RUMORED
        if any(w in text for w in ("alleged", "probe", "investigating", "whistleblower claims")):
            return NewsEventAssertionStatus.ALLEGED
        if any(w in text for w in ("denies", "refutes", "dismisses reports")):
            return NewsEventAssertionStatus.DENIED
        if any(w in text for w in ("disputed", "contested")):
            return NewsEventAssertionStatus.DISPUTED

        # If official regulator or corporate announcement
        if article.article_type == "OFFICIAL_ANNOUNCEMENT" or article.source_provider_id in (
            "regulator_announcements", "corporate_press_wire"
        ):
            return NewsEventAssertionStatus.OFFICIALLY_REPORTED

        return NewsEventAssertionStatus.THIRD_PARTY_REPORTED

    def _detect_lifecycle_status(
        self,
        text: str,
        assertion: NewsEventAssertionStatus,
    ) -> NewsEventLifecycleStatus:
        """Determines corporate lifecycle stage."""
        if assertion == NewsEventAssertionStatus.RUMORED or any(w in text for w in ("considering", "proposed", "exploring")):
            return NewsEventLifecycleStatus.PROPOSED
        if any(w in text for w in ("completed", "closed transaction", "finished")):
            return NewsEventLifecycleStatus.COMPLETED
        if any(w in text for w in ("approved", "adopts rules", "greenlit", "sanctioned")):
            return NewsEventLifecycleStatus.APPROVED
        if any(w in text for w in ("canceled", "cancelled", "abandoned", "called off")):
            return NewsEventLifecycleStatus.CANCELLED
        if any(w in text for w in ("pending", "under review", "subject to regulatory")):
            return NewsEventLifecycleStatus.PENDING

        return NewsEventLifecycleStatus.ANNOUNCED

    def _extract_amounts(
        self,
        text: str,
        event_type: FinancialEventType,
    ) -> list[EventAmount]:
        """Extracts source-reported financial figures without extrapolation."""
        amounts: list[EventAmount] = []

        # Central Bank target rate pattern (e.g. 5.25%-5.50% or 6.50%)
        rate_match = re.search(r"(\d+\.\d+)%\s*(?:to|-)\s*(\d+\.\d+)%", text)
        if rate_match and event_type == FinancialEventType.CENTRAL_BANK_POLICY_DECISION:
            amounts.append(
                EventAmount(
                    amount_type=EventAmountType.INTEREST_RATE_TARGET,
                    amount_value=float(rate_match.group(2)),
                    currency="PERCENT",
                    approximation_status=EventAmountApproximation.RANGE_MAX,
                    source_text=rate_match.group(0),
                )
            )
            return amounts

        single_rate = re.search(r"(\d+\.\d+)%", text)
        if single_rate and event_type == FinancialEventType.CENTRAL_BANK_POLICY_DECISION:
            amounts.append(
                EventAmount(
                    amount_type=EventAmountType.INTEREST_RATE_TARGET,
                    amount_value=float(single_rate.group(1)),
                    currency="PERCENT",
                    approximation_status=EventAmountApproximation.EXACT,
                    source_text=single_rate.group(0),
                )
            )
            return amounts

        # Dollar magnitude extraction: e.g. $1 billion, $500 million
        dollar_match = re.search(r"\$(\d+(?:\.\d+)?)\s*(billion|million|bn|m)\b", text)
        if dollar_match:
            val = float(dollar_match.group(1))
            unit = dollar_match.group(2).lower()
            multiplier = 1_000_000_000 if "b" in unit else 1_000_000
            amt_type = EventAmountType.TRANSACTION_VALUE
            if event_type == FinancialEventType.SHARE_REPURCHASE:
                amt_type = EventAmountType.BUYBACK_AUTHORIZATION
            elif event_type == FinancialEventType.EARNINGS_RELEASE:
                amt_type = EventAmountType.QUARTERLY_REVENUE

            amounts.append(
                EventAmount(
                    amount_type=amt_type,
                    amount_value=val * multiplier,
                    currency="USD",
                    approximation_status=EventAmountApproximation.EXACT,
                    source_text=dollar_match.group(0),
                )
            )

        return amounts

    def _resolve_participants(
        self,
        article: NewsArticle,
        primary_id: str,
        primary_name: str,
        event_type: FinancialEventType,
    ) -> list[EventParticipant]:
        """Constructs role-qualified participant list."""
        participants: list[EventParticipant] = []

        primary_role = EventParticipantRole.PRIMARY_SUBJECT
        if event_type == FinancialEventType.CENTRAL_BANK_POLICY_DECISION:
            primary_role = EventParticipantRole.REGULATOR
        elif event_type in (FinancialEventType.EQUITY_FINANCING, FinancialEventType.DEBT_FINANCING):
            primary_role = EventParticipantRole.ISSUER

        participants.append(
            EventParticipant(
                entity_id=primary_id,
                canonical_name=primary_name,
                role=primary_role,
                resolution_status="CONFIRMED",
            )
        )

        # Additional participants from linked entities
        for ent in article.linked_entities[1:]:
            if ent.entity_id and ent.entity_id != primary_id:
                participants.append(
                    EventParticipant(
                        entity_id=ent.entity_id,
                        canonical_name=ent.canonical_name,
                        role=EventParticipantRole.SUBJECT,
                        resolution_status="CONFIRMED",
                    )
                )

        return participants

    def _resolve_evidence_type(self, article: NewsArticle) -> NewsEvidenceType:
        """Identifies document evidence category."""
        if article.source_provider_id == "regulator_announcements":
            return NewsEvidenceType.CENTRAL_BANK_RELEASE if "fed" in article.publisher_id or "rbi" in article.publisher_id else NewsEvidenceType.REGULATORY_FILING
        if article.source_provider_id == "corporate_press_wire":
            return NewsEvidenceType.OFFICIAL_PRESS_RELEASE
        if article.article_type == "WIRE_REPORT":
            return NewsEvidenceType.WIRE_REPORT
        return NewsEvidenceType.PUBLISHER_REPORT

    def _generate_event_id(
        self,
        primary_entity_id: str,
        event_type: FinancialEventType,
        pub_at: datetime,
    ) -> str:
        """Deterministic event ID generator based on entity, type, and date."""
        date_str = pub_at.strftime("%Y%m%d")
        seed = f"{primary_entity_id}:{event_type}:{date_str}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        return f"fev-{digest}"
