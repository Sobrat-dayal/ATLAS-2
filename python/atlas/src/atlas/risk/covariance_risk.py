"""ATLAS Financial Risk Foundation — Covariance-Based Model Risk Engine (Stage 115).

Calculates model-estimated portfolio variance, model volatility, marginal volatility contributions,
component risk contributions, percentage risk contributions, and Euler decomposition reconciliation.
"""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np

from .errors import (
    RiskCovarianceDimensionMismatchError,
    RiskCovarianceNotPSDError,
    RiskCovarianceNumericalFailureError,
)
from .models import ComponentRiskContribution, CovarianceDiagnostics


class ModelRiskEngine:
    """Computes analytical portfolio variance, volatility, and security-level risk contributions."""

    @staticmethod
    def validate_covariance_matrix(
        matrix: np.ndarray,
        symbols: List[str],
        regularize_if_needed: bool = True,
    ) -> Tuple[np.ndarray, bool, float, float, bool]:
        """Validates symmetry, square dimensions, and positive semi-definiteness (PSD).

        Returns:
            Tuple[clean_matrix, is_psd, min_eigenvalue, condition_number, regularization_applied]
        """
        n = len(symbols)
        if matrix.shape != (n, n):
            raise RiskCovarianceDimensionMismatchError(
                f"Covariance matrix shape {matrix.shape} does not match {n} assets."
            )

        # Enforce exact symmetry
        sym_matrix = 0.5 * (matrix + matrix.T)

        # Eigenvalue decomposition
        eigenvalues = np.linalg.eigvalsh(sym_matrix)
        min_eig = float(np.min(eigenvalues))
        max_eig = float(np.max(eigenvalues))

        is_psd = min_eig >= 1e-7
        regularization_applied = False

        if not is_psd:
            if regularize_if_needed:
                # Diagonal loading jitter to restore PSD
                jitter = abs(min_eig) + 1e-6
                sym_matrix = sym_matrix + np.eye(n) * jitter
                eigenvalues = np.linalg.eigvalsh(sym_matrix)
                min_eig = float(np.min(eigenvalues))
                max_eig = float(np.max(eigenvalues))
                is_psd = True
                regularization_applied = True
            else:
                raise RiskCovarianceNotPSDError(
                    f"Covariance matrix is not positive semi-definite; min eigenvalue is {min_eig:.4e}."
                )

        cond_number = float(max_eig / max(min_eig, 1e-12))
        return sym_matrix, is_psd, min_eig, cond_number, regularization_applied

    @staticmethod
    def compute_portfolio_variance(weights: np.ndarray, covariance: np.ndarray) -> float:
        """Computes model-estimated portfolio variance: sigma_P^2 = w^T * Sigma * w."""
        variance = float(weights.T @ covariance @ weights)
        return max(0.0, variance)

    @staticmethod
    def compute_portfolio_volatility(weights: np.ndarray, covariance: np.ndarray) -> float:
        """Computes model-estimated portfolio volatility: sigma_P = sqrt(w^T * Sigma * w)."""
        var = ModelRiskEngine.compute_portfolio_variance(weights, covariance)
        return math.sqrt(var)

    @staticmethod
    def compute_risk_contributions(
        symbols: List[str],
        names: List[str],
        categories: List[str],
        weights: np.ndarray,
        covariance: np.ndarray,
    ) -> Tuple[float, float, List[ComponentRiskContribution]]:
        """Computes Euler risk decomposition of portfolio volatility and variance by asset.

        Identities:
            VC_i = w_i * (Sigma * w)_i
            sum(VC_i) == sigma_P^2

            MRC_i = (Sigma * w)_i / sigma_P
            CRC_i = w_i * MRC_i
            sum(CRC_i) == sigma_P

            PCR_i = CRC_i / sigma_P = VC_i / sigma_P^2
            sum(PCR_i) == 1.0 (100%)
        """
        n = len(symbols)
        if len(weights) != n or covariance.shape != (n, n):
            raise RiskCovarianceDimensionMismatchError("Input dimensions do not match.")

        sigma_sq = ModelRiskEngine.compute_portfolio_variance(weights, covariance)
        sigma = math.sqrt(sigma_sq)

        # Sigma * w vector
        sigma_w = covariance @ weights

        contributions: List[ComponentRiskContribution] = []

        for i in range(n):
            sym = symbols[i]
            nm = names[i] if i < len(names) else sym
            cat = categories[i] if i < len(categories) else "Equity"
            w_i = float(weights[i])
            sw_i = float(sigma_w[i])

            # Variance contribution: w_i * (Sigma * w)_i
            vc_i = w_i * sw_i

            if sigma > 1e-12:
                # Marginal volatility contribution
                mrc_i = sw_i / sigma
                # Component volatility contribution: w_i * MRC_i
                crc_i = w_i * mrc_i
                # Percentage contribution to volatility
                pcr_i = crc_i / sigma
            else:
                mrc_i = 0.0
                crc_i = 0.0
                pcr_i = 0.0

            contributions.append(
                ComponentRiskContribution(
                    symbol=sym,
                    name=nm,
                    category_label=cat,
                    weight=w_i,
                    marginal_volatility_contribution=mrc_i,
                    component_volatility_contribution=crc_i,
                    percentage_volatility_contribution=pcr_i,
                    variance_contribution=vc_i,
                )
            )

        return sigma_sq, sigma, contributions

    @staticmethod
    def compute_covariance_diagnostics(
        symbols: List[str],
        covariance: np.ndarray,
        weights: np.ndarray,
        model_name: str = "LEDOIT_WOLF_SHRINKAGE",
    ) -> CovarianceDiagnostics:
        """Computes correlation matrix, condition number, and diversification ratio."""
        n = len(symbols)
        clean_cov, is_psd, min_eig, cond, reg_applied = (
            ModelRiskEngine.validate_covariance_matrix(covariance, symbols)
        )

        # Diagonal volatilities: sigma_i = sqrt(Sigma_ii)
        diag_vars = np.diag(clean_cov)
        diag_vols = np.sqrt(np.maximum(1e-12, diag_vars))

        # Correlation matrix: Corr_ij = Cov_ij / (sigma_i * sigma_j)
        inv_vols = 1.0 / diag_vols
        corr_matrix = clean_cov * np.outer(inv_vols, inv_vols)
        # Clamping to [-1.0, 1.0] and diagonal = 1.0
        np.clip(corr_matrix, -1.0, 1.0, out=corr_matrix)
        np.fill_diagonal(corr_matrix, 1.0)

        # Diversification Ratio: DR = sum(w_i * sigma_i) / sigma_P
        weighted_vol_sum = float(np.sum(weights * diag_vols))
        port_vol = ModelRiskEngine.compute_portfolio_volatility(weights, clean_cov)
        div_ratio = (
            float(weighted_vol_sum / port_vol) if port_vol > 1e-12 else 1.0
        )

        return CovarianceDiagnostics(
            model_name=model_name,
            dimensions=n,
            is_psd=is_psd,
            condition_number=cond,
            min_eigenvalue=min_eig,
            regularization_applied=reg_applied,
            diversification_ratio=div_ratio,
            correlation_matrix=corr_matrix.tolist(),
            symbols=symbols,
        )

