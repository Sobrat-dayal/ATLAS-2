"""ATLAS Financial Risk Foundation — VaR Model Validation & Diagnostics (Stage 116).

Implements:
1. Historical point-in-time VaR exception identification (L_t > VaR_{alpha, t}).
2. Expected exceedance rates vs observed empirical exception frequencies.
3. Kupiec Likelihood Ratio Unconditional Coverage Test (LR_UC ~ Chi^2(1)).
4. Sample size adequacy evaluation and clustering diagnostics.
"""

from datetime import datetime
import math
from typing import List, Optional, Tuple
from scipy import stats

from .enums import KupiecTestStatus, VaRModelType
from .models import (
    KupiecTestResult,
    VaRBacktestRun,
    VaRExceptionObservation,
)


class VaRDiagnosticsEngine:
    """Institutional model validation and exception backtesting engine."""

    @staticmethod
    def evaluate_kupiec_test(
        total_observations: int,
        exception_count: int,
        confidence_level: float = 0.95,
    ) -> KupiecTestResult:
        """
        Calculates the Kupiec Likelihood Ratio Unconditional Coverage Test.
        
        Formula:
            p_0 = 1 - alpha
            p_hat = x / N
            LR_UC = -2 * ln( ((1 - p_0)^{N-x} * p_0^x) / ((1 - p_hat)^{N-x} * p_hat^x) )
            LR_UC ~ Chi^2(1)
        """
        n = total_observations
        x = exception_count
        p0 = 1.0 - confidence_level

        if n <= 0:
            return KupiecTestResult(
                total_observations=0,
                exception_count=0,
                confidence_level=confidence_level,
                expected_rate=p0,
                observed_rate=0.0,
                likelihood_ratio_stat=0.0,
                critical_value_95=3.841459,
                p_value=1.0,
                status=KupiecTestStatus.INSUFFICIENT_SAMPLE,
                is_sample_adequate=False,
                warnings=["Zero observations provided for backtest."],
            )

        phat = x / n
        warnings: List[str] = []

        # Calculate likelihood ratio test statistic with boundary guards
        if x == 0:
            lr_stat = -2.0 * n * math.log(1.0 - p0)
        elif x == n:
            lr_stat = -2.0 * n * math.log(p0)
        else:
            term1 = (n - x) * math.log((1.0 - p0) / (1.0 - phat))
            term2 = x * math.log(p0 / phat)
            lr_stat = -2.0 * (term1 + term2)

        lr_stat = max(0.0, lr_stat)
        critical_val = 3.841459  # Chi-squared critical value for df=1 at 95%
        p_val = float(1.0 - stats.chi2.cdf(lr_stat, df=1))

        # Check sample adequacy: asymptotic chi-square requires at least ~30 to 100 observations
        is_adequate = n >= 30
        if not is_adequate:
            status = KupiecTestStatus.INSUFFICIENT_SAMPLE
            warnings.append(
                f"Backtest sample size (N={n}) is too small for asymptotic Chi-Square validity. Minimum 30 recommended."
            )
        elif lr_stat <= critical_val:
            status = KupiecTestStatus.ACCEPT_UNCONDITIONAL_COVERAGE
        elif phat > p0:
            status = KupiecTestStatus.REJECT_TOO_MANY_EXCEPTIONS
            warnings.append(
                f"Observed exception rate ({phat:.1%}) significantly exceeds expected rate ({p0:.1%}). Model may underestimate tail risk."
            )
        else:
            status = KupiecTestStatus.REJECT_TOO_FEW_EXCEPTIONS
            warnings.append(
                f"Observed exception rate ({phat:.1%}) is significantly below expected rate ({p0:.1%}). Model may be overly conservative."
            )

        return KupiecTestResult(
            total_observations=n,
            exception_count=x,
            confidence_level=confidence_level,
            expected_rate=p0,
            observed_rate=phat,
            likelihood_ratio_stat=lr_stat,
            critical_value_95=critical_val,
            p_value=p_val,
            status=status,
            is_sample_adequate=is_adequate,
            warnings=warnings,
        )

    @classmethod
    def run_var_backtest(
        cls,
        observations: Optional[List[Tuple[datetime, float, float]]] = None,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
        model_type: VaRModelType = VaRModelType.HISTORICAL_SIMULATION,
        portfolio_id: str = "PORTFOLIO",
        timestamps: Optional[List[datetime]] = None,
        realized_returns: Optional[List[float]] = None,
        estimation_window_size: int = 252,
    ) -> VaRBacktestRun:
        """
        Executes a historical point-in-time VaR backtest.
        
        Args:
            observations: List of (date, forecast_var, realized_loss)
            confidence_level: e.g. 0.95
            timestamps: Optional timestamps series for rolling window estimation
            realized_returns: Optional return series for rolling window estimation
            estimation_window_size: Rolling window size (default 252)
        """
        if observations is None:
            observations = []
            if timestamps is not None and realized_returns is not None:
                n = len(realized_returns)
                win = min(estimation_window_size, max(20, n // 2))
                for t in range(win, n):
                    sub_losses = sorted([-r for r in realized_returns[t - win : t]])
                    idx = max(0, min(len(sub_losses) - 1, math.ceil(confidence_level * len(sub_losses)) - 1))
                    f_var = sub_losses[idx]
                    r_loss = -realized_returns[t]
                    observations.append((timestamps[t], f_var, r_loss))
            if not observations:
                now = datetime.utcnow()
                observations = [(now, 0.02, 0.01)]

        backtest_id = f"BTEST_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        exceptions: List[VaRExceptionObservation] = []

        for dt, f_var, r_loss in observations:
            is_exc = r_loss > f_var
            exceedance = max(0.0, r_loss - f_var)
            exceptions.append(
                VaRExceptionObservation(
                    observation_date=dt,
                    forecast_var=f_var,
                    realized_loss=r_loss,
                    is_exception=is_exc,
                    exceedance_amount=exceedance,
                )
            )

        total_obs = len(exceptions)
        exc_count = sum(1 for e in exceptions if e.is_exception)

        kupiec = cls.evaluate_kupiec_test(
            total_observations=total_obs,
            exception_count=exc_count,
            confidence_level=confidence_level,
        )

        obs_start = exceptions[0].observation_date if exceptions else datetime.utcnow()
        obs_end = exceptions[-1].observation_date if exceptions else datetime.utcnow()

        return VaRBacktestRun(
            backtest_id=backtest_id,
            portfolio_id=portfolio_id,
            model_type=model_type,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            observation_start=obs_start,
            observation_end=obs_end,
            total_forecasts=total_obs,
            exceptions=exceptions,
            kupiec_test=kupiec,
            created_at=datetime.utcnow(),
        )
