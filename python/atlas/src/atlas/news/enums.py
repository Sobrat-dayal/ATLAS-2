"""Canonical Enums for Institutional News Platform (Stage 99)."""

from enum import StrEnum


class NewsArticleType(StrEnum):
    """Canonical classification of financial news content types."""

    NEWS_REPORT = "NEWS_REPORT"
    WIRE_REPORT = "WIRE_REPORT"
    PRESS_RELEASE = "PRESS_RELEASE"
    OFFICIAL_ANNOUNCEMENT = "OFFICIAL_ANNOUNCEMENT"
    MARKET_COMMENTARY = "MARKET_COMMENTARY"
    OPINION = "OPINION"
    ANALYSIS = "ANALYSIS"


class NewsAvailabilityStatus(StrEnum):
    """Availability status of a news article entity."""

    AVAILABLE = "AVAILABLE"
    METADATA_ONLY = "METADATA_ONLY"
    SOURCE_RESTRICTED = "SOURCE_RESTRICTED"
    WITHDRAWN = "WITHDRAWN"
    REMOVED = "REMOVED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"


class NewsLicensingStatus(StrEnum):
    """Publisher copyright and licensing display constraints."""

    FULL_DISPLAY = "FULL_DISPLAY"
    EXCERPT_ONLY = "EXCERPT_ONLY"
    HEADLINE_ONLY = "HEADLINE_ONLY"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    RESTRICTED = "RESTRICTED"


class NewsCategory(StrEnum):
    """Institutional financial news taxonomy categories."""

    GENERAL_FINANCIAL = "GENERAL_FINANCIAL"
    COMPANY = "COMPANY"
    EQUITIES = "EQUITIES"
    FIXED_INCOME = "FIXED_INCOME"
    FOREIGN_EXCHANGE = "FOREIGN_EXCHANGE"
    COMMODITIES = "COMMODITIES"
    ECONOMICS = "ECONOMICS"
    CENTRAL_BANKS = "CENTRAL_BANKS"
    REGULATION = "REGULATION"
    CORPORATE_ACTIONS = "CORPORATE_ACTIONS"
    TECHNOLOGY = "TECHNOLOGY"


class NewsProviderType(StrEnum):
    """Type of upstream news integration mechanism."""

    LICENSED_NEWS_API = "LICENSED_NEWS_API"
    OFFICIAL_PUBLISHER_API = "OFFICIAL_PUBLISHER_API"
    LICENSED_RSS_FEED = "LICENSED_RSS_FEED"
    OFFICIAL_PUBLIC_FEED = "OFFICIAL_PUBLIC_FEED"
    APPROVED_STRUCTURED_DATASET = "APPROVED_STRUCTURED_DATASET"


class NewsLatencyClass(StrEnum):
    """Cadence and delivery SLA of a news source."""

    REALTIME = "REALTIME"
    NEAR_REALTIME = "NEAR_REALTIME"
    DELAYED_15M = "DELAYED_15M"
    END_OF_DAY = "END_OF_DAY"


class NewsPublisherType(StrEnum):
    """Publisher classification."""

    WIRE_SERVICE = "WIRE_SERVICE"
    FINANCIAL_NEWSPAPER = "FINANCIAL_NEWSPAPER"
    BROADCASTER = "BROADCASTER"
    PRESS_RELEASE_DISTRIBUTOR = "PRESS_RELEASE_DISTRIBUTOR"
    OFFICIAL_REGULATOR = "OFFICIAL_REGULATOR"


class NewsEntityMentionType(StrEnum):
    """Role of an entity mentioned in an article."""

    PRIMARY_SUBJECT = "PRIMARY_SUBJECT"
    PEER_MENTION = "PEER_MENTION"
    MACRO_CONTEXT = "MACRO_CONTEXT"
    SOURCE_TAG = "SOURCE_TAG"


class NewsEntityResolutionMethod(StrEnum):
    """Method used to link an article to an entity."""

    VERIFIED_SOURCE_TAG = "VERIFIED_SOURCE_TAG"
    VERIFIED_IDENTIFIER_MATCH = "VERIFIED_IDENTIFIER_MATCH"
    HIGH_CONFIDENCE_DETERMINISTIC = "HIGH_CONFIDENCE_DETERMINISTIC"
    EXCHANGE_AWARE_RESOLVER = "EXCHANGE_AWARE_RESOLVER"
    UNRESOLVED = "UNRESOLVED"


