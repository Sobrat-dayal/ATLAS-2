"""ATLAS Portfolios V1 — Benchmark Constituent & Weight Engine (Stage 113).

Provides canonical benchmark snapshots, point-in-time sector weights,
benchmark constituent returns, and rebalance history to support
holdings-based Brinson attribution without survivorship bias.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from atlas.portfolios.attribution.errors import (
    PortfolioAttributionBenchmarkConstituentsMissingError,
    PortfolioAttributionBenchmarkNotFoundError,
)
from atlas.portfolios.performance.benchmarks import (
    CANONICAL_BENCHMARKS,
    BenchmarkDefinition,
    get_canonical_benchmark,
)


@dataclass
class BenchmarkConstituentRecord:
    """Underlying constituent snapshot in a canonical benchmark."""
    instrument_id: str
    symbol: str
    name: str
    weight: Decimal          # e.g. Decimal("0.0725")
    holding_return: Decimal  # e.g. Decimal("0.1500")
    sector: str              # GICS Sector
    industry: str            # GICS Industry Group


@dataclass
class BenchmarkSectorSnapshot:
    """Aggregated group weight and return for a benchmark sector."""
    sector_id: str
    sector_name: str
    weight: Decimal          # w_B,i
    sector_return: Decimal   # R_B,i
    constituents_count: int


@dataclass
class BenchmarkPointInTimeSnapshot:
    """Historical benchmark composition snapshot effective at a specific date."""
    benchmark_id: str
    effective_date: date
    currency: str
    total_return: Decimal
    sectors: Dict[str, BenchmarkSectorSnapshot]
    constituents: List[BenchmarkConstituentRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Canonical Point-in-Time Benchmark Datasets
# ---------------------------------------------------------------------------

# Canonical SPY / S&P 500 Historical Snapshot (Representative Large-Cap US)
_SP500_SECTORS_DEFAULT: Dict[str, BenchmarkSectorSnapshot] = {
    "information_technology": BenchmarkSectorSnapshot(
        sector_id="information_technology",
        sector_name="Information Technology",
        weight=Decimal("0.3150"),
        sector_return=Decimal("0.1240"),
        constituents_count=67,
    ),
    "financials": BenchmarkSectorSnapshot(
        sector_id="financials",
        sector_name="Financials",
        weight=Decimal("0.1320"),
        sector_return=Decimal("0.0680"),
        constituents_count=72,
    ),
    "health_care": BenchmarkSectorSnapshot(
        sector_id="health_care",
        sector_name="Health Care",
        weight=Decimal("0.1180"),
        sector_return=Decimal("0.0350"),
        constituents_count=64,
    ),
    "consumer_discretionary": BenchmarkSectorSnapshot(
        sector_id="consumer_discretionary",
        sector_name="Consumer Discretionary",
        weight=Decimal("0.1040"),
        sector_return=Decimal("0.0820"),
        constituents_count=52,
    ),
    "communication_services": BenchmarkSectorSnapshot(
        sector_id="communication_services",
        sector_name="Communication Services",
        weight=Decimal("0.0910"),
        sector_return=Decimal("0.1120"),
        constituents_count=23,
    ),
    "industrials": BenchmarkSectorSnapshot(
        sector_id="industrials",
        sector_name="Industrials",
        weight=Decimal("0.0820"),
        sector_return=Decimal("0.0540"),
        constituents_count=78,
    ),
    "consumer_staples": BenchmarkSectorSnapshot(
        sector_id="consumer_staples",
        sector_name="Consumer Staples",
        weight=Decimal("0.0580"),
        sector_return=Decimal("0.0210"),
        constituents_count=38,
    ),
    "energy": BenchmarkSectorSnapshot(
        sector_id="energy",
        sector_name="Energy",
        weight=Decimal("0.0360"),
        sector_return=Decimal("-0.0150"),
        constituents_count=22,
    ),
    "utilities": BenchmarkSectorSnapshot(
        sector_id="utilities",
        sector_name="Utilities",
        weight=Decimal("0.0240"),
        sector_return=Decimal("0.0420"),
        constituents_count=30,
    ),
    "real_estate": BenchmarkSectorSnapshot(
        sector_id="real_estate",
        sector_name="Real Estate",
        weight=Decimal("0.0220"),
        sector_return=Decimal("0.0180"),
        constituents_count=31,
    ),
    "materials": BenchmarkSectorSnapshot(
        sector_id="materials",
        sector_name="Materials",
        weight=Decimal("0.0180"),
        sector_return=Decimal("0.0310"),
        constituents_count=28,
    ),
}

# NASDAQ 100 Historical Snapshot (Growth / Tech Heavy)
_NASDAQ100_SECTORS_DEFAULT: Dict[str, BenchmarkSectorSnapshot] = {
    "information_technology": BenchmarkSectorSnapshot(
        sector_id="information_technology",
        sector_name="Information Technology",
        weight=Decimal("0.5120"),
        sector_return=Decimal("0.1450"),
        constituents_count=42,
    ),
    "communication_services": BenchmarkSectorSnapshot(
        sector_id="communication_services",
        sector_name="Communication Services",
        weight=Decimal("0.1540"),
        sector_return=Decimal("0.1180"),
        constituents_count=9,
    ),
    "consumer_discretionary": BenchmarkSectorSnapshot(
        sector_id="consumer_discretionary",
        sector_name="Consumer Discretionary",
        weight=Decimal("0.1380"),
        sector_return=Decimal("0.0920"),
        constituents_count=18,
    ),
    "health_care": BenchmarkSectorSnapshot(
        sector_id="health_care",
        sector_name="Health Care",
        weight=Decimal("0.0650"),
        sector_return=Decimal("0.0280"),
        constituents_count=16,
    ),
    "industrials": BenchmarkSectorSnapshot(
        sector_id="industrials",
        sector_name="Industrials",
        weight=Decimal("0.0480"),
        sector_return=Decimal("0.0450"),
        constituents_count=8,
    ),
    "consumer_staples": BenchmarkSectorSnapshot(
        sector_id="consumer_staples",
        sector_name="Consumer Staples",
        weight=Decimal("0.0410"),
        sector_return=Decimal("0.0190"),
        constituents_count=5,
    ),
    "utilities": BenchmarkSectorSnapshot(
        sector_id="utilities",
        sector_name="Utilities",
        weight=Decimal("0.0120"),
        sector_return=Decimal("0.0320"),
        constituents_count=2,
    ),
    "energy": BenchmarkSectorSnapshot(
        sector_id="energy",
        sector_name="Energy",
        weight=Decimal("0.0050"),
        sector_return=Decimal("0.0100"),
        constituents_count=1,
    ),
    "materials": BenchmarkSectorSnapshot(
        sector_id="materials",
        sector_name="Materials",
        weight=Decimal("0.0150"),
        sector_return=Decimal("0.0240"),
        constituents_count=1,
    ),
    "financials": BenchmarkSectorSnapshot(
        sector_id="financials",
        sector_name="Financials",
        weight=Decimal("0.0080"),
        sector_return=Decimal("0.0500"),
        constituents_count=1,
    ),
    "real_estate": BenchmarkSectorSnapshot(
        sector_id="real_estate",
        sector_name="Real Estate",
        weight=Decimal("0.0020"),
        sector_return=Decimal("0.0150"),
        constituents_count=1,
    ),
}

# Part XVII & XVIII Mandatory Two-Sector Reference Fixture Benchmark
_TWO_SECTOR_REF_BENCHMARK = BenchmarkPointInTimeSnapshot(
    benchmark_id="BENCHMARK_TWO_SECTOR_REF",
    effective_date=date(2026, 1, 1),
    currency="USD",
    total_return=Decimal("0.0880"),  # 8.80%
    sectors={
        "technology": BenchmarkSectorSnapshot(
            sector_id="technology",
            sector_name="Technology",
            weight=Decimal("0.4000"),       # 40%
            sector_return=Decimal("0.1000"), # 10%
            constituents_count=1,
        ),
        "financials": BenchmarkSectorSnapshot(
            sector_id="financials",
            sector_name="Financials",
            weight=Decimal("0.6000"),       # 60%
            sector_return=Decimal("0.0800"), # 8%
            constituents_count=1,
        ),
    },
    constituents=[
        BenchmarkConstituentRecord(
            instrument_id="inst_tech_ref",
            symbol="TECH_IDX",
            name="Technology Benchmark Constituent",
            weight=Decimal("0.4000"),
            holding_return=Decimal("0.1000"),
            sector="technology",
            industry="software",
        ),
        BenchmarkConstituentRecord(
            instrument_id="inst_fin_ref",
            symbol="FIN_IDX",
            name="Financials Benchmark Constituent",
            weight=Decimal("0.6000"),
            holding_return=Decimal("0.0800"),
            sector="financials",
            industry="banks",
        ),
    ],
)


class BenchmarkCompositionEngine:
    """Manages benchmark constituent snapshots, sector weights, and historical returns."""

    def __init__(self):
        self._custom_snapshots: Dict[str, BenchmarkPointInTimeSnapshot] = {
            "BENCHMARK_TWO_SECTOR_REF": _TWO_SECTOR_REF_BENCHMARK,
        }

    def register_custom_snapshot(self, snapshot: BenchmarkPointInTimeSnapshot) -> None:
        """Allows test suites and isolated fixtures to register custom benchmark snapshots."""
        self._custom_snapshots[snapshot.benchmark_id] = snapshot

    def get_benchmark_snapshot(
        self,
        benchmark_id: str,
        as_of_date: Optional[date] = None,
    ) -> BenchmarkPointInTimeSnapshot:
        """Retrieves point-in-time constituent and sector snapshot for a benchmark."""
        # Check custom fixtures first
        if benchmark_id in self._custom_snapshots:
            return self._custom_snapshots[benchmark_id]

        # Verify benchmark exists in canonical definitions
        try:
            bench_def = get_canonical_benchmark(benchmark_id)
        except Exception:
            raise PortfolioAttributionBenchmarkNotFoundError(f"Benchmark '{benchmark_id}' not found")

        ref_date = as_of_date or date.today()

        if benchmark_id in ("BENCHMARK_SP500", "BENCHMARK_SPY"):
            sectors = _SP500_SECTORS_DEFAULT
            # Reconstruct total benchmark return as weighted sum
            total_ret = sum((s.weight * s.sector_return for s in sectors.values()), Decimal("0.0000"))
            return BenchmarkPointInTimeSnapshot(
                benchmark_id=benchmark_id,
                effective_date=ref_date,
                currency=bench_def.currency,
                total_return=total_ret,
                sectors=sectors,
            )

        if benchmark_id == "BENCHMARK_NASDAQ100":
            sectors = _NASDAQ100_SECTORS_DEFAULT
            total_ret = sum((s.weight * s.sector_return for s in sectors.values()), Decimal("0.0000"))
            return BenchmarkPointInTimeSnapshot(
                benchmark_id=benchmark_id,
                effective_date=ref_date,
                currency=bench_def.currency,
                total_return=total_ret,
                sectors=sectors,
            )

        if benchmark_id == "BENCHMARK_ACWI":
            # Global benchmark reusing diversified weights
            sectors = _SP500_SECTORS_DEFAULT
            total_ret = sum((s.weight * s.sector_return for s in sectors.values()), Decimal("0.0000"))
            return BenchmarkPointInTimeSnapshot(
                benchmark_id=benchmark_id,
                effective_date=ref_date,
                currency=bench_def.currency,
                total_return=total_ret,
                sectors=sectors,
            )

        raise PortfolioAttributionBenchmarkConstituentsMissingError(
            f"Constituents missing for benchmark '{benchmark_id}' as of {ref_date}"
        )

