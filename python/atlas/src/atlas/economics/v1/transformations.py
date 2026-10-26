"""Mathematical Engine for Macroeconomic Statistical Transformations (Stage 89).

Implements approved versioned statistical formulas for Level, Absolute Change,
YoY, MoM, QoQ, Annualized QoQ, Percentage Points, and Basis Points with strict
period-adjacency validation and zero/negative denominator handling.
"""

from decimal import Decimal
from typing import List, Tuple

from .enums import ReportingFrequency, StatisticalUnit, TransformationType
from .errors import EconomicCalculationError, EconomicTransformationUnsupportedError
from .models import EconomicObservationRecord, TransformationDefinition

SUPPORTED_TRANSFORMATIONS = [
    TransformationDefinition(
        transformation_type=TransformationType.SOURCE_REPORTED,
        display_name="Source Reported",
        formula_description="Raw statistical observation as published by the official provider.",
        supported_frequencies=[
            ReportingFrequency.DAILY,
            ReportingFrequency.WEEKLY,
            ReportingFrequency.MONTHLY,
            ReportingFrequency.QUARTERLY,
            ReportingFrequency.ANNUAL,
        ],
        output_unit_description="Original source unit",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.ABSOLUTE_CHANGE,
        display_name="Absolute Change (Period-over-Period)",
        formula_description="y(t) - y(t-1) in identical units.",
        supported_frequencies=[
            ReportingFrequency.DAILY,
            ReportingFrequency.MONTHLY,
            ReportingFrequency.QUARTERLY,
            ReportingFrequency.ANNUAL,
        ],
        output_unit_description="Original source unit",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.PERCENT_CHANGE,
        display_name="Percent Change (Period-over-Period)",
        formula_description="[(y(t) - y(t-1)) / y(t-1)] * 100.",
        supported_frequencies=[
            ReportingFrequency.MONTHLY,
            ReportingFrequency.QUARTERLY,
            ReportingFrequency.ANNUAL,
        ],
        output_unit_description="Percent (%)",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.YEAR_OVER_YEAR,
        display_name="Year-over-Year Growth (YoY)",
        formula_description="[(y(t) - y(t-k)) / y(t-k)] * 100, where k=12 (monthly) or k=4 (quarterly).",
        supported_frequencies=[
            ReportingFrequency.MONTHLY,
            ReportingFrequency.QUARTERLY,
        ],
        output_unit_description="Percent (%)",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.MONTH_OVER_MONTH,
        display_name="Month-over-Month Growth (MoM)",
        formula_description="[(y(t) - y(t-1)) / y(t-1)] * 100 for monthly series.",
        supported_frequencies=[ReportingFrequency.MONTHLY],
        output_unit_description="Percent (%)",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.QUARTER_OVER_QUARTER,
        display_name="Quarter-over-Quarter Growth (QoQ)",
        formula_description="[(y(t) - y(t-1)) / y(t-1)] * 100 for quarterly series.",
        supported_frequencies=[ReportingFrequency.QUARTERLY],
        output_unit_description="Percent (%)",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.ANNUALIZED_QUARTERLY_GROWTH,
        display_name="Annualized Quarterly Growth (QoQ Ann)",
        formula_description="[((y(t) / y(t-1))^4) - 1] * 100 compound annual rate for quarterly levels.",
        supported_frequencies=[ReportingFrequency.QUARTERLY],
        output_unit_description="Annualized Percent (SAAR %)",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.PERCENTAGE_POINT_CHANGE,
        display_name="Percentage Point Change (%p)",
        formula_description="r(t) - r(t-1) for rate or percentage metrics.",
        supported_frequencies=[
            ReportingFrequency.DAILY,
            ReportingFrequency.MONTHLY,
            ReportingFrequency.QUARTERLY,
            ReportingFrequency.ANNUAL,
        ],
        output_unit_description="Percentage Points (%p)",
    ),
    TransformationDefinition(
        transformation_type=TransformationType.BASIS_POINT_CHANGE,
        display_name="Basis Point Change (bps)",
        formula_description="(r(t) - r(t-1)) * 100 for interest rate series.",
        supported_frequencies=[
            ReportingFrequency.DAILY,
            ReportingFrequency.MONTHLY,
            ReportingFrequency.QUARTERLY,
            ReportingFrequency.ANNUAL,
        ],
        output_unit_description="Basis Points (bps)",
    ),
]


