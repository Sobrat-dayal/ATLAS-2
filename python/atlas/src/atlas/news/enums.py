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
