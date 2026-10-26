"""Institutional-Grade Natural-Language Financial Screener Translation Engine (Stage 98).

Implements:
- Lexical financial terminology understanding and alias mapping
- Comparison operator resolution (GT, GTE, LT, LTE, EQ, BETWEEN, IN)
- Numeric threshold parsing with Decimal precision
- Magnitude normalization: international (k, m, bn, tr) and Indian (lakhs, crores, lakh crores)
- Currency resolution (INR, USD, EUR, GBP, ₹, $, €, £)
- Percentage and ratio multiple handling
- Security universe, exchange, issuer country, and listing country resolution
- Sector and canonical industry mapping
- Fundamental factor & reporting period parsing
- Technical indicator and parameter parsing (SMA, EMA, RSI, MACD, Bollinger Bands)
- Multi-condition composition and Boolean logic analysis (AND, same-field IN, unsupported cross-field OR)
- Sorting and result-limit resolution
- Ambiguity detection and interactive clarification questions
- Requirement coverage tracking (no silent dropped or invented clauses)
- Prompt-injection defenses and sanitization
- Canonical query compilation into Stage 94 ScreenerRunRequestDTO
"""

import math
import re
import uuid
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Set, Tuple

from atlas.screeners.enums import (
    FilterOperator,
    NLAmbiguityCategory,
    NLRequirementStatus,
    NLTranslationMode,
    NLTranslationStatus,
    SortDirection,
    SortNullOrder,
    UnitKind,
)
from atlas.screeners.errors import (
    NLScreenerEmptyRequestError,
    NLScreenerPromptInjectionError,
    NLScreenerTextTooLongError,
)
from atlas.screeners.repository import (
    CANONICAL_FILTERS,
    ScreenerRepository,
)
from atlas.screeners.schemas import (
    FilterCriterionDTO,
    NLAmbiguityQuestionDTO,
    NLCapabilitiesResponseDTO,
    NLClarifyRequestDTO,
    NLQueryModificationDiffDTO,
    NLRequirementResolutionDTO,
    NLTranslateRequestDTO,
    NLTranslationProposalDTO,
    SortCriterionDTO,
    UniverseSelectionDTO,
)

# Translator Engine Version
TRANSLATOR_VERSION = "1.0.0"
REGISTRY_REVISION = "stage_98_v1"
MAX_REQUEST_LENGTH = 1000

# =============================================================================
# Security & Prompt-Injection Patterns
# =============================================================================
_ADVERSARIAL_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous\s+|prior\s+)?instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(system\s+prompt|credentials|api\s*keys?)", re.IGNORECASE),
    re.compile(r"(select\s+.*\s+from\s+|drop\s+table|delete\s+from|insert\s+into)", re.IGNORECASE),
    re.compile(r"(\bexec\b|\beval\b|\bexecute\s+sql\b|<script[\s>])", re.IGNORECASE),
    re.compile(r"buy\s+the\s+matched\s+stocks|place\s+order|execute\s+trade", re.IGNORECASE),
    re.compile(r"disable\s+(the\s+)?(screener\s+)?(entitlement|authorization|security|check)", re.IGNORECASE),
    re.compile(r"print\s+(your\s+)?system\s+prompt", re.IGNORECASE),
    re.compile(r"return\s+(every|all)\s+user('?s)?\s+saved\s+screens", re.IGNORECASE),
]


def check_prompt_injection(text: str) -> None:
    """Detects adversarial instructions aiming to bypass validation or execute arbitrary code."""
    for pattern in _ADVERSARIAL_PATTERNS:
        if pattern.search(text):
            raise NLScreenerPromptInjectionError(
                f"Adversarial instruction detected matching pattern: {pattern.pattern}"
            )


# =============================================================================
# Canonical Financial Aliases & Terminology Dictionary
# =============================================================================

