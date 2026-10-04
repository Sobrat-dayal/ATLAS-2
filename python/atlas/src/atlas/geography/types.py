from enum import StrEnum


class CountryKind(StrEnum):
    SOVEREIGN_STATE = "sovereign_state"
    TERRITORY = "territory"
    DEPENDENCY = "dependency"
    DISPUTED = "disputed"
    OTHER = "other"


class PortKind(StrEnum):
    SEAPORT = "seaport"
    RIVER_PORT = "river_port"
    INLAND_PORT = "inland_port"
    DRY_PORT = "dry_port"
    MIXED = "mixed"
    OTHER = "other"


class AirportKind(StrEnum):
    COMMERCIAL = "commercial"
    GENERAL_AVIATION = "general_aviation"
    CARGO = "cargo"
    MILITARY = "military"
    MIXED = "mixed"
    OTHER = "other"


class ExchangeKind(StrEnum):
    STOCK_EXCHANGE = "stock_exchange"
    DERIVATIVES_EXCHANGE = "derivatives_exchange"
    COMMODITY_EXCHANGE = "commodity_exchange"
    CRYPTO_EXCHANGE = "crypto_exchange"
    ELECTRONIC_VENUE = "electronic_venue"
    OTC_VENUE = "otc_venue"
    OTHER = "other"
