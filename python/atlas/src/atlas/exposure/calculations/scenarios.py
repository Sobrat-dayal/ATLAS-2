"""Deterministic Scenario & Sensitivity Calculations (Stage 137).

Enforces institutional scenario invariants:
- Every scenario calculation is strictly deterministic, reproducing explicit mathematical transformations.
- Results are prominently marked as HYPOTHETICAL SCENARIO RESULT.
- Local linear sensitivity approximations (e.g. DV01 * delta_bps) are strictly labeled as first-order scenario estimates.
- Option delta-equivalent exposures computed as Contracts * Multiplier * Underlying Price * Delta without fabricated higher-order Greeks.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from atlas.exposure.domain import (
    AtlasExposureResult,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureRelationshipStrength,
    ExposureScenarioRun,
    ExposureScenarioShock,
    ExposureType,
    UncertaintyClass,
)


def evaluate_position_scenario_shocks(
    run_id: str,
    scenario_id: str,
    positions: List[Dict[str, any]],
    shocks: List[ExposureScenarioShock],
    base_currency: str = "USD"
) -> ExposureScenarioRun:
    """Evaluate hypothetical user shocks against verified positions."""
    results: List[AtlasExposureResult] = []
    total_conditional_pnl = Decimal("0.0")

    shock_map: Dict[str, ExposureScenarioShock] = {
        f"{s.target_dimension.upper()}:{s.target_identifier.upper()}": s
        for s in shocks
    }

    for pos in positions:
        pos_id = pos.get("id", "UNKNOWN")
        symbol = pos.get("symbol", "UNKNOWN")
        mv = Decimal(str(pos.get("market_value", "0.0")))
        sector = pos.get("sector", "")
        country = pos.get("country", "")

        applied_shock: Optional[ExposureScenarioShock] = None

        # Check symbol/security shock
        if f"SECURITY:{symbol.upper()}" in shock_map:
            applied_shock = shock_map[f"SECURITY:{symbol.upper()}"]
        elif f"SECTOR:{sector.upper()}" in shock_map:
            applied_shock = shock_map[f"SECTOR:{sector.upper()}"]
        elif f"COUNTRY:{country.upper()}" in shock_map:
            applied_shock = shock_map[f"COUNTRY:{country.upper()}"]

        if applied_shock:
            # Percentage shock (e.g. -10.0 means -10%)
            shock_pct = applied_shock.shock_value / Decimal("100.0")
            cond_pnl = mv * shock_pct
            total_conditional_pnl += cond_pnl

            results.append(
                AtlasExposureResult(
                    exposure_id=f"exp-scen-{run_id}-{pos_id}",
                    analysis_run_id=run_id,
                    subject_entity_ref=pos.get("node_ref"),
                    target_entity_ref=pos.get("node_ref"),
                    exposure_domain=ExposureDomain.PORTFOLIO,
                    exposure_type=ExposureType.SCENARIO_EXPOSURE,
                    exposure_measure_id="SCENARIO_CONDITIONAL_PNL_V1",
                    evidence_class=ExposureEvidenceClass.USER_DEFINED_SCENARIO,
                    relationship_strength=ExposureRelationshipStrength.ASSUMPTION_DEPENDENT,
                    amount=cond_pnl,
                    currency=base_currency,
                    unit="CURRENCY",
                    percentage=applied_shock.shock_value,
                    numerator_value=cond_pnl,
                    denominator_value=mv,
                    calculation_method_id="DETERMINISTIC_SHOCK_APPLICATION",
                    uncertainty_class=UncertaintyClass.SCENARIO_ASSUMPTION,
                    explanation=(
                        f"Hypothetical {applied_shock.shock_value}% shock applied to {symbol} "
                        f"(Value: {mv} {base_currency}) yielding conditional P&L of {cond_pnl} {base_currency}."
                    )
                )
            )

    from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
    default_ref = CanonicalGraphNodeRef(
        node_type=GraphNodeType.OTHER_SUPPORTED_CANONICAL_ENTITY,
        entity_id="PORTFOLIO_ROOT",
        canonical_name="Target Portfolio"
    )

    return ExposureScenarioRun(
        run_id=run_id,
        scenario_id=scenario_id,
        subject_entity_ref=positions[0].get("node_ref", default_ref) if positions else default_ref,
        results=results,
        total_conditional_pnl=total_conditional_pnl,
        base_currency=base_currency
    )


def calculate_dv01_sensitivity(
    dv01_per_bp: Decimal,
    rate_shift_bps: Decimal,
    currency: str = "USD"
) -> Decimal:
    """Calculate local linear dollar sensitivity for an interest rate shift.
    
    Formula: -DV01 * Delta_y_bps
    Example: DV01 = $100/bp, rate hike +25 bps -> -$2,500 approximate P&L.
    """
    return -(dv01_per_bp * rate_shift_bps)


def calculate_option_delta_equivalent(
    contracts: Decimal,
    multiplier: Decimal,
    underlying_price: Decimal,
    delta: Decimal,
    currency: str = "USD"
) -> Decimal:
    """Calculate delta-equivalent dollar exposure for an option position.
    
    Formula: Contracts * Multiplier * Underlying_Price * Delta
    """
    return contracts * multiplier * underlying_price * delta