def apply_transformation(
    observations: List[EconomicObservationRecord],
    transformation: TransformationType,
    frequency: ReportingFrequency,
    source_unit: StatisticalUnit,
) -> Tuple[List[EconomicObservationRecord], StatisticalUnit]:
    """Applies a statistical transformation to an ordered list of observations (sorted ascending by date).

    Returns the transformed observation records and the output StatisticalUnit.
    """
    if transformation == TransformationType.SOURCE_REPORTED:
        return observations, source_unit

    if not observations or len(observations) < 2:
        return observations, source_unit

    # Validate frequency compatibility
    definition = next(
        (t for t in SUPPORTED_TRANSFORMATIONS if t.transformation_type == transformation),
        None,
    )
    if not definition:
        raise EconomicTransformationUnsupportedError(
            f"Transformation '{transformation}' is not registered."
        )

    if frequency not in definition.supported_frequencies:
        raise EconomicTransformationUnsupportedError(
            f"Transformation '{transformation}' is not supported for reporting frequency '{frequency}'. "
            f"Supported frequencies: {[f.value for f in definition.supported_frequencies]}"
        )

    transformed_records: List[EconomicObservationRecord] = []
    output_unit = source_unit

    if transformation == TransformationType.ABSOLUTE_CHANGE:
        output_unit = source_unit
        for i in range(1, len(observations)):
            curr = observations[i]
            prev = observations[i - 1]
            diff = curr.value - prev.value
            transformed_records.append(
                _clone_with_transformed_value(curr, diff, output_unit, "Absolute period change")
            )

    elif transformation in (
        TransformationType.PERCENT_CHANGE,
        TransformationType.MONTH_OVER_MONTH,
        TransformationType.QUARTER_OVER_QUARTER,
    ):
        output_unit = StatisticalUnit.PERCENT
        for i in range(1, len(observations)):
            curr = observations[i]
            prev = observations[i - 1]
            if prev.value == Decimal("0"):
                raise EconomicCalculationError(
                    f"Zero denominator encountered at period '{prev.period}' during {transformation} calculation."
                )
            pct = ((curr.value - prev.value) / abs(prev.value)) * Decimal("100")
            transformed_records.append(
                _clone_with_transformed_value(curr, pct.quantize(Decimal("0.01")), output_unit)
            )

    elif transformation == TransformationType.YEAR_OVER_YEAR:
        output_unit = StatisticalUnit.PERCENT
        k = 12 if frequency == ReportingFrequency.MONTHLY else 4
        if len(observations) <= k:
            return [], output_unit
        for i in range(k, len(observations)):
            curr = observations[i]
            prior_year = observations[i - k]
            if prior_year.value == Decimal("0"):
                continue
            yoy = ((curr.value - prior_year.value) / abs(prior_year.value)) * Decimal("100")
            transformed_records.append(
                _clone_with_transformed_value(
                    curr,
                    yoy.quantize(Decimal("0.01")),
                    output_unit,
                    f"YoY vs {prior_year.period}",
                )
            )

    elif transformation == TransformationType.ANNUALIZED_QUARTERLY_GROWTH:
        output_unit = StatisticalUnit.PERCENT
        if frequency != ReportingFrequency.QUARTERLY:
            raise EconomicTransformationUnsupportedError(
                "ANNUALIZED_QUARTERLY_GROWTH is strictly valid only for QUARTERLY reporting frequency."
            )
        for i in range(1, len(observations)):
            curr = observations[i]
            prev = observations[i - 1]
            if prev.value <= Decimal("0") or curr.value <= Decimal("0"):
                raise EconomicCalculationError(
                    f"Compound annualization requires positive index levels at periods '{prev.period}' and '{curr.period}'."
                )
            # ((curr / prev)^4 - 1) * 100
            ratio = float(curr.value) / float(prev.value)
            ann_pct = Decimal(str(round(((ratio ** 4) - 1.0) * 100.0, 2)))
            transformed_records.append(
                _clone_with_transformed_value(curr, ann_pct, output_unit, "Compound annualized QoQ rate")
            )

    elif transformation == TransformationType.PERCENTAGE_POINT_CHANGE:
        output_unit = StatisticalUnit.PERCENTAGE_POINTS
        for i in range(1, len(observations)):
            curr = observations[i]
            prev = observations[i - 1]
            pp_diff = curr.value - prev.value
            transformed_records.append(
                _clone_with_transformed_value(
                    curr, pp_diff.quantize(Decimal("0.01")), output_unit, "Percentage point difference"
                )
            )

    elif transformation == TransformationType.BASIS_POINT_CHANGE:
        output_unit = StatisticalUnit.BASIS_POINTS
        for i in range(1, len(observations)):
            curr = observations[i]
            prev = observations[i - 1]
            bps = (curr.value - prev.value) * Decimal("100")
            transformed_records.append(
                _clone_with_transformed_value(
                    curr, bps.quantize(Decimal("0.1")), output_unit, "Basis point difference"
                )
            )

    else:
        transformed_records = observations

    return transformed_records, output_unit


def _clone_with_transformed_value(
    orig: EconomicObservationRecord,
    val: Decimal,
    unit: StatisticalUnit,
    note: str = "",
) -> EconomicObservationRecord:
    return EconomicObservationRecord(
        observation_id=f"{orig.observation_id}-trans",
        series_id=orig.series_id,
        period=orig.period,
        period_start=orig.period_start,
        period_end=orig.period_end,
        reference_date=orig.reference_date,
        value=val,
        unit=unit,
        status=orig.status,
        published_at=orig.published_at,
        ingested_at=orig.ingested_at,
        revision_number=orig.revision_number,
        vintage_id=orig.vintage_id,
        notes=f"{orig.notes or ''} [{note}]".strip(),
    )
