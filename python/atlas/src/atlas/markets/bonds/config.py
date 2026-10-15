"""Canonical Fixed-Income Configuration for ATLAS Bonds & Debt Markets V1 (Stage 61).

Defines deterministic UUID5 identity namespaces, verified issuers, canonical bond securities,
and fixed-income classification enums.
"""

import uuid
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BondTypeEnum(str, Enum):
    """Classification of fixed-income debt instrument."""

    SOVEREIGN = "sovereign"
    CORPORATE = "corporate"
    MUNICIPAL = "municipal"
    AGENCY = "agency"
    SUPRANATIONAL = "supranational"
    TREASURY_BILL = "treasury_bill"


class IssuerCategoryEnum(str, Enum):
    """Classification of legal debt issuer."""

    SOVEREIGN = "sovereign"
    CORPORATE = "corporate"
    MUNICIPAL = "municipal"
    AGENCY = "agency"
    SUPRANATIONAL = "supranational"


class CouponTypeEnum(str, Enum):
    """Contractual coupon structure."""

    FIXED = "fixed"
    FLOATING = "floating"
    ZERO_COUPON = "zero_coupon"
    STEP_UP = "step_up"
    INFLATION_LINKED = "inflation_linked"
    OTHER = "other"


class CouponFrequencyEnum(str, Enum):
    """Annual frequency of periodic coupon payments."""

    ANNUAL = "annual"
    SEMIANNUAL = "semiannual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    ZERO = "zero"


class PriceBasisEnum(str, Enum):
    """Price observation quotation basis."""

    CLEAN = "clean"
    DIRTY = "dirty"
    UNKNOWN = "unknown"


class PriceQuoteUnitEnum(str, Enum):
    """Quotation unit and scale of bond price."""

    PERCENTAGE_OF_PAR = "percentage_of_par"
    PRICE_PER_100_FACE = "price_per_100_face"
    ABSOLUTE_AMOUNT = "absolute_amount"


class PriceKindEnum(str, Enum):
    """Observed price methodology / execution status."""

    TRADE_PRICE = "trade_price"
    INDICATIVE_QUOTE = "indicative_quote"
    EVALUATED_PRICE = "evaluated_price"
    REFERENCE_PRICE = "reference_price"
    UNKNOWN = "unknown"


class YieldTypeEnum(str, Enum):
    """Classification of observed or reported yield metric."""

    YTM = "ytm"
    YTC = "ytc"
    YTW = "ytw"
    CURRENT_YIELD = "current_yield"
    DISCOUNT_YIELD = "discount_yield"
    UNKNOWN = "unknown"


class DayCountConventionEnum(str, Enum):
    """Day-count convention for accrued interest calculation."""

    ACT_ACT_ICMA = "ACT/ACT ICMA"
    THIRTY_360 = "30/360"
    ACT_360 = "ACT/360"
    ACT_365 = "ACT/365"
    UNKNOWN = "UNKNOWN"


class SeniorityEnum(str, Enum):
    """Debt seniority and capital structure ranking."""

    SENIOR_SECURED = "senior_secured"
    SENIOR_UNSECURED = "senior_unsecured"
    SUBORDINATED = "subordinated"
    JUNIOR = "junior"
    UNKNOWN = "unknown"


class MaturityBucketEnum(str, Enum):
    """Maturity time bucket approximation."""

    UNDER_1_YEAR = "under_1_year"
    ONE_TO_THREE_YEARS = "1_to_3_years"
    THREE_TO_FIVE_YEARS = "3_to_5_years"
    FIVE_TO_TEN_YEARS = "5_to_10_years"
    OVER_TEN_YEARS = "over_10_years"
    PERPETUAL = "perpetual"


