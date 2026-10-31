"""Model Registry for Quantitative Derivative Pricing (Stage 142)."""

from __future__ import annotations

from typing import Dict, List, Optional
from atlas.options.domain import ExerciseStyle
from atlas.options.quant.domain import PricingModelFamily, QuantPricingModelDefinition
from atlas.options.quant.errors import QuantModelIncompatibleError

CANONICAL_MODELS: Dict[str, QuantPricingModelDefinition] = {
    "BLACK_SCHOLES_MERTON": QuantPricingModelDefinition(
        model_id="BLACK_SCHOLES_MERTON",
        family=PricingModelFamily.BLACK_SCHOLES_MERTON,
        name="Black-Scholes-Merton (Analytic)",
        description="Standard analytical continuous-time lognormal pricing engine for European-style vanilla options.",
        supported_exercise_styles=[ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=False,
        supports_analytic_greeks=True,
        engine_class_name="AnalyticEuropeanEngine",
    ),
    "BARONE_ADESI_WHALEY": QuantPricingModelDefinition(
        model_id="BARONE_ADESI_WHALEY",
        family=PricingModelFamily.BARONE_ADESI_WHALEY,
        name="Barone-Adesi-Whaley (American Analytic Approximation)",
        description="Quadratic approximation engine for American options with early exercise premium valuation.",
        supported_exercise_styles=[ExerciseStyle.AMERICAN, ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=False,
        supports_analytic_greeks=False,
        engine_class_name="BaroneAdesiWhaleyApproximationEngine",
    ),
    "BJERKSUND_STENSLAND": QuantPricingModelDefinition(
        model_id="BJERKSUND_STENSLAND",
        family=PricingModelFamily.BJERKSUND_STENSLAND,
        name="Bjerksund-Stensland (American Approximation)",
        description="Bjerksund-Stensland closed-form approximation for American options with flat yield curves and cost-of-carry.",
        supported_exercise_styles=[ExerciseStyle.AMERICAN, ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=False,
        supports_analytic_greeks=False,
        engine_class_name="BjerksundStenslandApproximationEngine",
    ),
    "BINOMIAL_CRR": QuantPricingModelDefinition(
        model_id="BINOMIAL_CRR",
        family=PricingModelFamily.BINOMIAL_CRR,
        name="Cox-Ross-Rubinstein Binomial Tree",
        description="Recombining lattice binomial tree supporting both American early-exercise and European exercise boundaries.",
        supported_exercise_styles=[ExerciseStyle.AMERICAN, ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=False,
        supports_analytic_greeks=False,
        engine_class_name="BinomialCRRVanillaEngine",
        default_numerical_steps=100,
    ),
    "FINITE_DIFFERENCE": QuantPricingModelDefinition(
        model_id="FINITE_DIFFERENCE",
        family=PricingModelFamily.FINITE_DIFFERENCE,
        name="Finite Difference Black-Scholes (FDM)",
        description="Crank-Nicolson / Douglas finite difference numerical engine supporting American early-exercise and discrete dividend schedules.",
        supported_exercise_styles=[ExerciseStyle.AMERICAN, ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=True,
        supports_analytic_greeks=False,
        engine_class_name="FdBlackScholesVanillaEngine",
        default_numerical_steps=100,
    ),
    "BLACK_76": QuantPricingModelDefinition(
        model_id="BLACK_76",
        family=PricingModelFamily.BLACK_76,
        name="Black-76 (Futures & Forward-Underlying)",
        description="Black-76 model for options on futures contracts, commodity forwards, and forward equity indices.",
        supported_exercise_styles=[ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=False,
        supports_analytic_greeks=True,
        engine_class_name="BlackCalculator",
    ),
    "BACHELIER": QuantPricingModelDefinition(
        model_id="BACHELIER",
        family=PricingModelFamily.BACHELIER,
        name="Bachelier Normal Model",
        description="Normal-volatility pricing model supporting zero or negative underlying price domains.",
        supported_exercise_styles=[ExerciseStyle.EUROPEAN],
        supports_discrete_dividends=False,
        supports_analytic_greeks=True,
        engine_class_name="BachelierCalculator",
    ),
}


class ModelRegistry:
    """Registry managing available pricing model definitions and validating contract compatibility."""

    def __init__(self, models: Optional[Dict[str, QuantPricingModelDefinition]] = None):
        self._models = dict(models or CANONICAL_MODELS)

    def list_models(self) -> List[QuantPricingModelDefinition]:
        return list(self._models.values())

    def get_model(self, model_id: str) -> Optional[QuantPricingModelDefinition]:
        return self._models.get(model_id.upper())

    def validate_model_compatibility(
        self,
        model_id: str,
        exercise_style: ExerciseStyle,
        has_discrete_dividends: bool = False,
    ) -> QuantPricingModelDefinition:
        """Validate that the selected model is registered and compatible with the contract terms."""
        model = self.get_model(model_id)
        if not model:
            raise QuantModelIncompatibleError(model_id, f"Model '{model_id}' is not registered.")

        if exercise_style not in model.supported_exercise_styles:
            raise QuantModelIncompatibleError(
                model_id,
                f"Model '{model.name}' does not support '{exercise_style.value}' exercise style. "
                f"Supported: {[s.value for s in model.supported_exercise_styles]}.",
            )

        if has_discrete_dividends and not model.supports_discrete_dividends:
            raise QuantModelIncompatibleError(
                model_id,
                f"Model '{model.name}' does not support discrete dividend schedules. Use 'FINITE_DIFFERENCE'.",
            )

        return model
