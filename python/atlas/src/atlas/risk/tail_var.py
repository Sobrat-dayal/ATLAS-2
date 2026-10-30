"""ATLAS Financial Risk Foundation — Tail Risk Engine (Stage 116).

Implements:
1. Historical Simulation Value at Risk & Expected Shortfall (fractional tail weighting).
2. Parametric Normal Variance-Covariance VaR & Expected Shortfall.
3. Bounded Monte Carlo Gaussian VaR & Expected Shortfall with reproducible seed.
4. Loss distribution histogram binning, quantiles, and tail adequacy diagnostics.
"""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import stats

from .enums import (
    ExpectedShortfallMethod,
    RiskMetricStatus,
    VaRModelType,
)
from .errors import (
    RiskESInsufficientTailSampleError,
    RiskVaRConfidenceInvalidError,
    RiskVaRHorizonInvalidError,
    RiskVaRInsufficientHistoryError,
    RiskVaRNumericalFailureError,
)
from .models import (
    ExpectedShortfallResult,
    LossDistribution,
    VaRResult,
)


class TailRiskEngine:
    """Institutional calculation engine for VaR, Expected Shortfall, and Tail Risk."""

    @staticmethod
    def validate_confidence(confidence: float) -> None:
        """Validates that confidence level alpha is strictly inside (0.50, 1.00)."""
        if confidence <= 0.50 or confidence >= 1.00:
            raise RiskVaRConfidenceInvalidError(
                f"Confidence level {confidence} must be strictly between 0.50 and 1.00."
            )

    @staticmethod
    def validate_horizon(horizon_days: int) -> None:
        """Validates that horizon is a positive integer between 1 and 252 days."""
        if horizon_days < 1 or horizon_days > 252:
            raise RiskVaRHorizonInvalidError(
                f"Measurement horizon {horizon_days} must be between 1 and 252 trading days."
            )

    @classmethod
    def calculate_historical_var_and_es(
        cls,
        losses: Optional[List[float]] = None,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
        portfolio_nav: float = 1.0,
        returns: Optional[List[float]] = None,
        baseline_portfolio_value: Optional[float] = None,
        method: Optional[ExpectedShortfallMethod] = None,
    ) -> Tuple[VaRResult, ExpectedShortfallResult, LossDistribution]:
        """
        Calculates Historical Simulation VaR and Expected Shortfall.
        
        Uses the empirical inverse-CDF quantile convention:
            k = ceil(alpha * N)
            VaR_alpha = L_{(k)}
            
        Expected Shortfall is calculated via exact fractional tail integration:
            ES_alpha = 1/(1 - alpha) * integral_{alpha}^1 Q(u) du
            
        Verified by Part XVI Reference Fixture:
            losses = [-2%, -1%, 0%, +1%, +3%], alpha = 80%
            VaR = +1%, ES = +3%.
        """
        cls.validate_confidence(confidence_level)
        cls.validate_horizon(horizon_days)

        if baseline_portfolio_value is not None:
            portfolio_nav = baseline_portfolio_value

        if losses is None:
            if returns is not None:
                losses = [-r for r in returns]
            else:
                raise RiskVaRInsufficientHistoryError("Either 'losses' or 'returns' series must be provided.")

        n = len(losses)
        if n < 2:
            raise RiskVaRInsufficientHistoryError(
                f"Insufficient historical observations (N={n}). Minimum 2 required."
            )

        sorted_losses = sorted(losses)

        # Scale for multi-period horizon if horizon_days > 1
        # Following Gaussian square-root scaling convention with explicit documentation
        scale_factor = math.sqrt(horizon_days) if horizon_days > 1 else 1.0
        scaled_losses = [l * scale_factor for l in sorted_losses]

        # 1. Empirical Inverse-CDF VaR
        # k = ceil(alpha * N). In 0-indexed: index = ceil(alpha * N) - 1
        idx = max(0, min(n - 1, math.ceil(confidence_level * n) - 1))
        var_fraction = scaled_losses[idx]
        var_monetary = var_fraction * portfolio_nav

        # 2. Exact Fractional Tail Weighted Expected Shortfall
        # Each observation i (1 to N) occupies interval ((i-1)/N, i/N].
        # We integrate over [alpha, 1.0].
        tail_prob = 1.0 - confidence_level
        es_sum = 0.0
        effective_tail_count = tail_prob * n

        for i in range(1, n + 1):
            interval_start = (i - 1) / n
            interval_end = i / n
            overlap = max(0.0, min(interval_end, 1.0) - max(interval_start, confidence_level))
            if overlap > 0.0:
                weight = overlap / tail_prob
                es_sum += weight * scaled_losses[i - 1]

        es_fraction = es_sum
        es_monetary = es_fraction * portfolio_nav

        # Strict identity check: ES >= VaR within numerical float tolerance
        if es_fraction < var_fraction - 1e-9:
            # Fallback for extreme degenerate floating edge cases
            es_fraction = max(es_fraction, var_fraction)
            es_monetary = es_fraction * portfolio_nav

        # Warning if effective tail sample is very small (< 5 observations)
        status = RiskMetricStatus.AVAILABLE
        warning: Optional[str] = None
        if effective_tail_count < 5.0:
            status = RiskMetricStatus.AVAILABLE_WITH_WARNINGS
            warning = f"Small effective tail sample size ({effective_tail_count:.2f} observations). Statistical uncertainty is elevated."

        # Distribution & quantiles
        distribution = cls.build_loss_distribution(scaled_losses, var_fraction)

        var_result = VaRResult(
            model_type=VaRModelType.HISTORICAL_SIMULATION,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            var_fraction=var_fraction,
            var_monetary=var_monetary,
            status=status,
            warning=warning,
        )

        es_result = ExpectedShortfallResult(
            method=ExpectedShortfallMethod.EMPIRICAL_TAIL_MEAN,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            es_fraction=es_fraction,
            es_monetary=es_monetary,
            effective_tail_count=effective_tail_count,
            tail_probability=tail_prob,
            status=status,
            warning=warning,
        )

        return var_result, es_result, distribution

    @classmethod
    def calculate_parametric_var_and_es(
        cls,
        mean_return: Optional[float] = None,
        volatility: Optional[float] = None,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
        portfolio_nav: float = 1.0,
        mean: Optional[float] = None,
        standard_deviation: Optional[float] = None,
        baseline_portfolio_value: Optional[float] = None,
    ) -> Tuple[VaRResult, ExpectedShortfallResult]:
        """
        Calculates Parametric Normal Variance-Covariance VaR and Expected Shortfall.
        
        Formulas:
            mu_h = horizon_days * mu
            sigma_h = sqrt(horizon_days) * sigma
            z_alpha = Phi^{-1}(alpha)
            VaR_alpha = -mu_h + sigma_h * z_alpha
            ES_alpha = -mu_h + sigma_h * (phi(z_alpha) / (1 - alpha))
            
        Verified by Part XX Reference Fixture:
            mu = 0, sigma = 2%, alpha = 95%
            z_0.95 approx 1.64485362695
            VaR approx 3.2897073%
            ES approx 4.1254%
        """
        cls.validate_confidence(confidence_level)
        cls.validate_horizon(horizon_days)

        if baseline_portfolio_value is not None:
            portfolio_nav = baseline_portfolio_value

        mean_return = mean if mean is not None else (mean_return if mean_return is not None else 0.0)
        volatility = standard_deviation if standard_deviation is not None else (volatility if volatility is not None else 0.0)

        if volatility < 0.0 or not math.isfinite(volatility):
            raise RiskVaRNumericalFailureError(
                f"Volatility must be a finite non-negative number, got {volatility}."
            )

        if not math.isfinite(mean_return):
            raise RiskVaRNumericalFailureError(
                f"Mean return must be finite, got {mean_return}."
            )

        # Horizon scaling under Gaussian i.i.d. assumption
        mu_h = horizon_days * mean_return
        sigma_h = math.sqrt(horizon_days) * volatility

        if sigma_h == 0.0:
            # Degenerate zero-volatility model: loss is deterministic -mu_h
            var_fraction = -mu_h
            es_fraction = -mu_h
        else:
            z_alpha = stats.norm.ppf(confidence_level)
            phi_z = stats.norm.pdf(z_alpha)
            var_fraction = -mu_h + sigma_h * z_alpha
            es_fraction = -mu_h + sigma_h * (phi_z / (1.0 - confidence_level))

        var_monetary = var_fraction * portfolio_nav
        es_monetary = es_fraction * portfolio_nav

        var_result = VaRResult(
            model_type=VaRModelType.PARAMETRIC_NORMAL,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            var_fraction=var_fraction,
            var_monetary=var_monetary,
            status=RiskMetricStatus.AVAILABLE,
        )

        es_result = ExpectedShortfallResult(
            method=ExpectedShortfallMethod.PARAMETRIC_NORMAL,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            es_fraction=es_fraction,
            es_monetary=es_monetary,
            effective_tail_count=float("inf"),
            tail_probability=1.0 - confidence_level,
            status=RiskMetricStatus.AVAILABLE,
        )

        return var_result, es_result

    @classmethod
    def calculate_monte_carlo_var_and_es(
        cls,
        weights: np.ndarray,
        means: np.ndarray,
        cov_matrix: Optional[np.ndarray] = None,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
        num_simulations: int = 2500,
        random_seed: int = 42,
        portfolio_nav: float = 1.0,
        covariance_matrix: Optional[np.ndarray] = None,
        seed: Optional[int] = None,
        baseline_portfolio_value: Optional[float] = None,
    ) -> Tuple[VaRResult, ExpectedShortfallResult, LossDistribution]:
        """
        Calculates Monte Carlo Gaussian VaR and Expected Shortfall with reproducible seed.
        
        Simulates correlated returns:
            R = mu_h + A_h * Z, where A_h A_h^T = Sigma_h
            R_P = w^T R
            L = -R_P
        """
        cls.validate_confidence(confidence_level)
        cls.validate_horizon(horizon_days)

        if covariance_matrix is not None:
            cov_matrix = covariance_matrix
        if seed is not None:
            random_seed = seed
        if baseline_portfolio_value is not None:
            portfolio_nav = baseline_portfolio_value

        # Clamp simulations between 100 and 10,000 to respect resource budgets
        num_simulations = max(100, min(10000, num_simulations))

        w = np.asarray(weights, dtype=float)
        m = np.asarray(means, dtype=float)
        cov = np.asarray(cov_matrix, dtype=float)

        n_assets = len(w)
        if cov.shape != (n_assets, n_assets):
            raise RiskVaRNumericalFailureError(
                f"Covariance dimension {cov.shape} does not match weight count {n_assets}."
            )

        # Horizon scaling
        mu_h = m * horizon_days
        cov_h = cov * horizon_days

        # Eigenvalue inspection & factorization A A^T = Sigma
        eigenvalues, eigenvectors = np.linalg.eigh(cov_h)
        # Regularize to guarantee positive semi-definiteness
        clipped_eigenvalues = np.maximum(eigenvalues, 1e-7)
        sqrt_diag = np.diag(np.sqrt(clipped_eigenvalues))
        a_factor = eigenvectors @ sqrt_diag

        # Seeded standard normal generation
        rng = np.random.default_rng(random_seed)
        z = rng.standard_normal((n_assets, num_simulations))

        # Correlated simulated asset returns and portfolio returns
        sim_asset_returns = mu_h[:, np.newaxis] + a_factor @ z
        sim_port_returns = w @ sim_asset_returns
        sim_losses = -sim_port_returns

        sorted_losses = np.sort(sim_losses).tolist()

        # Compute empirical VaR and ES from simulated paths
        idx = max(0, min(num_simulations - 1, math.ceil(confidence_level * num_simulations) - 1))
        var_fraction = sorted_losses[idx]
        var_monetary = var_fraction * portfolio_nav

        tail_prob = 1.0 - confidence_level
        es_sum = 0.0
        effective_tail_count = tail_prob * num_simulations

        for i in range(1, num_simulations + 1):
            interval_start = (i - 1) / num_simulations
            interval_end = i / num_simulations
            overlap = max(0.0, min(interval_end, 1.0) - max(interval_start, confidence_level))
            if overlap > 0.0:
                weight = overlap / tail_prob
                es_sum += weight * sorted_losses[i - 1]

        es_fraction = max(es_sum, var_fraction)
        es_monetary = es_fraction * portfolio_nav

        distribution = cls.build_loss_distribution(sorted_losses, var_fraction)

        var_result = VaRResult(
            model_type=VaRModelType.MONTE_CARLO_GAUSSIAN,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            var_fraction=var_fraction,
            var_monetary=var_monetary,
            status=RiskMetricStatus.AVAILABLE,
        )

        es_result = ExpectedShortfallResult(
            method=ExpectedShortfallMethod.MONTE_CARLO,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            es_fraction=es_fraction,
            es_monetary=es_monetary,
            effective_tail_count=effective_tail_count,
            tail_probability=tail_prob,
            status=RiskMetricStatus.AVAILABLE,
        )

        return var_result, es_result, distribution

    @staticmethod
    def build_loss_distribution(
        losses: List[float],
        var_cutoff: float,
        num_bins: int = 25,
    ) -> LossDistribution:
        """Constructs histogram bins, summary quantiles, and tail losses."""
        arr = np.asarray(losses, dtype=float)
        min_loss = float(np.min(arr))
        max_loss = float(np.max(arr))
        mean_loss = float(np.mean(arr))

        counts, bin_edges = np.histogram(arr, bins=num_bins)
        bins_list = [float(b) for b in bin_edges]
        counts_list = [int(c) for c in counts]

        quantiles = {
            "p50": float(np.percentile(arr, 50)),
            "p90": float(np.percentile(arr, 90)),
            "p95": float(np.percentile(arr, 95)),
            "p97_5": float(np.percentile(arr, 97.5)),
            "p99": float(np.percentile(arr, 99)),
        }

        # Tail losses exceeding VaR cutoff
        tail_losses = [float(l) for l in arr if l >= var_cutoff]

        return LossDistribution(
            bins=bins_list,
            counts=counts_list,
            sample_count=len(arr),
            min_loss=min_loss,
            max_loss=max_loss,
            mean_loss=mean_loss,
            quantiles=quantiles,
            tail_losses=tail_losses,
        )