class BondIssuerConfig(BaseModel):
    """Metadata record for a verified legal debt issuer in ATLAS."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer_entity_id: UUID = Field(..., description="Canonical Organization Entity UUID.")
    name: str = Field(..., min_length=2, max_length=128)
    issuer_category: IssuerCategoryEnum
    country_code: str = Field(..., min_length=2, max_length=8)
    jurisdiction: str = Field(..., min_length=2, max_length=64)
    description: str = Field(default="", max_length=512)


class CanonicalBondSecurityConfig(BaseModel):
    """Configuration record for a canonical bond security in ATLAS."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    symbol: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=2, max_length=128)
    isin: Optional[str] = Field(default=None, max_length=12)
    cusip: Optional[str] = Field(default=None, max_length=9)
    issuer_entity_id: UUID
    issuer_name: str = Field(..., min_length=2, max_length=128)
    issuer_category: IssuerCategoryEnum
    bond_type: BondTypeEnum
    currency: str = Field(..., min_length=3, max_length=3)
    issue_date: str = Field(..., description="YYYY-MM-DD issue date.")
    dated_date: Optional[str] = Field(default=None, description="Accrual start date.")
    maturity_date: Optional[str] = Field(default=None, description="Contractual maturity date.")
    is_perpetual: bool = Field(default=False)
    coupon_type: CouponTypeEnum
    coupon_rate: Optional[Decimal] = Field(
        default=None, description="Contractual annual coupon percentage (e.g. 4.25 for 4.25%)."
    )
    coupon_frequency: CouponFrequencyEnum = Field(default=CouponFrequencyEnum.SEMIANNUAL)
    day_count_convention: DayCountConventionEnum = Field(default=DayCountConventionEnum.THIRTY_360)
    face_value: Decimal = Field(default=Decimal("100.00"), ge=Decimal("0.01"))
    face_value_convention: str = Field(default="PER_100_FACE", max_length=32)
    seniority: SeniorityEnum = Field(default=SeniorityEnum.SENIOR_UNSECURED)
    is_callable: bool = Field(default=False)
    is_putable: bool = Field(default=False)
    reference_index: Optional[str] = Field(default=None, max_length=32)
    floating_margin_bps: Optional[Decimal] = None
    default_clean_price: Optional[Decimal] = None
    default_dirty_price: Optional[Decimal] = None
    default_accrued_interest: Optional[Decimal] = None
    default_price_basis: PriceBasisEnum = Field(default=PriceBasisEnum.CLEAN)
    default_quote_unit: PriceQuoteUnitEnum = Field(default=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR)
    default_price_kind: PriceKindEnum = Field(default=PriceKindEnum.EVALUATED_PRICE)
    default_bid: Optional[Decimal] = None
    default_ask: Optional[Decimal] = None
    default_yield_value: Optional[Decimal] = None
    default_yield_type: YieldTypeEnum = Field(default=YieldTypeEnum.YTM)
    default_price_change_24h: Optional[Decimal] = None
    default_yield_change_bps_24h: Optional[Decimal] = None
    default_provider: str = Field(default="OPENBB")
    provider_series_id: str = Field(..., max_length=64)


# Deterministic UUID5 namespaces
BOND_ISSUER_NAMESPACE = uuid.UUID("e3b0c442-98fc-1c14-9afb-4c729938e21a")
BOND_INSTRUMENT_NAMESPACE = uuid.UUID("d4c3b2a1-0e9f-8a7b-6c5d-4e3f2a1b0c9d")


def generate_issuer_id(key: str) -> UUID:
    """Generate a deterministic UUID5 for a bond issuer."""
    return uuid.uuid5(BOND_ISSUER_NAMESPACE, key.upper())


def generate_bond_id(isin_or_symbol: str) -> UUID:
    """Generate a deterministic UUID5 for a canonical bond security."""
    return uuid.uuid5(BOND_INSTRUMENT_NAMESPACE, isin_or_symbol.upper())


# Verified Legal Debt Issuers
ISSUER_US_TREASURY_ID = generate_issuer_id("US_TREASURY")
ISSUER_UK_DMO_ID = generate_issuer_id("UK_DMO")
ISSUER_GERMANY_FINANCE_ID = generate_issuer_id("GERMANY_FINANCE_AGENCY")
ISSUER_JAPAN_MOF_ID = generate_issuer_id("JAPAN_MOF")
ISSUER_APPLE_ID = generate_issuer_id("APPLE_INC")
ISSUER_MICROSOFT_ID = generate_issuer_id("MICROSOFT_CORP")
ISSUER_JPMORGAN_ID = generate_issuer_id("JPMORGAN_CHASE")
ISSUER_PFIZER_ID = generate_issuer_id("PFIZER_INC")
ISSUER_EIB_ID = generate_issuer_id("EUROPEAN_INVESTMENT_BANK")
ISSUER_WORLD_BANK_ID = generate_issuer_id("WORLD_BANK_IBRD")
ISSUER_ENEL_ID = generate_issuer_id("ENEL_FINANCE")

