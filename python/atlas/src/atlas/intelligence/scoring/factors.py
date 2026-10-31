"""Factor Transformations and Contribution Calculations for Intelligence Scoring (Stage 139)."""

import math
from typing import Any, Dict, Optional, Tuple
from .domain import FactorContribution, FactorTransformationMethod


class FactorMath:
    """Deterministic mathematical transformations mapping raw inputs into normalized [0.0, 1.0] intervals."""

    @staticmethod
    def transform_binary(val: Optional[bool]) -> float:
        return 1.0 if bool(val) else 0.0

    @staticmethod
    def transform_bounded_proportion(val: Optional[float], max_bound: float = 100.0) -> float:
        if val is None:
            return 0.0
        try:
            f = float(val)
            if f <= 0.0:
                return 0.0
            return min(f / max_bound, 1.0)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def transform_exponential_decay(elapsed_hours: Optional[float], half_life_hours: float = 72.0) -> float:
        if elapsed_hours is None:
            return 0.0
        try:
            h = max(0.0, float(elapsed_hours))
            return math.pow(2.0, -h / half_life_hours)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def transform_distance_step(distance_km: Optional[float]) -> float:
        if distance_km is None:
            return 0.0
        try:
            d = float(distance_km)
            if d <= 10.0:
                return 1.0
            if d <= 50.0:
                return 0.70
            if d <= 100.0:
                return 0.40
            if d <= 250.0:
                return 0.20
            return 0.05
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def transform_ordinal_count(count: Optional[int], saturation_point: int = 5) -> float:
        if count is None:
            return 0.0
        try:
            c = max(0, int(count))
            return min(float(c) / float(saturation_point), 1.0)
        except (ValueError, TypeError):
            return 0.0


def compute_factor_contribution(
    factor_id: str,
    factor_name: str,
    raw_value: Any,
    transformation_method: FactorTransformationMethod,
    weight: float,
    is_missing: bool = False,
    half_life_hours: float = 72.0,
    max_bound: float = 100.0,
    source_reference: Optional[str] = None,
) -> FactorContribution:
    """Calculates normalized factor value and contribution."""
    if is_missing or raw_value is None:
        return FactorContribution(
            factor_id=factor_id,
            factor_name=factor_name,
            raw_value=None,
            transformed_value=0.0,
            transformation_method=transformation_method,
            weight=weight,
            contribution_points=0.0,
            is_missing=True,
            source_reference=source_reference,
            explanation=f"Factor '{factor_name}' is missing; assigned 0.0 contribution points under policy.",
        )

    if transformation_method == FactorTransformationMethod.BINARY_ELIGIBILITY:
        t_val = FactorMath.transform_binary(raw_value)
        expl = f"Binary match: {'Present' if t_val > 0.5 else 'Absent'}."
    elif transformation_method == FactorTransformationMethod.BOUNDED_PROPORTION:
        t_val = FactorMath.transform_bounded_proportion(raw_value, max_bound=max_bound)
        expl = f"Proportion {raw_value}% against scale ceiling {max_bound}% = {t_val:.3f}."
    elif transformation_method == FactorTransformationMethod.EXPONENTIAL_DECAY:
        t_val = FactorMath.transform_exponential_decay(raw_value, half_life_hours=half_life_hours)
        expl = f"Recency decay: {raw_value:.1f}h elapsed with half-life {half_life_hours:.1f}h = {t_val:.3f}."
    elif transformation_method == FactorTransformationMethod.DISTANCE_STEP_FUNCTION:
        t_val = FactorMath.transform_distance_step(raw_value)
        expl = f"Proximity step: {raw_value:.1f} km distance maps to {t_val:.2f} relevance."
    elif transformation_method == FactorTransformationMethod.ORDINAL_MAPPING:
        t_val = FactorMath.transform_ordinal_count(raw_value, saturation_point=int(max_bound))
        expl = f"Count of {raw_value} against saturation cap {int(max_bound)} = {t_val:.3f}."
    else:
        t_val = FactorMath.transform_binary(raw_value)
        expl = f"Direct transformation: {raw_value}."

    contrib = t_val * weight * 100.0

    return FactorContribution(
        factor_id=factor_id,
        factor_name=factor_name,
        raw_value=raw_value,
        transformed_value=t_val,
        transformation_method=transformation_method,
        weight=weight,
        contribution_points=contrib,
        is_missing=False,
        source_reference=source_reference,
        explanation=expl,
    )
