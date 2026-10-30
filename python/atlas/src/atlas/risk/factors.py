"""ATLAS Factor Risk Engine (Stage 117).

Implements:
1. Canonical Factor Registry & Definitions.
2. Synchronized Factor Return Alignment.
3. Ordinary Least Squares (OLS) Security Factor Beta Regression.
4. Regression Diagnostics (Rank, Condition Number, Residual Variance, R^2, t-stats).
5. Exposure Matrix B and Portfolio Factor Loadings b = B^T w.
6. Benchmark-Relative Active Factor Exposures b_A = b_P - b_B.
7. Factor Covariance F and Residual Specific Covariance D.
8. Systematic and Specific Risk Decomposition:
   V_systematic = b^T F b, V_specific = w^T D w, V_total = V_systematic + V_specific.
9. Factor Variance and Volatility Contributions (Euler Decomposition):
   VC_k = b_k (F b)_k, RC_k = VC_k / sigma_P.
10. Strict Mathematical Reconciliation and Reference Fixtures (Part XIV & Part XXII).
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .enums import (
    FactorFamily,
    FactorReturnBasis,
    ModelDiagnosticStatus,
)
from .errors import (
    RiskFactorCollinearityDetectedError,
    RiskFactorCovarianceNotPSDError,
    RiskFactorNotFoundError,
    RiskFactorRegressionRankDeficientError,
    RiskFactorReturnHistoryInsufficientError,
)
from .models import (
    FactorModelDiagnostics,
    FactorRiskContribution,
    RiskFactorDefinition,
    SecurityFactorExposure,
)


# ---------------------------------------------------------------------------
# 1. Canonical Factor Registry
# ---------------------------------------------------------------------------

PREDEFINED_FACTORS: Dict[str, RiskFactorDefinition] = {
    "FACTOR_MKT": RiskFactorDefinition(
        factor_id="FACTOR_MKT",
        factor_code="MKT",
        factor_name="Market Equity Risk",
        family=FactorFamily.MARKET,
        description="Broad equity market excess return over the risk-free rate.",
        methodology="Capital Asset Pricing Model / Fama-French Market Excess Factor",
        geographical_scope="GLOBAL",
        currency="USD",
        return_basis=FactorReturnBasis.EXCESS_RETURN,
        version="1.0.0",
    ),
    "FACTOR_SMB": RiskFactorDefinition(
        factor_id="FACTOR_SMB",
        factor_code="SMB",
        factor_name="Size (Small Minus Big)",
        family=FactorFamily.STYLE,
        description="Return spread of small-cap portfolios minus large-cap portfolios.",
        methodology="Fama-French Size Factor (Market Capitalization)",
        geographical_scope="GLOBAL",
        currency="USD",
        return_basis=FactorReturnBasis.EXCESS_RETURN,
        version="1.0.0",
    ),
    "FACTOR_HML": RiskFactorDefinition(
        factor_id="FACTOR_HML",
        factor_code="HML",
        factor_name="Value (High Minus Low)",
        family=FactorFamily.STYLE,
        description="Return spread of high book-to-market (value) minus low book-to-market (growth) stocks.",
        methodology="Fama-French Value Factor (Book-to-Market Ratio)",
        geographical_scope="GLOBAL",
        currency="USD",
        return_basis=FactorReturnBasis.EXCESS_RETURN,
        version="1.0.0",
    ),
    "FACTOR_MOM": RiskFactorDefinition(
        factor_id="FACTOR_MOM",
        factor_code="MOM",
        factor_name="Momentum (Winner Minus Loser)",
        family=FactorFamily.STYLE,
        description="Return spread of 12-2 month prior return winners minus prior losers.",
        methodology="Carhart 4-Factor Momentum Factor",
        geographical_scope="GLOBAL",
        currency="USD",
        return_basis=FactorReturnBasis.EXCESS_RETURN,
        version="1.0.0",
    ),
    "FACTOR_QMJ": RiskFactorDefinition(
        factor_id="FACTOR_QMJ",
        factor_code="QMJ",
        factor_name="Quality (Quality Minus Junk)",
        family=FactorFamily.STYLE,
        description="Return spread of high-quality profitable companies minus leveraged speculative firms.",
        methodology="Asness-Frazzini-Pedersen Quality Factor",
        geographical_scope="GLOBAL",
        currency="USD",
        return_basis=FactorReturnBasis.EXCESS_RETURN,
        version="1.0.0",
    ),
    "FACTOR_CMA": RiskFactorDefinition(
        factor_id="FACTOR_CMA",
        factor_code="CMA",
        factor_name="Investment (Conservative Minus Aggressive)",
        family=FactorFamily.STYLE,
        description="Return spread of firms that invest conservatively minus aggressive capex firms.",
        methodology="Fama-French 5-Factor Investment Factor",
        geographical_scope="GLOBAL",
        currency="USD",
        return_basis=FactorReturnBasis.EXCESS_RETURN,
        version="1.0.0",
    ),
}


# ---------------------------------------------------------------------------
# 2. Factor Risk Engine
# ---------------------------------------------------------------------------

class FactorRiskEngine:
    """Scientific multi-factor exposure estimation, covariance modeling, and risk decomposition."""

    @staticmethod
    def estimate_security_betas(
        security_returns: List[float],
        factor_matrix: List[List[float]],
        include_intercept: bool = True,
    ) -> Tuple[float, List[float], float, float, Dict[str, float], FactorModelDiagnostics]:
        """Performs Ordinary Least Squares (OLS) multi-factor regression for an individual security.

        Model: r_{i,t} = alpha_i + sum_k beta_{i,k} f_{k,t} + epsilon_{i,t}
        Returns:
            intercept, betas, residual_variance, r_squared, t_stats, diagnostics
        """
        y = np.array(security_returns, dtype=float)
        T = len(y)
        F = np.array(factor_matrix, dtype=float)

        if F.ndim == 1:
            F = F.reshape(-1, 1)

        K = F.shape[1]
        warnings_list: List[str] = []

        if T < K + (2 if include_intercept else 1):
            raise RiskFactorReturnHistoryInsufficientError(
                f"Observation sample size T={T} is insufficient for K={K} factors."
            )

        # Design matrix X: [1, F]
        if include_intercept:
            X = np.column_stack([np.ones(T), F])
            num_params = K + 1
        else:
            X = F
            num_params = K

        # Rank check
        rank = int(np.linalg.matrix_rank(X))
        is_rank_deficient = rank < num_params

        # Condition number
        s = np.linalg.svd(X, compute_uv=False)
        cond = float(s[0] / s[-1]) if s[-1] > 1e-12 else float("inf")
        is_collinear = cond > 1000.0 or is_rank_deficient

        diag_status = ModelDiagnosticStatus.HEALTHY
        if is_rank_deficient:
            diag_status = ModelDiagnosticStatus.WARNING_RANK_DEFICIENT
            warnings_list.append(f"Design matrix rank {rank} is deficient for {num_params} parameters.")
        elif is_collinear:
            diag_status = ModelDiagnosticStatus.WARNING_COLLINEARITY
            warnings_list.append(f"High multicollinearity detected across factors (condition number {cond:.1f}).")

        # Solve normal equations: (X^T X) beta = X^T y using least squares
        coef, residuals_sum, _, _ = np.linalg.lstsq(X, y, rcond=None)

        if include_intercept:
            alpha = float(coef[0])
            betas = [float(b) for b in coef[1:]]
        else:
            alpha = 0.0
            betas = [float(b) for b in coef]

        # Residuals
        y_pred = X @ coef
        residuals = y - y_pred
        ss_res = float(np.sum(residuals ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))

        r_squared = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-12 else 0.0
        r_squared = max(0.0, min(1.0, r_squared))

        df_resid = max(1, T - num_params)
        residual_variance = float(ss_res / df_resid)

        # Parameter standard errors & t-statistics
        t_stats: Dict[str, float] = {}
        try:
            cov_params = np.linalg.pinv(X.T @ X) * residual_variance
            se = np.sqrt(np.maximum(1e-12, np.diag(cov_params)))
            t_vals = coef / se
            if include_intercept:
                t_stats["alpha"] = float(t_vals[0])
                for idx, tv in enumerate(t_vals[1:]):
                    t_stats[f"beta_{idx}"] = float(tv)
            else:
                for idx, tv in enumerate(t_vals):
                    t_stats[f"beta_{idx}"] = float(tv)
        except Exception:
            warnings_list.append("Could not invert normal equations for t-statistics.")

        diagnostics = FactorModelDiagnostics(
            observation_count=T,
            factor_count=K,
            design_matrix_rank=rank,
            condition_number=cond,
            is_rank_deficient=is_rank_deficient,
            is_collinear=is_collinear,
            status=diag_status,
            warnings=warnings_list,
        )

        return alpha, betas, residual_variance, r_squared, t_stats, diagnostics

    @staticmethod
    def aggregate_portfolio_factor_exposures(
        weights: List[float],
        exposure_matrix: List[List[float]],
    ) -> List[float]:
        """Calculates portfolio systematic factor exposures b = B^T w.

        Args:
            weights: Portfolio weights w in R^n.
            exposure_matrix: Security-factor exposure matrix B in R^{n x K}.
        Returns:
            Portfolio factor loading vector b in R^K.
        """
        w = np.array(weights, dtype=float)
        B = np.array(exposure_matrix, dtype=float)

        if len(w) != B.shape[0]:
            raise ValueError(
                f"Weight dimension {len(w)} does not match exposure matrix rows {B.shape[0]}."
            )

        b = B.T @ w
        return [float(x) for x in b]

    @staticmethod
    def calculate_active_factor_exposures(
        portfolio_exposures: Dict[str, float],
        benchmark_exposures: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculates benchmark-relative active factor exposures: b_A = b_P - b_B."""
        active: Dict[str, float] = {}
        for f_id, b_p in portfolio_exposures.items():
            b_b = benchmark_exposures.get(f_id, 0.0)
            active[f_id] = float(b_p - b_b)
        return active

    @staticmethod
    def estimate_factor_covariance(
        factor_return_series: List[List[float]],
        annualization_factor: float = 252.0,
    ) -> List[List[float]]:
        """Estimates annualized factor covariance matrix F = Cov(f) * K."""
        F_obs = np.array(factor_return_series, dtype=float)
        if F_obs.ndim == 1:
            F_obs = F_obs.reshape(-1, 1)

        cov = np.cov(F_obs, rowvar=False) * annualization_factor
        if cov.ndim == 0:
            cov = np.array([[float(cov)]])

        # Validate PSD
        eigvals = np.linalg.eigvalsh(cov)
        if np.min(eigvals) < -1e-6:
            raise RiskFactorCovarianceNotPSDError(
                f"Factor covariance matrix is not positive semi-definite (min eigenvalue {np.min(eigvals):.6e})."
            )

        # Symmetrize
        cov = 0.5 * (cov + cov.T)
        return cov.tolist()

    @staticmethod
    def decompose_factor_risk(
        weights: List[float],
        portfolio_factor_exposures: List[float],
        factor_covariance: List[List[float]],
        residual_variances: List[float],
        factor_ids: List[str],
        factor_names: Optional[List[str]] = None,
    ) -> Tuple[
        float,
        float,
        float,
        float,
        List[FactorRiskContribution],
        float,
        float,
        bool,
        float,
    ]:
        """Decomposes portfolio variance into systematic and specific components using Euler's theorem.

        Systematic Variance: V_systematic = b^T F b
        Specific Variance:   V_specific   = w^T D w = sum_i w_i^2 sigma_{epsilon,i}^2
        Total Variance:      V_total      = V_systematic + V_specific
        Total Volatility:    sigma_P      = sqrt(V_total)

        Factor Variance Contribution:   VC_k = b_k (F b)_k
        Factor Volatility Contribution: RC_k = VC_k / sigma_P
        Specific Volatility Contrib:    RC_spec = V_specific / sigma_P

        Reconciliation Invariants:
            sum_k VC_k === V_systematic
            sum_k VC_k + V_specific === V_total
            sum_k RC_k + RC_spec === sigma_P
        """
        w = np.array(weights, dtype=float)
        b = np.array(portfolio_factor_exposures, dtype=float)
        F = np.array(factor_covariance, dtype=float)
        d = np.array(residual_variances, dtype=float)

        K = len(b)
        if F.shape != (K, K):
            raise ValueError(f"Factor covariance dimensions {F.shape} mismatch factor count {K}.")

        names = factor_names or factor_ids

        # 1. Systematic Variance: b^T F b
        Fb = F @ b
        v_systematic = float(b.T @ Fb)

        # 2. Specific Variance: w^T D w
        v_specific = float(np.sum((w ** 2) * d))

        # 3. Total Variance and Volatility
        v_total = float(v_systematic + v_specific)
        sigma_p = math.sqrt(max(0.0, v_total))

        # 4. Factor Contributions
        contributions: List[FactorRiskContribution] = []
        vc_sum = 0.0

        for k in range(K):
            vc_k = float(b[k] * Fb[k])
            rc_k = float(vc_k / sigma_p) if sigma_p > 1e-12 else 0.0
            pvc_k = float(vc_k / v_total) if v_total > 1e-12 else 0.0

            contributions.append(
                FactorRiskContribution(
                    factor_id=factor_ids[k],
                    factor_name=names[k],
                    portfolio_exposure=float(b[k]),
                    variance_contribution=vc_k,
                    volatility_contribution=rc_k,
                    percentage_of_variance=pvc_k,
                )
            )
            vc_sum += vc_k

        # 5. Specific Risk Contributions
        rc_spec = float(v_specific / sigma_p) if sigma_p > 1e-12 else 0.0

        # 6. Reconciliation Check
        diff_sys = abs(vc_sum - v_systematic)
        diff_tot = abs((vc_sum + v_specific) - v_total)
        diff_vol = abs((sum(c.volatility_contribution for c in contributions) + rc_spec) - sigma_p)
        reconciliation_diff = max(diff_sys, diff_tot, diff_vol)
        is_reconciled = reconciliation_diff < 1e-5

        return (
            v_systematic,
            v_specific,
            v_total,
            sigma_p,
            contributions,
            rc_spec,
            v_specific,
            is_reconciled,
            reconciliation_diff,
        )