CANONICAL_BOND_ISSUERS: Dict[UUID, BondIssuerConfig] = {
    ISSUER_US_TREASURY_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_US_TREASURY_ID,
        name="United States Department of the Treasury",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        country_code="USA",
        jurisdiction="United States",
        description="Executive agency responsible for issuing United States sovereign debt.",
    ),
    ISSUER_UK_DMO_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_UK_DMO_ID,
        name="United Kingdom Debt Management Office",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        country_code="GBR",
        jurisdiction="United Kingdom",
        description="Executive agency of HM Treasury responsible for UK Government Gilt issuance.",
    ),
    ISSUER_GERMANY_FINANCE_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_GERMANY_FINANCE_ID,
        name="Federal Republic of Germany (Finanzagentur)",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        country_code="DEU",
        jurisdiction="Germany",
        description="Central service provider for the Federal Republic of Germany's borrowing.",
    ),
    ISSUER_JAPAN_MOF_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_JAPAN_MOF_ID,
        name="Ministry of Finance Japan",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        country_code="JPN",
        jurisdiction="Japan",
        description="Cabinet-level ministry responsible for Japanese Government Bond (JGB) issues.",
    ),
    ISSUER_APPLE_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_APPLE_ID,
        name="Apple Inc.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        country_code="USA",
        jurisdiction="United States",
        description="Global consumer electronics and enterprise technology hardware leader.",
    ),
    ISSUER_MICROSOFT_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_MICROSOFT_ID,
        name="Microsoft Corporation",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        country_code="USA",
        jurisdiction="United States",
        description="Global enterprise cloud, software, and developer technology leader.",
    ),
    ISSUER_JPMORGAN_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_JPMORGAN_ID,
        name="JPMorgan Chase & Co.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        country_code="USA",
        jurisdiction="United States",
        description="Global financial services holding company and institutional investment bank.",
    ),
    ISSUER_PFIZER_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_PFIZER_ID,
        name="Pfizer Inc.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        country_code="USA",
        jurisdiction="United States",
        description="Multinational pharmaceutical and biomedical research leader.",
    ),
    ISSUER_EIB_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_EIB_ID,
        name="European Investment Bank",
        issuer_category=IssuerCategoryEnum.SUPRANATIONAL,
        country_code="EU",
        jurisdiction="European Union",
        description="Lending arm of the European Union financing sustainable investments.",
    ),
    ISSUER_WORLD_BANK_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_WORLD_BANK_ID,
        name="International Bank for Reconstruction and Development (World Bank)",
        issuer_category=IssuerCategoryEnum.SUPRANATIONAL,
        country_code="IBRD",
        jurisdiction="Global",
        description="International financial institution offering loans to middle-income nations.",
    ),
    ISSUER_ENEL_ID: BondIssuerConfig(
        issuer_entity_id=ISSUER_ENEL_ID,
        name="Enel Finance International N.V.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        country_code="NLD",
        jurisdiction="Netherlands / Italy",
        description="Financing vehicle for Enel S.p.A., multinational electric utility leader.",
    ),
}

