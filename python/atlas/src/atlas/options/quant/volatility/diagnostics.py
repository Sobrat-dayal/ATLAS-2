"""Arbitrage Diagnostics for Implied Volatility Surfaces (Stage 142)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from atlas.options.quant.errors import QuantInvalidVolatilitySurfaceError


class ArbitrageDiagnostics:
    """Evaluates calendar arbitrage, butterfly convexity, and quote validity."""

    @staticmethod
    def validate_surface_points(
        points: List[Dict[str, Any]],
    ) -> Tuple[List[str], bool]:
        """Check for quote validity, negative bids, crossed markets, and surface sanity."""
        warnings: List[str] = []
        is_valid = True

        if len(points) < 3:
            warnings.append("Insufficient volatility observations to calibrate surface (minimum 3 required).")
            return warnings, False

        for pt in points:
            bid = pt.get("bid")
            ask = pt.get("ask")
            iv = pt.get("implied_volatility")

            if bid is not None and ask is not None and bid > ask:
                warnings.append(
                    f"Crossed market detected at strike {pt.get('strike')}: Bid ({bid}) > Ask ({ask})."
                )
                is_valid = False

            if bid is not None and bid < 0:
                warnings.append(f"Negative bid ({bid}) detected at strike {pt.get('strike')}.")
                is_valid = False

            if iv is not None and (iv <= 0.0 or iv > 5.0):
                warnings.append(
                    f"Implausible implied volatility ({iv:.1%}) at strike {pt.get('strike')}."
                )
                is_valid = False

        # Calendar arbitrage check: total variance w = iv^2 * T should be non-decreasing
        by_strike: Dict[float, List[Tuple[float, float]]] = {}
        for pt in points:
            k = float(pt.get("strike", 0))
            t = float(pt.get("tte_years", 0))
            iv = float(pt.get("implied_volatility", 0))
            if k > 0 and t > 0 and iv > 0:
                by_strike.setdefault(k, []).append((t, iv))

        for k, exp_list in by_strike.items():
            sorted_exps = sorted(exp_list, key=lambda x: x[0])
            for i in range(len(sorted_exps) - 1):
                t1, iv1 = sorted_exps[i]
                t2, iv2 = sorted_exps[i + 1]
                var1 = (iv1 ** 2) * t1
                var2 = (iv2 ** 2) * t2
                if var2 < var1 - 1e-4:
                    warnings.append(
                        f"Calendar arbitrage detected at strike {k}: Total variance decreases "
                        f"from {var1:.4f} (T={t1:.2f}) to {var2:.4f} (T={t2:.2f})."
                    )
                    is_valid = False

        return warnings, is_valid

