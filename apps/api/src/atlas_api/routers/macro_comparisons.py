"""FastAPI Router for Institutional Macroeconomic Comparisons & Benchmarking (Stage 93)."""

from typing import Dict, List, Optional

from atlas.economics.comparisons import (
    ComparableIndicatorDTO,
    ComparisonEligibilityRecordDTO,
    ComparisonMatrixRequestDTO,
    ComparisonMatrixResponseDTO,
    CorrelationAnalysisRequestDTO,
    CorrelationAnalysisResponseDTO,
    DistributionStatisticsRequestDTO,
    DistributionSummaryDTO,
    DivergenceAnalysisRequestDTO,
    DivergenceAnalysisResponseDTO,
    EconomicRankingsRequestDTO,
    EconomicRankingsResponseDTO,
    GeographicCohortDTO,
    HistoricalTrendsRequestDTO,
    HistoricalTrendsResponseDTO,
    MacroComparisonError,
    MacroComparisonInsufficientSampleError,
    MacroComparisonPeriodMismatchError,
    MacroComparisonQueryLimitExceededError,
    MacroComparisonsService,
    MacroCoverageSummaryDTO,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(prefix="/api/v1/economics/comparisons", tags=["Macro Comparisons"])

# Global singleton service
_service_instance: Optional[MacroComparisonsService] = None


def get_comparison_service() -> MacroComparisonsService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MacroComparisonsService()
    return _service_instance


@router.get(
    "/indicators",
    response_model=List[ComparableIndicatorDTO],
    summary="List cross-country comparable macroeconomic indicators",
)
def list_comparable_indicators(
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> List[ComparableIndicatorDTO]:
    return service.list_indicators()


@router.get(
    "/geographies",
    response_model=List[Dict[str, str]],
    summary="List sovereign economies available for comparative benchmarking",
)
def list_comparison_geographies(
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> List[Dict[str, str]]:
    return service.list_geographies()


@router.get(
    "/cohorts",
    response_model=List[GeographicCohortDTO],
    summary="List canonical geopolitical and economic groups (G7, G20, BRICS, OECD, etc.)",
)
def list_geographic_cohorts(
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> List[GeographicCohortDTO]:
    return service.list_cohorts()


@router.post(
    "/eligibility",
    response_model=ComparisonEligibilityRecordDTO,
    summary="Check statistical comparability between a country and metric",
)
def check_indicator_eligibility(
    geography_id: str = Query(..., description="Geographic Entity ID, e.g., geo-us"),
    metric_kind: str = Query(..., description="Canonical metric kind"),
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> ComparisonEligibilityRecordDTO:
    try:
        from atlas.economics.comparisons.enums import ComparisonMetricKind
        m = ComparisonMetricKind(metric_kind)
        return service.check_eligibility(geography_id, m)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metric kind: '{metric_kind}'",
        )


@router.post(
    "/matrix",
    response_model=ComparisonMatrixResponseDTO,
    summary="Generate high-density cross-country comparison matrix",
)
def get_comparison_matrix(
    payload: ComparisonMatrixRequestDTO,
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> ComparisonMatrixResponseDTO:
    try:
        return service.get_comparison_matrix(payload)
    except MacroComparisonQueryLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except MacroComparisonError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.post(
    "/rankings",
    response_model=EconomicRankingsResponseDTO,
    summary="Calculate sovereign rankings for a specific economic indicator",
)
def calculate_rankings(
    payload: EconomicRankingsRequestDTO,
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> EconomicRankingsResponseDTO:
    try:
        return service.calculate_rankings(payload)
    except MacroComparisonError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/distributions",
    response_model=DistributionSummaryDTO,
    summary="Calculate descriptive statistics (mean, median, quartiles, std dev) for a cohort",
)
def calculate_distributions(
    payload: DistributionStatisticsRequestDTO,
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> DistributionSummaryDTO:
    try:
        return service.calculate_distributions(payload)
    except MacroComparisonInsufficientSampleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except MacroComparisonError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/history",
    response_model=HistoricalTrendsResponseDTO,
    summary="Fetch multi-country historical time series with optional base rebasing (index to 100)",
)
def get_historical_trends(
    payload: HistoricalTrendsRequestDTO,
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> HistoricalTrendsResponseDTO:
    try:
        return service.get_historical_trends(payload)
    except MacroComparisonError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/divergence",
    response_model=DivergenceAnalysisResponseDTO,
    summary="Compute pairwise historical growth or inflation differentials and ratios",
)
def calculate_divergence(
    payload: DivergenceAnalysisRequestDTO,
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> DivergenceAnalysisResponseDTO:
    try:
        return service.calculate_divergence(payload)
    except MacroComparisonPeriodMismatchError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except MacroComparisonError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/correlations",
    response_model=CorrelationAnalysisResponseDTO,
    summary="Compute Pearson or Spearman correlation across aligned economic time series",
)
def calculate_correlations(
    payload: CorrelationAnalysisRequestDTO,
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> CorrelationAnalysisResponseDTO:
    try:
        return service.calculate_correlations(payload)
    except MacroComparisonError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/coverage",
    response_model=MacroCoverageSummaryDTO,
    summary="Get coverage statistics across sovereign jurisdictions and source methodologies",
)
def get_coverage_summary(
    service: MacroComparisonsService = Depends(get_comparison_service),
) -> MacroCoverageSummaryDTO:
    return service.get_coverage_summary()
