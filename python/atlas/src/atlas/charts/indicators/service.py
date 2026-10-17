"""Technical Indicator Calculation Service for ATLAS Charts (Stage 69).

Coordinates:
- Registration lookup and parameter validation.
- Historical bar input retrieval via canonical chart service.
- Bounded warmup lookback management.
- Deterministic calculation execution.
- Resource limits (max 5 active instances per request).
- Read-only guarantees: 0 database writes, 0 provider fetches on read.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from ..service import HistoricalChartService
from .models import (
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    IndicatorCalculationResult,
    IndicatorCatalogResponse,
    IndicatorStatus,
)
from .registry import IndicatorRegistry, default_indicator_registry

logger = logging.getLogger(__name__)

# Resource limits
MAX_INSTANCES_PER_REQUEST = 5
MAX_LOOKBACK_BARS = 1000


class TechnicalIndicatorService:
    """Service orchestrating technical indicator calculations over canonical market data."""

    def __init__(
        self,
        registry: Optional[IndicatorRegistry] = None,
        chart_service: Optional[HistoricalChartService] = None,
    ) -> None:
        self.registry = registry or default_indicator_registry
        self.chart_service = chart_service or HistoricalChartService()

    def get_catalog(self) -> IndicatorCatalogResponse:
        """Return the catalog of all registered indicator definitions."""
        return IndicatorCatalogResponse(indicators=self.registry.list_definitions())

    def calculate_indicators(
        self, request: IndicatorCalculationRequest
    ) -> IndicatorCalculationResponse:
        """Execute indicator calculations for the requested instances on a canonical instrument.

        Enforces:
        - Maximum 5 active instances per request.
        - Validated canonical instrument resolution.
        - Warmup lookback retrieval from canonical history.
        - Deterministic math with no forward look-ahead.
        """
        if not request.instances:
            raise ValueError(
                "At least one indicator instance must be provided in the calculation request."
            )

        if len(request.instances) > MAX_INSTANCES_PER_REQUEST:
            raise ValueError(
                f"Too many indicator instances requested: maximum allowed is "
                f"{MAX_INSTANCES_PER_REQUEST}, but received {len(request.instances)}."
            )

        # 1. Resolve canonical instrument metadata
        target_ident = request.instrument_id or request.symbol
        if not target_ident:
            raise ValueError("Either 'instrument_id' or 'symbol' must be provided.")

        metadata = self.chart_service.resolve_instrument(target_ident)
        if not metadata:
            raise ValueError(f"Instrument '{target_ident}' not found in canonical chart catalog.")

        # 2. Pre-validate instances and determine maximum lookback requirement
        validated_instances: List[tuple] = []
        max_lookback = 0

        for inst in request.instances:
            try:
                definition, calculator = self.registry.get(inst.indicator_id, inst.version)
            except KeyError as e:
                raise ValueError(str(e))

            # Validate parameters
            validated_params = calculator.validate_parameters(inst.parameters)
            lookback = calculator.get_required_lookback(validated_params)
            if lookback > MAX_LOOKBACK_BARS:
                raise ValueError(
                    f"Indicator '{inst.indicator_id}' requested lookback of {lookback} bars, "
                    f"which exceeds the safety limit of {MAX_LOOKBACK_BARS} bars."
                )
            if lookback > max_lookback:
                max_lookback = lookback

            validated_instances.append((inst, definition, calculator, validated_params))

        # 3. Retrieve qualified canonical historical bars with warmup lookback
        # We query with limit sufficiently large to cover visible window + max_lookback
        history_response = self.chart_service.get_chart_history(
            instrument_identifier=metadata.entity_id,
            interval=request.interval,
            start_time=None,  # fetch from earliest required to capture warmup lookback
            end_time=request.end,
            limit=min(2000, 500 + max_lookback),
        )

        bars = history_response.bars

        # 4. Compute each indicator instance deterministically
        results: List[IndicatorCalculationResult] = []

        for inst, definition, calculator, norm_params in validated_instances:
            try:
                result = calculator.calculate(
                    instance_id=inst.instance_id,
                    bars=bars,
                    params=norm_params,
                    requested_start=request.start,
                    requested_end=request.end,
                )

                # Apply client color or line width overrides if specified
                if inst.color or inst.line_width:
                    for s in result.series:
                        if inst.color:
                            s.color = inst.color
                        if inst.line_width:
                            s.line_width = inst.line_width

                results.append(result)
            except Exception as e:
                logger.error(
                    f"Error calculating indicator '{inst.indicator_id}': {e}", exc_info=True
                )
                results.append(
                    IndicatorCalculationResult(
                        instance_id=inst.instance_id,
                        indicator_id=definition.indicator_id,
                        version=definition.version,
                        parameters=norm_params,
                        rendering_target=definition.rendering_target,
                        status=IndicatorStatus.CALCULATION_ERROR,
                        error_message=f"Calculation error: {str(e)}",
                        required_lookback_bars=calculator.get_required_lookback(norm_params),
                        series=[],
                    )
                )

        return IndicatorCalculationResponse(
            instrument_entity_id=str(metadata.entity_id),
            symbol=metadata.display_symbol,
            interval=request.interval,
            calculated_at=datetime.now(timezone.utc).isoformat(),
            results=results,
        )
