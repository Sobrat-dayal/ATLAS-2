"""ATLAS Financial Risk Foundation — Historical Volatility Engine (Stage 115).

Deterministic calculation of sample variance, sample standard deviation,
square-root-of-time annualization, and rolling volatility series.
"""

import math
from datetime import datetime
from typing import List, Optional, Tuple

from .enums import AnnualizationPolicy, RiskReturnFrequency
from .errors import RiskInsufficientObservationsError
from .models import RollingRiskObservation


class HistoricalVolatilityEngine:
    """Computes historical and rolling realized volatility with strict statistical conventions."""

    @staticmethod
    def get_annualization_factor(
        frequency: RiskReturnFrequency,
        policy: AnnualizationPolicy = AnnualizationPolicy.DAYS_252,
    ) -> float:
        """Resolves the square-root annualization factor K based on frequency and policy."""
        if policy == AnnualizationPolicy.NONE:
            return 1.0

        if frequency == RiskReturnFrequency.DAILY:
            if policy == AnnualizationPolicy.DAYS_260:
                return 260.0
            return 252.0  # Standard market trading day convention
        elif frequency == RiskReturnFrequency.WEEKLY:
            return 52.0
        elif frequency == RiskReturnFrequency.MONTHLY:
            return 12.0
        return 252.0

    @staticmethod
    def compute_sample_mean(returns: List[float]) -> float:
        """Computes arithmetic sample mean return."""
        if not returns:
            return 0.0
        return sum(returns) / float(len(returns))

    @staticmethod
    def compute_sample_variance(returns: List[float]) -> float:
        """Computes unbiased sample variance with Bessel's correction (T - 1 denominator).

        Raises:
            RiskInsufficientObservationsError: If fewer than 2 return observations.
        """
        n = len(returns)
        if n < 2:
            raise RiskInsufficientObservationsError(
                f"Sample variance requires at least 2 return observations; received {n}."
            )

        mean = sum(returns) / float(n)
        sum_sq_diff = sum((r - mean) ** 2 for r in returns)
        return sum_sq_diff / float(n - 1)

    @staticmethod
    def compute_realized_volatility(
        returns: List[float],
        annualization_factor: float = 252.0,
    ) -> Tuple[float, float, float]:
        """Computes (sample_variance, period_volatility, annualized_volatility).

        Formula:
            s^2 = (1 / (T - 1)) * sum((r_t - r_bar)^2)
            s = sqrt(s^2)
            sigma_annual = s * sqrt(K)
        """
        var = HistoricalVolatilityEngine.compute_sample_variance(returns)
        period_vol = math.sqrt(max(0.0, var))
        annualized_vol = period_vol * math.sqrt(max(1.0, annualization_factor))
        return var, period_vol, annualized_vol

    @staticmethod
    def compute_rolling_volatility(
        timestamps: List[datetime],
        returns: List[float],
        window_size: int = 20,
        annualization_factor: float = 252.0,
    ) -> List[RollingRiskObservation]:
        """Computes moving-window realized volatility series without hindsight/forward-looking bias.

        For each t >= window_size - 1, computes volatility over returns[t - window_size + 1 : t + 1].
        """
        n = len(returns)
        if n != len(timestamps) or window_size < 2 or n < window_size:
            return []

        observations: List[RollingRiskObservation] = []
        for i in range(window_size - 1, n):
            window_slice = returns[i - window_size + 1 : i + 1]
            try:
                _, _, ann_vol = HistoricalVolatilityEngine.compute_realized_volatility(
                    window_slice, annualization_factor=annualization_factor
                )
                observations.append(
                    RollingRiskObservation(
                        window_end=timestamps[i],
                        metric_value=ann_vol,
                        observation_count=window_size,
                        is_complete=True,
                    )
                )
            except RiskInsufficientObservationsError:
                continue

        return observations

