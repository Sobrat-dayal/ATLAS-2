"""ATLAS Financial Risk Foundation — Benchmark Sensitivity Engine (Stage 115).

Calculates timestamp-aligned benchmark covariance, Pearson correlation,
historical beta, and active tracking error with zero-variance protection.
"""

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .enums import RiskMetricStatus
from .errors import (
    RiskBenchmarkVarianceZeroError,
    RiskCorrelationUndefinedError,
    RiskInsufficientObservationsError,
)
from .models import BenchmarkSensitivityResult
from .volatility import HistoricalVolatilityEngine


class BenchmarkSensitivityEngine:
    """Calculates linear benchmark sensitivity and co-movement metrics without causal attribution."""

    @staticmethod
    def align_series(
        p_dates: List[datetime],
        p_returns: List[float],
        b_dates: List[datetime],
        b_returns: List[float],
    ) -> Tuple[List[datetime], List[float], List[float]]:
        """Aligns portfolio and benchmark return series by exact calendar date (YYYY-MM-DD).

        Never pairs observations by naive array index alone.
        """
        b_map: Dict[str, float] = {
            dt.strftime("%Y-%m-%d"): ret for dt, ret in zip(b_dates, b_returns)
        }

        aligned_dates: List[datetime] = []
        aligned_p: List[float] = []
        aligned_b: List[float] = []

        for dt, ret in zip(p_dates, p_returns):
            key = dt.strftime("%Y-%m-%d")
            if key in b_map:
                aligned_dates.append(dt)
                aligned_p.append(ret)
                aligned_b.append(b_map[key])

        return aligned_dates, aligned_p, aligned_b

    @staticmethod
    def compute_sample_covariance(x: List[float], y: List[float]) -> float:
        """Computes unbiased sample covariance between two aligned series (T - 1 denominator)."""
        n = len(x)
        if n < 2 or len(y) != n:
            raise RiskInsufficientObservationsError(
                f"Sample covariance requires at least 2 aligned observations; received {n}."
            )

        mean_x = sum(x) / float(n)
        mean_y = sum(y) / float(n)
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / float(n - 1)
        return cov

    @staticmethod
    def compute_beta(p_returns: List[float], b_returns: List[float]) -> float:
        """Computes historical market beta: beta = Cov(R_P, R_B) / Var(R_B).

        Raises:
            RiskBenchmarkVarianceZeroError: If benchmark variance is numerically zero.
        """
        cov = BenchmarkSensitivityEngine.compute_sample_covariance(p_returns, b_returns)
        b_var = HistoricalVolatilityEngine.compute_sample_variance(b_returns)

        if b_var <= 1e-12:
            raise RiskBenchmarkVarianceZeroError(
                "Benchmark return variance is zero; historical beta is mathematically undefined."
            )

        return cov / b_var

    @staticmethod
    def compute_correlation(p_returns: List[float], b_returns: List[float]) -> float:
        """Computes Pearson product-moment correlation coefficient: rho = Cov / (sigma_P * sigma_B).

        Raises:
            RiskCorrelationUndefinedError: If either portfolio or benchmark has zero variance.
        """
        cov = BenchmarkSensitivityEngine.compute_sample_covariance(p_returns, b_returns)
        p_var = HistoricalVolatilityEngine.compute_sample_variance(p_returns)
        b_var = HistoricalVolatilityEngine.compute_sample_variance(b_returns)

        if p_var <= 1e-12 or b_var <= 1e-12:
            raise RiskCorrelationUndefinedError(
                "Return series standard deviation is zero; correlation is mathematically undefined."
            )

        denom = math.sqrt(p_var * b_var)
        corr = cov / denom
        # Numerical clamping to strictly [-1.0, 1.0]
        return max(-1.0, min(1.0, corr))

    @staticmethod
    def compute_tracking_error(
        p_returns: List[float],
        b_returns: List[float],
        annualization_factor: float = 252.0,
    ) -> float:
        """Computes annualized sample tracking error: s(R_P - R_B) * sqrt(K)."""
        active_returns = [p - b for p, b in zip(p_returns, b_returns)]
        _, _, ann_te = HistoricalVolatilityEngine.compute_realized_volatility(
            active_returns, annualization_factor=annualization_factor
        )
        return ann_te

    @staticmethod
    def evaluate_sensitivity(
        benchmark_id: str,
        benchmark_symbol: str,
        benchmark_name: str,
        p_dates: List[datetime],
        p_returns: List[float],
        b_dates: List[datetime],
        b_returns: List[float],
        annualization_factor: float = 252.0,
    ) -> BenchmarkSensitivityResult:
        """Executes complete aligned benchmark sensitivity analysis."""
        aligned_dates, aligned_p, aligned_b = BenchmarkSensitivityEngine.align_series(
            p_dates, p_returns, b_dates, b_returns
        )
        matched = len(aligned_p)

        if matched < 2:
            return BenchmarkSensitivityResult(
                benchmark_id=benchmark_id,
                benchmark_symbol=benchmark_symbol,
                benchmark_name=benchmark_name,
                beta=None,
                correlation=None,
                tracking_error_annualized=None,
                benchmark_volatility_annualized=None,
                portfolio_volatility_annualized=None,
                covariance=None,
                matched_observations=matched,
                status=RiskMetricStatus.INSUFFICIENT_HISTORY,
                warning="Insufficient overlapping observation timestamps between portfolio and benchmark.",
            )

        try:
            cov = BenchmarkSensitivityEngine.compute_sample_covariance(aligned_p, aligned_b)
            _, _, p_vol = HistoricalVolatilityEngine.compute_realized_volatility(
                aligned_p, annualization_factor=annualization_factor
            )
            _, _, b_vol = HistoricalVolatilityEngine.compute_realized_volatility(
                aligned_b, annualization_factor=annualization_factor
            )
            beta = BenchmarkSensitivityEngine.compute_beta(aligned_p, aligned_b)
            corr = BenchmarkSensitivityEngine.compute_correlation(aligned_p, aligned_b)
            te = BenchmarkSensitivityEngine.compute_tracking_error(
                aligned_p, aligned_b, annualization_factor=annualization_factor
            )

            return BenchmarkSensitivityResult(
                benchmark_id=benchmark_id,
                benchmark_symbol=benchmark_symbol,
                benchmark_name=benchmark_name,
                beta=beta,
                correlation=corr,
                tracking_error_annualized=te,
                benchmark_volatility_annualized=b_vol,
                portfolio_volatility_annualized=p_vol,
                covariance=cov,
                matched_observations=matched,
                status=RiskMetricStatus.AVAILABLE,
            )
        except RiskBenchmarkVarianceZeroError as e:
            return BenchmarkSensitivityResult(
                benchmark_id=benchmark_id,
                benchmark_symbol=benchmark_symbol,
                benchmark_name=benchmark_name,
                beta=None,
                correlation=None,
                tracking_error_annualized=None,
                benchmark_volatility_annualized=0.0,
                portfolio_volatility_annualized=None,
                covariance=0.0,
                matched_observations=matched,
                status=RiskMetricStatus.INVALID_NUMERICAL_DOMAIN,
                warning=str(e),
            )
        except RiskCorrelationUndefinedError as e:
            return BenchmarkSensitivityResult(
                benchmark_id=benchmark_id,
                benchmark_symbol=benchmark_symbol,
                benchmark_name=benchmark_name,
                beta=None,
                correlation=None,
                tracking_error_annualized=None,
                benchmark_volatility_annualized=None,
                portfolio_volatility_annualized=None,
                covariance=cov,
                matched_observations=matched,
                status=RiskMetricStatus.INVALID_NUMERICAL_DOMAIN,
                warning=str(e),
            )

