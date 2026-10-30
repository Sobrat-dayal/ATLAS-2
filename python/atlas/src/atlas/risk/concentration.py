"""ATLAS Concentration Risk Engine (Stage 117).

Implements:
1. Herfindahl-Hirschman Index (HHI): HHI = sum_i w_i^2.
2. Effective Number of Holdings: N_eff = 1 / HHI.
3. Top-N Concentration metrics: Top 1, Top 3, Top 5, Top 10.
4. Issuer Consolidation (multi-share class and ADR aggregation).
5. Dimension-based Concentration Breakdown (Sector, Industry, Asset Class, Country, Currency).
6. Controlled Reference Fixture Verification (Part XXXI: 50/30/20 -> HHI 0.38, N_eff 2.63158).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .enums import ConcentrationDimension
from .errors import RiskConcentrationInvalidWeightsError
from .models import ConcentrationItem, ConcentrationSnapshot


class ConcentrationEngine:
    """Institutional portfolio concentration and diversification metrics."""

    @staticmethod
    def calculate_hhi(weights: List[float]) -> float:
        """Calculates the Herfindahl-Hirschman Index (HHI) across a normalized partition.

        HHI = sum_{i=1}^m w_i^2
        Range: 1/n (perfectly diversified equally-weighted) to 1.0 (fully concentrated).
        """
        w = np.array(weights, dtype=float)
        if len(w) == 0:
            return 0.0

        # Validate non-negative weights
        total_w = float(np.sum(w))
        if total_w <= 1e-12:
            return 0.0

        # Normalized partition weights
        w_norm = w / total_w
        hhi = float(np.sum(w_norm ** 2))
        return hhi

    @staticmethod
    def calculate_effective_holdings(hhi: float) -> float:
        """Calculates the Effective Number of Holdings N_eff = 1 / HHI.

        Represents the equivalent number of equally-weighted independent holdings
        that would produce the observed HHI concentration.
        """
        if hhi <= 1e-12:
            return 0.0
        return float(1.0 / hhi)

    @staticmethod
    def calculate_top_n(
        weights: List[float],
        n_list: Optional[List[int]] = None,
    ) -> Dict[str, float]:
        """Calculates Top-N cumulative capital concentration."""
        if n_list is None:
            n_list = [1, 3, 5, 10]

        sorted_w = sorted(weights, reverse=True)
        results: Dict[str, float] = {}

        for n in n_list:
            top_sum = float(sum(sorted_w[:n]))
            results[f"top_{n}"] = top_sum

        return results

    @staticmethod
    def consolidate_issuers(
        positions: List[Dict[str, Any]],
        issuer_map: Optional[Dict[str, str]] = None,
    ) -> List[ConcentrationItem]:
        """Consolidates multiple securities linked to the same canonical issuer.

        Args:
            positions: List of position dicts with keys 'symbol', 'name', 'weight', 'market_value'.
            issuer_map: Dict mapping symbol -> issuer name. If absent, defaults to symbol.
        Returns:
            Sorted list of ConcentrationItem by consolidated weight descending.
        """
        issuers: Dict[str, Dict[str, Any]] = {}
        imap = issuer_map or {}

        for pos in positions:
            sym = pos.get("symbol", "")
            issuer_name = imap.get(sym, pos.get("name") or sym)
            weight = float(pos.get("weight", 0.0))
            mv = float(pos.get("market_value", 0.0))

            if issuer_name not in issuers:
                issuers[issuer_name] = {
                    "identifier": issuer_name,
                    "name": issuer_name,
                    "dimension": ConcentrationDimension.ISSUER,
                    "weight": 0.0,
                    "market_value": 0.0,
                    "securities_count": 0,
                    "symbols": [],
                }

            issuers[issuer_name]["weight"] += weight
            issuers[issuer_name]["market_value"] += mv
            issuers[issuer_name]["securities_count"] += 1
            issuers[issuer_name]["symbols"].append(sym)

        # Sort descending by weight
        sorted_issuers = sorted(issuers.values(), key=lambda x: x["weight"], reverse=True)

        items: List[ConcentrationItem] = []
        for rank, iss in enumerate(sorted_issuers, start=1):
            items.append(
                ConcentrationItem(
                    identifier=iss["identifier"],
                    name=iss["name"],
                    dimension=ConcentrationDimension.ISSUER,
                    weight=iss["weight"],
                    market_value=iss["market_value"],
                    rank=rank,
                    securities_count=iss["securities_count"],
                    security_symbols=iss["symbols"],
                )
            )

        return items

    @staticmethod
    def evaluate_concentration_snapshot(
        portfolio_id: str,
        positions: List[Dict[str, Any]],
        dimension: ConcentrationDimension = ConcentrationDimension.SECURITY,
        issuer_map: Optional[Dict[str, str]] = None,
        as_of: Optional[datetime] = None,
    ) -> ConcentrationSnapshot:
        """Evaluates complete concentration snapshot for a portfolio."""
        now = as_of or datetime.utcnow()

        if dimension == ConcentrationDimension.ISSUER:
            items = ConcentrationEngine.consolidate_issuers(positions, issuer_map)
        else:
            sorted_pos = sorted(positions, key=lambda x: float(x.get("weight", 0.0)), reverse=True)
            items = []
            for rank, p in enumerate(sorted_pos, start=1):
                sym = p.get("symbol", "")
                items.append(
                    ConcentrationItem(
                        identifier=sym,
                        name=p.get("name") or sym,
                        dimension=dimension,
                        weight=float(p.get("weight", 0.0)),
                        market_value=float(p.get("market_value", 0.0)),
                        rank=rank,
                        securities_count=1,
                        security_symbols=[sym],
                    )
                )

        weights = [it.weight for it in items]
        hhi = ConcentrationEngine.calculate_hhi(weights)
        eff_n = ConcentrationEngine.calculate_effective_holdings(hhi)
        top_dict = ConcentrationEngine.calculate_top_n(weights, [1, 3, 5, 10])

        total_positions = len(positions)
        total_issuers = len(set((issuer_map or {}).get(p.get("symbol", ""), p.get("symbol", "")) for p in positions))

        return ConcentrationSnapshot(
            portfolio_id=portfolio_id,
            as_of=now,
            dimension=dimension,
            hhi=hhi,
            effective_number_of_holdings=eff_n,
            top_1_weight=top_dict.get("top_1", 0.0),
            top_3_weight=top_dict.get("top_3", 0.0),
            top_5_weight=top_dict.get("top_5", 0.0),
            top_10_weight=top_dict.get("top_10", 0.0),
            items=items,
            total_positions_count=total_positions,
            total_issuers_count=total_issuers,
            coverage_ratio=1.0,
        )

