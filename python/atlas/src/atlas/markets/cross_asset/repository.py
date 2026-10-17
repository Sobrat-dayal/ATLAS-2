"""Repository for ATLAS Cross-Asset Markets V1 (Stage 65).

Provides canonical multi-asset market observations spanning Equities, ETFs, FX,
Cryptocurrency, Sovereign Debt / Bonds, and Exchange-Traded Futures.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID, uuid5

from .config import (
    AssetClassEnum,
    CrossAssetWindow,
    NativeMetricKind,
    ProxyKind,
)

CROSS_ASSET_NAMESPACE = UUID("65656565-6565-5656-a656-000000000001")


def _gen_instrument_id(symbol: str) -> UUID:
    """Generate deterministic UUID for cross-asset canonical instruments."""
    return uuid5(CROSS_ASSET_NAMESPACE, f"instrument:{symbol.upper()}")


class CandidateMarketData:
    """Raw candidate market observation package for a cross-asset instrument."""

    def __init__(
        self,
        symbol: str,
        display_name: str,
        asset_class: AssetClassEnum,
        market_or_venue: str,
        market_series_identity: str,
        quote_currency: str,
        quote_unit: str,
        native_metric_kind: NativeMetricKind,
        native_display_label: str,
        native_unit: str,
        current_value: Decimal,
        reference_value: Optional[Decimal],
        change_value: Optional[Decimal],
        change_percent: Optional[Decimal],
        as_of_time: datetime,
        session_status: str = "OPEN",
        is_benchmark: bool = False,
        is_proxy: bool = False,
        proxy_kind: ProxyKind = ProxyKind.NONE,
        proxy_benchmark_target: Optional[str] = None,
        freshness_status: str = "FRESH",
        is_delayed: bool = False,
        delay_minutes: int = 0,
        provider: str = "CANONICAL_FEED",
        # Window-specific price references for aligned mode
        window_start_prices: Optional[Dict[CrossAssetWindow, Decimal]] = None,
        window_start_offsets_sec: Optional[Dict[CrossAssetWindow, int]] = None,
        is_price_series: bool = True,
    ):
        self.instrument_entity_id = _gen_instrument_id(symbol)
        self.symbol = symbol
        self.display_name = display_name
        self.asset_class = asset_class
        self.market_or_venue = market_or_venue
        self.market_series_identity = market_series_identity
        self.quote_currency = quote_currency
        self.quote_unit = quote_unit
        self.native_metric_kind = native_metric_kind
        self.native_display_label = native_display_label
        self.native_unit = native_unit
        self.current_value = current_value
        self.reference_value = reference_value
        self.change_value = change_value
        self.change_percent = change_percent
        self.as_of_time = as_of_time
        self.session_status = session_status
        self.is_benchmark = is_benchmark
        self.is_proxy = is_proxy
        self.proxy_kind = proxy_kind
        self.proxy_benchmark_target = proxy_benchmark_target
        self.freshness_status = freshness_status
        self.is_delayed = is_delayed
        self.delay_minutes = delay_minutes
        self.provider = provider
        self.window_start_prices = window_start_prices or {}
        self.window_start_offsets_sec = window_start_offsets_sec or {}
        self.is_price_series = is_price_series


class CrossAssetMarketRepository:
    """Repository retrieving canonical cross-asset observations."""

    def __init__(self, anchor_time: Optional[datetime] = None) -> None:
        # Canonical anchor instant in UTC
        self._anchor_time = anchor_time or datetime(2026, 10, 17, 18, 0, 0, tzinfo=timezone.utc)

    def get_candidate_catalog(self) -> Dict[str, CandidateMarketData]:
        """Returns the canonical catalog of multi-asset market observations."""
        now = self._anchor_time

        catalog: Dict[str, CandidateMarketData] = {
            # 1. Equities
            "AAPL": CandidateMarketData(
                symbol="AAPL",
                display_name="Apple Inc.",
                asset_class=AssetClassEnum.EQUITIES,
                market_or_venue="NASDAQ",
                market_series_identity="NASDAQ:AAPL",
                quote_currency="USD",
                quote_unit="USD/share",
                native_metric_kind=NativeMetricKind.EQUITY_PRICE_CHANGE,
                native_display_label="Price Change vs Prev Close",
                native_unit="%",
                current_value=Decimal("234.85"),
                reference_value=Decimal("231.50"),
                change_value=Decimal("3.35"),
                change_percent=Decimal("1.4471"),
                as_of_time=now - timedelta(minutes=5),
                session_status="OPEN",
                is_benchmark=False,
                is_proxy=False,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("231.50"),
                    CrossAssetWindow.LAST_7D: Decimal("227.10"),
                    CrossAssetWindow.LAST_30D: Decimal("220.40"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 120,
                    CrossAssetWindow.LAST_7D: 600,
                    CrossAssetWindow.LAST_30D: 1800,
                },
            ),
            # 2. ETFs (S&P 500 Proxy)
            "SPY": CandidateMarketData(
                symbol="SPY",
                display_name="SPDR S&P 500 ETF Trust",
                asset_class=AssetClassEnum.ETFS,
                market_or_venue="NYSE Arca",
                market_series_identity="ARCX:SPY",
                quote_currency="USD",
                quote_unit="USD/share",
                native_metric_kind=NativeMetricKind.ETF_MARKET_PRICE_CHANGE,
                native_display_label="Exchange Market Price Change",
                native_unit="%",
                current_value=Decimal("586.20"),
                reference_value=Decimal("582.10"),
                change_value=Decimal("4.10"),
                change_percent=Decimal("0.7043"),
                as_of_time=now - timedelta(minutes=3),
                session_status="OPEN",
                is_benchmark=False,
                is_proxy=True,
                proxy_kind=ProxyKind.ETF_PROXY,
                proxy_benchmark_target="S&P 500 Index",
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("582.10"),
                    CrossAssetWindow.LAST_7D: Decimal("575.40"),
                    CrossAssetWindow.LAST_30D: Decimal("560.80"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 60,
                    CrossAssetWindow.LAST_7D: 300,
                    CrossAssetWindow.LAST_30D: 900,
                },
            ),
            "QQQ": CandidateMarketData(
                symbol="QQQ",
                display_name="Invesco QQQ Trust",
                asset_class=AssetClassEnum.ETFS,
                market_or_venue="NASDAQ",
                market_series_identity="NASDAQ:QQQ",
                quote_currency="USD",
                quote_unit="USD/share",
                native_metric_kind=NativeMetricKind.ETF_MARKET_PRICE_CHANGE,
                native_display_label="Exchange Market Price Change",
                native_unit="%",
                current_value=Decimal("495.40"),
                reference_value=Decimal("490.20"),
                change_value=Decimal("5.20"),
                change_percent=Decimal("1.0608"),
                as_of_time=now - timedelta(minutes=4),
                session_status="OPEN",
                is_benchmark=False,
                is_proxy=True,
                proxy_kind=ProxyKind.ETF_PROXY,
                proxy_benchmark_target="Nasdaq-100 Index",
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("490.20"),
                    CrossAssetWindow.LAST_7D: Decimal("482.00"),
                    CrossAssetWindow.LAST_30D: Decimal("468.50"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 180,
                    CrossAssetWindow.LAST_7D: 450,
                    CrossAssetWindow.LAST_30D: 1200,
                },
            ),
            # 3. FX Markets
            "EURUSD": CandidateMarketData(
                symbol="EURUSD",
                display_name="Euro / US Dollar",
                asset_class=AssetClassEnum.FX,
                market_or_venue="OTC FX",
                market_series_identity="FX:EURUSD",
                quote_currency="USD",
                quote_unit="USD per EUR",
                native_metric_kind=NativeMetricKind.FX_SPOT_RATE_CHANGE,
                native_display_label="Spot Rate Change %",
                native_unit="%",
                current_value=Decimal("1.0845"),
                reference_value=Decimal("1.0890"),
                change_value=Decimal("-0.0045"),
                change_percent=Decimal("-0.4132"),
                as_of_time=now - timedelta(minutes=1),
                session_status="OPEN",
                is_benchmark=True,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("1.0890"),
                    CrossAssetWindow.LAST_7D: Decimal("1.0925"),
                    CrossAssetWindow.LAST_30D: Decimal("1.1010"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 30,
                    CrossAssetWindow.LAST_7D: 120,
                    CrossAssetWindow.LAST_30D: 600,
                },
            ),
            "USDJPY": CandidateMarketData(
                symbol="USDJPY",
                display_name="US Dollar / Japanese Yen",
                asset_class=AssetClassEnum.FX,
                market_or_venue="OTC FX",
                market_series_identity="FX:USDJPY",
                quote_currency="JPY",
                quote_unit="JPY per USD",
                native_metric_kind=NativeMetricKind.FX_SPOT_RATE_CHANGE,
                native_display_label="Spot Rate Change %",
                native_unit="%",
                current_value=Decimal("152.40"),
                reference_value=Decimal("151.85"),
                change_value=Decimal("0.55"),
                change_percent=Decimal("0.3622"),
                as_of_time=now - timedelta(minutes=2),
                session_status="OPEN",
                is_benchmark=True,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("151.85"),
                    CrossAssetWindow.LAST_7D: Decimal("149.60"),
                    CrossAssetWindow.LAST_30D: Decimal("145.20"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 45,
                    CrossAssetWindow.LAST_7D: 150,
                    CrossAssetWindow.LAST_30D: 700,
                },
            ),
            # 4. Cryptocurrency Spot Markets (24/7 rolling convention)
            "BTCUSDT": CandidateMarketData(
                symbol="BTCUSDT",
                display_name="Bitcoin / Tether",
                asset_class=AssetClassEnum.CRYPTO,
                market_or_venue="BINANCE",
                market_series_identity="BINANCE:BTCUSDT",
                quote_currency="USDT",
                quote_unit="USDT/BTC",
                native_metric_kind=NativeMetricKind.CRYPTO_SPOT_24H_CHANGE,
                native_display_label="Rolling 24h Spot Return",
                native_unit="%",
                current_value=Decimal("68450.00"),
                reference_value=Decimal("66800.00"),
                change_value=Decimal("1650.00"),
                change_percent=Decimal("2.4701"),
                as_of_time=now,
                session_status="OPEN",
                is_benchmark=True,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("66800.00"),
                    CrossAssetWindow.LAST_7D: Decimal("62100.00"),
                    CrossAssetWindow.LAST_30D: Decimal("58500.00"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 10,
                    CrossAssetWindow.LAST_7D: 40,
                    CrossAssetWindow.LAST_30D: 100,
                },
            ),
            "ETHUSDT": CandidateMarketData(
                symbol="ETHUSDT",
                display_name="Ethereum / Tether",
                asset_class=AssetClassEnum.CRYPTO,
                market_or_venue="BINANCE",
                market_series_identity="BINANCE:ETHUSDT",
                quote_currency="USDT",
                quote_unit="USDT/ETH",
                native_metric_kind=NativeMetricKind.CRYPTO_SPOT_24H_CHANGE,
                native_display_label="Rolling 24h Spot Return",
                native_unit="%",
                current_value=Decimal("2640.50"),
                reference_value=Decimal("2580.00"),
                change_value=Decimal("60.50"),
                change_percent=Decimal("2.3450"),
                as_of_time=now,
                session_status="OPEN",
                is_benchmark=False,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("2580.00"),
                    CrossAssetWindow.LAST_7D: Decimal("2450.00"),
                    CrossAssetWindow.LAST_30D: Decimal("2320.00"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 12,
                    CrossAssetWindow.LAST_7D: 50,
                    CrossAssetWindow.LAST_30D: 120,
                },
            ),
            # 5. Government Bonds (Yield Level & Basis Points; NO PRICE RETURN SERIES)
            "US10Y": CandidateMarketData(
                symbol="US10Y",
                display_name="US 10-Year Benchmark Treasury",
                asset_class=AssetClassEnum.BONDS,
                market_or_venue="US Treasury OTC",
                market_series_identity="BOND:US10Y_BENCHMARK",
                quote_currency="USD",
                quote_unit="%",
                native_metric_kind=NativeMetricKind.BOND_YIELD_BPS_CHANGE,
                native_display_label="Yield Level / bps Change",
                native_unit="bps",
                current_value=Decimal("4.225"),  # 4.225%
                reference_value=Decimal("4.150"),  # 4.150%
                change_value=Decimal("7.5"),  # +7.5 bps
                change_percent=None,  # Not a percentage return!
                as_of_time=now - timedelta(minutes=15),
                session_status="OPEN",
                is_benchmark=True,
                is_price_series=False,  # Evaluated yield only! Cannot calculate price return!
                window_start_prices={},
                window_start_offsets_sec={},
            ),
            # 6. Futures & Commodities
            "CLZ26": CandidateMarketData(
                symbol="CLZ26",
                display_name="WTI Crude Oil Dec 2026",
                asset_class=AssetClassEnum.FUTURES,
                market_or_venue="NYMEX",
                market_series_identity="NYMEX:CLZ26",
                quote_currency="USD",
                quote_unit="USD/barrel",
                native_metric_kind=NativeMetricKind.FUTURES_SETTLEMENT_CHANGE,
                native_display_label="Last Price vs Prior Settlement",
                native_unit="USD/barrel",
                current_value=Decimal("71.40"),
                reference_value=Decimal("70.25"),
                change_value=Decimal("1.15"),
                change_percent=Decimal("1.6370"),
                as_of_time=now - timedelta(minutes=8),
                session_status="OPEN",
                is_benchmark=True,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("70.25"),
                    CrossAssetWindow.LAST_7D: Decimal("68.80"),
                    CrossAssetWindow.LAST_30D: Decimal("66.50"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 200,
                    CrossAssetWindow.LAST_7D: 600,
                    CrossAssetWindow.LAST_30D: 1500,
                },
            ),
            "GCZ26": CandidateMarketData(
                symbol="GCZ26",
                display_name="Gold Dec 2026",
                asset_class=AssetClassEnum.FUTURES,
                market_or_venue="COMEX",
                market_series_identity="COMEX:GCZ26",
                quote_currency="USD",
                quote_unit="USD/troy oz",
                native_metric_kind=NativeMetricKind.FUTURES_SETTLEMENT_CHANGE,
                native_display_label="Last Price vs Prior Settlement",
                native_unit="USD/troy oz",
                current_value=Decimal("2745.20"),
                reference_value=Decimal("2732.00"),
                change_value=Decimal("13.20"),
                change_percent=Decimal("0.4832"),
                as_of_time=now - timedelta(minutes=6),
                session_status="OPEN",
                is_benchmark=True,
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("2732.00"),
                    CrossAssetWindow.LAST_7D: Decimal("2685.00"),
                    CrossAssetWindow.LAST_30D: Decimal("2590.00"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 150,
                    CrossAssetWindow.LAST_7D: 500,
                    CrossAssetWindow.LAST_30D: 1200,
                },
            ),
            "ESZ26": CandidateMarketData(
                symbol="ESZ26",
                display_name="E-mini S&P 500 Dec 2026",
                asset_class=AssetClassEnum.FUTURES,
                market_or_venue="CME",
                market_series_identity="CME:ESZ26",
                quote_currency="USD",
                quote_unit="Index points",
                native_metric_kind=NativeMetricKind.FUTURES_SETTLEMENT_CHANGE,
                native_display_label="Last Price vs Prior Settlement",
                native_unit="Index points",
                current_value=Decimal("5910.25"),
                reference_value=Decimal("5870.00"),
                change_value=Decimal("40.25"),
                change_percent=Decimal("0.6857"),
                as_of_time=now - timedelta(minutes=7),
                session_status="OPEN",
                is_benchmark=False,
                is_proxy=True,
                proxy_kind=ProxyKind.FUTURES_PROXY,
                proxy_benchmark_target="S&P 500 Index",
                window_start_prices={
                    CrossAssetWindow.LAST_24H: Decimal("5870.00"),
                    CrossAssetWindow.LAST_7D: Decimal("5790.00"),
                    CrossAssetWindow.LAST_30D: Decimal("5650.00"),
                },
                window_start_offsets_sec={
                    CrossAssetWindow.LAST_24H: 180,
                    CrossAssetWindow.LAST_7D: 550,
                    CrossAssetWindow.LAST_30D: 1300,
                },
            ),
        }
        return catalog

    def get_candidates_by_symbols(self, symbols: List[str]) -> List[CandidateMarketData]:
        """Filter candidates by specific canonical symbol names."""
        catalog = self.get_candidate_catalog()
        upper_symbols = [s.upper() for s in symbols]
        return [catalog[sym] for sym in upper_symbols if sym in catalog]
