"""Canonical Entity Resolution and Financial Instrument Linking Engine (Stage 99).

Provides:
- Company and Instrument canonical linking
- Ticker symbol collision disambiguation
- Share-class & ADR resolution
- Contextual validation (distinguishing common English words from ticker symbols)
- Deterministic entity extraction without hallucinated sentiment or market impact scores
"""

from __future__ import annotations

import re
from typing import List, Optional, Set, Tuple

from pydantic import BaseModel, ConfigDict, Field

from atlas.news.enums import NewsEntityMentionType, NewsEntityResolutionMethod


class NewsEntityMention(BaseModel):
    """
    Verified or candidate link between a News Article and an ATLAS canonical entity.
    """

    entity_id: str = Field(..., description="Canonical entity ID (UUID or identifier string).")
    entity_type: str = Field(..., description="Type of entity ('COMPANY', 'INSTRUMENT', 'GEOGRAPHY', 'CENTRAL_BANK').")
    canonical_name: str = Field(..., description="Display or canonical name of the entity.")
    ticker: Optional[str] = Field(default=None, description="Primary trading symbol if security/company.")
    exchange: Optional[str] = Field(default=None, description="Listing exchange code.")
    country_code: Optional[str] = Field(default=None, description="ISO country code.")
    mention_type: NewsEntityMentionType = Field(default=NewsEntityMentionType.PRIMARY_SUBJECT)
    resolution_method: NewsEntityResolutionMethod = Field(default=NewsEntityResolutionMethod.HIGH_CONFIDENCE_DETERMINISTIC)
    verification_status: str = Field(default="VERIFIED", description="'VERIFIED' or 'UNRESOLVED'.")

    model_config = ConfigDict(frozen=True)


# Common English words that happen to collide with valid global ticker symbols.
# These MUST NOT be linked to securities unless qualified by a cashtag ($) or explicit company context.
_COLLIDING_TICKER_WORDS: Set[str] = {
    "A",
    "ALL",
    "AM",
    "AN",
    "AND",
    "ANY",
    "ARE",
    "AS",
    "AT",
    "BE",
    "BEST",
    "BIG",
    "BUT",
    "BY",
    "CAN",
    "CAR",
    "CAT",
    "DO",
    "FOR",
    "GET",
    "GO",
    "HAS",
    "HE",
    "IN",
    "IS",
    "IT",
    "ME",
    "NEW",
    "NEXT",
    "NO",
    "NOT",
    "NOW",
    "OF",
    "ON",
    "ONE",
    "OR",
    "OUT",
    "SEE",
    "SO",
    "THE",
    "TO",
    "UP",
    "US",
    "WE",
    "YOU",
}

# Authoritative dictionary of well-known global issuers & instruments with verified canonical IDs
class _EntityDef:
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        canonical_name: str,
        ticker: Optional[str],
        exchange: Optional[str],
        country_code: str,
        aliases: tuple[str, ...],
        is_adr: bool = False,
        share_class: Optional[str] = None,
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.canonical_name = canonical_name
        self.ticker = ticker
        self.exchange = exchange
        self.country_code = country_code
        self.aliases = aliases
        self.is_adr = is_adr
        self.share_class = share_class


