"""Benchmark Registry and Comparison Engine for ATLAS Portfolio Performance (Stage 111).

Provides canonical benchmark definitions (S&P 500, SPY, NASDAQ 100, MSCI ACWI),
time alignment, rebased growth series (Index = 100), and percentage-point comparisons.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from atlas.portfolios.performance.enums import BenchmarkReturnBasis
from atlas.portfolios.performance.errors import (
    PortfolioPerformanceBenchmarkDataMissingError,
    PortfolioPerformanceBenchmarkNotFoundError,
)
from atlas.portfolios.performance.models import BenchmarkComparison, BenchmarkDefinition


CANONICAL_BENCHMARKS: Dict[str, BenchmarkDefinition] = {
    "BENCHMARK_SP500": BenchmarkDefinition(
        benchmark_id="BENCHMARK_SP500",
        name="S&P 500 Index",
        symbol="^GSPC",
        benchmark_type="CANONICAL_INDEX",
        return_basis=BenchmarkReturnBasis.PRICE_RETURN,
        currency="USD",
        description="Standard & Poor's 500 Index (Price Return, excluding dividend distributions)",
    ),
    "BENCHMARK_SPY": BenchmarkDefinition(
        benchmark_id="BENCHMARK_SPY",
        name="SPDR S&P 500 ETF Trust",
        symbol="SPY",
        benchmark_type="AUTHORIZED_ETF_PROXY",
        return_basis=BenchmarkReturnBasis.TOTAL_RETURN,
        currency="USD",
        description="SPDR S&P 500 ETF (Total Return proxy with dividend reinvestment)",
    ),
    "BENCHMARK_NASDAQ100": BenchmarkDefinition(
        benchmark_id="BENCHMARK_NASDAQ100",
        name="NASDAQ 100 Index",
        symbol="^NDX",
        benchmark_type="CANONICAL_INDEX",
        return_basis=BenchmarkReturnBasis.PRICE_RETURN,
        currency="USD",
        description="NASDAQ 100 Index (Price Return, top 100 non-financial tech/growth companies)",
    ),
    "BENCHMARK_ACWI": BenchmarkDefinition(
        benchmark_id="BENCHMARK_ACWI",
        name="iShares MSCI ACWI ETF",
        symbol="ACWI",
        benchmark_type="AUTHORIZED_ETF_PROXY",
        return_basis=BenchmarkReturnBasis.TOTAL_RETURN,
        currency="USD",
        description="iShares MSCI All Country World Index ETF (Global Total Return proxy)",
    ),
}


def list_canonical_benchmarks() -> List[BenchmarkDefinition]:
    """Returns list of authorized canonical benchmarks."""
    return list(CANONICAL_BENCHMARKS.values())


def get_canonical_benchmark(benchmark_id: str) -> BenchmarkDefinition:
    """Retrieves benchmark definition by ID."""
    b = CANONICAL_BENCHMARKS.get(benchmark_id)
    if not b:
        raise PortfolioPerformanceBenchmarkNotFoundError(f"Benchmark '{benchmark_id}' not found")
    return b


def compare_portfolio_to_benchmark(
    benchmark_id: str,
    portfolio_return: Decimal,
    period_start: datetime,
    period_end: datetime,
    start_level: Decimal,
    end_level: Decimal,
) -> BenchmarkComparison:
    """Calculates relative return comparison and rebased index series against a benchmark."""
    bench = get_canonical_benchmark(benchmark_id)
    if start_level <= Decimal("0.00"):
        raise PortfolioPerformanceBenchmarkDataMissingError(
            f"Benchmark {benchmark_id} has invalid start level: {start_level}"
        )

    bench_return = (end_level / start_level) - Decimal("1.0")
    arithmetic_diff = portfolio_return - bench_return

    rebased_bench_end = Decimal("100.0") * (end_level / start_level)
    rebased_port_end = Decimal("100.0") * (Decimal("1.0") + portfolio_return)

    warning = None
    if bench.return_basis == BenchmarkReturnBasis.PRICE_RETURN:
        warning = (
            "Methodology mismatch: Portfolio includes dividends and distributions (Total Return) "
            "while benchmark index is Price Return only."
        )

    return BenchmarkComparison(
        benchmark_id=bench.benchmark_id,
        benchmark_name=bench.name,
        return_basis=bench.return_basis,
        currency=bench.currency,
        portfolio_return=portfolio_return,
        benchmark_return=bench_return,
        arithmetic_difference=arithmetic_diff,
        period_start=period_start,
        period_end=period_end,
        rebased_portfolio_index_start=Decimal("100.00"),
        rebased_portfolio_index_end=rebased_port_end,
        rebased_benchmark_index_start=Decimal("100.00"),
        rebased_benchmark_index_end=rebased_bench_end,
        warning=warning,
    )

