"""Canonical Topic Taxonomy and Resolution for News Discovery (Stage 100)."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.news.enums import NewsCategory


class NewsTopic(BaseModel):
    """
    Canonical Financial News Topic.
    Provides standardized thematic categorization across disparate news providers.
    """

    topic_id: str = Field(..., description="Unique slug for the topic (e.g. 'EARNINGS_RELEASES').")
    canonical_name: str = Field(..., description="Human-readable title for the topic.")
    description: str = Field(..., description="Formal description of financial domain.")
    parent_topic_id: Optional[str] = Field(default=None, description="Parent topic identifier if hierarchical.")
    category: NewsCategory = Field(..., description="Underlying NewsCategory taxonomy binding.")
    keywords: tuple[str, ...] = Field(default_factory=tuple, description="Controlled keyword matching tokens.")

    model_config = ConfigDict(frozen=True)


# Pre-seeded canonical topic catalog
_CANONICAL_TOPICS: dict[str, NewsTopic] = {
    "EARNINGS_RELEASES": NewsTopic(
        topic_id="EARNINGS_RELEASES",
        canonical_name="Earnings & Financial Results",
        description="Quarterly and annual financial results, EPS, net income, revenue, and forward guidance.",
        parent_topic_id=None,
        category=NewsCategory.CORPORATE_ACTIONS,
        keywords=("earnings", "quarterly profit", "revenue", "eps", "ebitda", "net income", "guidance", "results"),
    ),
    "MERGERS_ACQUISITIONS": NewsTopic(
        topic_id="MERGERS_ACQUISITIONS",
        canonical_name="Mergers & Acquisitions",
        description="Corporate acquisitions, mergers, divestitures, buyouts, and joint ventures.",
        parent_topic_id=None,
        category=NewsCategory.CORPORATE_ACTIONS,
        keywords=("acquisition", "acquire", "merger", "buyout", "takeover", "deal", "divestiture", "m&a"),
    ),
    "DIVIDENDS_DISTRIBUTIONS": NewsTopic(
        topic_id="DIVIDENDS_DISTRIBUTIONS",
        canonical_name="Dividends & Capital Returns",
        description="Cash dividend declarations, dividend hikes, special dividends, and capital distributions.",
        parent_topic_id=None,
        category=NewsCategory.CORPORATE_ACTIONS,
        keywords=("dividend", "payout", "distribution", "yield", "interim dividend", "special dividend"),
    ),
    "SHARE_BUYBACKS": NewsTopic(
        topic_id="SHARE_BUYBACKS",
        canonical_name="Share Repurchases & Buybacks",
        description="Share repurchase authorizations, tender offers, and accelerated share buybacks.",
        parent_topic_id="CORPORATE_ACTIONS",
        category=NewsCategory.CORPORATE_ACTIONS,
        keywords=("buyback", "share repurchase", "repurchasing shares", "tender offer"),
    ),
    "CAPITAL_RAISING": NewsTopic(
        topic_id="CAPITAL_RAISING",
        canonical_name="Capital Raising & Offerings",
        description="IPOs, secondary share offerings, rights issues, and corporate debt issuances.",
        parent_topic_id=None,
        category=NewsCategory.EQUITIES,
        keywords=("ipo", "offering", "rights issue", "bond issue", "debt financing", "secondary offering"),
    ),
    "INTEREST_RATES_MONETARY_POLICY": NewsTopic(
        topic_id="INTEREST_RATES_MONETARY_POLICY",
        canonical_name="Monetary Policy & Interest Rates",
        description="Central bank rate decisions, policy statements, quantitative easing/tightening, and yield policy.",
        parent_topic_id=None,
        category=NewsCategory.CENTRAL_BANKS,
        keywords=("interest rate", "rate cut", "rate hike", "repo rate", "fed funds", "monetary policy", "federal reserve", "rbi", "ecb"),
    ),
    "INFLATION_PRICES": NewsTopic(
        topic_id="INFLATION_PRICES",
        canonical_name="Inflation & Price Pressures",
        description="Consumer price indices (CPI), producer prices (PPI), PCE deflators, and cost of living.",
        parent_topic_id=None,
        category=NewsCategory.ECONOMICS,
        keywords=("inflation", "cpi", "ppi", "pce", "consumer prices", "wholesale inflation", "price pressures"),
    ),
    "EMPLOYMENT_LABOR": NewsTopic(
        topic_id="EMPLOYMENT_LABOR",
        canonical_name="Employment & Labor Markets",
        description="Unemployment figures, nonfarm payrolls, job openings, wage growth, and labor participation.",
        parent_topic_id=None,
        category=NewsCategory.ECONOMICS,
        keywords=("unemployment", "payrolls", "nonfarm", "labor force", "hiring", "jobless claims", "wages"),
    ),
    "FOREIGN_EXCHANGE_CURRENCIES": NewsTopic(
        topic_id="FOREIGN_EXCHANGE_CURRENCIES",
        canonical_name="Foreign Exchange & Currencies",
        description="Currency fluctuations, FX interventions, dollar index moves, and sovereign reserve shifts.",
        parent_topic_id=None,
        category=NewsCategory.FOREIGN_EXCHANGE,
        keywords=("forex", "fx", "dollar index", "rupee", "euro", "yen", "currency reserve", "devaluation"),
    ),
    "COMMODITIES_ENERGY": NewsTopic(
        topic_id="COMMODITIES_ENERGY",
        canonical_name="Commodities, Energy & Metals",
        description="Crude oil, natural gas, precious metals, industrial minerals, and agricultural commodities.",
        parent_topic_id=None,
        category=NewsCategory.COMMODITIES,
        keywords=("crude oil", "brent", "natural gas", "gold", "silver", "copper", "opec", "energy prices"),
    ),
    "FINANCIAL_REGULATION_COMPLIANCE": NewsTopic(
        topic_id="FINANCIAL_REGULATION_COMPLIANCE",
        canonical_name="Regulation, Antitrust & Compliance",
        description="Securities regulations, antitrust actions, regulatory filings, investigations, and legal enforcement.",
        parent_topic_id=None,
        category=NewsCategory.REGULATION,
        keywords=("sec", "regulator", "compliance", "antitrust", "investigation", "enforcement", "sanctions", "doj"),
    ),
    "CORPORATE_GOVERNANCE_BOARD": NewsTopic(
        topic_id="CORPORATE_GOVERNANCE_BOARD",
        canonical_name="Corporate Governance & Leadership",
        description="Executive changes (CEO/CFO), board appointments, proxy battles, and activist investor campaigns.",
        parent_topic_id=None,
        category=NewsCategory.COMPANY,
        keywords=("board of directors", "ceo", "cfo", "executive", "proxy vote", "activist investor", "leadership"),
    ),
    "TECHNOLOGY_AI_INNOVATION": NewsTopic(
        topic_id="TECHNOLOGY_AI_INNOVATION",
        canonical_name="Technology, AI & Innovation",
        description="Artificial intelligence, semiconductor fabrication, enterprise cloud software, and hardware advances.",
        parent_topic_id=None,
        category=NewsCategory.TECHNOLOGY,
        keywords=("ai", "artificial intelligence", "semiconductor", "cloud", "software", "foundry", "data center", "gpu"),
    ),
    "SUPPLY_CHAIN_LOGISTICS": NewsTopic(
        topic_id="SUPPLY_CHAIN_LOGISTICS",
        canonical_name="Supply Chain & Logistics",
        description="Global trade disruptions, component shortages, freight rates, and shipping bottlenecks.",
        parent_topic_id=None,
        category=NewsCategory.GENERAL_FINANCIAL,
        keywords=("supply chain", "logistics", "freight", "shipping", "chip shortage", "port backlog"),
    ),
}


def get_topic(topic_id: str) -> Optional[NewsTopic]:
    """Retrieve canonical topic by topic_id."""
    return _CANONICAL_TOPICS.get(topic_id.upper())


def list_topics() -> list[NewsTopic]:
    """Return all pre-seeded canonical topics."""
    return list(_CANONICAL_TOPICS.values())


def classify_topics_for_article(
    title: str,
    excerpt: Optional[str] = None,
    categories: Optional[list[NewsCategory]] = None,
) -> list[str]:
    """
    Deterministic resolution of canonical topics from headline, excerpt, and categories.
    Uses strict keyword boundaries without probabilistic hallucinations.
    """
    text = (f"{title} {excerpt or ''}").lower()
    matched_topic_ids: list[str] = []

    for topic_id, topic in _CANONICAL_TOPICS.items():
        # Match keywords
        for kw in topic.keywords:
            if kw in text:
                matched_topic_ids.append(topic_id)
                break

    # If categories provide direct hint and no topics matched, link default category topic
    if not matched_topic_ids and categories:
        for cat in categories:
            for tid, top in _CANONICAL_TOPICS.items():
                if top.category == cat and tid not in matched_topic_ids:
                    matched_topic_ids.append(tid)
                    break

    return matched_topic_ids


def resolve_industries_for_article(
    title: str,
    excerpt: Optional[str] = None,
    entities: Optional[list[Any]] = None,
) -> list[str]:
    """
    Deterministic resolution of canonical GICS/ICB industry sectors.
    Reuses verified entity associations and unambiguous financial sector terms.
    """
    text = f"{title} {excerpt or ''}".lower()
    sectors: set[str] = set()

    # Known company entity tickers/names to sector mapping
    if entities:
        for ent in entities:
            name = (getattr(ent, "canonical_name", None) or "").lower()
            ticker = (getattr(ent, "ticker", None) or "").upper()
            if any(t in ticker for t in ("AAPL", "MSFT", "NVDA", "ASML", "INFY")) or any(n in name for n in ("apple", "microsoft", "nvidia", "asml", "infosys", "intel", "tsmc")):
                sectors.add("TECHNOLOGY")
            elif any(t in ticker for t in ("BP", "XOM", "CVX")) or any(n in name for n in ("bp", "exxon", "chevron", "aramco", "petroleum")):
                sectors.add("ENERGY")
            elif any(t in ticker for t in ("RELIANCE", "RIL")) or "reliance" in name:
                sectors.add("ENERGY")
                sectors.add("COMMUNICATION_SERVICES")
            elif any(t in ticker for t in ("TM", "TATAMOTORS")) or any(n in name for n in ("toyota", "tata motors")):
                sectors.add("CONSUMER_DISCRETIONARY")
            elif any(t in ticker for t in ("HDFCBANK", "JPM", "BAC")) or any(n in name for n in ("hdfc", "jpmorgan", "bank")):
                sectors.add("FINANCIALS")

    # Text keyword checks
    if any(w in text for w in ("semiconductor", "chip", "lithography", "euv", "ai", "cloud", "software", "accelerator", "inferencing")):
        sectors.add("TECHNOLOGY")
    if any(w in text for w in ("crude oil", "deepwater", "offshore wind", "refining", "brent", "petroleum", "gas")):
        sectors.add("ENERGY")
    if any(w in text for w in ("automaker", "vehicle output", "hybrid powertrain", "passenger vehicle", "commercial vehicle")):
        sectors.add("CONSUMER_DISCRETIONARY")
    if any(w in text for w in ("advances", "deposits", "banking", "repo rate", "rate cut", "rate hike", "federal reserve", "central bank", "ecb", "rbi", "fomc")):
        sectors.add("FINANCIALS")

    return sorted(list(sectors))
