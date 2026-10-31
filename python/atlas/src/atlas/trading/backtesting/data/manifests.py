"""Historical Dataset Manifests and License Entitlement Registry (Stage 143)."""

from __future__ import annotations

import dataclasses
import hashlib
from typing import Dict, List, Optional
from atlas.trading.backtesting.domain import DataGranularity, HistoricalDatasetManifest
from atlas.trading.backtesting.errors import (
    BacktestDatasetNotFoundError,
    BacktestLicenseRevokedError,
)


class HistoricalDatasetRegistry:
    """Authoritative registry of licensed historical datasets and coverage manifests."""

    def __init__(self):
        self._manifests: Dict[str, HistoricalDatasetManifest] = {}
        self._revoked_licenses: set[str] = set()
        self._seed_canonical_manifests()

    def _seed_canonical_manifests(self):
        """Seed baseline manifests for canonical research instruments."""
        # 1. SPY Daily Bars (2020 - 2024)
        m_spy = HistoricalDatasetManifest(
            dataset_id="ds_spy_daily_2024",
            provider_id="SRC_CBOE_HISTORICAL",
            symbol="SPY",
            instrument_type="EQUITY",
            data_granularity=DataGranularity.BARS_1D,
            start_date="2024-01-01",
            end_date="2024-12-31",
            records_count=252,
            has_gaps=False,
            checksum="chk_spy_2024_sha256",
            license_id="SRC_HISTORICAL_AUTHORIZED",
            currency="USD",
            has_options_quotes=True,
            is_delisted_inclusive=True,
        )
        self._manifests[m_spy.dataset_id] = m_spy
        self._manifests["ds_spy_daily"] = dataclasses.replace(m_spy, dataset_id="ds_spy_daily")

        # SPY Minute Bars
        m_spy_min = HistoricalDatasetManifest(
            dataset_id="ds_spy_minute_2024",
            provider_id="SRC_CBOE_HISTORICAL",
            symbol="SPY",
            instrument_type="EQUITY",
            data_granularity=DataGranularity.BARS_1M,
            start_date="2024-01-01",
            end_date="2024-01-31",
            records_count=10000,
            has_gaps=False,
            checksum="chk_spy_min_2024_sha256",
            license_id="SRC_HISTORICAL_AUTHORIZED",
            currency="USD",
            has_options_quotes=True,
            is_delisted_inclusive=True,
        )
        self._manifests[m_spy_min.dataset_id] = m_spy_min
        self._manifests["ds_spy_minute"] = dataclasses.replace(m_spy_min, dataset_id="ds_spy_minute")

        # 2. AAPL Daily Bars
        m_aapl = HistoricalDatasetManifest(
            dataset_id="ds_aapl_daily_2024",
            provider_id="SRC_NASDAQ_HISTORICAL",
            symbol="AAPL",
            instrument_type="EQUITY",
            data_granularity=DataGranularity.BARS_1D,
            start_date="2024-01-01",
            end_date="2024-12-31",
            records_count=252,
            has_gaps=False,
            checksum="chk_aapl_2024_sha256",
            license_id="SRC_HISTORICAL_AUTHORIZED",
            currency="USD",
            has_options_quotes=True,
            is_delisted_inclusive=True,
        )
        self._manifests[m_aapl.dataset_id] = m_aapl

        # 3. Delisted Enron Historical Fixture (For Test H survivorship bias testing)
        m_delisted = HistoricalDatasetManifest(
            dataset_id="ds_delisted_corp_2001",
            provider_id="SRC_NYSE_HISTORICAL",
            symbol="ENRNQ",
            instrument_type="EQUITY",
            data_granularity=DataGranularity.BARS_1D,
            start_date="2001-01-01",
            end_date="2001-12-02",
            records_count=230,
            has_gaps=False,
            checksum="chk_enrnq_2001_sha256",
            license_id="SRC_HISTORICAL_AUTHORIZED",
            currency="USD",
            has_options_quotes=False,
            is_delisted_inclusive=True,
        )
        self._manifests[m_delisted.dataset_id] = m_delisted

        # 4. Underlying Only Dataset (For Test K - no options quotes)
        m_no_opt = HistoricalDatasetManifest(
            dataset_id="ds_underlying_only_stock",
            provider_id="SRC_PUBLIC_OHLC",
            symbol="XYZ",
            instrument_type="EQUITY",
            data_granularity=DataGranularity.BARS_1D,
            start_date="2024-01-01",
            end_date="2024-06-30",
            records_count=125,
            has_gaps=False,
            checksum="chk_xyz_2024_sha256",
            license_id="SRC_HISTORICAL_AUTHORIZED",
            currency="USD",
            has_options_quotes=False,  # Lacks options quotes!
            is_delisted_inclusive=True,
        )
        self._manifests[m_no_opt.dataset_id] = m_no_opt

    def get_manifest(self, dataset_id: str) -> HistoricalDatasetManifest:
        manifest = self._manifests.get(dataset_id)
        if not manifest:
            raise BacktestDatasetNotFoundError(dataset_id)

        # Enforce source licensing entitlement (Test U)
        if manifest.license_id in self._revoked_licenses:
            raise BacktestLicenseRevokedError(manifest.license_id)

        return manifest

    def list_manifests(self) -> List[HistoricalDatasetManifest]:
        return [
            m for m in self._manifests.values()
            if m.license_id not in self._revoked_licenses
        ]

    def register_manifest(self, manifest: HistoricalDatasetManifest) -> None:
        self._manifests[manifest.dataset_id] = manifest

    def revoke_license(self, license_id: str) -> None:
        """Revoke a historical data license (Test U)."""
        self._revoked_licenses.add(license_id)

    def restore_license(self, license_id: str) -> None:
        self._revoked_licenses.discard(license_id)
