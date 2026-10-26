"""Canonical Publisher Entities and Registry (Stage 99)."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.news.enums import NewsPublisherType


class NewsPublisher(BaseModel):
    """
    Canonical Publisher Entity representing a verified financial media outlet,
    wire service, broadcaster, or regulatory organization.
    """

    publisher_id: str = Field(..., description="Unique slug for the publisher (e.g., 'reuters', 'bloomberg').")
    canonical_name: str = Field(..., description="Official publisher name.")
    verified_domain: str = Field(..., description="Authoritative web domain of the publisher.")
    known_aliases: tuple[str, ...] = Field(default_factory=tuple, description="Known aliases and acronyms.")
    publisher_type: NewsPublisherType = Field(default=NewsPublisherType.FINANCIAL_NEWSPAPER)
    country_code: Optional[str] = Field(default=None, description="ISO-3166-1 alpha-2 country of headquarters.")
    official_website: str = Field(..., description="Full canonical homepage URL.")
    attribution_required: bool = Field(default=True, description="Whether explicit publisher attribution is required.")
    status: str = Field(default="VERIFIED", description="Verification status ('VERIFIED', 'ACTIVE', 'RESTRICTED').")
    licensing_tier: str = Field(default="STANDARD", description="Publisher licensing contract tier.")

    model_config = ConfigDict(frozen=True)


# Pre-populated authoritative financial publishers registry
_VERIFIED_PUBLISHERS_CATALOG: Dict[str, NewsPublisher] = {
    "reuters": NewsPublisher(
        publisher_id="reuters",
        canonical_name="Reuters",
        verified_domain="reuters.com",
        known_aliases=("Thomson Reuters", "Reuters News"),
        publisher_type=NewsPublisherType.WIRE_SERVICE,
        country_code="GB",
        official_website="https://www.reuters.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "bloomberg": NewsPublisher(
        publisher_id="bloomberg",
        canonical_name="Bloomberg News",
        verified_domain="bloomberg.com",
        known_aliases=("Bloomberg", "Bloomberg LP", "Bloomberg Terminal"),
        publisher_type=NewsPublisherType.WIRE_SERVICE,
        country_code="US",
        official_website="https://www.bloomberg.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "wsj": NewsPublisher(
        publisher_id="wsj",
        canonical_name="The Wall Street Journal",
        verified_domain="wsj.com",
        known_aliases=("Wall Street Journal", "WSJ", "Dow Jones"),
        publisher_type=NewsPublisherType.FINANCIAL_NEWSPAPER,
        country_code="US",
        official_website="https://www.wsj.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "ft": NewsPublisher(
        publisher_id="ft",
        canonical_name="Financial Times",
        verified_domain="ft.com",
        known_aliases=("FT", "The Financial Times"),
        publisher_type=NewsPublisherType.FINANCIAL_NEWSPAPER,
        country_code="GB",
        official_website="https://www.ft.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "cnbc": NewsPublisher(
        publisher_id="cnbc",
        canonical_name="CNBC",
        verified_domain="cnbc.com",
        known_aliases=("NBC Universal CNBC", "CNBC International"),
        publisher_type=NewsPublisherType.BROADCASTER,
        country_code="US",
        official_website="https://www.cnbc.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "marketwatch": NewsPublisher(
        publisher_id="marketwatch",
        canonical_name="MarketWatch",
        verified_domain="marketwatch.com",
        known_aliases=("Market Watch", "MW"),
        publisher_type=NewsPublisherType.FINANCIAL_NEWSPAPER,
        country_code="US",
        official_website="https://www.marketwatch.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "ap_news": NewsPublisher(
        publisher_id="ap_news",
        canonical_name="Associated Press",
        verified_domain="apnews.com",
        known_aliases=("AP", "AP News"),
        publisher_type=NewsPublisherType.WIRE_SERVICE,
        country_code="US",
        official_website="https://apnews.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "economic_times": NewsPublisher(
        publisher_id="economic_times",
        canonical_name="The Economic Times",
        verified_domain="economictimes.indiatimes.com",
        known_aliases=("ET", "Economic Times India"),
        publisher_type=NewsPublisherType.FINANCIAL_NEWSPAPER,
        country_code="IN",
        official_website="https://economictimes.indiatimes.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "mint": NewsPublisher(
        publisher_id="mint",
        canonical_name="Mint",
        verified_domain="livemint.com",
        known_aliases=("Livemint", "Mint News"),
        publisher_type=NewsPublisherType.FINANCIAL_NEWSPAPER,
        country_code="IN",
        official_website="https://www.livemint.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "nikkei": NewsPublisher(
        publisher_id="nikkei",
        canonical_name="Nikkei Asia",
        verified_domain="asia.nikkei.com",
        known_aliases=("Nikkei", "Nihon Keizai Shimbun"),
        publisher_type=NewsPublisherType.FINANCIAL_NEWSPAPER,
        country_code="JP",
        official_website="https://asia.nikkei.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "sec_gov": NewsPublisher(
        publisher_id="sec_gov",
        canonical_name="U.S. Securities and Exchange Commission",
        verified_domain="sec.gov",
        known_aliases=("SEC", "U.S. SEC"),
        publisher_type=NewsPublisherType.OFFICIAL_REGULATOR,
        country_code="US",
        official_website="https://www.sec.gov",
        attribution_required=True,
        status="VERIFIED",
    ),
    "fed_reserve": NewsPublisher(
        publisher_id="fed_reserve",
        canonical_name="Federal Reserve Board",
        verified_domain="federalreserve.gov",
        known_aliases=("The Fed", "Board of Governors of the Federal Reserve"),
        publisher_type=NewsPublisherType.OFFICIAL_REGULATOR,
        country_code="US",
        official_website="https://www.federalreserve.gov",
        attribution_required=True,
        status="VERIFIED",
    ),
    "rbi_org": NewsPublisher(
        publisher_id="rbi_org",
        canonical_name="Reserve Bank of India",
        verified_domain="rbi.org.in",
        known_aliases=("RBI", "Reserve Bank"),
        publisher_type=NewsPublisherType.OFFICIAL_REGULATOR,
        country_code="IN",
        official_website="https://www.rbi.org.in",
        attribution_required=True,
        status="VERIFIED",
    ),
    "ecb_europa": NewsPublisher(
        publisher_id="ecb_europa",
        canonical_name="European Central Bank",
        verified_domain="ecb.europa.eu",
        known_aliases=("ECB", "Banque Centrale Européenne"),
        publisher_type=NewsPublisherType.OFFICIAL_REGULATOR,
        country_code="EU",
        official_website="https://www.ecb.europa.eu",
        attribution_required=True,
        status="VERIFIED",
    ),
    "prnewswire": NewsPublisher(
        publisher_id="prnewswire",
        canonical_name="PR Newswire",
        verified_domain="prnewswire.com",
        known_aliases=("PRN", "Cision PR Newswire"),
        publisher_type=NewsPublisherType.PRESS_RELEASE_DISTRIBUTOR,
        country_code="US",
        official_website="https://www.prnewswire.com",
        attribution_required=True,
        status="VERIFIED",
    ),
    "businesswire": NewsPublisher(
        publisher_id="businesswire",
        canonical_name="Business Wire",
        verified_domain="businesswire.com",
        known_aliases=("BW", "Berkshire Hathaway Business Wire"),
        publisher_type=NewsPublisherType.PRESS_RELEASE_DISTRIBUTOR,
        country_code="US",
        official_website="https://www.businesswire.com",
        attribution_required=True,
        status="VERIFIED",
    ),
}


def get_verified_publisher(publisher_id: str) -> Optional[NewsPublisher]:
    """Retrieve a verified publisher by slug ID."""
    return _VERIFIED_PUBLISHERS_CATALOG.get(publisher_id.lower())


def list_verified_publishers() -> List[NewsPublisher]:
    """List all verified publishers in the canonical registry."""
    return list(_VERIFIED_PUBLISHERS_CATALOG.values())


def resolve_publisher_by_domain_or_name(text: str) -> Optional[NewsPublisher]:
    """Attempt to resolve publisher from domain or name/alias string."""
    norm = text.strip().lower()
    for pub in _VERIFIED_PUBLISHERS_CATALOG.values():
        if norm == pub.publisher_id:
            return pub
        if norm == pub.verified_domain or norm.endswith("." + pub.verified_domain):
            return pub
        if norm == pub.canonical_name.lower():
            return pub
        for alias in pub.known_aliases:
            if norm == alias.lower():
                return pub
    return None
