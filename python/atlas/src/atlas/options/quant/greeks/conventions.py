"""Greeks Unit Conventions and Normalization Helpers (Stage 142)."""

from __future__ import annotations


def vega_unit_to_point(vega_unscaled: float) -> float:
    """Convert QuantLib raw vega (per 1.0 full volatility unit) to vega per 1 percentage point (0.01)."""
    return vega_unscaled / 100.0


def vega_point_to_unit(vega_point: float) -> float:
    """Convert vega per percentage point to raw vega per 1.0 volatility unit."""
    return vega_point * 100.0


def rho_unit_to_point(rho_unscaled: float) -> float:
    """Convert QuantLib raw rho (per 1.0 full rate unit) to rho per 1 percentage point (0.01)."""
    return rho_unscaled / 100.0


def rho_unit_to_bp(rho_unscaled: float) -> float:
    """Convert QuantLib raw rho to rho per 1 basis point (0.0001)."""
    return rho_unscaled / 10000.0


def theta_annual_to_per_day(theta_annual: float) -> float:
    """Convert annualized theta to theta per calendar day (using Actual/365 convention)."""
    return theta_annual / 365.0
