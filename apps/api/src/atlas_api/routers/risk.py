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
    ExpectedShortfallMethod,
    KupiecTestStatus,
    RiskCalculationStatus,
    RiskMetricCode,
    RiskMetricStatus,
    RiskModelType,
    RiskReturnFrequency,
    RiskSubjectType,
    ScenarioShockType,
    ScenarioType,
    ShockTargetType,
    VaRModelType,
)
from atlas.risk.errors import RiskError
from atlas.risk.models import (
    BenchmarkSensitivityResult,
    ComponentRiskContribution,
    CovarianceDiagnostics,
    DrawdownEpisode,
    ExpectedShortfallResult,
    KupiecTestResult,
    LossDistribution,
    PortfolioRiskSnapshot,
    RiskCalculationRun,
    RiskDataCoverage,
    RiskInputManifest,
    RiskMetricDefinition,
    RiskModelDefinition,
    RiskScenario,
    RiskScenarioRun,
    RollingRiskObservation,
    ScenarioPositionResult,
    ScenarioShock,
    TailRiskCalculationRun,
    VaRBacktestRun,
    VaRExceptionObservation,
    VaRResult,
)
from atlas.risk.schemas import (
    BenchmarkSensitivityDTO,
    CalculateRiskRequest,
    CalculateTailRiskRequest,
    ContributionsResponseDTO,
    CovarianceDiagnosticsDTO,
    CreateScenarioRequest,
    DrawdownEpisodeDTO,
    DrawdownsResponseDTO,
    ExecuteScenarioRequest,
    ExpectedShortfallResultDTO,
    KupiecTestResultDTO,
    LossDistributionBinDTO,
    LossDistributionDTO,
    PortfolioRiskSummaryDTO,
    RiskCalculationRunDTO,
    RiskContributionItemDTO,
    RiskDataCoverageDTO,
    RiskInputManifestDTO,
    RiskMetricDefinitionDTO,
    RiskModelDefinitionDTO,
    RiskRunsListDTO,
    RiskScenarioDTO,
    RiskScenarioRunDTO,
    RollingObservationDTO,
    RunVaRBacktestRequest,
    ScenarioComparisonItemDTO,
    ScenarioComparisonRequest,
    ScenarioComparisonResponseDTO,
    ScenarioPositionResultDTO,
    ScenarioShockDTO,
    TailRiskCalculationRunDTO,
    VaRBacktestRunDTO,
    VaRExceptionObservationDTO,
    VaRResultDTO,
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


def _map_loss_distribution_to_dto(ld: LossDistribution) -> LossDistributionDTO:
    bins_dto: List[LossDistributionBinDTO] = []
    tot_obs = max(1, getattr(ld, "sample_count", getattr(ld, "total_observations", 1)))
    n_counts = len(getattr(ld, "counts", []))
    b_edges = getattr(ld, "bins", [])
    for i in range(n_counts):
        b_start = b_edges[i] if i < len(b_edges) else 0.0
        b_end = b_edges[i + 1] if (i + 1) < len(b_edges) else b_start
        freq = ld.counts[i]
        bins_dto.append(
            LossDistributionBinDTO(
                bin_start=float(b_start),
                bin_end=float(b_end),
                frequency=int(freq),
                relative_frequency=float(freq / tot_obs),
            )
        )

    return LossDistributionDTO(
        total_observations=tot_obs,
        min_loss=ld.min_loss,
        max_loss=ld.max_loss,
        mean_loss=ld.mean_loss,
        quantiles=ld.quantiles,
        bins=bins_dto,
        tail_losses=ld.tail_losses,
    )


def _map_tail_run_to_dto(run: TailRiskCalculationRun) -> TailRiskCalculationRunDTO:
    loss_dist_dto: Optional[LossDistributionDTO] = None
    if run.loss_distribution:
        loss_dist_dto = _map_loss_distribution_to_dto(run.loss_distribution)

    return TailRiskCalculationRunDTO(
        run_id=run.run_id,
        portfolio_id=run.portfolio_id,
        account_id=run.account_id,
        as_of=run.as_of.isoformat(),
        reporting_currency=run.reporting_currency,
        baseline_nav=run.baseline_nav,
        model_type=run.model_type,
        confidence_level=run.confidence_level,
        horizon_days=run.horizon_days,
        var=VaRResultDTO(
            model_type=run.var.model_type,
            confidence_level=run.var.confidence_level,
            horizon_days=run.var.horizon_days,
            var_return=run.var.var_return,
            var_amount=run.var.var_amount,
            effective_tail_sample_size=run.var.effective_tail_sample_size,
            total_sample_size=run.var.total_sample_size,
            method_notes=run.var.method_notes,
        ),
        expected_shortfall=ExpectedShortfallResultDTO(
            method=run.expected_shortfall.method,
            confidence_level=run.expected_shortfall.confidence_level,
            horizon_days=run.expected_shortfall.horizon_days,
            es_return=run.expected_shortfall.es_return,
            es_amount=run.expected_shortfall.es_amount,
            var_return=run.expected_shortfall.var_return,
            effective_tail_sample_size=run.expected_shortfall.effective_tail_sample_size,
            total_sample_size=run.expected_shortfall.total_sample_size,
            tail_weighting_scheme=run.expected_shortfall.tail_weighting_scheme,
        ),
        loss_distribution=loss_dist_dto,
        status=run.status,
        input_hash=run.input_hash,
        warnings=run.warnings,
        created_at=run.created_at.isoformat(),
    )


def _map_scenario_to_dto(s: RiskScenario) -> RiskScenarioDTO:
    return RiskScenarioDTO(
        scenario_id=s.scenario_id,
        name=s.name,
        scenario_type=s.scenario_type,
        description=s.description,
        shocks=[
            ScenarioShockDTO(
                shock_type=shk.shock_type,
                target_type=shk.target_type,
                target_id=shk.target_id,
                shock_percentage=shk.shock_value,
                currency_pair=getattr(shk, "currency_pair", None),
                description=shk.description,
            )
            for shk in s.shocks
        ],
        user_id=s.owner_user_id,
        organization_id=s.organization_id,
        is_system_predefined=(s.owner_user_id == "SYSTEM"),
        created_at=getattr(s, "created_at", datetime.utcnow()).isoformat(),
        updated_at=getattr(s, "updated_at", datetime.utcnow()).isoformat(),
    )


def _map_scenario_run_to_dto(r: RiskScenarioRun) -> RiskScenarioRunDTO:
    return RiskScenarioRunDTO(
        run_id=r.run_id,
        portfolio_id=r.portfolio_id,
        account_id=r.account_id,
        scenario_id=r.scenario_id,
        scenario_name=r.scenario_name,
        scenario_type=r.scenario_type,
        as_of=r.calculation_as_of.isoformat(),
        reporting_currency=getattr(r, "reporting_currency", "USD"),
        baseline_nav=r.baseline_nav,
        shocked_nav=r.shocked_nav,
        portfolio_pnl=r.portfolio_pnl,
        portfolio_scenario_return_pct=r.scenario_return,
        position_results=[
            ScenarioPositionResultDTO(
                instrument_id=p.instrument_id,
                symbol=p.symbol,
                security_name=p.symbol,
                sector=p.sector,
                currency=p.currency,
                baseline_weight=p.pre_shock_weight,
                baseline_market_value=p.pre_shock_value,
                applied_price_shock_pct=p.price_shock_pct,
                applied_fx_shock_pct=p.fx_shock_pct,
                compounded_return_pct=p.effective_total_shock_pct,
                shocked_market_value=p.post_shock_value,
                position_pnl=p.pnl_impact,
                contribution_to_portfolio_pnl_pct=p.percentage_pnl_contribution,
                shock_source_rule=p.applied_rule_description,
            )
            for p in r.position_results
        ],
        reconciliation_residual=r.reconciliation_difference,
        is_reconciled=r.reconciled,
        warnings=r.warnings,
        created_at=r.created_at.isoformat(),
    )


def _map_backtest_run_to_dto(b: VaRBacktestRun) -> VaRBacktestRunDTO:
    return VaRBacktestRunDTO(
        backtest_id=b.backtest_id,
        portfolio_id=b.portfolio_id,
        confidence_level=b.confidence_level,
        horizon_days=b.horizon_days,
        model_type=b.model_type,
        start_date=b.start_date.isoformat(),
        end_date=b.end_date.isoformat(),
        observations=[
            VaRExceptionObservationDTO(
                date=obs.date.isoformat(),
                realized_portfolio_return=obs.realized_return,
                realized_portfolio_loss=obs.realized_loss,
                var_forecast_return=obs.var_forecast,
                is_exception=obs.is_exception,
                exceedance_amount=obs.exceedance_amount,
            )
            for obs in b.observations
        ],
        kupiec_test=KupiecTestResultDTO(
            total_observations=b.kupiec_test.total_observations,
            exception_count=b.kupiec_test.exception_count,
            expected_exception_count=b.kupiec_test.expected_exceptions,
            observed_exception_rate=b.kupiec_test.observed_failure_rate,
            expected_exception_rate=b.kupiec_test.expected_failure_rate,
            likelihood_ratio_stat=b.kupiec_test.lr_statistic,
            critical_value_95=b.kupiec_test.critical_value,
            p_value=b.kupiec_test.p_value,
            status=b.kupiec_test.test_status,
            sample_adequate=b.kupiec_test.sample_adequate,
            decision_text=b.kupiec_test.decision_text,
        ),
        created_at=b.created_at.isoformat(),
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


# ============================================================================
# STAGE 116: VALUE AT RISK & EXPECTED SHORTFALL ENDPOINTS
# ============================================================================

@router.get("/tail/models")
def get_tail_risk_models() -> List[Dict[str, Any]]:
    """Returns supported VaR models, ES estimation methods, and methodology descriptions."""
    return [
        {
            "model_type": VaRModelType.HISTORICAL_SIMULATION,
            "display_name": "Historical Simulation VaR & ES",
            "description": "Non-parametric empirical quantile and exact fractional tail expectation.",
            "supported_horizons": [1, 5, 10, 20],
            "confidence_levels": [0.90, 0.95, 0.975, 0.99],
            "requires_covariance": False,
        },
        {
            "model_type": VaRModelType.PARAMETRIC_NORMAL,
            "display_name": "Parametric Normal (Delta-Normal) VaR & ES",
            "description": "Analytical Gaussian distribution quantile and closed-form tail expectation.",
            "supported_horizons": [1, 5, 10, 20],
            "confidence_levels": [0.90, 0.95, 0.975, 0.99],
            "requires_covariance": False,
        },
        {
            "model_type": VaRModelType.MONTE_CARLO_GAUSSIAN,
            "display_name": "Monte Carlo Gaussian Simulation VaR & ES",
            "description": "Multi-asset correlated Gaussian path simulation with Cholesky/eigenvalue factor decomposition.",
            "supported_horizons": [1, 5, 10, 20],
            "confidence_levels": [0.90, 0.95, 0.975, 0.99],
            "requires_covariance": True,
        },
    ]


@router.post("/tail/calculate", response_model=TailRiskCalculationRunDTO)
def calculate_tail_risk(
    request: CalculateTailRiskRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> TailRiskCalculationRunDTO:
    """Calculates on-demand Value at Risk and Expected Shortfall for a portfolio."""
    try:
        portfolio_id = request.portfolio_id or "default"
        run = service.calculate_tail_risk(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            request=request,
        )
        return _map_tail_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/tail/runs/{run_id}", response_model=TailRiskCalculationRunDTO)
def get_tail_risk_run(
    run_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> TailRiskCalculationRunDTO:
    """Retrieves a specific tail risk calculation run."""
    try:
        run = service.get_tail_run(run_id=run_id, user_id=current_user.sub)
        return _map_tail_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/tail/runs/{run_id}/distribution", response_model=LossDistributionDTO)
def get_tail_loss_distribution(
    run_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> LossDistributionDTO:
    """Retrieves loss distribution histogram and quantiles for a tail run."""
    try:
        run = service.get_tail_run(run_id=run_id, user_id=current_user.sub)
        if not run.loss_distribution:
            raise HTTPException(status_code=404, detail="Loss distribution not available for this run.")
        return _map_loss_distribution_to_dto(run.loss_distribution)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/tail", response_model=TailRiskCalculationRunDTO)
def get_portfolio_tail_risk(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    confidence_level: float = Query(0.95, gt=0.5, lt=1.0),
    horizon_days: int = Query(1, ge=1, le=252),
    model_type: VaRModelType = Query(VaRModelType.HISTORICAL_SIMULATION),
) -> TailRiskCalculationRunDTO:
    """Retrieves or calculates latest tail risk metrics for a portfolio."""
    try:
        run = service.get_latest_tail_risk(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            confidence_level=confidence_level,
            horizon_days=horizon_days,
            model_type=model_type,
        )
        return _map_tail_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


# ============================================================================
# STAGE 116: SCENARIO ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/scenarios", response_model=List[RiskScenarioDTO])
def list_risk_scenarios(
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[RiskScenarioDTO]:
    """Lists predefined historical shock library and user-defined custom scenarios."""
    try:
        scenarios = service.list_scenarios(user_id=current_user.sub)
        return [_map_scenario_to_dto(s) for s in scenarios]
    except Exception as e:
        _handle_error(e)


@router.post("/scenarios", response_model=RiskScenarioDTO)
def create_risk_scenario(
    request: CreateScenarioRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskScenarioDTO:
    """Creates a new user-defined custom shock scenario."""
    try:
        scenario = service.create_scenario(
            user_id=current_user.sub,
            request=request,
        )
        return _map_scenario_to_dto(scenario)
    except Exception as e:
        _handle_error(e)


@router.get("/scenarios/{scenario_id}", response_model=RiskScenarioDTO)
def get_risk_scenario(
    scenario_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskScenarioDTO:
    """Retrieves scenario definition by ID."""
    try:
        scenario = service.get_scenario(scenario_id=scenario_id, user_id=current_user.sub)
        return _map_scenario_to_dto(scenario)
    except Exception as e:
        _handle_error(e)


@router.post("/scenarios/{scenario_id}/execute", response_model=RiskScenarioRunDTO)
def execute_risk_scenario(
    scenario_id: str,
    portfolio_id: str = Query(...),
    request: Optional[ExecuteScenarioRequest] = None,
    service: Annotated[RiskService, Depends(get_risk_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
) -> RiskScenarioRunDTO:
    """Executes a scenario shock test on a portfolio."""
    try:
        req = request or ExecuteScenarioRequest()
        run = service.execute_scenario(
            portfolio_id=portfolio_id,
            scenario_id=scenario_id,
            user_id=current_user.sub,
            account_id=req.account_id,
            as_of=req.as_of,
        )
        return _map_scenario_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/scenarios/runs/{run_id}", response_model=RiskScenarioRunDTO)
def get_scenario_execution_run(
    run_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskScenarioRunDTO:
    """Retrieves results of a previous scenario shock evaluation."""
    try:
        run = service.get_scenario_run(run_id=run_id, user_id=current_user.sub)
        return _map_scenario_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.post("/scenarios/compare", response_model=ScenarioComparisonResponseDTO)
def compare_risk_scenarios(
    request: ScenarioComparisonRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ScenarioComparisonResponseDTO:
    """Compares multiple scenarios side by side on a portfolio."""
    try:
        runs = service.compare_scenarios(
            portfolio_id=request.portfolio_id,
            scenario_ids=request.scenario_ids,
            user_id=current_user.sub,
            account_id=request.account_id,
        )
        if not runs:
            raise HTTPException(status_code=400, detail="No scenario runs produced.")
        first = runs[0]
        return ScenarioComparisonResponseDTO(
            portfolio_id=request.portfolio_id,
            reporting_currency=getattr(first, "reporting_currency", "USD"),
            baseline_nav=first.baseline_nav,
            items=[
                ScenarioComparisonItemDTO(
                    scenario_id=r.scenario_id,
                    scenario_name=r.scenario_name,
                    scenario_type=r.scenario_type,
                    baseline_nav=r.baseline_nav,
                    shocked_nav=r.shocked_nav,
                    portfolio_pnl=r.portfolio_pnl,
                    portfolio_scenario_return_pct=r.scenario_return,
                    run_id=r.run_id,
                )
                for r in runs
            ],
        )
    except Exception as e:
        _handle_error(e)


# ============================================================================
# STAGE 116: VAR BACKTESTING & KUPIEC DIAGNOSTICS ENDPOINTS
# ============================================================================

@router.post("/tail/backtests", response_model=VaRBacktestRunDTO)
def run_var_backtest(
    request: RunVaRBacktestRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> VaRBacktestRunDTO:
    """Conducts a rolling VaR backtest with Kupiec POF unconditional coverage test."""
    try:
        run = service.run_var_backtest(
            portfolio_id=request.portfolio_id,
            user_id=current_user.sub,
            confidence_level=request.confidence_level,
            horizon_days=request.horizon_days,
            model_type=request.model_type,
            window_size=request.window_size,
        )
        return _map_backtest_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/tail/backtests/{backtest_id}", response_model=VaRBacktestRunDTO)
def get_var_backtest(
    backtest_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> VaRBacktestRunDTO:
    """Retrieves a completed VaR backtest run with exception timeline and Kupiec result."""
    try:
        run = service.get_backtest_run(backtest_id=backtest_id, user_id=current_user.sub)
        return _map_backtest_run_to_dto(run)
    except Exception as e:
        _handle_error(e)

