"""ATLAS Portfolios V1 — Canonical Classification Registry & Fund Datasets (Stage 112).

Provides source-qualified metadata for instruments, companies/issuers,
sector taxonomies, country mappings, and fund constituent disclosures.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from atlas.portfolios.exposure.enums import AssetClass, GeographyPolicy


@dataclass
class InstrumentClassificationMetadata:
    """Canonical classification records for a financial instrument."""
    instrument_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    issuer_id: str
    issuer_name: str
    sector: str
    industry: str
    domicile_country: str
    headquarters_country: str
    listing_country: str
    region: str
    currency: str
    exchange_mic: Optional[str] = None
    share_class: Optional[str] = None
    is_adr: bool = False
    underlying_issuer_id: Optional[str] = None
    is_fund: bool = False
    taxonomy_version: str = "GICS-2024"


# Convenient alias
InstrumentClassification = InstrumentClassificationMetadata


@dataclass
class FundConstituentRecord:
    """Underlying constituent disclosure within an ETF or fund."""
    constituent_id: str
    symbol: str
    name: str
    weight: Decimal  # Decimal fraction, e.g. 0.0725 for 7.25%
    asset_class: AssetClass = AssetClass.EQUITY
    sector: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None


@dataclass
class FundHoldingsDataset:
    """Verified fund constituent portfolio disclosure."""
    fund_instrument_id: str
    fund_symbol: str
    fund_name: str
    holdings_as_of: datetime
    publication_date: Optional[datetime]
    source_provider: str
    constituents: List[FundConstituentRecord]
    residual_unclassified_weight: Decimal = Decimal("0.00")


# Standard Sector to Industry Hierarchy (GICS-inspired)
SECTOR_INDUSTRY_HIERARCHY: Dict[str, List[str]] = {
    "Information Technology": ["Software", "Semiconductors", "IT Services", "Technology Hardware"],
    "Financials": ["Banks", "Capital Markets", "Insurance", "Diversified Financial Services"],
    "Health Care": ["Pharmaceuticals", "Biotechnology", "Health Care Equipment", "Health Care Providers"],
    "Consumer Discretionary": ["Automobiles", "Internet & Direct Marketing Retail", "Hotels, Restaurants & Leisure", "Textiles & Luxury"],
    "Communication Services": ["Interactive Media & Services", "Entertainment", "Telecom Services", "Media"],
    "Industrials": ["Aerospace & Defense", "Machinery", "Air Freight & Logistics", "Commercial Services"],
    "Consumer Staples": ["Beverages", "Food Products", "Household Products", "Personal Care"],
    "Energy": ["Oil, Gas & Consumable Fuels", "Energy Equipment & Services"],
    "Materials": ["Chemicals", "Metals & Mining", "Construction Materials"],
    "Utilities": ["Electric Utilities", "Gas Utilities", "Multi-Utilities", "Water Utilities"],
    "Real Estate": ["Equity Real Estate Investment Trusts (REITs)", "Real Estate Management & Development"],
    "Unknown Sector": ["Unknown Industry"],
}

# Country to Region standard mapping
COUNTRY_REGION_MAPPING: Dict[str, str] = {
    "United States": "North America",
    "Canada": "North America",
    "United Kingdom": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "Switzerland": "Europe",
    "Ireland": "Europe",
    "Netherlands": "Europe",
    "India": "Asia-Pacific",
    "Japan": "Asia-Pacific",
    "China": "Asia-Pacific",
    "Singapore": "Asia-Pacific",
    "Australia": "Asia-Pacific",
    "Brazil": "Latin America",
    "Mexico": "Latin America",
    "South Africa": "Middle East & Africa",
    "United Arab Emirates": "Middle East & Africa",
}


class ClassificationRegistry:
    """Authoritative source of instrument, issuer, sector, and fund look-through mappings."""

    def __init__(self) -> None:
        self._instruments: Dict[str, InstrumentClassificationMetadata] = {}
        self._funds: Dict[str, FundHoldingsDataset] = {}
        self._seed_default_universe()

    def _seed_default_universe(self) -> None:
        """Seed canonical institutional universe and benchmark constituents."""
        now = datetime(2026, 1, 1)

        # 1. Tech Leaders
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_aapl",
                symbol="AAPL",
                name="Apple Inc.",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_aapl",
                issuer_name="Apple Inc.",
                sector="Information Technology",
                industry="Technology Hardware",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNAS",
            )
        )
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_msft",
                symbol="MSFT",
                name="Microsoft Corporation",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_msft",
                issuer_name="Microsoft Corporation",
                sector="Information Technology",
                industry="Software",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNAS",
            )
        )
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_nvda",
                symbol="NVDA",
                name="NVIDIA Corporation",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_nvda",
                issuer_name="NVIDIA Corporation",
                sector="Information Technology",
                industry="Semiconductors",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNAS",
            )
        )

        # 2. Multi-Class Shares (GOOG & GOOGL -> Alphabet Inc.)
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_googl",
                symbol="GOOGL",
                name="Alphabet Inc. Class A",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_alphabet",
                issuer_name="Alphabet Inc.",
                sector="Communication Services",
                industry="Interactive Media & Services",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNAS",
                share_class="Class A",
            )
        )
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_goog",
                symbol="GOOG",
                name="Alphabet Inc. Class C",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_alphabet",
                issuer_name="Alphabet Inc.",
                sector="Communication Services",
                industry="Interactive Media & Services",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNAS",
                share_class="Class C",
            )
        )

        # 3. Financials
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_jpm",
                symbol="JPM",
                name="JPMorgan Chase & Co.",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_jpm",
                issuer_name="JPMorgan Chase & Co.",
                sector="Financials",
                industry="Banks",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNYS",
            )
        )

        # 4. Indian Cross-Border / Multi-Currency (Infosys local vs ADR)
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_infy_inr",
                symbol="INFY",
                name="Infosys Limited (NSE)",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_infy",
                issuer_name="Infosys Limited",
                sector="Information Technology",
                industry="IT Services",
                domicile_country="India",
                headquarters_country="India",
                listing_country="India",
                region="Asia-Pacific",
                currency="INR",
                exchange_mic="XNSE",
            )
        )
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_infy_adr",
                symbol="INFY.N",
                name="Infosys Limited ADR (NYSE)",
                asset_class=AssetClass.EQUITY,
                issuer_id="iss_infy",
                issuer_name="Infosys Limited",
                sector="Information Technology",
                industry="IT Services",
                domicile_country="India",
                headquarters_country="India",
                listing_country="United States",  # Listed in US, economic domicile in India!
                region="Asia-Pacific",
                currency="USD",
                exchange_mic="XNYS",
                is_adr=True,
                underlying_issuer_id="iss_infy",
            )
        )

        # 5. Fixed Income
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_ust10y",
                symbol="UST10Y",
                name="US Treasury 10-Year Bond",
                asset_class=AssetClass.FIXED_INCOME,
                issuer_id="iss_us_treasury",
                issuer_name="United States Department of the Treasury",
                sector="Government / Sovereign",
                industry="Sovereign Debt",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
            )
        )

        # 6. Canonical ETFs (SPY, QQQ)
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_spy",
                symbol="SPY",
                name="SPDR S&P 500 ETF Trust",
                asset_class=AssetClass.FUND,
                issuer_id="iss_ssga",
                issuer_name="State Street Global Advisors",
                sector="Financials",
                industry="Capital Markets",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNYS",
                is_fund=True,
            )
        )
        self.register_instrument(
            InstrumentClassificationMetadata(
                instrument_id="inst_qqq",
                symbol="QQQ",
                name="Invesco QQQ Trust",
                asset_class=AssetClass.FUND,
                issuer_id="iss_invesco",
                issuer_name="Invesco Capital Management",
                sector="Financials",
                industry="Capital Markets",
                domicile_country="United States",
                headquarters_country="United States",
                listing_country="United States",
                region="North America",
                currency="USD",
                exchange_mic="XNAS",
                is_fund=True,
            )
        )

        # 7. Seed Fund Holdings Datasets
        # SPY Holdings Snapshot
        self.register_fund_holdings(
            FundHoldingsDataset(
                fund_instrument_id="inst_spy",
                fund_symbol="SPY",
                fund_name="SPDR S&P 500 ETF Trust",
                holdings_as_of=now,
                publication_date=now,
                source_provider="SSGA_OFFICIAL_DISCLOSURE",
                constituents=[
                    FundConstituentRecord(
                        constituent_id="inst_msft",
                        symbol="MSFT",
                        name="Microsoft Corporation",
                        weight=Decimal("0.0725"),  # 7.25%
                        sector="Information Technology",
                        country="United States",
                        currency="USD",
                    ),
                    FundConstituentRecord(
                        constituent_id="inst_aapl",
                        symbol="AAPL",
                        name="Apple Inc.",
                        weight=Decimal("0.0650"),  # 6.50%
                        sector="Information Technology",
                        country="United States",
                        currency="USD",
                    ),
                    FundConstituentRecord(
                        constituent_id="inst_nvda",
                        symbol="NVDA",
                        name="NVIDIA Corporation",
                        weight=Decimal("0.0600"),  # 6.00%
                        sector="Information Technology",
                        country="United States",
                        currency="USD",
                    ),
                    FundConstituentRecord(
                        constituent_id="inst_jpm",
                        symbol="JPM",
                        name="JPMorgan Chase & Co.",
                        weight=Decimal("0.0125"),  # 1.25%
                        sector="Financials",
                        country="United States",
                        currency="USD",
                    ),
                ],
                residual_unclassified_weight=Decimal("0.7900"),  # 79% other constituents
            )
        )

        # QQQ Holdings Snapshot
        self.register_fund_holdings(
            FundHoldingsDataset(
                fund_instrument_id="inst_qqq",
                fund_symbol="QQQ",
                fund_name="Invesco QQQ Trust",
                holdings_as_of=now,
                publication_date=now,
                source_provider="INVESCO_OFFICIAL_DISCLOSURE",
                constituents=[
                    FundConstituentRecord(
                        constituent_id="inst_msft",
                        symbol="MSFT",
                        name="Microsoft Corporation",
                        weight=Decimal("0.0880"),  # 8.80%
                        sector="Information Technology",
                        country="United States",
                        currency="USD",
                    ),
                    FundConstituentRecord(
                        constituent_id="inst_aapl",
                        symbol="AAPL",
                        name="Apple Inc.",
                        weight=Decimal("0.0800"),  # 8.00%
                        sector="Information Technology",
                        country="United States",
                        currency="USD",
                    ),
                    FundConstituentRecord(
                        constituent_id="inst_nvda",
                        symbol="NVDA",
                        name="NVIDIA Corporation",
                        weight=Decimal("0.0750"),  # 7.50%
                        sector="Information Technology",
                        country="United States",
                        currency="USD",
                    ),
                ],
                residual_unclassified_weight=Decimal("0.7570"),
            )
        )

    def register_instrument(self, metadata: InstrumentClassificationMetadata) -> None:
        """Register or update an instrument's classification metadata."""
        self._instruments[metadata.instrument_id] = metadata

    def get_instrument_metadata(self, instrument_id: str) -> Optional[InstrumentClassificationMetadata]:
        """Fetch classification metadata for an instrument ID."""
        return self._instruments.get(instrument_id)

    def register_fund_holdings(self, dataset: FundHoldingsDataset) -> None:
        """Register a fund's reported constituent holdings dataset."""
        self._funds[dataset.fund_instrument_id] = dataset

    def get_fund_holdings(self, fund_instrument_id: str) -> Optional[FundHoldingsDataset]:
        """Fetch constituent holdings for an ETF or fund."""
        return self._funds.get(fund_instrument_id)

    def resolve_geography(
        self,
        metadata: Optional[InstrumentClassificationMetadata],
        policy: GeographyPolicy,
    ) -> Tuple[str, str]:
        """Resolves country and region according to the chosen geographical policy."""
        if not metadata:
            return "Unknown Country", "Unknown Region"

        country = "Unknown Country"
        if policy == GeographyPolicy.ISSUER_DOMICILE:
            country = metadata.domicile_country or "Unknown Country"
        elif policy == GeographyPolicy.HEADQUARTERS:
            country = metadata.headquarters_country or metadata.domicile_country or "Unknown Country"
        elif policy == GeographyPolicy.LISTING_VENUE:
            country = metadata.listing_country or "Unknown Country"
        elif policy == GeographyPolicy.REVENUE_GEOGRAPHY:
            # When segment disclosures are unavailable, fall back to headquarters with explicit warning
            country = metadata.headquarters_country or metadata.domicile_country or "Unknown Country"

        region = COUNTRY_REGION_MAPPING.get(country, metadata.region or "Unknown Region")
        return country, region