# Verified Canonical Bond Catalog (16 securities across Sovereign, Corporate, Supra, T-Bill, Perp)
CANONICAL_BOND_SECURITIES: List[CanonicalBondSecurityConfig] = [
    # US Treasury 5-Year Benchmark Note
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US91282CJZ72"),
        symbol="UST 4.250 02/15/29",
        name="US Treasury Note 4.250% 15-Feb-2029",
        isin="US91282CJZ72",
        cusip="91282CJZ7",
        issuer_entity_id=ISSUER_US_TREASURY_ID,
        issuer_name="United States Department of the Treasury",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="USD",
        issue_date="2024-02-15",
        dated_date="2024-02-15",
        maturity_date="2029-02-15",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.2500"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("99.4500"),
        default_dirty_price=Decimal("100.1583"),
        default_accrued_interest=Decimal("0.7083"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("99.4375"),
        default_ask=Decimal("99.4625"),
        default_yield_value=Decimal("4.3750"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.1250"),
        default_yield_change_bps_24h=Decimal("2.8"),
        default_provider="OPENBB",
        provider_series_id="UST_5Y_2029_02",
    ),
    # US Treasury 10-Year Benchmark Bond
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US912810TW43"),
        symbol="UST 4.500 02/15/34",
        name="US Treasury Bond 4.500% 15-Feb-2034",
        isin="US912810TW43",
        cusip="912810TW4",
        issuer_entity_id=ISSUER_US_TREASURY_ID,
        issuer_name="United States Department of the Treasury",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="USD",
        issue_date="2024-02-15",
        dated_date="2024-02-15",
        maturity_date="2034-02-15",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.5000"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("101.1250"),
        default_dirty_price=Decimal("101.8750"),
        default_accrued_interest=Decimal("0.7500"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("101.1094"),
        default_ask=Decimal("101.1406"),
        default_yield_value=Decimal("4.3520"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.1875"),
        default_yield_change_bps_24h=Decimal("3.1"),
        default_provider="OPENBB",
        provider_series_id="UST_10Y_2034_02",
    ),
    # US Treasury 30-Year Long Bond
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US912810TY09"),
        symbol="UST 4.750 11/15/53",
        name="US Treasury Bond 4.750% 15-Nov-2053",
        isin="US912810TY09",
        cusip="912810TY0",
        issuer_entity_id=ISSUER_US_TREASURY_ID,
        issuer_name="United States Department of the Treasury",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="USD",
        issue_date="2023-11-15",
        dated_date="2023-11-15",
        maturity_date="2053-11-15",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.7500"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("102.8000"),
        default_dirty_price=Decimal("104.7792"),
        default_accrued_interest=Decimal("1.9792"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("102.7500"),
        default_ask=Decimal("102.8500"),
        default_yield_value=Decimal("4.5780"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.3500"),
        default_yield_change_bps_24h=Decimal("4.2"),
        default_provider="OPENBB",
        provider_series_id="UST_30Y_2053_11",
    ),
    # US Treasury Bill (Discount / Zero-Coupon Money Market)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US912797HR81"),
        symbol="USTB 0.000 08/15/24",
        name="US Treasury Bill 0.000% 15-Aug-2024",
        isin="US912797HR81",
        cusip="912797HR8",
        issuer_entity_id=ISSUER_US_TREASURY_ID,
        issuer_name="United States Department of the Treasury",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.TREASURY_BILL,
        currency="USD",
        issue_date="2024-02-15",
        dated_date="2024-02-15",
        maturity_date="2024-08-15",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.ZERO_COUPON,
        coupon_rate=Decimal("0.0000"),
        coupon_frequency=CouponFrequencyEnum.ZERO,
        day_count_convention=DayCountConventionEnum.ACT_360,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("97.4100"),
        default_dirty_price=Decimal("97.4100"),
        default_accrued_interest=Decimal("0.0000"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.REFERENCE_PRICE,
        default_bid=Decimal("97.4000"),
        default_ask=Decimal("97.4200"),
        default_yield_value=Decimal("5.2200"),
        default_yield_type=YieldTypeEnum.DISCOUNT_YIELD,
        default_price_change_24h=Decimal("0.0200"),
        default_yield_change_bps_24h=Decimal("-1.5"),
        default_provider="OPENBB",
        provider_series_id="USTB_6M_2024_08",
    ),
    # UK 5-Year Gilt
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("GB00BQC4DT01"),
        symbol="UKT 3.750 10/22/28",
        name="United Kingdom Gilt 3.750% 22-Oct-2028",
        isin="GB00BQC4DT01",
        issuer_entity_id=ISSUER_UK_DMO_ID,
        issuer_name="United Kingdom Debt Management Office",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="GBP",
        issue_date="2023-10-22",
        dated_date="2023-10-22",
        maturity_date="2028-10-22",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("3.7500"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("98.6000"),
        default_dirty_price=Decimal("99.2250"),
        default_accrued_interest=Decimal("0.6250"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("98.5500"),
        default_ask=Decimal("98.6500"),
        default_yield_value=Decimal("4.0840"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("0.1500"),
        default_yield_change_bps_24h=Decimal("-3.5"),
        default_provider="OPENBB",
        provider_series_id="GILT_5Y_2028_10",
    ),
    # UK 10-Year Gilt
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("GB00BM8Z2S21"),
        symbol="UKT 4.250 06/07/32",
        name="United Kingdom Gilt 4.250% 07-Jun-2032",
        isin="GB00BM8Z2S21",
        issuer_entity_id=ISSUER_UK_DMO_ID,
        issuer_name="United Kingdom Debt Management Office",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="GBP",
        issue_date="2022-06-07",
        dated_date="2022-06-07",
        maturity_date="2032-06-07",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.2500"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("100.2000"),
        default_dirty_price=Decimal("101.2625"),
        default_accrued_interest=Decimal("1.0625"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("100.1500"),
        default_ask=Decimal("100.2500"),
        default_yield_value=Decimal("4.2180"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("0.0800"),
        default_yield_change_bps_24h=Decimal("-1.8"),
        default_provider="OPENBB",
        provider_series_id="GILT_10Y_2032_06",
    ),
    # Germany 10-Year Federal Bond (Bund)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("DE000BU2Z007"),
        symbol="DBR 2.200 02/15/34",
        name="German Federal Republic Bund 2.200% 15-Feb-2034",
        isin="DE000BU2Z007",
        issuer_entity_id=ISSUER_GERMANY_FINANCE_ID,
        issuer_name="Federal Republic of Germany (Finanzagentur)",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="EUR",
        issue_date="2024-02-15",
        dated_date="2024-02-15",
        maturity_date="2034-02-15",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("2.2000"),
        coupon_frequency=CouponFrequencyEnum.ANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("98.9000"),
        default_dirty_price=Decimal("99.4500"),
        default_accrued_interest=Decimal("0.5500"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("98.8800"),
        default_ask=Decimal("98.9200"),
        default_yield_value=Decimal("2.3320"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.0500"),
        default_yield_change_bps_24h=Decimal("0.6"),
        default_provider="OPENBB",
        provider_series_id="BUND_10Y_2034_02",
    ),
    # Germany Green Bund (Zero-Coupon Sovereign)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("DE0001030708"),
        symbol="DBR 0.000 08/15/30",
        name="German Federal Republic Green Bund 0.000% 15-Aug-2030",
        isin="DE0001030708",
        issuer_entity_id=ISSUER_GERMANY_FINANCE_ID,
        issuer_name="Federal Republic of Germany (Finanzagentur)",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="EUR",
        issue_date="2020-09-02",
        dated_date="2020-08-15",
        maturity_date="2030-08-15",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.ZERO_COUPON,
        coupon_rate=Decimal("0.0000"),
        coupon_frequency=CouponFrequencyEnum.ZERO,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("87.4500"),
        default_dirty_price=Decimal("87.4500"),
        default_accrued_interest=Decimal("0.0000"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.EVALUATED_PRICE,
        default_bid=Decimal("87.4000"),
        default_ask=Decimal("87.5000"),
        default_yield_value=Decimal("2.1950"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.1000"),
        default_yield_change_bps_24h=Decimal("1.2"),
        default_provider="OPENBB",
        provider_series_id="BUND_GREEN_2030_08",
    ),
    # Japan 10-Year Government Bond (JGB)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("JP1103741P42"),
        symbol="JGB 0.800 03/20/34",
        name="Japan Government 10Y Bond 0.800% 20-Mar-2034",
        isin="JP1103741P42",
        issuer_entity_id=ISSUER_JAPAN_MOF_ID,
        issuer_name="Ministry of Finance Japan",
        issuer_category=IssuerCategoryEnum.SOVEREIGN,
        bond_type=BondTypeEnum.SOVEREIGN,
        currency="JPY",
        issue_date="2024-03-20",
        dated_date="2024-03-20",
        maturity_date="2034-03-20",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("0.8000"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_365,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("99.8500"),
        default_dirty_price=Decimal("100.1833"),
        default_accrued_interest=Decimal("0.3333"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.TRADE_PRICE,
        default_bid=Decimal("99.8200"),
        default_ask=Decimal("99.8800"),
        default_yield_value=Decimal("0.8160"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("0.0500"),
        default_yield_change_bps_24h=Decimal("-0.5"),
        default_provider="OPENBB",
        provider_series_id="JGB_10Y_2034_03",
    ),
    # Apple Inc. Corporate Senior Unsecured Bond (30Y)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US037833BY77"),
        symbol="AAPL 3.850 08/04/46",
        name="Apple Inc. Senior Notes 3.850% 04-Aug-2046",
        isin="US037833BY77",
        cusip="037833BY7",
        issuer_entity_id=ISSUER_APPLE_ID,
        issuer_name="Apple Inc.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        bond_type=BondTypeEnum.CORPORATE,
        currency="USD",
        issue_date="2016-08-04",
        dated_date="2016-08-04",
        maturity_date="2046-08-04",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("3.8500"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.THIRTY_360,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=True,
        is_putable=False,
        default_clean_price=Decimal("84.5000"),
        default_dirty_price=Decimal("85.2700"),
        default_accrued_interest=Decimal("0.7700"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.EVALUATED_PRICE,
        default_bid=Decimal("84.3500"),
        default_ask=Decimal("84.6500"),
        default_yield_value=Decimal("4.9540"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.2200"),
        default_yield_change_bps_24h=Decimal("2.1"),
        default_provider="OPENBB",
        provider_series_id="AAPL_2046_08",
    ),
    # Microsoft Corp. Corporate Senior Unsecured Bond (3Y)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US594918BY93"),
        symbol="MSFT 3.300 02/06/27",
        name="Microsoft Corp. Senior Notes 3.300% 06-Feb-2027",
        isin="US594918BY93",
        cusip="594918BY9",
        issuer_entity_id=ISSUER_MICROSOFT_ID,
        issuer_name="Microsoft Corporation",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        bond_type=BondTypeEnum.CORPORATE,
        currency="USD",
        issue_date="2017-02-06",
        dated_date="2017-02-06",
        maturity_date="2027-02-06",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("3.3000"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.THIRTY_360,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=True,
        is_putable=False,
        default_clean_price=Decimal("97.4000"),
        default_dirty_price=Decimal("98.0050"),
        default_accrued_interest=Decimal("0.6050"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.EVALUATED_PRICE,
        default_bid=Decimal("97.3000"),
        default_ask=Decimal("97.5000"),
        default_yield_value=Decimal("4.4520"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("0.0500"),
        default_yield_change_bps_24h=Decimal("-1.2"),
        default_provider="OPENBB",
        provider_series_id="MSFT_2027_02",
    ),
    # JPMorgan Chase Fixed-to-Floating Rate Senior Note
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US46647PBV96"),
        symbol="JPM 4.323 04/26/28",
        name="JPMorgan Chase & Co. Fixed-to-Float Notes 4.323% 26-Apr-2028",
        isin="US46647PBV96",
        cusip="46647PBV9",
        issuer_entity_id=ISSUER_JPMORGAN_ID,
        issuer_name="JPMorgan Chase & Co.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        bond_type=BondTypeEnum.CORPORATE,
        currency="USD",
        issue_date="2022-04-26",
        dated_date="2022-04-26",
        maturity_date="2028-04-26",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.3230"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.THIRTY_360,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=True,
        is_putable=False,
        reference_index="SOFR",
        floating_margin_bps=Decimal("156.0"),
        default_clean_price=Decimal("98.7500"),
        default_dirty_price=Decimal("99.5130"),
        default_accrued_interest=Decimal("0.7630"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.EVALUATED_PRICE,
        default_bid=Decimal("98.6500"),
        default_ask=Decimal("98.8500"),
        default_yield_value=Decimal("4.6980"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.1000"),
        default_yield_change_bps_24h=Decimal("1.8"),
        default_provider="OPENBB",
        provider_series_id="JPM_2028_04",
    ),
    # Pfizer Inc. Senior Corporate Bond (10Y)
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US717081EY87"),
        symbol="PFE 4.750 05/19/33",
        name="Pfizer Inc. Senior Notes 4.750% 19-May-2033",
        isin="US717081EY87",
        cusip="717081EY8",
        issuer_entity_id=ISSUER_PFIZER_ID,
        issuer_name="Pfizer Inc.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        bond_type=BondTypeEnum.CORPORATE,
        currency="USD",
        issue_date="2023-05-19",
        dated_date="2023-05-19",
        maturity_date="2033-05-19",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.7500"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.THIRTY_360,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=True,
        is_putable=False,
        default_clean_price=Decimal("98.1000"),
        default_dirty_price=Decimal("99.0229"),
        default_accrued_interest=Decimal("0.9229"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.EVALUATED_PRICE,
        default_bid=Decimal("97.9800"),
        default_ask=Decimal("98.2200"),
        default_yield_value=Decimal("5.0210"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("-0.1500"),
        default_yield_change_bps_24h=Decimal("2.4"),
        default_provider="OPENBB",
        provider_series_id="PFE_2033_05",
    ),
    # European Investment Bank (EIB) Supranational Benchmark EARN
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("LU1824424706"),
        symbol="EIB 2.750 07/28/28",
        name="European Investment Bank EARN 2.750% 28-Jul-2028",
        isin="LU1824424706",
        issuer_entity_id=ISSUER_EIB_ID,
        issuer_name="European Investment Bank",
        issuer_category=IssuerCategoryEnum.SUPRANATIONAL,
        bond_type=BondTypeEnum.SUPRANATIONAL,
        currency="EUR",
        issue_date="2023-07-28",
        dated_date="2023-07-28",
        maturity_date="2028-07-28",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("2.7500"),
        coupon_frequency=CouponFrequencyEnum.ANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("100.1000"),
        default_dirty_price=Decimal("100.6875"),
        default_accrued_interest=Decimal("0.5875"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.INDICATIVE_QUOTE,
        default_bid=Decimal("100.0500"),
        default_ask=Decimal("100.1500"),
        default_yield_value=Decimal("2.7210"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("0.0400"),
        default_yield_change_bps_24h=Decimal("-1.0"),
        default_provider="OPENBB",
        provider_series_id="EIB_2028_07",
    ),
    # World Bank (IBRD) Sustainable Development Bond
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("US459058JW79"),
        symbol="IBRD 4.000 01/24/29",
        name="World Bank (IBRD) Sustainable Dev Notes 4.000% 24-Jan-2029",
        isin="US459058JW79",
        cusip="459058JW7",
        issuer_entity_id=ISSUER_WORLD_BANK_ID,
        issuer_name="International Bank for Reconstruction and Development (World Bank)",
        issuer_category=IssuerCategoryEnum.SUPRANATIONAL,
        bond_type=BondTypeEnum.SUPRANATIONAL,
        currency="USD",
        issue_date="2024-01-24",
        dated_date="2024-01-24",
        maturity_date="2029-01-24",
        is_perpetual=False,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("4.0000"),
        coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
        day_count_convention=DayCountConventionEnum.THIRTY_360,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SENIOR_UNSECURED,
        is_callable=False,
        is_putable=False,
        default_clean_price=Decimal("99.6000"),
        default_dirty_price=Decimal("100.2667"),
        default_accrued_interest=Decimal("0.6667"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR,
        default_price_kind=PriceKindEnum.INDICATIVE_QUOTE,
        default_bid=Decimal("99.5500"),
        default_ask=Decimal("99.6500"),
        default_yield_value=Decimal("4.0950"),
        default_yield_type=YieldTypeEnum.YTM,
        default_price_change_24h=Decimal("0.0200"),
        default_yield_change_bps_24h=Decimal("-0.8"),
        default_provider="OPENBB",
        provider_series_id="IBRD_2029_01",
    ),
    # Enel Corporate Subordinated Perpetual Hybrid Bond
    CanonicalBondSecurityConfig(
        instrument_entity_id=generate_bond_id("XS2314246521"),
        symbol="ENEL 6.375 PERP",
        name="Enel Finance International Subordinated Perpetual Hybrid 6.375%",
        isin="XS2314246521",
        issuer_entity_id=ISSUER_ENEL_ID,
        issuer_name="Enel Finance International N.V.",
        issuer_category=IssuerCategoryEnum.CORPORATE,
        bond_type=BondTypeEnum.CORPORATE,
        currency="EUR",
        issue_date="2021-03-10",
        dated_date="2021-03-10",
        maturity_date=None,
        is_perpetual=True,
        coupon_type=CouponTypeEnum.FIXED,
        coupon_rate=Decimal("6.3750"),
        coupon_frequency=CouponFrequencyEnum.ANNUAL,
        day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
        face_value=Decimal("100.00"),
        face_value_convention="PER_100_FACE",
        seniority=SeniorityEnum.SUBORDINATED,
        is_callable=True,
        is_putable=False,
        default_clean_price=Decimal("97.5000"),
        default_dirty_price=Decimal("99.1250"),
        default_accrued_interest=Decimal("1.6250"),
        default_price_basis=PriceBasisEnum.CLEAN,
        default_quote_unit=PriceQuoteUnitEnum.PRICE_PER_100_FACE,
        default_price_kind=PriceKindEnum.EVALUATED_PRICE,
        default_bid=Decimal("97.2500"),
        default_ask=Decimal("97.7500"),
        default_yield_value=Decimal("6.5520"),
        default_yield_type=YieldTypeEnum.YTC,
        default_price_change_24h=Decimal("-0.3000"),
        default_yield_change_bps_24h=Decimal("3.8"),
        default_provider="OPENBB",
        provider_series_id="ENEL_HYBRID_PERP",
    ),
]
