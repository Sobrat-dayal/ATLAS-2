"""FastAPI Router for Financial Risk Management Foundation (Stage 115).

Exposes risk metric and model catalogs, calculation execution, historical volatility,
drawdown analytics, benchmark sensitivity, and covariance-based risk contributions.
"""

from datetime import datetime
import logging
from typing import Annotated, Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.portfolios.errors import PortfolioError
from atlas.portfolios.service import PortfolioService
from atlas.risk.enums import (
    AnnualizationPolicy,
    RiskCalculationStatus,
    RiskMetricCode,
    RiskMetricStatus,
    RiskModelType,
    RiskReturnFrequency,
    RiskSubjectType,
)
from atlas.risk.errors import RiskError
from atlas.risk.models import (
    BenchmarkSensitivityResult,
    ComponentRiskContribution,
    CovarianceDiagnostics,
    DrawdownEpisode,
    RiskCalculationRun,
    RiskDataCoverage,
    RiskInputManifest,
    RiskMetricDefinition,
    RiskModelDefinition,
    RollingRiskObservation,
)
from atlas.risk.schemas import (
    BenchmarkSensitivityDTO,
    CalculateRiskRequest,
    ContributionsResponseDTO,
    CovarianceDiagnosticsDTO,
    DrawdownEpisodeDTO,
    DrawdownsResponseDTO,
    PortfolioRiskSummaryDTO,
    RiskCalculationRunDTO,
    RiskContributionItemDTO,
    RiskDataCoverageDTO,
    RiskInputManifestDTO,
    RiskMetricDefinitionDTO,
    RiskModelDefinitionDTO,
    RiskRunsListDTO,
    RollingObservationDTO,
    VolatilityResponseDTO,
)
from atlas.risk.service import RiskService
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["Risk"])

# Singleton service instances for memory persistence across calls
_portfolio_service_instance: Optional[PortfolioService] = None
_risk_service_instance: Optional[RiskService] = None


def get_portfolio_service() -> PortfolioService:
    global _portfolio_service_instance
    if _portfolio_service_instance is None:
        _portfolio_service_instance = PortfolioService()
    return _portfolio_service_instance


def get_risk_service(
    portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)]
) -> RiskService:
    global _risk_service_instance
    if _risk_service_instance is None or _risk_service_instance.portfolio_service is not portfolio_service:
        _risk_service_instance = RiskService(portfolio_service)
    return _risk_service_instance


def _handle_error(e: Exception) -> None:
    if isinstance(e, (RiskError, PortfolioError)):
        code = getattr(e, "code", e.__class__.__name__)
        message = getattr(e, "message", str(e))
        status_code = getattr(e, "status_code", 400)
        raise HTTPException(
            status_code=status_code,
            detail={"code": code, "message": message},
        )
    logger.exception("Unexpected error in risk router: %s", e)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred in the risk engine."},
    )