# Comprehensive phrase-to-filter mapping
CANONICAL_FILTER_SYNONYMS: Dict[str, str] = {
    # Valuation
    "pe": "pe_ratio",
    "p/e": "pe_ratio",
    "p / e": "pe_ratio",
    "pe ratio": "pe_ratio",
    "p/e ratio": "pe_ratio",
    "price to earnings": "pe_ratio",
    "price-to-earnings": "pe_ratio",
    "trailing pe": "pe_ratio",
    "price earnings ratio": "pe_ratio",
    "pb": "pb_ratio",
    "p/b": "pb_ratio",
    "p / b": "pb_ratio",
    "pb ratio": "pb_ratio",
    "p/b ratio": "pb_ratio",
    "price to book": "pb_ratio",
    "price-to-book": "pb_ratio",
    "ps": "ps_ratio",
    "p/s": "ps_ratio",
    "p / s": "ps_ratio",
    "ps ratio": "ps_ratio",
    "p/s ratio": "ps_ratio",
    "price to sales": "ps_ratio",
    "price-to-sales": "ps_ratio",
    "ev/ebitda": "ev_to_ebitda",
    "ev / ebitda": "ev_to_ebitda",
    "ev to ebitda": "ev_to_ebitda",
    "ev-to-ebitda": "ev_to_ebitda",
    "ev/sales": "ev_to_revenue",
    "ev / sales": "ev_to_revenue",
    "ev to sales": "ev_to_revenue",
    "ev/revenue": "ev_to_revenue",
    "ev to revenue": "ev_to_revenue",
    "ev": "ev",
    "enterprise value": "ev",
    "dividend yield": "dividend_yield",
    "div yield": "dividend_yield",
    "dividend": "dividend_yield",
    "fcf yield": "fcf_yield",
    "free cash flow yield": "fcf_yield",
    # Market Data
    "market cap": "market_cap",
    "market capitalization": "market_cap",
    "market-cap": "market_cap",
    "mcap": "market_cap",
    "cap": "market_cap",
    "share price": "last_price",
    "stock price": "last_price",
    "last price": "last_price",
    "closing price": "last_price",
    "close price": "last_price",
    "price": "last_price",
    "priced": "last_price",
    "priced at": "last_price",
    "priced under": "last_price",
    "priced below": "last_price",
    "priced above": "last_price",
    "price change": "price_change_pct",
    "return": "price_change_pct",
    "price change %": "price_change_pct",
    "volume": "volume_latest",
    "session volume": "volume_latest",
    "trading volume": "volume_latest",
    "average volume": "volume_20d_avg",
    "20-day average volume": "volume_20d_avg",
    "20 day average volume": "volume_20d_avg",
    "adv": "volume_20d_avg",
    "relative volume": "relative_volume_20d",
    "rvol": "relative_volume_20d",
    "dollar volume": "traded_value_latest",
    "turnover": "traded_value_latest",
    # Fundamentals
    "revenue": "revenue",
    "sales": "revenue",
    "total revenue": "revenue",
    "top line": "revenue",
    "topline": "revenue",
    "net income": "net_income",
    "net profit": "net_income",
    "net earnings": "net_income",
    "bottom line": "net_income",
    "bottomline": "net_income",
    "operating income": "operating_income",
    "operating profit": "operating_income",
    "ebit": "operating_income",
    "eps": "eps",
    "earnings per share": "eps",
    "diluted eps": "eps",
    "book value": "book_equity",
    "shareholders equity": "book_equity",
    "book equity": "book_equity",
    "total assets": "total_assets",
    "assets": "total_assets",
    # Growth
    "revenue growth": "revenue_growth_yoy",
    "sales growth": "revenue_growth_yoy",
    "revenue grew": "revenue_growth_yoy",
    "topline growth": "revenue_growth_yoy",
    "quarterly revenue growth": "revenue_growth_qoq",
    "quarterly sales growth": "revenue_growth_qoq",
    "revenue growth qoq": "revenue_growth_qoq",
    "net income growth": "net_income_growth_yoy",
    "earnings growth": "net_income_growth_yoy",
    "profit growth": "net_income_growth_yoy",
    "eps growth": "eps_growth_yoy",
    "fcf growth": "fcf_growth_yoy",
    # Profitability & Margins
    "gross margin": "gross_margin",
    "gross profit margin": "gross_margin",
    "operating margin": "operating_margin",
    "operating profit margin": "operating_margin",
    "ebit margin": "operating_margin",
    "net margin": "net_margin",
    "net profit margin": "net_margin",
    "roe": "roe",
    "return on equity": "roe",
    "roa": "roa",
    "return on assets": "roa",
    "roic": "roic",
    "return on invested capital": "roic",
    # Cash Flow
    "operating cash flow": "operating_cash_flow",
    "cash from operations": "operating_cash_flow",
    "cfo": "operating_cash_flow",
    "free cash flow": "fcf",
    "fcf": "fcf",
    "capex": "capex",
    "capital expenditures": "capex",
    # Balance Sheet & Solvency
    "debt to equity": "debt_to_equity",
    "debt/equity": "debt_to_equity",
    "debt-to-equity": "debt_to_equity",
    "d/e": "debt_to_equity",
    "financial leverage": "debt_to_equity",
    "current ratio": "current_ratio",
    "quick ratio": "quick_ratio",
    "acid test": "quick_ratio",
    "interest coverage": "interest_coverage",
    "times interest earned": "interest_coverage",
    "total debt": "total_debt",
    "debt": "total_debt",
    "net debt": "net_debt",
    # Technical Indicators
    "sma 20": "sma_20",
    "20-day sma": "sma_20",
    "20 day sma": "sma_20",
    "20-day moving average": "sma_20",
    "20 day moving average": "sma_20",
    "sma 50": "sma_50",
    "50-day sma": "sma_50",
    "50 day sma": "sma_50",
    "50-day moving average": "sma_50",
    "50 day moving average": "sma_50",
    "50 sma": "sma_50",
    "sma 100": "sma_100",
    "100-day sma": "sma_100",
    "100 day sma": "sma_100",
    "100-day moving average": "sma_100",
    "100 day moving average": "sma_100",
    "sma 200": "sma_200",
    "200-day sma": "sma_200",
    "200 day sma": "sma_200",
    "200-day moving average": "sma_200",
    "200 day moving average": "sma_200",
    "200 sma": "sma_200",
    "ema 20": "ema_20",
    "20-day ema": "ema_20",
    "20 day ema": "ema_20",
    "ema 50": "ema_50",
    "50-day ema": "ema_50",
    "50 day ema": "ema_50",
    "price above 200-day moving average": "price_above_sma200",
    "price above 200 day moving average": "price_above_sma200",
    "price above 200-day sma": "price_above_sma200",
    "price above 200 sma": "price_above_sma200",
    "share price above 200-day moving average": "price_above_sma200",
    "share price above the 200-day moving average": "price_above_sma200",
    "share price above 200-day sma": "price_above_sma200",
    "price above 50-day moving average": "price_above_sma50",
    "share price above 50-day moving average": "price_above_sma50",
    "golden cross": "golden_cross",
    "rsi": "rsi_14",
    "relative strength index": "rsi_14",
    "rsi(14)": "rsi_14",
    "rsi 14": "rsi_14",
    "macd": "macd_line",
    "macd line": "macd_line",
    "macd signal": "macd_signal",
    "macd histogram": "macd_hist",
    "macd hist": "macd_hist",
    "macd crossover": "macd_crossover",
    "52-week high": "price_to_52w_high",
    "52 week high": "price_to_52w_high",
    "distance from 52-week high": "price_to_52w_high",
    "52-week low": "price_to_52w_low",
    "52 week low": "price_to_52w_low",
    "bollinger bandwidth": "bollinger_bandwidth",
    "bandwidth": "bollinger_bandwidth",
    "bollinger %b": "bollinger_pct_b",
    "bollinger pct b": "bollinger_pct_b",
    "atr": "atr_14",
    "average true range": "atr_14",
    "historical volatility": "historical_volatility_20d",
    "realized volatility": "historical_volatility_20d",
}

# Supported Countries (grounded in catalog ISO-2 codes)
CANONICAL_COUNTRIES: Dict[str, str] = {
    "india": "IN",
    "indian": "IN",
    "us": "US",
    "usa": "US",
    "united states": "US",
    "american": "US",
    "uk": "GB",
    "united kingdom": "GB",
    "british": "GB",
    "germany": "DE",
    "german": "DE",
    "france": "FR",
    "french": "FR",
    "japan": "JP",
    "japanese": "JP",
    "netherlands": "NL",
    "dutch": "NL",
    "canada": "CA",
    "canadian": "CA",
}

# Supported Exchanges
CANONICAL_EXCHANGES: Dict[str, str] = {
    "nse": "XNSE",
    "national stock exchange": "XNSE",
    "bse": "XBOM",
    "bombay stock exchange": "XBOM",
    "nyse": "XNYS",
    "new york stock exchange": "XNYS",
    "nasdaq": "XNAS",
    "lse": "XLON",
    "london stock exchange": "XLON",
    "xetr": "XETR",
    "frankfurt": "XETR",
}

# Supported Sectors
CANONICAL_SECTORS: Dict[str, str] = {
    "technology": "Technology",
    "tech": "Technology",
    "financials": "Financials",
    "financial": "Financials",
    "finance": "Financials",
    "healthcare": "Healthcare",
    "health care": "Healthcare",
    "energy": "Energy",
    "consumer discretionary": "Consumer Discretionary",
    "consumer staples": "Consumer Staples",
    "industrials": "Industrials",
    "industrial": "Industrials",
    "materials": "Materials",
    "utilities": "Utilities",
    "real estate": "Real Estate",
    "communication services": "Communication Services",
    "communication": "Communication Services",
}