class NewsChangeType(StrEnum):
    """Type of update in an article revision lifecycle."""

    INITIAL_INGESTION = "INITIAL_INGESTION"
    HEADLINE_CORRECTION = "HEADLINE_CORRECTION"
    EXCERPT_UPDATE = "EXCERPT_UPDATE"
    METADATA_UPDATE = "METADATA_UPDATE"
    ENTITY_LINK_ADDED = "ENTITY_LINK_ADDED"
    WITHDRAWAL = "WITHDRAWAL"
    REMOVAL = "REMOVAL"


class NewsDiscoveryMode(StrEnum):
    """Exploration mode for financial news discovery."""

    ALL = "ALL"
    MARKETS = "MARKETS"
    COMPANIES = "COMPANIES"
    SECURITIES = "SECURITIES"
    TOPICS = "TOPICS"
    INDUSTRIES = "INDUSTRIES"
    WATCHLIST = "WATCHLIST"


class NewsTimelineInterval(StrEnum):
    """Aggregation bucket duration for chronological news timelines."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class NewsSortOrder(StrEnum):
    """Sort criteria for news feeds and discovery searches."""

    PUBLISHED_DESC = "PUBLISHED_DESC"
    PUBLISHED_ASC = "PUBLISHED_ASC"
    RELEVANCE_DESC = "RELEVANCE_DESC"


class NewsDatePreset(StrEnum):
    """Standardized relative publication date filters."""

    ALL_TIME = "ALL_TIME"
    TODAY = "TODAY"
    PAST_24H = "PAST_24H"
    PAST_7D = "PAST_7D"
    PAST_30D = "PAST_30D"
    CUSTOM = "CUSTOM"


class NewsIndustrySector(StrEnum):
    """Canonical GICS/ICB economic industry sectors for news tagging."""

    TECHNOLOGY = "TECHNOLOGY"
    COMMUNICATION_SERVICES = "COMMUNICATION_SERVICES"
    CONSUMER_DISCRETIONARY = "CONSUMER_DISCRETIONARY"
    CONSUMER_STAPLES = "CONSUMER_STAPLES"
    ENERGY = "ENERGY"
    FINANCIALS = "FINANCIALS"
    HEALTHCARE = "HEALTHCARE"
    INDUSTRIALS = "INDUSTRIALS"
    MATERIALS = "MATERIALS"
    REAL_ESTATE = "REAL_ESTATE"
    UTILITIES = "UTILITIES"


# ---------------------------------------------------------------------------
# Stage 101: Story Intelligence & Financial Event Enums
# ---------------------------------------------------------------------------

class NewsStoryStatus(StrEnum):
    """Operational lifecycle status of a multi-source news story thread."""

    ACTIVE = "ACTIVE"
    DEVELOPING = "DEVELOPING"
    QUIET = "QUIET"
    ARCHIVED = "ARCHIVED"
    MERGED = "MERGED"
    WITHDRAWN_FROM_DISPLAY = "WITHDRAWN_FROM_DISPLAY"


class NewsStoryMembershipReason(StrEnum):
    """Auditable rationale for associating an article with a story thread."""

    SHARED_EVENT_IDENTITY = "SHARED_EVENT_IDENTITY"
    SHARED_TRANSACTION_FILING = "SHARED_TRANSACTION_FILING"
    TEMPORAL_ENTITY_COVERAGE = "TEMPORAL_ENTITY_COVERAGE"
    REPORTED_DEVELOPMENT = "REPORTED_DEVELOPMENT"


class NewsStoryMembershipStatus(StrEnum):
    """Verification confidence of article story cluster membership."""

    CONFIRMED = "CONFIRMED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


class FinancialEventType(StrEnum):
    """Canonical classification taxonomy of corporate and macroeconomic events."""

    # Corporate Announcements
    EARNINGS_RELEASE = "EARNINGS_RELEASE"
    EARNINGS_GUIDANCE = "EARNINGS_GUIDANCE"
    DIVIDEND_DECLARATION = "DIVIDEND_DECLARATION"
    SHARE_REPURCHASE = "SHARE_REPURCHASE"
    MERGER_ACQUISITION_PROPOSAL = "MERGER_ACQUISITION_PROPOSAL"
    MERGER_ACQUISITION_AGREEMENT = "MERGER_ACQUISITION_AGREEMENT"
    MERGER_ACQUISITION_COMPLETION = "MERGER_ACQUISITION_COMPLETION"
    EQUITY_FINANCING = "EQUITY_FINANCING"
    DEBT_FINANCING = "DEBT_FINANCING"
    MANAGEMENT_APPOINTMENT = "MANAGEMENT_APPOINTMENT"
    MANAGEMENT_DEPARTURE = "MANAGEMENT_DEPARTURE"
    REGULATORY_ACTION = "REGULATORY_ACTION"
    LITIGATION_FILING = "LITIGATION_FILING"
    BANKRUPTCY_FILING = "BANKRUPTCY_FILING"
    RESTRUCTURING = "RESTRUCTURING"
    PRODUCT_LAUNCH = "PRODUCT_LAUNCH"
    FACILITY_EXPANSION = "FACILITY_EXPANSION"

    # Macroeconomic & Policy
    CENTRAL_BANK_POLICY_DECISION = "CENTRAL_BANK_POLICY_DECISION"
    ECONOMIC_RELEASE = "ECONOMIC_RELEASE"
    GOVERNMENT_POLICY = "GOVERNMENT_POLICY"


class NewsEventLifecycleStatus(StrEnum):
    """Factual corporate lifecycle state of an underlying financial event."""

    PROPOSED = "PROPOSED"
    ANNOUNCED = "ANNOUNCED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    WITHDRAWN = "WITHDRAWN"
    UNKNOWN = "UNKNOWN"


class NewsEventAssertionStatus(StrEnum):
    """Evidentiary qualification of source claims regarding a financial event."""

    OFFICIALLY_REPORTED = "OFFICIALLY_REPORTED"
    THIRD_PARTY_REPORTED = "THIRD_PARTY_REPORTED"
    ALLEGED = "ALLEGED"
    RUMORED = "RUMORED"
    DENIED = "DENIED"
    DISPUTED = "DISPUTED"
    CORRECTED = "CORRECTED"
    UNRESOLVED = "UNRESOLVED"


class EventParticipantRole(StrEnum):
    """Specific role of an entity in a corporate or regulatory transaction."""

    PRIMARY_SUBJECT = "PRIMARY_SUBJECT"
    ACQUIRER = "ACQUIRER"
    TARGET = "TARGET"
    SELLER = "SELLER"
    BUYER = "BUYER"
    ISSUER = "ISSUER"
    LENDER = "LENDER"
    INVESTOR = "INVESTOR"
    UNDERWRITER = "UNDERWRITER"
    REGULATOR = "REGULATOR"
    SUBJECT = "SUBJECT"
    RESPONDENT = "RESPONDENT"
    OFFICER = "OFFICER"


class EventAmountType(StrEnum):
    """Category of monetary or quantitative figure reported in event evidence."""

    TRANSACTION_VALUE = "TRANSACTION_VALUE"
    DIVIDEND_PER_SHARE = "DIVIDEND_PER_SHARE"
    BUYBACK_AUTHORIZATION = "BUYBACK_AUTHORIZATION"
    QUARTERLY_REVENUE = "QUARTERLY_REVENUE"
    NET_INCOME = "NET_INCOME"
    FINANCING_PROCEEDS = "FINANCING_PROCEEDS"
    REGULATORY_FINE = "REGULATORY_FINE"
    TARGET_PRICE = "TARGET_PRICE"
    INTEREST_RATE_TARGET = "INTEREST_RATE_TARGET"


class EventAmountApproximation(StrEnum):
    """Degree of approximation in reported financial amounts."""

    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    RANGE_MIN = "RANGE_MIN"
    RANGE_MAX = "RANGE_MAX"


class EventTimePrecision(StrEnum):
    """Temporal resolution of reported event occurrence."""

    EXACT_INSTANT = "EXACT_INSTANT"
    CALENDAR_DAY = "CALENDAR_DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"
    UNKNOWN = "UNKNOWN"


class NewsEvidenceType(StrEnum):
    """Classification of source evidence document supporting a financial event."""

    OFFICIAL_PRESS_RELEASE = "OFFICIAL_PRESS_RELEASE"
    REGULATORY_FILING = "REGULATORY_FILING"
    COMPANY_DISCLOSURE = "COMPANY_DISCLOSURE"
    CENTRAL_BANK_RELEASE = "CENTRAL_BANK_RELEASE"
    PUBLISHER_REPORT = "PUBLISHER_REPORT"
    WIRE_REPORT = "WIRE_REPORT"
    THIRD_PARTY_CLAIM = "THIRD_PARTY_CLAIM"


class NewsSentimentLabel(StrEnum):
    """Canonical target-aware financial news sentiment classification."""

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class NewsFinancialAspect(StrEnum):
    """Financial domain aspect evaluated in news language."""

    EARNINGS_PERFORMANCE = "EARNINGS_PERFORMANCE"
    EARNINGS_GUIDANCE = "EARNINGS_GUIDANCE"
    REVENUE_GROWTH = "REVENUE_GROWTH"
    PROFITABILITY = "PROFITABILITY"
    CASH_FLOW = "CASH_FLOW"
    BALANCE_SHEET = "BALANCE_SHEET"
    DEBT_FINANCING = "DEBT_FINANCING"
    CORPORATE_GOVERNANCE = "CORPORATE_GOVERNANCE"
    REGULATORY_EXPOSURE = "REGULATORY_EXPOSURE"
    PRODUCT_DEVELOPMENT = "PRODUCT_DEVELOPMENT"
    OPERATIONAL_PERFORMANCE = "OPERATIONAL_PERFORMANCE"
    MANAGEMENT = "MANAGEMENT"
    CORPORATE_TRANSACTION = "CORPORATE_TRANSACTION"
    GENERAL = "GENERAL"


class NewsEntityRelevanceClass(StrEnum):
    """Degree of direct journalistic relevance of an article to an entity."""

    PRIMARY_SUBJECT = "PRIMARY_SUBJECT"
    DIRECT_PARTICIPANT = "DIRECT_PARTICIPANT"
    VERIFIED_MENTION = "VERIFIED_MENTION"
    VERIFIED_RELATED_ENTITY = "VERIFIED_RELATED_ENTITY"
    CONTEXTUAL_MARKET_REFERENCE = "CONTEXTUAL_MARKET_REFERENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class NewsEvidenceScope(StrEnum):
    """Scope of licensed text utilized for sentiment classification."""

    HEADLINE = "HEADLINE"
    LICENSED_EXCERPT = "LICENSED_EXCERPT"
    LICENSED_BODY = "LICENSED_BODY"
    SOURCE_STRUCTURED_LABEL = "SOURCE_STRUCTURED_LABEL"


class NewsClassificationMethod(StrEnum):
    """Methodology employed to derive financial news annotations."""

    DETERMINISTIC_RULES = "DETERMINISTIC_RULES"
    FINANCIAL_LANGUAGE_MODEL = "FINANCIAL_LANGUAGE_MODEL"
    HYBRID_VALIDATED = "HYBRID_VALIDATED"
    MANUAL_AUDITED = "MANUAL_AUDITED"


class NewsMarketReactionWindow(StrEnum):
    """Standardized trading observation windows for descriptive market price alignment."""

    INTRADAY_PRE_POST_1H = "INTRADAY_PRE_POST_1H"
    PREV_CLOSE_TO_NEXT_CLOSE = "PREV_CLOSE_TO_NEXT_CLOSE"
    SESSION_OPEN_TO_CLOSE = "SESSION_OPEN_TO_CLOSE"
    MULTI_DAY_T_MINUS_1_TO_PLUS_1 = "MULTI_DAY_T_MINUS_1_TO_PLUS_1"
    MULTI_DAY_T_0_TO_PLUS_3 = "MULTI_DAY_T_0_TO_PLUS_3"


# ---------------------------------------------------------------------------
# Stage 103 News Monitoring, Alerts & Digests Enums
# ---------------------------------------------------------------------------

class NewsMonitoringRuleType(StrEnum):
    """Categorization of monitoring scope targets."""

    COMPANY = "COMPANY"
    INSTRUMENT = "INSTRUMENT"
    WATCHLIST = "WATCHLIST"
    TOPIC = "TOPIC"
    EVENT_TYPE = "EVENT_TYPE"
    STORY = "STORY"
    CUSTOM_FEED = "CUSTOM_FEED"
    ALL_WATCHED = "ALL_WATCHED"


class NewsAlertPriority(StrEnum):
    """User-selected urgency level for news monitoring alerts."""

    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class NewsTriggerPolicy(StrEnum):
    """Triggering event criteria determining when a rule fires."""

    ON_NEW_ARTICLE = "ON_NEW_ARTICLE"
    ON_EVENT_VERIFIED = "ON_EVENT_VERIFIED"
    ON_STATUS_CHANGE = "ON_STATUS_CHANGE"
    ON_STORY_UPDATE = "ON_STORY_UPDATE"
    DAILY_DIGEST_ONLY = "DAILY_DIGEST_ONLY"


class NewsDeliveryChannel(StrEnum):
    """Destination delivery mechanism for alert notifications."""

    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    BROWSER_PUSH = "BROWSER_PUSH"


class NewsAlertMatchStatus(StrEnum):
    """Lifecycle disposition of an evaluated monitoring match."""

    DELIVERED = "DELIVERED"
    COOLDOWN_ACTIVE = "COOLDOWN_ACTIVE"
    SUPPRESSED_SYNDICATION = "SUPPRESSED_SYNDICATION"
    DEFERRED_QUIET_HOURS = "DEFERRED_QUIET_HOURS"
    FAILED = "FAILED"


class NewsDigestCadence(StrEnum):
    """Periodic schedule cadence for aggregated news digests."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"