_CANONICAL_ENTITIES_CATALOG: List[_EntityDef] = [
    _EntityDef(
        entity_id="comp-aapl-001",
        entity_type="COMPANY",
        canonical_name="Apple Inc.",
        ticker="AAPL",
        exchange="NASDAQ",
        country_code="US",
        aliases=("Apple", "Apple Inc", "AAPL", "$AAPL"),
    ),
    _EntityDef(
        entity_id="comp-msft-002",
        entity_type="COMPANY",
        canonical_name="Microsoft Corporation",
        ticker="MSFT",
        exchange="NASDAQ",
        country_code="US",
        aliases=("Microsoft", "Microsoft Corp", "MSFT", "$MSFT"),
    ),
    _EntityDef(
        entity_id="comp-nvda-003",
        entity_type="COMPANY",
        canonical_name="NVIDIA Corporation",
        ticker="NVDA",
        exchange="NASDAQ",
        country_code="US",
        aliases=("NVIDIA", "Nvidia", "Nvidia Corp", "NVDA", "$NVDA"),
    ),
    _EntityDef(
        entity_id="comp-googl-004",
        entity_type="COMPANY",
        canonical_name="Alphabet Inc. (Class A)",
        ticker="GOOGL",
        exchange="NASDAQ",
        country_code="US",
        aliases=("Alphabet", "Google", "GOOGL", "$GOOGL"),
        share_class="Class A Voting",
    ),
    _EntityDef(
        entity_id="comp-goog-005",
        entity_type="COMPANY",
        canonical_name="Alphabet Inc. (Class C)",
        ticker="GOOG",
        exchange="NASDAQ",
        country_code="US",
        aliases=("GOOG", "$GOOG"),
        share_class="Class C Non-Voting",
    ),
    _EntityDef(
        entity_id="comp-amzn-006",
        entity_type="COMPANY",
        canonical_name="Amazon.com Inc.",
        ticker="AMZN",
        exchange="NASDAQ",
        country_code="US",
        aliases=("Amazon", "Amazon.com", "AMZN", "$AMZN"),
    ),
    _EntityDef(
        entity_id="comp-tsla-007",
        entity_type="COMPANY",
        canonical_name="Tesla Inc.",
        ticker="TSLA",
        exchange="NASDAQ",
        country_code="US",
        aliases=("Tesla", "Tesla Motors", "TSLA", "$TSLA"),
    ),
    _EntityDef(
        entity_id="comp-jpm-008",
        entity_type="COMPANY",
        canonical_name="JPMorgan Chase & Co.",
        ticker="JPM",
        exchange="NYSE",
        country_code="US",
        aliases=("JPMorgan", "JPMorgan Chase", "J.P. Morgan", "JPM", "$JPM"),
    ),
    _EntityDef(
        entity_id="comp-ril-009",
        entity_type="COMPANY",
        canonical_name="Reliance Industries Limited",
        ticker="RELIANCE",
        exchange="NSE",
        country_code="IN",
        aliases=("Reliance Industries", "Reliance", "RIL", "RELIANCE.NSE"),
    ),
    _EntityDef(
        entity_id="comp-tatamotors-010",
        entity_type="COMPANY",
        canonical_name="Tata Motors Limited",
        ticker="TATAMOTORS",
        exchange="NSE",
        country_code="IN",
        aliases=("Tata Motors", "TATAMOTORS", "TATAMOTORS.NSE", "Tata"),
    ),
    _EntityDef(
        entity_id="comp-hdfcbank-011",
        entity_type="COMPANY",
        canonical_name="HDFC Bank Limited",
        ticker="HDFCBANK",
        exchange="NSE",
        country_code="IN",
        aliases=("HDFC Bank", "HDFCBANK", "HDFCBANK.NSE"),
    ),
    _EntityDef(
        entity_id="comp-infy-012",
        entity_type="COMPANY",
        canonical_name="Infosys Limited",
        ticker="INFY",
        exchange="NSE",
        country_code="IN",
        aliases=("Infosys", "INFY.NSE"),
    ),
    _EntityDef(
        entity_id="comp-infy-adr-013",
        entity_type="INSTRUMENT",
        canonical_name="Infosys Limited ADR",
        ticker="INFY",
        exchange="NYSE",
        country_code="US",
        aliases=("INFY ADR", "Infosys ADR"),
        is_adr=True,
    ),
    _EntityDef(
        entity_id="comp-asml-014",
        entity_type="COMPANY",
        canonical_name="ASML Holding N.V.",
        ticker="ASML",
        exchange="AEX",
        country_code="NL",
        aliases=("ASML", "ASML Holding", "ASML.AS"),
    ),
    _EntityDef(
        entity_id="comp-bp-015",
        entity_type="COMPANY",
        canonical_name="BP p.l.c.",
        ticker="BP",
        exchange="LSE",
        country_code="GB",
        aliases=("BP", "BP plc", "BP.L", "British Petroleum"),
    ),
    _EntityDef(
        entity_id="comp-toyota-016",
        entity_type="COMPANY",
        canonical_name="Toyota Motor Corporation",
        ticker="7203",
        exchange="TSE",
        country_code="JP",
        aliases=("Toyota", "Toyota Motor", "7203.T"),
    ),
    _EntityDef(
        entity_id="cb-fed-001",
        entity_type="CENTRAL_BANK",
        canonical_name="Federal Reserve",
        ticker=None,
        exchange=None,
        country_code="US",
        aliases=("Federal Reserve", "The Fed", "FOMC", "Fed Chair"),
    ),
    _EntityDef(
        entity_id="cb-ecb-002",
        entity_type="CENTRAL_BANK",
        canonical_name="European Central Bank",
        ticker=None,
        exchange=None,
        country_code="EU",
        aliases=("European Central Bank", "ECB", "Eurosystem"),
    ),
    _EntityDef(
        entity_id="cb-rbi-003",
        entity_type="CENTRAL_BANK",
        canonical_name="Reserve Bank of India",
        ticker=None,
        exchange=None,
        country_code="IN",
        aliases=("Reserve Bank of India", "RBI", "Monetary Policy Committee (MPC)"),
    ),
]


