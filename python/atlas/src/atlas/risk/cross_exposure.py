"""ATLAS Cross-Exposure Intelligence Engine (Stage 117).

Implements:
1. Factor x Sector 2D Exposure Matrix (b_{s,k} = sum_{i in s} w_i beta_{i,k}).
2. Currency x Sector 2D Capital Matrix.
3. Issuer x Sector 2D Capital Matrix.
4. Dimensional reconciliation and consistency checks.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .models import CrossExposureCell, CrossExposureMatrix


class CrossExposureEngine:
    """Multi-dimensional cross-exposure distribution and joint allocation analytics."""

    @staticmethod
    def build_factor_by_sector_matrix(
        symbols: List[str],
        weights: List[float],
        factor_betas: Dict[str, Dict[str, float]],
        sector_map: Dict[str, str],
        factor_ids: List[str],
    ) -> CrossExposureMatrix:
        """Constructs a 2D matrix of Factor Exposures partitioned by Economic Sector.

        For each factor k and sector s:
            b_{s,k} = sum_{i in s} w_i * beta_{i,k}

        Reconciliation Invariant:
            sum_s b_{s,k} === b_k (Total Portfolio Factor Loading)
        """
        sectors = sorted(list(set(sector_map.values())))
        if not sectors:
            sectors = ["General"]

        # Aggregate b_{s,k}
        agg: Dict[Tuple[str, str], float] = {}
        for f_id in factor_ids:
            for sec in sectors:
                agg[(f_id, sec)] = 0.0

        for i, sym in enumerate(symbols):
            w_i = weights[i] if i < len(weights) else 0.0
            sec = sector_map.get(sym, "General")
            betas = factor_betas.get(sym, {})
            for f_id in factor_ids:
                b_ik = betas.get(f_id, 0.0)
                agg[(f_id, sec)] += float(w_i * b_ik)

        cells: List[CrossExposureCell] = []
        for f_id in factor_ids:
            for sec in sectors:
                val = agg.get((f_id, sec), 0.0)
                cells.append(
                    CrossExposureCell(
                        row_key=f_id,
                        col_key=sec,
                        value=round(val, 6),
                        unit="FACTOR_LOADING",
                    )
                )

        return CrossExposureMatrix(
            row_dimension="FACTOR",
            col_dimension="SECTOR",
            row_keys=factor_ids,
            col_keys=sectors,
            cells=cells,
            unit="FACTOR_LOADING",
        )

    @staticmethod
    def build_currency_by_sector_matrix(
        symbols: List[str],
        weights: List[float],
        currency_map: Dict[str, str],
        sector_map: Dict[str, str],
    ) -> CrossExposureMatrix:
        """Constructs a 2D matrix of Portfolio Weights partitioned by Currency and Sector."""
        currencies = sorted(list(set(currency_map.values())))
        sectors = sorted(list(set(sector_map.values())))

        if not currencies:
            currencies = ["USD"]
        if not sectors:
            sectors = ["General"]

        agg: Dict[Tuple[str, str], float] = {}
        for c in currencies:
            for s in sectors:
                agg[(c, s)] = 0.0

        for i, sym in enumerate(symbols):
            w_i = weights[i] if i < len(weights) else 0.0
            c = currency_map.get(sym, "USD")
            s = sector_map.get(sym, "General")
            agg[(c, s)] += float(w_i)

        cells: List[CrossExposureCell] = []
        for c in currencies:
            for s in sectors:
                val = agg.get((c, s), 0.0)
                cells.append(
                    CrossExposureCell(
                        row_key=c,
                        col_key=s,
                        value=round(val, 6),
                        unit="WEIGHT_PERCENT",
                    )
                )

        return CrossExposureMatrix(
            row_dimension="CURRENCY",
            col_dimension="SECTOR",
            row_keys=currencies,
            col_keys=sectors,
            cells=cells,
            unit="WEIGHT_PERCENT",
        )

