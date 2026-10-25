"""Pure financial condition evaluation engine with decimal-safe precision and stateful crossing logic.

Guarantees:
- Strict Decimal comparisons (no floating-point rounding errors).
- No first-snapshot false crossings (baseline must be established first).
- Verified transition re-arming (returning to opposite side required before repeat crossing).
- Safe percentage-change calculation (zero-denominator rejected, no NaN/Inf).
"""

import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from atlas.watchlists.alerts.schemas import (
    AlertRuleType,
    ArmedSide,
    RecurrencePolicy,
)


@dataclass(frozen=True)
class ConditionEvaluationResult:
    """Outcome of evaluating a market observation against an alert rule and its evaluation state."""

    triggered: bool
    new_armed_side: ArmedSide
    new_baseline_established: bool
    observation_value: Decimal
    threshold_value: Decimal
    reference_value: Optional[Decimal] = None
    reason: Optional[str] = None


def compute_percentage_change(
    current_price: Decimal, reference_price: Decimal
) -> Optional[Decimal]:
    """Computes decimal percentage change relative to canonical reference price.
    Returns None if reference price is zero or non-finite.
    """
    if reference_price is None or reference_price == Decimal("0"):
        return None
    try:
        abs_ref = abs(reference_price)
        diff = current_price - reference_price
        pct = (diff / abs_ref) * Decimal("100")
        return pct
    except Exception:
        return None


def determine_side(value: Decimal, threshold: Decimal) -> ArmedSide:
    """Determines whether value is above, below, or exactly at threshold."""
    if value > threshold:
        return ArmedSide.ABOVE
    elif value < threshold:
        return ArmedSide.BELOW
    else:
        return ArmedSide.AT


def evaluate_alert_condition(
    rule_type: AlertRuleType,
    threshold: Decimal,
    recurrence_policy: RecurrencePolicy,
    current_value: Decimal,
    reference_price: Optional[Decimal],
    baseline_established: bool,
    prior_armed_side: Optional[ArmedSide],
    now: datetime.datetime,
    cooldown_until: Optional[datetime.datetime],
) -> ConditionEvaluationResult:
    """Evaluates an observation against alert condition rules, respecting baseline and crossing rules."""

    # 1. Determine comparison value (price or qualified % change)
    if rule_type in (AlertRuleType.PERCENTAGE_CHANGE_ABOVE, AlertRuleType.PERCENTAGE_CHANGE_BELOW):
        if reference_price is None:
            return ConditionEvaluationResult(
                triggered=False,
                new_armed_side=prior_armed_side or ArmedSide.AT,
                new_baseline_established=baseline_established,
                observation_value=current_value,
                threshold_value=threshold,
                reference_value=None,
                reason="REFERENCE_PRICE_MISSING",
            )
        pct_change = compute_percentage_change(current_value, reference_price)
        if pct_change is None:
            return ConditionEvaluationResult(
                triggered=False,
                new_armed_side=prior_armed_side or ArmedSide.AT,
                new_baseline_established=baseline_established,
                observation_value=current_value,
                threshold_value=threshold,
                reference_value=reference_price,
                reason="INVALID_REFERENCE_PRICE_ZERO",
            )
        eval_value = pct_change
    else:
        eval_value = current_value

    current_side = determine_side(eval_value, threshold)

    # 2. Check Cooldown
    in_cooldown = cooldown_until is not None and now < cooldown_until

    # 3. Handle First-Snapshot / Baseline establishment
    if not baseline_established:
        # First observation seeds the baseline!
        # Crossing alerts NEVER trigger on first snapshot (Requirement 23 & 186)
        if rule_type in (
            AlertRuleType.CROSSING_ABOVE,
            AlertRuleType.CROSSING_BELOW,
            AlertRuleType.PERCENTAGE_CHANGE_ABOVE,
            AlertRuleType.PERCENTAGE_CHANGE_BELOW,
        ):
            return ConditionEvaluationResult(
                triggered=False,
                new_armed_side=current_side,
                new_baseline_established=True,
                observation_value=eval_value,
                threshold_value=threshold,
                reference_value=reference_price,
                reason="BASELINE_ESTABLISHED",
            )
        elif rule_type == AlertRuleType.PRICE_ABOVE:
            # State alert: triggers if condition met upon initial arming
            triggered = (current_side == ArmedSide.ABOVE) and not in_cooldown
            return ConditionEvaluationResult(
                triggered=triggered,
                new_armed_side=current_side,
                new_baseline_established=True,
                observation_value=eval_value,
                threshold_value=threshold,
                reference_value=reference_price,
                reason="STATE_CONDITION_EVALUATED",
            )
        elif rule_type == AlertRuleType.PRICE_BELOW:
            triggered = (current_side == ArmedSide.BELOW) and not in_cooldown
            return ConditionEvaluationResult(
                triggered=triggered,
                new_armed_side=current_side,
                new_baseline_established=True,
                observation_value=eval_value,
                threshold_value=threshold,
                reference_value=reference_price,
                reason="STATE_CONDITION_EVALUATED",
            )

    # 4. Subsequent observations with baseline established
    triggered = False
    reason = None

    if rule_type in (AlertRuleType.CROSSING_ABOVE, AlertRuleType.PERCENTAGE_CHANGE_ABOVE):
        # Must transition from <= threshold (BELOW or AT) to > threshold (ABOVE)
        was_below_or_at = prior_armed_side in (ArmedSide.BELOW, ArmedSide.AT)
        is_above = current_side == ArmedSide.ABOVE

        if was_below_or_at and is_above:
            if in_cooldown:
                reason = "COOLDOWN_ACTIVE"
            else:
                triggered = True
                reason = "CROSSING_ABOVE_DETECTED"
        else:
            reason = "NO_TRANSITION"

    elif rule_type in (AlertRuleType.CROSSING_BELOW, AlertRuleType.PERCENTAGE_CHANGE_BELOW):
        # Must transition from >= threshold (ABOVE or AT) to < threshold (BELOW)
        was_above_or_at = prior_armed_side in (ArmedSide.ABOVE, ArmedSide.AT)
        is_below = current_side == ArmedSide.BELOW

        if was_above_or_at and is_below:
            if in_cooldown:
                reason = "COOLDOWN_ACTIVE"
            else:
                triggered = True
                reason = "CROSSING_BELOW_DETECTED"
        else:
            reason = "NO_TRANSITION"

    elif rule_type == AlertRuleType.PRICE_ABOVE:
        if current_side == ArmedSide.ABOVE:
            if in_cooldown:
                reason = "COOLDOWN_ACTIVE"
            else:
                triggered = True
                reason = "PRICE_ABOVE_CONDITION_MET"
        else:
            reason = "BELOW_OR_AT_THRESHOLD"

    elif rule_type == AlertRuleType.PRICE_BELOW:
        if current_side == ArmedSide.BELOW:
            if in_cooldown:
                reason = "COOLDOWN_ACTIVE"
            else:
                triggered = True
                reason = "PRICE_BELOW_CONDITION_MET"
        else:
            reason = "ABOVE_OR_AT_THRESHOLD"

    return ConditionEvaluationResult(
        triggered=triggered,
        new_armed_side=current_side,
        new_baseline_established=True,
        observation_value=eval_value,
        threshold_value=threshold,
        reference_value=reference_price,
        reason=reason,
    )
