"""Implied Volatility Surface Construction Engine (Stage 142)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
from atlas.options.quant.errors import QuantInvalidVolatilitySurfaceError
from atlas.options.quant.volatility.diagnostics import ArbitrageDiagnostics


class ImpliedVolatilitySurface:
    """Represents a validated, calibrated implied volatility surface over (Strike, Expiration)."""

    def __init__(
        self,
        underlying_symbol: str,
        evaluation_date: str,
        points: List[Dict[str, Any]],
        diagnostics: List[str],
        is_calibrated: bool,
    ):
        self.underlying_symbol = underlying_symbol
        self.evaluation_date = evaluation_date
        self.points = points
        self.diagnostics = diagnostics
        self.is_calibrated = is_calibrated

    def get_volatility(self, strike: float, tte_years: float) -> Optional[float]:
        """Interpolate implied volatility for arbitrary (strike, tte)."""
        if not self.is_calibrated or not self.points:
            return None

        # Filter valid points
        valid_pts = [p for p in self.points if p.get("implied_volatility") is not None]
        if not valid_pts:
            return None

        # 1D or Nearest Neighbor / Inverse Distance Weighted interpolation
        dists = []
        for p in valid_pts:
            pk = float(p.get("strike", 0))
            pt = float(p.get("tte_years", 0))
            p_iv = float(p.get("implied_volatility", 0))

            # Normalized distance in (log(K), sqrt(T)) space
            d_k = abs(math.log(max(1.0, strike)) - math.log(max(1.0, pk)))
            d_t = abs(math.sqrt(max(0.001, tte_years)) - math.sqrt(max(0.001, pt)))
            dist = math.sqrt(d_k ** 2 + d_t ** 2)

            if dist < 1e-5:
                return p_iv
            dists.append((dist, p_iv))

        dists.sort(key=lambda x: x[0])
        nearest = dists[:3]
        total_w = sum(1.0 / (d ** 2) for d, _ in nearest)
        weighted_iv = sum((1.0 / (d ** 2)) * iv for d, iv in nearest) / total_w

        return round(weighted_iv, 4)


class VolatilitySurfaceBuilder:
    """Constructs and validates volatility surfaces from market observations."""

    @classmethod
    def build_surface(
        cls,
        underlying_symbol: str,
        evaluation_date: str,
        observations: List[Dict[str, Any]],
        strict_validation: bool = False,
    ) -> ImpliedVolatilitySurface:
        """Validate input quotes and build surface object."""
        warnings, is_valid = ArbitrageDiagnostics.validate_surface_points(observations)

        if strict_validation and not is_valid:
            raise QuantInvalidVolatilitySurfaceError(
                reason="Surface contains arbitrage violations, crossed markets, or insufficient points.",
                details={"warnings": warnings, "observations_count": len(observations)},
            )

        # Filter out crossed or negative bid points
        clean_pts: List[Dict[str, Any]] = []
        for obs in observations:
            bid = obs.get("bid")
            ask = obs.get("ask")
            iv = obs.get("implied_volatility")

            if bid is not None and ask is not None and bid > ask:
                continue  # Discard crossed market
            if bid is not None and bid < 0:
                continue  # Discard negative bid
            if iv is None or iv <= 0:
                continue

            clean_pts.append(obs)

        can_calibrate = len(clean_pts) >= 3 and is_valid

        return ImpliedVolatilitySurface(
            underlying_symbol=underlying_symbol,
            evaluation_date=evaluation_date,
            points=clean_pts,
            diagnostics=warnings,
            is_calibrated=can_calibrate,
        )