def _map_run_to_dto(run: RiskCalculationRun) -> RiskCalculationRunDTO:
    bench_dto: Optional[BenchmarkSensitivityDTO] = None
    if run.benchmark_sensitivity:
        b = run.benchmark_sensitivity
        bench_dto = BenchmarkSensitivityDTO(
            benchmark_id=b.benchmark_id,
            benchmark_symbol=b.benchmark_symbol,
            benchmark_name=b.benchmark_name,
            beta=b.beta,
            correlation=b.correlation,
            tracking_error_annualized=b.tracking_error_annualized,
            benchmark_volatility_annualized=b.benchmark_volatility_annualized,
            portfolio_volatility_annualized=b.portfolio_volatility_annualized,
            covariance=b.covariance,
            matched_observations=b.matched_observations,
            status=b.status,
            warning=b.warning,
        )

    cov_diag_dto: Optional[CovarianceDiagnosticsDTO] = None
    if run.covariance_diagnostics:
        c = run.covariance_diagnostics
        cov_diag_dto = CovarianceDiagnosticsDTO(
            model_name=c.model_name,
            dimensions=c.dimensions,
            is_psd=c.is_psd,
            condition_number=c.condition_number,
            min_eigenvalue=c.min_eigenvalue,
            regularization_applied=c.regularization_applied,
            diversification_ratio=c.diversification_ratio,
            correlation_matrix=c.correlation_matrix,
            symbols=c.symbols,
        )

    return RiskCalculationRunDTO(
        risk_run_id=run.risk_run_id,
        subject_id=run.subject_id,
        subject_type=run.subject_type,
        model_type=run.model_type,
        model_version=run.model_version,
        calculation_as_of=run.calculation_as_of.isoformat(),
        observation_start=run.observation_start.isoformat(),
        observation_end=run.observation_end.isoformat(),
        reporting_currency=run.reporting_currency,
        frequency=run.frequency,
        annualization_factor=run.annualization_factor,
        status=run.status,
        historical_volatility=run.historical_volatility,
        historical_variance=run.historical_variance,
        rolling_volatility_series=[
            RollingObservationDTO(
                window_end=r.window_end.isoformat(),
                metric_value=r.metric_value,
                observation_count=r.observation_count,
                is_complete=r.is_complete,
            )
            for r in run.rolling_volatility_series
        ],
        wealth_index_series=run.wealth_index_series,
        drawdown_series=run.drawdown_series,
        max_drawdown=run.max_drawdown,
        current_drawdown=run.current_drawdown,
        drawdown_episodes=[
            DrawdownEpisodeDTO(
                episode_id=ep.episode_id,
                peak_date=ep.peak_date.isoformat(),
                peak_value=ep.peak_value,
                trough_date=ep.trough_date.isoformat(),
                trough_value=ep.trough_value,
                max_drawdown=ep.max_drawdown,
                recovery_date=ep.recovery_date.isoformat() if ep.recovery_date else None,
                time_to_trough_days=ep.time_to_trough_days,
                recovery_duration_days=ep.recovery_duration_days,
                status=ep.status,
            )
            for ep in run.drawdown_episodes
        ],
        benchmark_sensitivity=bench_dto,
        model_estimated_variance=run.model_estimated_variance,
        model_estimated_volatility=run.model_estimated_volatility,
        security_contributions=[
            RiskContributionItemDTO(
                symbol=sc.symbol,
                name=sc.name,
                category_label=sc.category_label,
                weight=sc.weight,
                marginal_volatility_contribution=sc.marginal_volatility_contribution,
                component_volatility_contribution=sc.component_volatility_contribution,
                percentage_volatility_contribution=sc.percentage_volatility_contribution,
                variance_contribution=sc.variance_contribution,
            )
            for sc in run.security_contributions
        ],
        covariance_diagnostics=cov_diag_dto,
        data_coverage=RiskDataCoverageDTO(
            required_observations=run.data_coverage.required_observations,
            available_observations=run.data_coverage.available_observations,
            matched_observations=run.data_coverage.matched_observations,
            coverage_ratio=run.data_coverage.coverage_ratio,
            missing_intervals=run.data_coverage.missing_intervals,
            stale_observations=run.data_coverage.stale_observations,
            unsupported_instruments=run.data_coverage.unsupported_instruments,
            status=run.data_coverage.status,
        ),
        input_manifest=RiskInputManifestDTO(
            portfolio_valuation_id=run.input_manifest.portfolio_valuation_id,
            performance_run_id=run.input_manifest.performance_run_id,
            benchmark_id=run.input_manifest.benchmark_id,
            return_frequency=run.input_manifest.return_frequency,
            annualization_policy=run.input_manifest.annualization_policy,
            reporting_currency=run.input_manifest.reporting_currency,
            input_hash=run.input_manifest.input_hash,
        ),
        warnings=run.warnings,
        created_at=run.created_at.isoformat(),
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
    )


# -------------------------------------------------------------------------
# Core Risk Registry & Calculation Endpoints
# -------------------------------------------------------------------------


