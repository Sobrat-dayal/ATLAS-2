from enum import StrEnum


class EquityKind(StrEnum):
    COMMON = "common"
    PREFERRED = "preferred"
    DEPOSITARY_RECEIPT = "depositary_receipt"
    OTHER = "other"


class ETFReplicationMethod(StrEnum):
    PHYSICAL_FULL = "physical_full"
    PHYSICAL_SAMPLING = "physical_sampling"
    SYNTHETIC = "synthetic"
    OTHER = "other"


class DistributionPolicy(StrEnum):
    ACCUMULATING = "accumulating"
    DISTRIBUTING = "distributing"
    MIXED = "mixed"
    OTHER = "other"


class BondCouponType(StrEnum):
    FIXED = "fixed"
    FLOATING = "floating"
    ZERO = "zero"
    VARIABLE = "variable"
    OTHER = "other"


class OptionRight(StrEnum):
    CALL = "call"
    PUT = "put"


class ExerciseStyle(StrEnum):
    AMERICAN = "american"
    EUROPEAN = "european"
    BERMUDAN = "bermudan"
    OTHER = "other"


class SettlementType(StrEnum):
    PHYSICAL = "physical"
    CASH = "cash"
    OTHER = "other"


class FundKind(StrEnum):
    MUTUAL_FUND = "mutual_fund"
    CLOSED_END_FUND = "closed_end_fund"
    MONEY_MARKET_FUND = "money_market_fund"
    UNIT_TRUST = "unit_trust"
    OTHER = "other"


class CryptoAssetKind(StrEnum):
    COIN = "coin"
    TOKEN = "token"
    STABLECOIN = "stablecoin"
    WRAPPED = "wrapped"
    OTHER = "other"


class CurrencyKind(StrEnum):
    FIAT = "fiat"
    SUPRANATIONAL = "supranational"
    OTHER = "other"


class CommodityCategory(StrEnum):
    ENERGY = "energy"
    METAL = "metal"
    AGRICULTURE = "agriculture"
    LIVESTOCK = "livestock"
    SOFT = "soft"
    OTHER = "other"


class MarketIndexKind(StrEnum):
    PRICE = "price"
    TOTAL_RETURN = "total_return"
    NET_TOTAL_RETURN = "net_total_return"
    VOLATILITY = "volatility"
    FIXED_INCOME = "fixed_income"
    STRATEGY = "strategy"
    OTHER = "other"