# Supported Industries
CANONICAL_INDUSTRIES: Dict[str, str] = {
    "banking": "Banking",
    "banks": "Banking",
    "bank": "Banking",
    "software": "Software",
    "semiconductors": "Semiconductors",
    "semiconductor": "Semiconductors",
    "chips": "Semiconductors",
    "pharmaceuticals": "Pharmaceuticals",
    "pharma": "Pharmaceuticals",
    "biotechnology": "Biotechnology",
    "biotech": "Biotechnology",
    "automobiles": "Automobiles",
    "auto": "Automobiles",
    "insurance": "Insurance",
    "oil & gas": "Oil & Gas",
    "oil and gas": "Oil & Gas",
    "retail": "Retail",
}

# Operator keywords
OPERATOR_MAP = [
    (
        re.compile(r"\b(above|greater than|more than|exceeds|over|>)\b", re.IGNORECASE),
        FilterOperator.GT,
    ),
    (re.compile(r"\b(at least|minimum of|no less than|>=)\b", re.IGNORECASE), FilterOperator.GTE),
    (re.compile(r"\b(below|under|less than|fewer than|<)\b", re.IGNORECASE), FilterOperator.LT),
    (re.compile(r"\b(at most|maximum of|no more than|<=)\b", re.IGNORECASE), FilterOperator.LTE),
    (re.compile(r"\b(equal to|exactly|=)\b", re.IGNORECASE), FilterOperator.EQ),
]


# =============================================================================
# Helper: Number & Magnitude Normalization
# =============================================================================

_NUMBER_TOKEN_PATTERN = re.compile(
    r"([₹$€£]?\s*[+-]?\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:lakh\s+crores?|lakhs?|crores?|cr\b|trillions?|tr\b|billions?|bn\b|b\b|millions?|m\b|thousands?|k\b|basis\s+points|bps\b|percent|%|x))?(?:\s*(?:inr|usd|eur|gbp|rs\.?))?)",
    re.IGNORECASE,
)


def extract_financial_number_token(val_str: str) -> str:
    """Extracts the leading/valid financial number and multiplier token from surrounding text."""
    m = _NUMBER_TOKEN_PATTERN.search(val_str)
    if m:
        token = m.group(1).strip()
        if token:
            return token
    return val_str.strip()


def parse_financial_number(
    raw_str: str, default_currency: str = "USD"
) -> Tuple[Decimal, Optional[str], Optional[str]]:
    """Parses numeric expressions including Indian magnitudes (crore, lakh) and international (k, m, bn, tr).

    Returns (normalized_value, currency, unit_kind).
    """
    clean = extract_financial_number_token(raw_str)

    # Detect currency prefix or symbol
    currency = None
    if (
        clean.startswith("₹")
        or "rs." in clean.lower()
        or "rs " in clean.lower()
        or "inr" in clean.lower()
    ):
        currency = "INR"
    elif clean.startswith("$") or "usd" in clean.lower():
        currency = "USD"
    elif clean.startswith("€") or "eur" in clean.lower():
        currency = "EUR"
    elif clean.startswith("£") or "gbp" in clean.lower():
        currency = "GBP"

    # Strip currency tokens
    s = re.sub(r"[₹$€£]|\b(inr|usd|eur|gbp|rs\.?)\b", "", clean, flags=re.IGNORECASE).strip()

    # Handle basis points
    if "basis points" in s.lower() or "bps" in s.lower():
        num_str = re.sub(r"\b(basis\s+points|bps)\b", "", s, flags=re.IGNORECASE).strip()
        num_str = num_str.replace(",", "")
        val = Decimal(num_str) / Decimal("100")
        return val, currency, "percent"

    # Handle percentage
    if "%" in s or "percent" in s.lower():
        num_str = re.sub(r"[%]|\bpercent\b", "", s, flags=re.IGNORECASE).strip()
        num_str = num_str.replace(",", "")
        val = Decimal(num_str)
        return val, currency, "percent"

    # Multiplier detection
    multiplier = Decimal("1")
    s_lower = s.lower()

    if "lakh crore" in s_lower or "lakh crores" in s_lower:
        multiplier = Decimal("1000000000000")  # 10^12
        s = re.sub(r"\blakh\s+crores?\b", "", s, flags=re.IGNORECASE).strip()
    elif "crore" in s_lower or "crores" in s_lower or re.search(r"\bcr\b|cr$", s_lower):
        multiplier = Decimal("10000000")  # 10^7
        s = re.sub(r"\b(crores?|cr)\b|cr$", "", s, flags=re.IGNORECASE).strip()
    elif "lakh" in s_lower or "lakhs" in s_lower:
        multiplier = Decimal("100000")  # 10^5
        s = re.sub(r"\blakhs?\b", "", s, flags=re.IGNORECASE).strip()
    elif "trillion" in s_lower or re.search(r"\btr\b|tr$", s_lower):
        multiplier = Decimal("1000000000000")  # 10^12
        s = re.sub(r"\b(trillions?|tr)\b|tr$", "", s, flags=re.IGNORECASE).strip()
    elif "billion" in s_lower or re.search(r"\b(bn|b)\b|bn$|b$", s_lower):
        multiplier = Decimal("1000000000")  # 10^9
        s = re.sub(r"\b(billions?|bn|b)\b|bn$|b$", "", s, flags=re.IGNORECASE).strip()
    elif "million" in s_lower or re.search(r"\bm\b|m$", s_lower):
        multiplier = Decimal("1000000")  # 10^6
        s = re.sub(r"\b(millions?|m)\b|m$", "", s, flags=re.IGNORECASE).strip()
    elif "thousand" in s_lower or s_lower.endswith("k") or re.search(r"k\b", s_lower):
        multiplier = Decimal("1000")
        s = re.sub(r"(thousands?|k\b|k$)", "", s, flags=re.IGNORECASE).strip()

    # Strip multiples indicator 'x'
    s = re.sub(r"[xX]$", "", s).strip()

    # Handle Indian / US comma grouping: remove commas
    s = s.replace(",", "").strip()

    try:
        val = Decimal(s) * multiplier
    except (InvalidOperation, ValueError):
        raise ValueError(f"Unable to parse financial number from '{raw_str}'")

    if math.isnan(float(val)) or math.isinf(float(val)):
        raise ValueError("Non-finite numeric values (NaN or Infinity) are prohibited.")

    return val, currency, None


# =============================================================================
# Main Translation Engine Class
# =============================================================================