@router.get("/metrics", response_model=List[RiskMetricDefinitionDTO])
def get_metrics_catalog(
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[RiskMetricDefinitionDTO]:
    """Returns canonical definitions of all supported risk metrics."""
    defs = service.get_metric_definitions()
    return [
        RiskMetricDefinitionDTO(
            metric_code=d.metric_code,
            display_name=d.display_name,
            category=d.category,
            mathematical_formula=d.mathematical_formula,
            default_frequency=d.default_frequency,
            annualization_policy=d.annualization_policy,
            supported_subject_types=d.supported_subject_types,
            units=d.units,
            methodology_version=d.methodology_version,
        )
        for d in defs
    ]


@router.get("/models", response_model=List[RiskModelDefinitionDTO])
def get_models_catalog(
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[RiskModelDefinitionDTO]:
    """Returns supported risk calculation models and their limitations."""
    defs = service.get_model_definitions()
    return [
        RiskModelDefinitionDTO(
            model_id=d.model_id,
            model_type=d.model_type,
            version=d.version,
            display_name=d.display_name,
            description=d.description,
            allowed_metrics=d.allowed_metrics,
            limitations=d.limitations,
        )
        for d in defs
    ]


@router.post("/calculations", response_model=RiskCalculationRunDTO, status_code=status.HTTP_201_CREATED)
def calculate_risk(
    req: CalculateRiskRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskCalculationRunDTO:
    """Initiates an authorized risk calculation run for a portfolio subject."""
    if not req.subject_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SUBJECT_ID_REQUIRED", "message": "subject_id is required."},
        )
    try:
        run = service.calculate_risk(
            subject_id=req.subject_id,
            user_id=current_user.sub,
            request=req,
        )
        return _map_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/calculations/{run_id}", response_model=RiskCalculationRunDTO)
def get_risk_run(
    run_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskCalculationRunDTO:
    """Retrieves a specific risk calculation run with ownership verification."""
    try:
        run = service.get_run(run_id=run_id, user_id=current_user.sub)
        return _map_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/calculations/{run_id}/sources", response_model=RiskInputManifestDTO)
def get_risk_run_sources(
    run_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskInputManifestDTO:
    """Retrieves cryptographic input manifest and provenance metadata for a run."""
    try:
        run = service.get_run(run_id=run_id, user_id=current_user.sub)
        return RiskInputManifestDTO(
            portfolio_valuation_id=run.input_manifest.portfolio_valuation_id,
            performance_run_id=run.input_manifest.performance_run_id,
            benchmark_id=run.input_manifest.benchmark_id,
            return_frequency=run.input_manifest.return_frequency,
            annualization_policy=run.input_manifest.annualization_policy,
            reporting_currency=run.input_manifest.reporting_currency,
            input_hash=run.input_manifest.input_hash,
        )
    except Exception as e:
        _handle_error(e)


# -------------------------------------------------------------------------
# Portfolio Risk Scoped Endpoints
# -------------------------------------------------------------------------


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioRiskSummaryDTO)
def get_portfolio_risk_summary(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> PortfolioRiskSummaryDTO:
    """Returns top-level market risk KPI summary for the specified portfolio."""
    try:
        run = service.get_latest_portfolio_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        return PortfolioRiskSummaryDTO(
            portfolio_id=portfolio_id,
            risk_run_id=run.risk_run_id,
            as_of=run.calculation_as_of.isoformat(),
            reporting_currency=run.reporting_currency,
            historical_volatility=run.historical_volatility,
            model_volatility=run.model_estimated_volatility,
            max_drawdown=run.max_drawdown,
            current_drawdown=run.current_drawdown,
            beta=run.benchmark_sensitivity.beta if run.benchmark_sensitivity else None,
            correlation=run.benchmark_sensitivity.correlation if run.benchmark_sensitivity else None,
            tracking_error=run.benchmark_sensitivity.tracking_error_annualized if run.benchmark_sensitivity else None,
            coverage_ratio=run.data_coverage.coverage_ratio,
            status=run.status,
            input_hash=run.input_manifest.input_hash,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/historical", response_model=RiskCalculationRunDTO)
def get_portfolio_historical_risk(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    lookback_days: int = Query(default=90, ge=10, le=1825),
) -> RiskCalculationRunDTO:
    """Returns full historical risk calculations for the given lookback."""
    try:
        run = service.get_historical_risk(portfolio_id=portfolio_id, user_id=current_user.sub, lookback_days=lookback_days)
        return _map_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/volatility", response_model=VolatilityResponseDTO)
def get_portfolio_volatility(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> VolatilityResponseDTO:
    """Returns realized volatility, model volatility, and rolling series."""
    try:
        res = service.get_volatility(portfolio_id=portfolio_id, user_id=current_user.sub)
        return VolatilityResponseDTO(
            historical_volatility_annualized=res["historical_volatility_annualized"],
            historical_variance=res["historical_variance"],
            model_volatility_annualized=res["model_volatility_annualized"],
            annualization_factor=res["annualization_factor"],
            frequency=res["frequency"],
            rolling_series=[
                RollingObservationDTO(
                    window_end=r["window_end"],
                    metric_value=r["metric_value"],
                    observation_count=r["observation_count"],
                    is_complete=r["is_complete"],
                )
                for r in res["rolling_series"]
            ],
            status=res["status"],
        )
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/drawdowns", response_model=DrawdownsResponseDTO)
def get_portfolio_drawdowns(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> DrawdownsResponseDTO:
    """Returns wealth index, drawdown series, and historical recovery episodes."""
    try:
        res = service.get_drawdowns(portfolio_id=portfolio_id, user_id=current_user.sub)
        return DrawdownsResponseDTO(
            max_drawdown=res["max_drawdown"],
            current_drawdown=res["current_drawdown"],
            drawdown_series=res["drawdown_series"],
            wealth_index_series=res["wealth_index_series"],
            episodes=[
                DrawdownEpisodeDTO(
                    episode_id=ep["episode_id"],
                    peak_date=ep["peak_date"],
                    peak_value=ep["peak_value"],
                    trough_date=ep["trough_date"],
                    trough_value=ep["trough_value"],
                    max_drawdown=ep["max_drawdown"],
                    recovery_date=ep["recovery_date"],
                    time_to_trough_days=ep["time_to_trough_days"],
                    recovery_duration_days=ep["recovery_duration_days"],
                    status=ep["status"],
                )
                for ep in res["episodes"]
            ],
            status=res["status"],
        )
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/benchmark", response_model=BenchmarkSensitivityDTO)
def get_portfolio_benchmark_sensitivity(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    benchmark_id: Optional[str] = Query(default=None),
) -> BenchmarkSensitivityDTO:
    """Returns market beta, correlation, and active tracking error."""
    try:
        res = service.get_benchmark_sensitivity(portfolio_id=portfolio_id, user_id=current_user.sub, benchmark_id=benchmark_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "BENCHMARK_SENSITIVITY_NOT_FOUND", "message": "No sensitivity results available."},
            )
        return BenchmarkSensitivityDTO(
            benchmark_id=res.benchmark_id,
            benchmark_symbol=res.benchmark_symbol,
            benchmark_name=res.benchmark_name,
            beta=res.beta,
            correlation=res.correlation,
            tracking_error_annualized=res.tracking_error_annualized,
            benchmark_volatility_annualized=res.benchmark_volatility_annualized,
            portfolio_volatility_annualized=res.portfolio_volatility_annualized,
            covariance=res.covariance,
            matched_observations=res.matched_observations,
            status=res.status,
            warning=res.warning,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/contributions", response_model=ContributionsResponseDTO)
def get_portfolio_risk_contributions(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ContributionsResponseDTO:
    """Returns security-level risk contributions and covariance matrix diagnostics."""
    try:
        res = service.get_contributions(portfolio_id=portfolio_id, user_id=current_user.sub)
        cov_diag: Optional[CovarianceDiagnosticsDTO] = None
        if res.get("covariance_diagnostics"):
            cd = res["covariance_diagnostics"]
            cov_diag = CovarianceDiagnosticsDTO(
                model_name=cd.model_name,
                dimensions=cd.dimensions,
                is_psd=cd.is_psd,
                condition_number=cd.condition_number,
                min_eigenvalue=cd.min_eigenvalue,
                regularization_applied=cd.regularization_applied,
                diversification_ratio=cd.diversification_ratio,
                correlation_matrix=cd.correlation_matrix,
                symbols=cd.symbols,
            )

        return ContributionsResponseDTO(
            model_variance=res["model_variance"],
            model_volatility=res["model_volatility"],
            diversification_ratio=res["diversification_ratio"],
            contributions=[
                RiskContributionItemDTO(
                    symbol=c["symbol"],
                    name=c["name"],
                    category_label=c["category_label"],
                    weight=c["weight"],
                    marginal_volatility_contribution=c["marginal_volatility_contribution"],
                    component_volatility_contribution=c["component_volatility_contribution"],
                    percentage_volatility_contribution=c["percentage_volatility_contribution"],
                    variance_contribution=c["variance_contribution"],
                )
                for c in res["contributions"]
            ],
            covariance_diagnostics=cov_diag,
            status=res["status"],
        )
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/quality", response_model=RiskDataCoverageDTO)
def get_portfolio_risk_quality(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskDataCoverageDTO:
    """Returns data coverage, observation counts, and staleness diagnostics."""
    try:
        cov = service.get_data_quality(portfolio_id=portfolio_id, user_id=current_user.sub)
        return RiskDataCoverageDTO(
            required_observations=cov.required_observations,
            available_observations=cov.available_observations,
            matched_observations=cov.matched_observations,
            coverage_ratio=cov.coverage_ratio,
            missing_intervals=cov.missing_intervals,
            stale_observations=cov.stale_observations,
            unsupported_instruments=cov.unsupported_instruments,
            status=cov.status,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/runs", response_model=RiskRunsListDTO)
def list_portfolio_risk_runs(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskRunsListDTO:
    """Lists calculation history runs for the specified portfolio."""
    try:
        runs = service.list_runs(portfolio_id=portfolio_id, user_id=current_user.sub)
        return RiskRunsListDTO(
            items=[_map_run_to_dto(r) for r in runs],
            total=len(runs),
        )
    except Exception as e:
        _handle_error(e)
