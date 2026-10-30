"""ATLAS Financial Risk Foundation — Reconciliation Engine (Stage 115).

Independent verification of mathematical identities, Euler risk decomposition,
and statistical consistency checks.
"""

import math
from typing import List, Tuple
from .models import ComponentRiskContribution


class RiskReconciliationEngine:
    """Verifies internal mathematical consistency and independent recalculation identities."""

    @staticmethod
    def reconcile_risk_contributions(
        model_variance: float,
        model_volatility: float,
        contributions: List[ComponentRiskContribution],
        tolerance: float = 1e-5,
    ) -> Tuple[bool, List[str]]:
        """Verifies Euler risk decomposition identities:

        1. sum(VC_i) == model_variance
        2. sum(CRC_i) == model_volatility
        3. sum(PCR_i) == 1.0 (if volatility > 0)
        """
        errors: List[str] = []

        if not contributions:
            return True, []

        sum_vc = sum(c.variance_contribution for c in contributions)
        sum_crc = sum(c.component_volatility_contribution for c in contributions)
        sum_pcr = sum(c.percentage_volatility_contribution for c in contributions)

        # 1. Variance contribution additivity
        vc_diff = abs(sum_vc - model_variance)
        if vc_diff > tolerance:
            errors.append(
                f"Variance contributions sum {sum_vc:.6f} does not match model variance {model_variance:.6f} (diff {vc_diff:.4e})."
            )

        # 2. Volatility contribution additivity (Euler)
        crc_diff = abs(sum_crc - model_volatility)
        if crc_diff > tolerance:
            errors.append(
                f"Component volatility contributions sum {sum_crc:.6f} does not match model volatility {model_volatility:.6f} (diff {crc_diff:.4e})."
            )

        # 3. Percentage additivity (100%)
        if model_volatility > 1e-6:
            pcr_diff = abs(sum_pcr - 1.0)
            if pcr_diff > 1e-4:
                errors.append(
                    f"Percentage volatility contributions sum {sum_pcr:.4f} does not sum to 100% (diff {pcr_diff:.4e})."
                )

        return len(errors) == 0, errors