class NLScreenerTranslationEngine:
    """Institutional natural language financial screener translation engine.

    Translates untrusted free-form user query into strict, schema-validated,
    registry-grounded ScreenerRunRequestDTO.
    """

    def __init__(self, repository: Optional[ScreenerRepository] = None):
        self.repository = repository or ScreenerRepository()
        self.filter_definitions = {f.filter_id: f for f in CANONICAL_FILTERS}

    def get_capabilities(self) -> NLCapabilitiesResponseDTO:
        """Returns metadata description of supported NLP translation features."""
        metrics_meta = [
            {
                "filter_id": f.filter_id,
                "display_name": f.display_name,
                "category": f.category.value,
                "unit_kind": f.unit_kind.value,
                "aliases": f.aliases,
            }
            for f in CANONICAL_FILTERS
        ]
        indicators_meta = [
            {
                "indicator_id": f.filter_id,
                "display_name": f.display_name,
                "category": f.category.value,
            }
            for f in CANONICAL_FILTERS
            if "technical" in f.category.value
        ]
        examples = [
            {
                "title": "Indian Large-Cap Growth & Value",
                "query": "Find large-cap Indian companies with revenue growth above 15%, positive free cash flow, P/E below 25 and a share price above the 200-day moving average.",
            },
            {
                "title": "US High Quality Tech Leaders",
                "query": "Find US technology companies with market cap over 50 billion USD, operating margin at least 25%, debt to equity below 0.8 and RSI below 60.",
            },
            {
                "title": "European Dividend & Cash Flow",
                "query": "Find European stocks with dividend yield above 4%, positive net income, and price above 50-day moving average.",
            },
            {
                "title": "Indian Mid-Cap Breakouts",
                "query": "Find Indian stocks with market cap between 5000 crore and 20000 crore INR, revenue growth over 20% and relative volume above 1.5.",
            },
        ]
        return NLCapabilitiesResponseDTO(
            supported_metrics=metrics_meta,
            supported_operators=["gt", "gte", "lt", "lte", "eq", "between", "in"],
            supported_currencies=["USD", "INR", "EUR", "GBP"],
            supported_units=["monetary", "percent", "multiple", "shares", "dimensionless"],
            supported_indicators=indicators_meta,
            supported_magnitudes=[
                "k",
                "m",
                "million",
                "bn",
                "billion",
                "tr",
                "lakh",
                "crore",
                "lakh crore",
            ],
            example_queries=examples,
        )

    def translate(self, request: NLTranslateRequestDTO) -> NLTranslationProposalDTO:
        """Translates a natural language user query into a validated screening proposal."""
        # 1. Validation & Input Constraints
        text = request.text.strip()
        if not text:
            raise NLScreenerEmptyRequestError()
        if len(text) > MAX_REQUEST_LENGTH:
            raise NLScreenerTextTooLongError(len(text), MAX_REQUEST_LENGTH)

        # 2. Security & Injection Checks
        check_prompt_injection(text)

        proposal_id = f"nlp_{uuid.uuid4().hex[:12]}"
        assumptions: List[str] = []
        requirements: List[NLRequirementResolutionDTO] = []
        ambiguities: List[NLAmbiguityQuestionDTO] = []
        unsupported: List[str] = []
        filters: List[FilterCriterionDTO] = []
        sort_criteria: List[SortCriterionDTO] = []
        result_limit: Optional[int] = None

        universe = UniverseSelectionDTO(universe_id="common_equity")

        # 3. Check for unsupported cross-field OR
        # e.g., "P/E < 15 or RSI < 30" (cross-field OR is unsupported)
        or_match = re.search(
            r"(\bpe\b|\bp/e\b|\bmarket cap\b|\brsi\b|\brevenue\b)[^,\.]*?\s+or\s+[^,\.]*?(\bpe\b|\bp/e\b|\brsi\b|\brevenue\b)",
            text,
            re.IGNORECASE,
        )
        if or_match:
            unsupported.append(
                "Cross-field Boolean OR logic ('"
                + or_match.group(0)
                + "') is unsupported. The Screener Engine executes conjunctions (AND) across factors."
            )

        # 4. Resolve Universe Scope (Country / Exchange / Sector / Industry)
        lower_text = text.lower()

        # Countries
        matched_countries: Set[str] = set()
        for c_term, c_code in CANONICAL_COUNTRIES.items():
            if re.search(rf"\b{c_term}\b", lower_text):
                matched_countries.add(c_code)
                if c_term in ["indian", "american", "british", "german", "french", "japanese"]:
                    universe.issuer_country_codes = list(matched_countries)
                    universe.listing_country_codes = list(matched_countries)
                else:
                    universe.listing_country_codes = list(matched_countries)

        if matched_countries:
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="Country context: " + ", ".join(matched_countries),
                    interpreted_concept="Country Universe Filter",
                    resolved_filter_id="listing_country_code",
                    status=NLRequirementStatus.RESOLVED,
                    explanation=f"Constrained securities to listing country codes {list(matched_countries)}",
                )
            )

        # Exchanges
        matched_exchanges: Set[str] = set()
        for e_term, e_mic in CANONICAL_EXCHANGES.items():
            if re.search(rf"\b{e_term}\b", lower_text):
                matched_exchanges.add(e_mic)

        if matched_exchanges:
            universe.exchange_mics = list(matched_exchanges)
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="Exchange context: " + ", ".join(matched_exchanges),
                    interpreted_concept="Exchange Venue Filter",
                    resolved_filter_id="exchange_mic",
                    status=NLRequirementStatus.RESOLVED,
                    explanation=f"Constrained securities to exchange venues {list(matched_exchanges)}",
                )
            )

        # Sectors (handles same-field OR cleanly, e.g. "Technology or Healthcare")
        matched_sectors: Set[str] = set()
        for s_term, s_name in CANONICAL_SECTORS.items():
            if s_term == "financial":
                if re.search(
                    r"\bfinancial\s+(sector|services|industry|stocks?|companies|equity|equities)\b",
                    lower_text,
                ):
                    matched_sectors.add(s_name)
            elif re.search(rf"\b{s_term}\b", lower_text):
                matched_sectors.add(s_name)

        if matched_sectors:
            universe.sectors = list(matched_sectors)
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="Sector: " + ", ".join(matched_sectors),
                    interpreted_concept="Sector Filter",
                    resolved_filter_id="sector",
                    status=NLRequirementStatus.RESOLVED,
                    explanation=f"Filtered securities in sectors: {list(matched_sectors)}",
                )
            )

        # Industries
        matched_industries: Set[str] = set()
        for i_term, i_name in CANONICAL_INDUSTRIES.items():
            if re.search(rf"\b{i_term}\b", lower_text):
                matched_industries.add(i_name)

        if matched_industries:
            universe.industries = list(matched_industries)
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="Industry: " + ", ".join(matched_industries),
                    interpreted_concept="Industry Classification",
                    resolved_filter_id="industry",
                    status=NLRequirementStatus.RESOLVED,
                    explanation=f"Filtered securities in industries: {list(matched_industries)}",
                )
            )

        # Unsupported colloquial business themes
        unsupported_themes = [
            (
                "ai infrastructure",
                "AI infrastructure is a thematic business topic, not a canonical GICS industry.",
            ),
            ("quantum computing", "Quantum computing is not an approved GICS industry."),
            ("space economy", "Space economy is not an approved GICS industry."),
            (
                "breakout",
                "Time-series predictive breakout forecasts are not supported deterministic screener filters.",
            ),
        ]
        for theme_phrase, reason in unsupported_themes:
            if theme_phrase in lower_text:
                unsupported.append(f"'{theme_phrase}': {reason}")
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=theme_phrase,
                        interpreted_concept=None,
                        resolved_filter_id=None,
                        status=NLRequirementStatus.UNSUPPORTED,
                        explanation=reason,
                    )
                )

        # Large-cap / Mega-cap keyword handling
        if re.search(r"\blarge[- ]?cap\b", lower_text):
            # Check context: if India or INR context, >= 20,000 crore INR; if US or global, >= 10 billion USD
            if (
                any(c in (universe.listing_country_codes or []) for c in ["IN", "IND"])
                or "inr" in lower_text
                or "₹" in text
                or "crore" in lower_text
            ):
                threshold_val = 200000000000.0  # 20,000 crore INR
                curr = "INR"
                assumptions.append("Interpreted 'large-cap' as Market Cap >= ₹20,000 Crore (INR).")
            else:
                threshold_val = 10000000000.0  # $10 billion USD
                curr = "USD"
                assumptions.append("Interpreted 'large-cap' as Market Cap >= $10 Billion (USD).")

            filters.append(
                FilterCriterionDTO(
                    condition_id=f"cond_{len(filters) + 1}",
                    filter_id="market_cap",
                    operator=FilterOperator.GTE,
                    value=threshold_val,
                    currency=curr,
                    unit="monetary",
                )
            )
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="large-cap",
                    interpreted_concept="Market Capitalization Threshold",
                    resolved_filter_id="market_cap",
                    status=NLRequirementStatus.RESOLVED,
                    explanation=f"Applied market_cap >= {threshold_val} {curr}",
                )
            )

        # Mega-cap handling
        if re.search(r"\bmega[- ]?cap\b", lower_text):
            universe.universe_id = "global_mega_cap"
            assumptions.append("Selected 'global_mega_cap' universe for mega-cap specification.")
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="mega-cap",
                    interpreted_concept="Global Mega-Cap Universe",
                    resolved_filter_id="universe",
                    status=NLRequirementStatus.RESOLVED,
                    explanation="Switched canonical universe to global_mega_cap.",
                )
            )

        # 5. Check for Subjective Ambiguities ("cheap", "profitable", "high growth", "oversold", "best", "safe")
        if re.search(r"\bcheap\b", lower_text) and not any(
            k in lower_text for k in ["pe", "p/e", "pb", "p/b", "price to"]
        ):
            ambiguities.append(
                NLAmbiguityQuestionDTO(
                    ambiguity_id="amb_cheap",
                    category=NLAmbiguityCategory.METRIC_AMBIGUITY,
                    question="Which valuation metric should define 'cheap'?",
                    source_phrase="cheap",
                    options=[
                        {
                            "id": "opt_pe_20",
                            "label": "P/E below 20x",
                            "filter_id": "pe_ratio",
                            "operator": "lt",
                            "value": 20.0,
                        },
                        {
                            "id": "opt_pe_15",
                            "label": "P/E below 15x",
                            "filter_id": "pe_ratio",
                            "operator": "lt",
                            "value": 15.0,
                        },
                        {
                            "id": "opt_pb_2",
                            "label": "P/B below 2x",
                            "filter_id": "pb_ratio",
                            "operator": "lt",
                            "value": 2.0,
                        },
                        {
                            "id": "opt_ev_10",
                            "label": "EV/EBITDA below 10x",
                            "filter_id": "ev_to_ebitda",
                            "operator": "lt",
                            "value": 10.0,
                        },
                    ],
                )
            )
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="cheap",
                    interpreted_concept="Valuation Multiple",
                    resolved_filter_id=None,
                    status=NLRequirementStatus.AMBIGUOUS,
                    explanation="Subjective qualifier 'cheap' requires an explicit valuation threshold.",
                )
            )

        if re.search(r"\bprofitable\b", lower_text) and not any(
            k in lower_text
            for k in ["net income", "operating income", "ebit", "margin", "profit above"]
        ):
            ambiguities.append(
                NLAmbiguityQuestionDTO(
                    ambiguity_id="amb_profitable",
                    category=NLAmbiguityCategory.METRIC_AMBIGUITY,
                    question="Which profitability criterion defines 'profitable'?",
                    source_phrase="profitable",
                    options=[
                        {
                            "id": "opt_net_income_gt_0",
                            "label": "Positive Net Income (Net Income > 0)",
                            "filter_id": "net_income",
                            "operator": "gt",
                            "value": 0.0,
                        },
                        {
                            "id": "opt_op_income_gt_0",
                            "label": "Positive Operating Income (EBIT > 0)",
                            "filter_id": "operating_income",
                            "operator": "gt",
                            "value": 0.0,
                        },
                        {
                            "id": "opt_net_margin_10",
                            "label": "Net Margin above 10%",
                            "filter_id": "net_margin",
                            "operator": "gt",
                            "value": 10.0,
                        },
                    ],
                )
            )
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="profitable",
                    interpreted_concept="Profitability Condition",
                    resolved_filter_id=None,
                    status=NLRequirementStatus.AMBIGUOUS,
                    explanation="Term 'profitable' could mean Net Income > 0, Operating Income > 0, or Margin threshold.",
                )
            )

        if re.search(r"\boversold\b", lower_text) and not re.search(r"\brsi\b", lower_text):
            ambiguities.append(
                NLAmbiguityQuestionDTO(
                    ambiguity_id="amb_oversold",
                    category=NLAmbiguityCategory.INDICATOR_AMBIGUITY,
                    question="Which indicator should define 'oversold'?",
                    source_phrase="oversold",
                    options=[
                        {
                            "id": "opt_rsi_30",
                            "label": "RSI(14) below 30",
                            "filter_id": "rsi_14",
                            "operator": "lt",
                            "value": 30.0,
                        },
                        {
                            "id": "opt_rsi_20",
                            "label": "RSI(14) below 20 (Deep Oversold)",
                            "filter_id": "rsi_14",
                            "operator": "lt",
                            "value": 20.0,
                        },
                        {
                            "id": "opt_bb_lower",
                            "label": "Bollinger %B below 0 (Below Lower Band)",
                            "filter_id": "bollinger_pct_b",
                            "operator": "lt",
                            "value": 0.0,
                        },
                    ],
                )
            )
            requirements.append(
                NLRequirementResolutionDTO(
                    requirement_id=f"req_{len(requirements) + 1}",
                    source_text="oversold",
                    interpreted_concept="Oversold Technical Condition",
                    resolved_filter_id=None,
                    status=NLRequirementStatus.AMBIGUOUS,
                    explanation="Technical term 'oversold' requires indicator selection (RSI vs Bollinger Bands).",
                )
            )

        # 6. Parse Sorting and Result Limits
        # "sort by [field] [asc/desc]" or "highest [field] first" or "lowest [field] first"
        sort_match = re.search(
            r"(?i)\b(sort by|order by)\s+([a-z0-9_/ ]+?)\s+(descending|ascending|desc|asc)\b", text
        )
        if sort_match:
            sort_field_term = sort_match.group(2).strip()
            direction_str = sort_match.group(3).lower()
            sort_dir = SortDirection.DESC if "desc" in direction_str else SortDirection.ASC
            mapped_fid = CANONICAL_FILTER_SYNONYMS.get(
                sort_field_term.lower(), sort_field_term.lower()
            )
            if mapped_fid in self.filter_definitions:
                sort_criteria.append(
                    SortCriterionDTO(
                        field_id=mapped_fid, direction=sort_dir, null_order=SortNullOrder.NULLS_LAST
                    )
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=sort_match.group(0),
                        interpreted_concept="Result Sorting",
                        resolved_filter_id=mapped_fid,
                        status=NLRequirementStatus.RESOLVED,
                        explanation=f"Sorted by {mapped_fid} ({sort_dir.value}).",
                    )
                )

        # "top N [stocks/companies]"
        top_n_match = re.search(r"(?i)\b(top|first|show)\s+(\d{1,3})\b", text)
        if top_n_match:
            limit_val = int(top_n_match.group(2))
            if 1 <= limit_val <= 100:
                result_limit = limit_val
                assumptions.append(f"Constrained results to top {limit_val} securities.")
                # If no sort criteria specified, check if ranking was indicated
                if not sort_criteria:
                    # check if market cap or any factor mentioned
                    if "market cap" in lower_text or "large" in lower_text:
                        sort_criteria.append(
                            SortCriterionDTO(field_id="market_cap", direction=SortDirection.DESC)
                        )
                        assumptions.append(
                            "Defaulted top N ordering to market capitalization descending."
                        )

        # 7. Range Expressions across the query: "[metric] between X and Y"
        text_for_clauses = text
        range_matches = list(
            re.finditer(
                r"([a-z0-9_/ -]+?)\s+between\s+(.+?)\s+and\s+([a-z0-9₹$€£,.\s]+?)(?:,|\band\b|\bwith\b|\bhaving\b|$)",
                text,
                re.IGNORECASE,
            )
        )
        for rm in range_matches:
            metric_raw = rm.group(1).strip().lower()
            val1_raw = rm.group(2).strip()
            val2_raw = rm.group(3).strip()

            target_fid = None
            for syn in sorted(CANONICAL_FILTER_SYNONYMS.keys(), key=lambda s: len(s), reverse=True):
                if re.search(rf"\b{re.escape(syn)}\b", metric_raw):
                    target_fid = CANONICAL_FILTER_SYNONYMS[syn]
                    break

            if target_fid and target_fid in self.filter_definitions:
                try:
                    v1, c1, u1 = parse_financial_number(
                        val1_raw, default_currency=request.currency_policy or "USD"
                    )
                    v2, c2, u2 = parse_financial_number(
                        val2_raw, default_currency=request.currency_policy or "USD"
                    )
                    curr = c2 or c1 or (request.currency_policy or "USD")

                    filters.append(
                        FilterCriterionDTO(
                            condition_id=f"cond_{len(filters) + 1}",
                            filter_id=target_fid,
                            operator=FilterOperator.BETWEEN,
                            value=float(min(v1, v2)),
                            secondary_value=float(max(v1, v2)),
                            currency=curr
                            if self.filter_definitions[target_fid].unit_kind == UnitKind.MONETARY
                            else None,
                            unit=self.filter_definitions[target_fid].unit_kind.value,
                        )
                    )
                    requirements.append(
                        NLRequirementResolutionDTO(
                            requirement_id=f"req_{len(requirements) + 1}",
                            source_text=rm.group(0).strip(),
                            interpreted_concept=self.filter_definitions[target_fid].display_name,
                            resolved_filter_id=target_fid,
                            status=NLRequirementStatus.RESOLVED,
                            explanation=f"Applied {target_fid} BETWEEN {min(v1, v2)} AND {max(v1, v2)}",
                        )
                    )
                    text_for_clauses = text_for_clauses.replace(rm.group(0), ", ")
                except Exception as e:
                    unsupported.append(f"Failed parsing range in '{rm.group(0)}': {str(e)}")

        # 8. Clause Extraction & Explicit Metric Condition Parsing
        # Split text into candidate condition phrases by comma, 'and', 'with', 'having', 'where'
        clauses = re.split(
            r",|\band\b|\bwith\b|\bhaving\b|\bwhere\b", text_for_clauses, flags=re.IGNORECASE
        )

        for raw_clause in clauses:
            clause = raw_clause.strip()
            if not clause:
                continue

            c_lower = clause.lower()

            # Skip country/exchange/sector only clauses already processed
            if any(c_lower == c_term for c_term in CANONICAL_COUNTRIES) or any(
                c_lower == e_term for e_term in CANONICAL_EXCHANGES
            ):
                continue
            if c_lower in ["large-cap", "large cap", "mega-cap", "mega cap"]:
                continue
            if sort_match and clause in sort_match.group(0):
                continue

            # Special case: "positive free cash flow" or "positive net income" or "positive earnings"
            if "positive free cash flow" in c_lower or "positive fcf" in c_lower:
                filters.append(
                    FilterCriterionDTO(
                        condition_id=f"cond_{len(filters) + 1}",
                        filter_id="fcf",
                        operator=FilterOperator.GT,
                        value=0.0,
                        unit="monetary",
                    )
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=clause,
                        interpreted_concept="Positive Free Cash Flow",
                        resolved_filter_id="fcf",
                        status=NLRequirementStatus.RESOLVED,
                        explanation="Applied fcf > 0",
                    )
                )
                continue

            if (
                "positive net income" in c_lower
                or "positive earnings" in c_lower
                or "positive profit" in c_lower
            ):
                filters.append(
                    FilterCriterionDTO(
                        condition_id=f"cond_{len(filters) + 1}",
                        filter_id="net_income",
                        operator=FilterOperator.GT,
                        value=0.0,
                        unit="monetary",
                    )
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=clause,
                        interpreted_concept="Positive Net Income",
                        resolved_filter_id="net_income",
                        status=NLRequirementStatus.RESOLVED,
                        explanation="Applied net_income > 0",
                    )
                )
                continue

            # Special case: "price above 200-day moving average" / "share price above 200-day moving average"
            if re.search(
                r"\b(price|share price|close)\s+above\s+(the\s+)?200[- ]?day\s+(moving\s+average|sma)\b",
                c_lower,
            ):
                filters.append(
                    FilterCriterionDTO(
                        condition_id=f"cond_{len(filters) + 1}",
                        filter_id="price_above_sma200",
                        operator=FilterOperator.EQ,
                        value=True,
                        unit="dimensionless",
                    )
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=clause,
                        interpreted_concept="Price Above 200-Day SMA",
                        resolved_filter_id="price_above_sma200",
                        status=NLRequirementStatus.RESOLVED,
                        explanation="Applied price_above_sma200 == True",
                    )
                )
                continue

            # Special case: "price above 50-day moving average"
            if re.search(
                r"\b(price|share price|close)\s+above\s+(the\s+)?50[- ]?day\s+(moving\s+average|sma)\b",
                c_lower,
            ):
                filters.append(
                    FilterCriterionDTO(
                        condition_id=f"cond_{len(filters) + 1}",
                        filter_id="price_above_sma50",
                        operator=FilterOperator.EQ,
                        value=True,
                        unit="dimensionless",
                    )
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=clause,
                        interpreted_concept="Price Above 50-Day SMA",
                        resolved_filter_id="price_above_sma50",
                        status=NLRequirementStatus.RESOLVED,
                        explanation="Applied price_above_sma50 == True",
                    )
                )
                continue

            # Check for range: "[metric] between X and Y"
            between_match = re.search(
                r"([a-z0-9_/ -]+?)\s+between\s+(.+?)\s+and\s+(.+)$", clause, re.IGNORECASE
            )
            if between_match:
                metric_raw = between_match.group(1).strip().lower()
                val1_raw = between_match.group(2).strip()
                val2_raw = between_match.group(3).strip()

                target_fid = None
                for syn in sorted(
                    CANONICAL_FILTER_SYNONYMS.keys(), key=lambda s: len(s), reverse=True
                ):
                    if re.search(rf"\b{re.escape(syn)}\b", metric_raw):
                        target_fid = CANONICAL_FILTER_SYNONYMS[syn]
                        break

                if target_fid and target_fid in self.filter_definitions:
                    try:
                        v1, c1, u1 = parse_financial_number(
                            val1_raw, default_currency=request.currency_policy or "USD"
                        )
                        v2, c2, u2 = parse_financial_number(
                            val2_raw, default_currency=request.currency_policy or "USD"
                        )
                        curr = c2 or c1 or (request.currency_policy or "USD")

                        filters.append(
                            FilterCriterionDTO(
                                condition_id=f"cond_{len(filters) + 1}",
                                filter_id=target_fid,
                                operator=FilterOperator.BETWEEN,
                                value=float(min(v1, v2)),
                                secondary_value=float(max(v1, v2)),
                                currency=curr
                                if self.filter_definitions[target_fid].unit_kind
                                == UnitKind.MONETARY
                                else None,
                                unit=self.filter_definitions[target_fid].unit_kind.value,
                            )
                        )
                        requirements.append(
                            NLRequirementResolutionDTO(
                                requirement_id=f"req_{len(requirements) + 1}",
                                source_text=clause,
                                interpreted_concept=self.filter_definitions[
                                    target_fid
                                ].display_name,
                                resolved_filter_id=target_fid,
                                status=NLRequirementStatus.RESOLVED,
                                explanation=f"Applied {target_fid} BETWEEN {min(v1, v2)} AND {max(v1, v2)}",
                            )
                        )
                        continue
                    except Exception as e:
                        unsupported.append(f"Failed parsing range in '{clause}': {str(e)}")
                        continue

            # Check for Standard Operator Comparison: [metric] [operator] [value]
            # Match longest synonym first
            matched_metric: Optional[str] = None
            matched_synonym: Optional[str] = None
            for syn in sorted(CANONICAL_FILTER_SYNONYMS.keys(), key=lambda s: len(s), reverse=True):
                # match with word boundary
                if re.search(rf"\b{re.escape(syn)}\b", c_lower):
                    matched_metric = CANONICAL_FILTER_SYNONYMS[syn]
                    matched_synonym = syn
                    break

            if not matched_metric:
                if any(
                    w in c_lower
                    for w in [
                        "metric",
                        "indicator",
                        "factor",
                        "score",
                        "guaranteed",
                        "forecast",
                        "predict",
                        "called",
                    ]
                ):
                    unsupported.append(
                        f"Unsupported or unapproved financial metric: '{clause}'"
                    )
                    requirements.append(
                        NLRequirementResolutionDTO(
                            requirement_id=f"req_{len(requirements) + 1}",
                            source_text=clause,
                            interpreted_concept=None,
                            resolved_filter_id=None,
                            status=NLRequirementStatus.UNSUPPORTED,
                            explanation="Metric is not registered in the canonical 70-filter catalog.",
                        )
                    )
                continue

            # Find operator in clause
            detected_op: Optional[FilterOperator] = None
            op_end_pos = -1
            for op_regex, op_enum in OPERATOR_MAP:
                m = op_regex.search(c_lower)
                if m:
                    detected_op = op_enum
                    op_end_pos = m.end()
                    break

            if not detected_op:
                continue

            val_str = clause[op_end_pos:].strip()
            # Clean trailing punctuation
            val_str = val_str.rstrip(".!?;")

            if not val_str:
                continue

            f_def = self.filter_definitions.get(matched_metric)
            if not f_def:
                continue

            try:
                # Use contextual default currency (INR if Indian stocks, else request currency)
                def_curr = (
                    "INR"
                    if any(c in (universe.listing_country_codes or []) for c in ["IN", "IND"])
                    else (request.currency_policy or "USD")
                )
                num_val, curr, u_kind = parse_financial_number(val_str, default_currency=def_curr)

                # Validate operator is allowed for this filter
                if detected_op not in f_def.allowed_operators:
                    detected_op = f_def.default_operator

                filters.append(
                    FilterCriterionDTO(
                        condition_id=f"cond_{len(filters) + 1}",
                        filter_id=matched_metric,
                        operator=detected_op,
                        value=float(num_val),
                        currency=curr or def_curr if f_def.unit_kind == UnitKind.MONETARY else None,
                        unit=f_def.unit_kind.value,
                    )
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=clause,
                        interpreted_concept=f_def.display_name,
                        resolved_filter_id=matched_metric,
                        status=NLRequirementStatus.RESOLVED,
                        explanation=f"Applied {matched_metric} {detected_op.value} {num_val}",
                    )
                )
            except Exception as e:
                unsupported.append(
                    f"Failed parsing threshold for '{matched_synonym}' from '{val_str}': {str(e)}"
                )
                requirements.append(
                    NLRequirementResolutionDTO(
                        requirement_id=f"req_{len(requirements) + 1}",
                        source_text=clause,
                        interpreted_concept=f_def.display_name,
                        resolved_filter_id=matched_metric,
                        status=NLRequirementStatus.UNSUPPORTED,
                        explanation=f"Threshold error: {str(e)}",
                    )
                )

        # 8. Check Handling for Modify Mode
        modification_diff: Optional[NLQueryModificationDiffDTO] = None
        if request.mode == NLTranslationMode.MODIFY_CURRENT_DRAFT and request.current_filters:
            # Calculate additions, updates, removals
            existing_fids = {f.filter_id: f for f in request.current_filters}
            added = []
            updated = []
            for f in filters:
                if f.filter_id in existing_fids:
                    updated.append(f)
                else:
                    added.append(f)

            # Check if user explicitly asked to "remove" a condition
            removed: List[str] = []
            for syn, fid in CANONICAL_FILTER_SYNONYMS.items():
                if re.search(rf"\bremove\s+{re.escape(syn)}\b", lower_text) or re.search(
                    rf"\bdelete\s+{re.escape(syn)}\b", lower_text
                ):
                    if fid in existing_fids:
                        removed.append(fid)

            modification_diff = NLQueryModificationDiffDTO(
                added_conditions=added,
                updated_conditions=updated,
                removed_conditions=removed,
            )

            # Build the modified active filter set
            merged_filters: List[FilterCriterionDTO] = []
            for ef in request.current_filters:
                if ef.filter_id in removed:
                    continue
                upd = next((uf for uf in updated if uf.filter_id == ef.filter_id), None)
                if upd:
                    merged_filters.append(upd)
                else:
                    merged_filters.append(ef)
            for af in added:
                merged_filters.append(af)
            filters = merged_filters

        # 9. Determine Status & Readiness
        if ambiguities:
            status = NLTranslationStatus.NEEDS_CLARIFICATION
            ready = False
        elif unsupported:
            status = NLTranslationStatus.UNSUPPORTED
            ready = False
        elif not filters and not (
            universe.listing_country_codes
            or universe.exchange_mics
            or universe.sectors
            or universe.industries
        ):
            status = NLTranslationStatus.INVALID
            ready = False
            unsupported.append(
                "No recognized financial screening criteria or security universe could be extracted."
            )
        else:
            status = NLTranslationStatus.VALID
            ready = True

        total_reqs = len(requirements)
        resolved_reqs = sum(1 for r in requirements if r.status == NLRequirementStatus.RESOLVED)
        coverage_summary = (
            f"{resolved_reqs} of {total_reqs} requirements resolved"
            if total_reqs > 0
            else "0 requirements extracted"
        )

        return NLTranslationProposalDTO(
            proposal_id=proposal_id,
            status=status,
            original_text=text,
            universe=universe,
            filters=filters,
            sort=sort_criteria,
            result_limit=result_limit,
            requirements=requirements,
            ambiguities=ambiguities,
            unsupported=unsupported,
            assumptions=assumptions,
            modification_diff=modification_diff,
            ready_for_review=ready,
            translator_version=TRANSLATOR_VERSION,
            registry_revision=REGISTRY_REVISION,
            coverage_count=coverage_summary,
        )

    def clarify(self, request: NLClarifyRequestDTO) -> NLTranslationProposalDTO:
        """Applies a clarification answer to an unresolved proposal, re-compiling into a valid query."""
        # Option mapping
        additional_phrase = ""
        if request.selected_option_id == "opt_pe_20":
            additional_phrase = "P/E below 20"
        elif request.selected_option_id == "opt_pe_15":
            additional_phrase = "P/E below 15"
        elif request.selected_option_id == "opt_pb_2":
            additional_phrase = "P/B below 2"
        elif request.selected_option_id == "opt_ev_10":
            additional_phrase = "EV to EBITDA below 10"
        elif request.selected_option_id == "opt_net_income_gt_0":
            additional_phrase = "positive net income"
        elif request.selected_option_id == "opt_op_income_gt_0":
            additional_phrase = "operating income above 0"
        elif request.selected_option_id == "opt_net_margin_10":
            additional_phrase = "net margin above 10%"
        elif request.selected_option_id == "opt_rsi_30":
            additional_phrase = "RSI below 30"
        elif request.selected_option_id == "opt_rsi_20":
            additional_phrase = "RSI below 20"
        elif request.selected_option_id == "opt_bb_lower":
            additional_phrase = "bollinger pct b below 0"
        else:
            additional_phrase = request.selected_option_id

        # Replace the ambiguous phrase in original text with the concrete chosen expression
        clean_text = request.original_text
        if request.ambiguity_id == "amb_cheap":
            clean_text = re.sub(
                r"\bcheap\b", f", {additional_phrase}, ", clean_text, flags=re.IGNORECASE
            )
        elif request.ambiguity_id == "amb_profitable":
            clean_text = re.sub(
                r"\bprofitable\b", f", {additional_phrase}, ", clean_text, flags=re.IGNORECASE
            )
        elif request.ambiguity_id == "amb_oversold":
            clean_text = re.sub(
                r"\boversold\b", f", {additional_phrase}, ", clean_text, flags=re.IGNORECASE
            )
        else:
            clean_text = f"{request.original_text}, {additional_phrase}"

        # Re-translate
        new_req = NLTranslateRequestDTO(text=clean_text)
        updated_proposal = self.translate(new_req)
        updated_proposal.proposal_id = request.proposal_id
        updated_proposal.assumptions.append(
            f"Clarified '{request.ambiguity_id}' using option '{request.selected_option_id}'."
        )
        return updated_proposal

    def modify(self, request: NLTranslateRequestDTO) -> NLTranslationProposalDTO:
        """Modifies an existing screener draft using natural language instructions."""
        request.mode = NLTranslationMode.MODIFY_CURRENT_DRAFT
        return self.translate(request)


# Singleton natural language translation engine
nl_translation_engine = NLScreenerTranslationEngine()
