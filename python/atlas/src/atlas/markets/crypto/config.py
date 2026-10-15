"""Canonical Cryptocurrency Configuration for ATLAS Crypto Markets V1 (Stage 60).

Defines deterministic UUID5 identity namespaces, verified digital asset catalogs,
exchange/venue registries, and canonical spot trading pairs.
"""

import uuid
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CryptoAssetKindEnum(str, Enum):
    """Classification of digital asset."""

    COIN = "coin"
    TOKEN = "token"
    STABLECOIN = "stablecoin"
    WRAPPED = "wrapped"
    OTHER = "other"


class QuoteAssetTypeEnum(str, Enum):
    """Classification of quotation asset denomination."""

    FIAT = "fiat"
    STABLECOIN = "stablecoin"
    CRYPTO = "crypto"


class CryptoVenueConfig(BaseModel):
    """Metadata record for a verified cryptocurrency exchange/trading venue."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    venue_id: str = Field(..., min_length=2, max_length=32)
    name: str = Field(..., min_length=2, max_length=64)
    venue_type: str = Field(default="CENTRALIZED_EXCHANGE")
    jurisdiction: str = Field(..., max_length=64)


class CanonicalCryptoAssetConfig(BaseModel):
    """Configuration record for a canonical digital asset in ATLAS."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    asset_entity_id: UUID = Field(..., description="Canonical Digital Asset Entity UUID authority.")
    symbol: str = Field(..., min_length=1, max_length=16)
    name: str = Field(..., min_length=1, max_length=128)
    asset_kind: CryptoAssetKindEnum = Field(default=CryptoAssetKindEnum.COIN)
    network_id: Optional[str] = Field(default=None, max_length=64)
    contract_address: Optional[str] = Field(default=None, max_length=128)
    token_standard: Optional[str] = Field(default=None, max_length=32)
    decimals: int = Field(default=8, ge=0, le=18)
    description: str = Field(default="", max_length=512)