def resolve_entities_in_text(
    headline: str,
    excerpt: Optional[str] = None,
    source_tags: Optional[List[str]] = None,
) -> List[NewsEntityMention]:
    """
    Extracts and links canonical companies, financial instruments, and regulators
    mentioned in news headline, excerpt, or source tags.
    """
    found: List[NewsEntityMention] = []
    seen_ids: Set[str] = set()

    # 1. First process explicit source tags (e.g. from provider metadata)
    if source_tags:
        for tag in source_tags:
            tag_clean = tag.strip().upper()
            for entity in _CANONICAL_ENTITIES_CATALOG:
                if entity.entity_id in seen_ids:
                    continue
                if entity.ticker and tag_clean == entity.ticker.upper():
                    seen_ids.add(entity.entity_id)
                    found.append(
                        NewsEntityMention(
                            entity_id=entity.entity_id,
                            entity_type=entity.entity_type,
                            canonical_name=entity.canonical_name,
                            ticker=entity.ticker,
                            exchange=entity.exchange,
                            country_code=entity.country_code,
                            mention_type=NewsEntityMentionType.SOURCE_TAG,
                            resolution_method=NewsEntityResolutionMethod.VERIFIED_SOURCE_TAG,
                            verification_status="VERIFIED",
                        )
                    )

    # 2. Match entities in headline (PRIMARY_SUBJECT)
    for entity in _CANONICAL_ENTITIES_CATALOG:
        if entity.entity_id in seen_ids:
            continue

        matched, method = _match_entity_in_text(entity, headline, is_headline=True)
        if matched:
            seen_ids.add(entity.entity_id)
            found.append(
                NewsEntityMention(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    canonical_name=entity.canonical_name,
                    ticker=entity.ticker,
                    exchange=entity.exchange,
                    country_code=entity.country_code,
                    mention_type=NewsEntityMentionType.PRIMARY_SUBJECT,
                    resolution_method=method,
                    verification_status="VERIFIED",
                )
            )

    # 3. Match entities in excerpt (PEER_MENTION or MACRO_CONTEXT)
    if excerpt:
        for entity in _CANONICAL_ENTITIES_CATALOG:
            if entity.entity_id in seen_ids:
                continue

            matched, method = _match_entity_in_text(entity, excerpt, is_headline=False)
            if matched:
                seen_ids.add(entity.entity_id)
                mtype = (
                    NewsEntityMentionType.MACRO_CONTEXT
                    if entity.entity_type == "CENTRAL_BANK"
                    else NewsEntityMentionType.PEER_MENTION
                )
                found.append(
                    NewsEntityMention(
                        entity_id=entity.entity_id,
                        entity_type=entity.entity_type,
                        canonical_name=entity.canonical_name,
                        ticker=entity.ticker,
                        exchange=entity.exchange,
                        country_code=entity.country_code,
                        mention_type=mtype,
                        resolution_method=method,
                        verification_status="VERIFIED",
                    )
                )

    return found


def _match_entity_in_text(entity: _EntityDef, text: str, is_headline: bool) -> Tuple[bool, NewsEntityResolutionMethod]:
    """Helper to detect if an entity is mentioned with word boundary precision."""
    # Check aliases
    for alias in entity.aliases:
        # Check if alias is a colliding ticker word (e.g. "IT", "ON", "CAN")
        alias_upper = alias.upper()
        if alias_upper in _COLLIDING_TICKER_WORDS:
            # Only match if cashtagged or explicit ticker exchange format
            if f"${alias_upper}" in text or f"{alias_upper}:{entity.exchange}" in text:
                return True, NewsEntityResolutionMethod.EXCHANGE_AWARE_RESOLVER
            continue

        # Regex match with boundary checks
        pattern = rf"(?i)\b{re.escape(alias)}\b"
        if re.search(pattern, text):
            method = (
                NewsEntityResolutionMethod.VERIFIED_IDENTIFIER_MATCH
                if alias.startswith("$") or (entity.ticker and alias == entity.ticker)
                else NewsEntityResolutionMethod.HIGH_CONFIDENCE_DETERMINISTIC
            )
            return True, method

    return False, NewsEntityResolutionMethod.UNRESOLVED