class CanonicalCryptoSpotMarketConfig(BaseModel):
    """Configuration record for a canonical exchange-aware crypto spot market."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    market_symbol: str = Field(..., description="Canonical BASE/QUOTE notation.")
    base_asset_symbol: str = Field(..., min_length=1, max_length=16)
    quote_asset_symbol: str = Field(..., min_length=1, max_length=16)
    quote_asset_type: QuoteAssetTypeEnum = Field(default=QuoteAssetTypeEnum.FIAT)
    venue_id: str = Field(..., min_length=2, max_length=32)
    venue_name: str = Field(..., min_length=2, max_length=64)
    venue_market_symbol: str = Field(..., min_length=2, max_length=32)
    market_type: str = Field(default="SPOT")
    price_precision: int = Field(default=2, ge=0, le=10)
    quantity_precision: int = Field(default=8, ge=0, le=18)
    min_quantity: Decimal = Field(default=Decimal("0.0001"))
    default_last_price: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_bid: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_ask: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_volume_24h_base: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_volume_24h_quote: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_change_24h_percent: Optional[Decimal] = None
    default_provider: str = Field(default="OPENBB")
    provider_aliases: List[str] = Field(default_factory=list)

    @field_validator("market_symbol")
    @classmethod
    def validate_market_symbol(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError(f"Market symbol '{v}' must be formatted as BASE/QUOTE.")
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError(f"Market symbol '{v}' must have exactly one slash separating assets.")
        return v.upper()


# Deterministic UUID5 namespaces
CRYPTO_ASSET_NAMESPACE = uuid.UUID("44444444-4444-6060-8888-000000000001")
CRYPTO_INSTRUMENT_NAMESPACE = uuid.UUID("44444444-4444-6060-8888-000000000002")


def generate_crypto_asset_uuid(symbol: str) -> UUID:
    """Generate deterministic UUID5 for a digital asset by canonical symbol."""
    return uuid.uuid5(CRYPTO_ASSET_NAMESPACE, f"CRYPTO_ASSET:{symbol.upper().strip()}")


def generate_crypto_instrument_uuid(venue: str, base: str, quote: str) -> UUID:
    """Generate deterministic UUID5 for a spot trading pair on a specific venue."""
    return uuid.uuid5(
        CRYPTO_INSTRUMENT_NAMESPACE,
        f"SPOT_CRYPTO:{venue.lower().strip()}:{base.upper().strip()}/{quote.upper().strip()}",
    )


# ─── 1. VERIFIED VENUES ──────────────────────────────────────────────────────────
DEFAULT_CRYPTO_VENUES: Dict[str, CryptoVenueConfig] = {
    "coinbase": CryptoVenueConfig(
        venue_id="coinbase",
        name="Coinbase",
        jurisdiction="United States",
    ),
    "binance": CryptoVenueConfig(
        venue_id="binance",
        name="Binance",
        jurisdiction="Global",
    ),
    "kraken": CryptoVenueConfig(
        venue_id="kraken",
        name="Kraken",
        jurisdiction="United States",
    ),
    "bitstamp": CryptoVenueConfig(
        venue_id="bitstamp",
        name="Bitstamp",
        jurisdiction="United Kingdom",
    ),
}


# ─── 2. CANONICAL DIGITAL ASSET CATALOG ─────────────────────────────────────────
DEFAULT_CRYPTO_ASSET_CATALOG: List[CanonicalCryptoAssetConfig] = [
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("BTC"),
        symbol="BTC",
        name="Bitcoin",
        asset_kind=CryptoAssetKindEnum.COIN,
        network_id="bitcoin",
        decimals=8,
        description="Decentralized peer-to-peer monetary network and store of value.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("ETH"),
        symbol="ETH",
        name="Ethereum",
        asset_kind=CryptoAssetKindEnum.COIN,
        network_id="ethereum",
        decimals=18,
        description="Smart contract platform and native gas asset of Ethereum.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("SOL"),
        symbol="SOL",
        name="Solana",
        asset_kind=CryptoAssetKindEnum.COIN,
        network_id="solana",
        decimals=9,
        description="High-throughput proof-of-history layer-1 blockchain.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("USDT"),
        symbol="USDT",
        name="Tether USD",
        asset_kind=CryptoAssetKindEnum.STABLECOIN,
        network_id="ethereum",
        contract_address="0xdac17f958d2ee523a2206206994597c13d831ec7",
        token_standard="ERC-20",
        decimals=6,
        description="Fiat-referenced stablecoin token issued by Tether.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("USDC"),
        symbol="USDC",
        name="USD Coin",
        asset_kind=CryptoAssetKindEnum.STABLECOIN,
        network_id="ethereum",
        contract_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        token_standard="ERC-20",
        decimals=6,
        description="Regulated fiat-backed stablecoin issued by Circle.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("WBTC"),
        symbol="WBTC",
        name="Wrapped Bitcoin",
        asset_kind=CryptoAssetKindEnum.WRAPPED,
        network_id="ethereum",
        contract_address="0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        token_standard="ERC-20",
        decimals=8,
        description="ERC-20 token backed 1:1 by Bitcoin custody reserves.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("AVAX"),
        symbol="AVAX",
        name="Avalanche",
        asset_kind=CryptoAssetKindEnum.COIN,
        network_id="avalanche",
        decimals=18,
        description="Layer-1 smart contract platform with Avalanche consensus.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("LINK"),
        symbol="LINK",
        name="Chainlink",
        asset_kind=CryptoAssetKindEnum.TOKEN,
        network_id="ethereum",
        contract_address="0x514910771af9ca656af840dff83e8264ecf986ca",
        token_standard="ERC-20",
        decimals=18,
        description="Decentralized oracle network connecting smart contracts to data.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("UNI"),
        symbol="UNI",
        name="Uniswap",
        asset_kind=CryptoAssetKindEnum.TOKEN,
        network_id="ethereum",
        contract_address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
        token_standard="ERC-20",
        decimals=18,
        description="Governance token for the Uniswap decentralized exchange protocol.",
    ),
    CanonicalCryptoAssetConfig(
        asset_entity_id=generate_crypto_asset_uuid("DOGE"),
        symbol="DOGE",
        name="Dogecoin",
        asset_kind=CryptoAssetKindEnum.COIN,
        network_id="dogecoin",
        decimals=8,
        description="Open-source peer-to-peer cryptocurrency based on Scrypt PoW.",
    ),
]


# ─── 3. CANONICAL CRYPTO SPOT MARKETS CATALOG ──────────────────────────────────
DEFAULT_CRYPTO_SPOT_CATALOG: List[CanonicalCryptoSpotMarketConfig] = [
    # Coinbase Spot Markets
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("coinbase", "BTC", "USD"),
        market_symbol="BTC/USD",
        base_asset_symbol="BTC",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="coinbase",
        venue_name="Coinbase",
        venue_market_symbol="BTC-USD",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.00001"),
        default_last_price=Decimal("67450.00"),
        default_bid=Decimal("67448.50"),
        default_ask=Decimal("67451.50"),
        default_volume_24h_base=Decimal("11200.50"),
        default_volume_24h_quote=Decimal("755473725.00"),
        default_change_24h_percent=Decimal("2.45"),
        provider_aliases=["BTC-USD", "BTCUSD", "COINBASE:BTC-USD"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("coinbase", "ETH", "USD"),
        market_symbol="ETH/USD",
        base_asset_symbol="ETH",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="coinbase",
        venue_name="Coinbase",
        venue_market_symbol="ETH-USD",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.0001"),
        default_last_price=Decimal("3520.00"),
        default_bid=Decimal("3519.20"),
        default_ask=Decimal("3520.80"),
        default_volume_24h_base=Decimal("65400.00"),
        default_volume_24h_quote=Decimal("230208000.00"),
        default_change_24h_percent=Decimal("1.80"),
        provider_aliases=["ETH-USD", "ETHUSD", "COINBASE:ETH-USD"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("coinbase", "SOL", "USD"),
        market_symbol="SOL/USD",
        base_asset_symbol="SOL",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="coinbase",
        venue_name="Coinbase",
        venue_market_symbol="SOL-USD",
        price_precision=2,
        quantity_precision=4,
        min_quantity=Decimal("0.01"),
        default_last_price=Decimal("182.50"),
        default_bid=Decimal("182.40"),
        default_ask=Decimal("182.60"),
        default_volume_24h_base=Decimal("320000.00"),
        default_volume_24h_quote=Decimal("58400000.00"),
        default_change_24h_percent=Decimal("4.20"),
        provider_aliases=["SOL-USD", "SOLUSD", "COINBASE:SOL-USD"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("coinbase", "AVAX", "USD"),
        market_symbol="AVAX/USD",
        base_asset_symbol="AVAX",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="coinbase",
        venue_name="Coinbase",
        venue_market_symbol="AVAX-USD",
        price_precision=2,
        quantity_precision=4,
        min_quantity=Decimal("0.01"),
        default_last_price=Decimal("34.80"),
        default_bid=Decimal("34.75"),
        default_ask=Decimal("34.85"),
        default_volume_24h_base=Decimal("450000.00"),
        default_volume_24h_quote=Decimal("15660000.00"),
        default_change_24h_percent=Decimal("-0.65"),
        provider_aliases=["AVAX-USD", "AVAXUSD", "COINBASE:AVAX-USD"],
    ),
    # Binance Spot Markets
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("binance", "BTC", "USDT"),
        market_symbol="BTC/USDT",
        base_asset_symbol="BTC",
        quote_asset_symbol="USDT",
        quote_asset_type=QuoteAssetTypeEnum.STABLECOIN,
        venue_id="binance",
        venue_name="Binance",
        venue_market_symbol="BTCUSDT",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.00001"),
        default_last_price=Decimal("67465.00"),
        default_bid=Decimal("67464.00"),
        default_ask=Decimal("67466.00"),
        default_volume_24h_base=Decimal("28400.00"),
        default_volume_24h_quote=Decimal("1916006000.00"),
        default_change_24h_percent=Decimal("2.48"),
        provider_aliases=["BTCUSDT", "BTC_USDT", "BINANCE:BTCUSDT"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("binance", "ETH", "USDT"),
        market_symbol="ETH/USDT",
        base_asset_symbol="ETH",
        quote_asset_symbol="USDT",
        quote_asset_type=QuoteAssetTypeEnum.STABLECOIN,
        venue_id="binance",
        venue_name="Binance",
        venue_market_symbol="ETHUSDT",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.0001"),
        default_last_price=Decimal("3522.50"),
        default_bid=Decimal("3522.00"),
        default_ask=Decimal("3523.00"),
        default_volume_24h_base=Decimal("145000.00"),
        default_volume_24h_quote=Decimal("510762500.00"),
        default_change_24h_percent=Decimal("1.85"),
        provider_aliases=["ETHUSDT", "ETH_USDT", "BINANCE:ETHUSDT"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("binance", "SOL", "USDT"),
        market_symbol="SOL/USDT",
        base_asset_symbol="SOL",
        quote_asset_symbol="USDT",
        quote_asset_type=QuoteAssetTypeEnum.STABLECOIN,
        venue_id="binance",
        venue_name="Binance",
        venue_market_symbol="SOLUSDT",
        price_precision=2,
        quantity_precision=4,
        min_quantity=Decimal("0.01"),
        default_last_price=Decimal("182.75"),
        default_bid=Decimal("182.70"),
        default_ask=Decimal("182.80"),
        default_volume_24h_base=Decimal("780000.00"),
        default_volume_24h_quote=Decimal("142545000.00"),
        default_change_24h_percent=Decimal("4.25"),
        provider_aliases=["SOLUSDT", "SOL_USDT", "BINANCE:SOLUSDT"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("binance", "ETH", "BTC"),
        market_symbol="ETH/BTC",
        base_asset_symbol="ETH",
        quote_asset_symbol="BTC",
        quote_asset_type=QuoteAssetTypeEnum.CRYPTO,
        venue_id="binance",
        venue_name="Binance",
        venue_market_symbol="ETHBTC",
        price_precision=6,
        quantity_precision=8,
        min_quantity=Decimal("0.001"),
        default_last_price=Decimal("0.052210"),
        default_bid=Decimal("0.052205"),
        default_ask=Decimal("0.052215"),
        default_volume_24h_base=Decimal("42000.00"),
        default_volume_24h_quote=Decimal("2192.82"),
        default_change_24h_percent=Decimal("-0.62"),
        provider_aliases=["ETHBTC", "ETH_BTC", "BINANCE:ETHBTC"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("binance", "LINK", "USDT"),
        market_symbol="LINK/USDT",
        base_asset_symbol="LINK",
        quote_asset_symbol="USDT",
        quote_asset_type=QuoteAssetTypeEnum.STABLECOIN,
        venue_id="binance",
        venue_name="Binance",
        venue_market_symbol="LINKUSDT",
        price_precision=3,
        quantity_precision=4,
        min_quantity=Decimal("0.1"),
        default_last_price=Decimal("14.850"),
        default_bid=Decimal("14.845"),
        default_ask=Decimal("14.855"),
        default_volume_24h_base=Decimal("1850000.00"),
        default_volume_24h_quote=Decimal("27472500.00"),
        default_change_24h_percent=Decimal("3.10"),
        provider_aliases=["LINKUSDT", "LINK_USDT", "BINANCE:LINKUSDT"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("binance", "DOGE", "USDT"),
        market_symbol="DOGE/USDT",
        base_asset_symbol="DOGE",
        quote_asset_symbol="USDT",
        quote_asset_type=QuoteAssetTypeEnum.STABLECOIN,
        venue_id="binance",
        venue_name="Binance",
        venue_market_symbol="DOGEUSDT",
        price_precision=5,
        quantity_precision=2,
        min_quantity=Decimal("1.0"),
        default_last_price=Decimal("0.14250"),
        default_bid=Decimal("0.14248"),
        default_ask=Decimal("0.14252"),
        default_volume_24h_base=Decimal("125000000.00"),
        default_volume_24h_quote=Decimal("17812500.00"),
        default_change_24h_percent=Decimal("5.40"),
        provider_aliases=["DOGEUSDT", "DOGE_USDT", "BINANCE:DOGEUSDT"],
    ),
    # Kraken Spot Markets
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("kraken", "BTC", "EUR"),
        market_symbol="BTC/EUR",
        base_asset_symbol="BTC",
        quote_asset_symbol="EUR",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="kraken",
        venue_name="Kraken",
        venue_market_symbol="XBT/EUR",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.00001"),
        default_last_price=Decimal("62150.00"),
        default_bid=Decimal("62145.00"),
        default_ask=Decimal("62155.00"),
        default_volume_24h_base=Decimal("4500.00"),
        default_volume_24h_quote=Decimal("279675000.00"),
        default_change_24h_percent=Decimal("2.10"),
        provider_aliases=["XBTEUR", "XBT/EUR", "BTC/EUR", "KRAKEN:XBTEUR"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("kraken", "ETH", "EUR"),
        market_symbol="ETH/EUR",
        base_asset_symbol="ETH",
        quote_asset_symbol="EUR",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="kraken",
        venue_name="Kraken",
        venue_market_symbol="ETH/EUR",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.0001"),
        default_last_price=Decimal("3245.00"),
        default_bid=Decimal("3243.50"),
        default_ask=Decimal("3246.50"),
        default_volume_24h_base=Decimal("18200.00"),
        default_volume_24h_quote=Decimal("59059000.00"),
        default_change_24h_percent=Decimal("1.55"),
        provider_aliases=["ETHEUR", "ETH/EUR", "KRAKEN:ETHEUR"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("kraken", "USDT", "USD"),
        market_symbol="USDT/USD",
        base_asset_symbol="USDT",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="kraken",
        venue_name="Kraken",
        venue_market_symbol="USDT/USD",
        price_precision=4,
        quantity_precision=2,
        min_quantity=Decimal("1.0"),
        default_last_price=Decimal("0.9998"),
        default_bid=Decimal("0.9997"),
        default_ask=Decimal("0.9999"),
        default_volume_24h_base=Decimal("52000000.00"),
        default_volume_24h_quote=Decimal("51989600.00"),
        default_change_24h_percent=Decimal("-0.02"),
        provider_aliases=["USDTUSD", "USDT/USD", "KRAKEN:USDTUSD"],
    ),
    # Bitstamp Spot Markets
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("bitstamp", "BTC", "USD"),
        market_symbol="BTC/USD",
        base_asset_symbol="BTC",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="bitstamp",
        venue_name="Bitstamp",
        venue_market_symbol="BTC/USD",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.00001"),
        default_last_price=Decimal("67440.00"),
        default_bid=Decimal("67435.00"),
        default_ask=Decimal("67445.00"),
        default_volume_24h_base=Decimal("2850.00"),
        default_volume_24h_quote=Decimal("192204000.00"),
        default_change_24h_percent=Decimal("2.42"),
        provider_aliases=["BTCUSD:BITSTAMP", "BITSTAMP:BTCUSD"],
    ),
    CanonicalCryptoSpotMarketConfig(
        instrument_entity_id=generate_crypto_instrument_uuid("bitstamp", "ETH", "USD"),
        market_symbol="ETH/USD",
        base_asset_symbol="ETH",
        quote_asset_symbol="USD",
        quote_asset_type=QuoteAssetTypeEnum.FIAT,
        venue_id="bitstamp",
        venue_name="Bitstamp",
        venue_market_symbol="ETH/USD",
        price_precision=2,
        quantity_precision=8,
        min_quantity=Decimal("0.0001"),
        default_last_price=Decimal("3518.50"),
        default_bid=Decimal("3517.00"),
        default_ask=Decimal("3520.00"),
        default_volume_24h_base=Decimal("12400.00"),
        default_volume_24h_quote=Decimal("43629400.00"),
        default_change_24h_percent=Decimal("1.76"),
        provider_aliases=["ETHUSD:BITSTAMP", "BITSTAMP:ETHUSD"],
    ),
]
