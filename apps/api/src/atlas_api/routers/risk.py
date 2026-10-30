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
    ConcentrationDimension,
    BondPricingModelId,
    CouponFrequency,
    CouponType,
    DayCountConvention,
    ExerciseStyle,
    OptionType,
    OptionsPricingModelId,
    YieldCurveInterpolation,
    CurrencyExposureType,
    ExpectedShortfallMethod,
    FactorFamily,
    FactorReturnBasis,
    KupiecTestStatus,
    ModelDiagnosticStatus,
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
    ConcentrationItem,
    ConcentrationSnapshot,
    CovarianceDiagnostics,
    CrossExposureCell,
    CrossExposureMatrix,
    CurrencyExposureItem,
    CurrencyRiskSnapshot,
    DrawdownEpisode,
    ExpectedShortfallResult,
    FactorModelDiagnostics,
    FactorRiskContribution,
    FactorRiskRun,
    IndustryRiskItem,
    KupiecTestResult,
    LossDistribution,
    PortfolioRiskSnapshot,
    RiskCalculationRun,
    RiskDataCoverage,
    RiskFactorDefinition,
    RiskInputManifest,
    RiskMetricDefinition,
    RiskModelDefinition,
    RiskScenario,
    RiskScenarioRun,
    RollingRiskObservation,
    ScenarioPositionResult,
    ScenarioShock,
    SectorRiskItem,
    SectorRiskSnapshot,
    BondCashFlowItem,
    BondCashFlowSchedule,
    BondPositionRiskResult,
    BondSensitivitiesResult,
    InterestRateCurveDefinition,
    KeyRateSensitivityItem,
    OptionContractRiskInput,
    OptionGreeksResult,
    OptionPositionRiskResult,
    PortfolioFixedIncomeRiskSummary,
    PortfolioInstrumentSensitivitiesSummary,
    PortfolioOptionsRiskSummary,
    YieldCurvePoint,
    SecurityFactorExposure,
    TailRiskCalculationRun,
    VaRBacktestRun,
    VaRExceptionObservation,
    VaRResult,
)
from atlas.risk.schemas import (
    BenchmarkSensitivityDTO,
    CalculateFactorRiskRequest,
    CalculateRiskRequest,
    CalculateTailRiskRequest,
    ConcentrationItemDTO,
    ConcentrationSnapshotDTO,
    ContributionsResponseDTO,
    CovarianceDiagnosticsDTO,
    CreateScenarioRequest,
    CrossExposureCellDTO,
    CrossExposureMatrixDTO,
    CurrencyExposureItemDTO,
    CurrencyRiskSnapshotDTO,
    DrawdownEpisodeDTO,
    DrawdownsResponseDTO,
    ExecuteScenarioRequest,
    ExpectedShortfallResultDTO,
    FactorModelDiagnosticsDTO,
    FactorRiskContributionDTO,
    FactorRiskRunDTO,
    IndustryRiskItemDTO,
    KupiecTestResultDTO,
    LossDistributionBinDTO,
    LossDistributionDTO,
    PortfolioRiskSummaryDTO,
    RiskCalculationRunDTO,
    RiskContributionItemDTO,
    RiskDataCoverageDTO,
    RiskFactorDefinitionDTO,
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
    SectorRiskItemDTO,
    SectorRiskSnapshotDTO,
    BondCashFlowItemDTO,
    BondCashFlowScheduleDTO,
    BondPositionRiskDTO,
    BondSensitivitiesResultDTO,
    CalculateFixedIncomeRiskRequest,
    CalculateOptionsRiskRequest,
    InterestRateCurveDefinitionDTO,
    KeyRateSensitivityItemDTO,
    OptionGreeksResultDTO,
    OptionPositionRiskDTO,
    PortfolioFixedIncomeRiskSummaryDTO,
    PortfolioInstrumentSensitivitiesSummaryDTO,
    PortfolioOptionsRiskSummaryDTO,
    YieldCurvePointDTO,
    SecurityFactorExposureDTO,
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


def _map_option_greeks_to_dto(g: OptionGreeksResult) -> OptionGreeksResultDTO:
    return OptionGreeksResultDTO(
        theoretical_price=g.theoretical_price,
        delta=g.delta,
        gamma=g.gamma,
        vega=g.vega,
        vega_per_vol_point=g.vega_per_vol_point,
        theta=g.theta,
        theta_per_day=g.theta_per_day,
        rho=g.rho,
        rho_per_basis_point=g.rho_per_basis_point,
        intrinsic_value=g.intrinsic_value,
        time_value=g.time_value,
        implied_volatility=g.implied_volatility,
        d1=g.d1,
        d2=g.d2,
        put_call_parity_diff=g.put_call_parity_diff,
        is_pricing_valid=g.is_pricing_valid,
        pricing_model=str(g.pricing_model),
    )


def _map_option_position_to_dto(p: OptionPositionRiskResult) -> OptionPositionRiskDTO:
    return OptionPositionRiskDTO(
        position_id=p.position_id,
        instrument_id=p.instrument_id,
        underlying_symbol=p.underlying_symbol,
        option_type=p.option_type,
        exercise_style=p.exercise_style,
        strike_price=p.strike_price,
        time_to_expiry_years=p.time_to_expiry_years,
        contracts_quantity=p.contracts_quantity,
        contract_multiplier=p.contract_multiplier,
        position_market_value=p.position_market_value,
        underlying_price=p.underlying_price,
        currency=p.currency,
        base_currency=p.base_currency,
        fx_rate_to_base=p.fx_rate_to_base,
        per_contract_greeks=_map_option_greeks_to_dto(p.per_contract_greeks),
        position_delta_units=p.position_delta_units,
        position_delta_notional=p.position_delta_notional,
        position_gamma_units=p.position_gamma_units,
        position_vega_per_vol_point=p.position_vega_per_vol_point,
        position_theta_per_day=p.position_theta_per_day,
        position_rho_per_basis_point=p.position_rho_per_basis_point,
        base_currency_delta_notional=p.base_currency_delta_notional,
        base_currency_vega_per_vol_point=p.base_currency_vega_per_vol_point,
        base_currency_theta_per_day=p.base_currency_theta_per_day,
        base_currency_rho_per_basis_point=p.base_currency_rho_per_basis_point,
        approximate_pnl_shock=p.approximate_pnl_shock,
        full_reprice_pnl_shock=p.full_reprice_pnl_shock,
    )


def _map_portfolio_options_summary_to_dto(s: PortfolioOptionsRiskSummary) -> PortfolioOptionsRiskSummaryDTO:
    return PortfolioOptionsRiskSummaryDTO(
        portfolio_id=s.portfolio_id,
        as_of=s.as_of.isoformat(),
        base_currency=s.base_currency,
        total_options_market_value=s.total_options_market_value,
        options_count=s.options_count,
        net_delta_notional=s.net_delta_notional,
        gross_delta_notional=s.gross_delta_notional,
        net_vega_per_vol_point=s.net_vega_per_vol_point,
        gross_vega_per_vol_point=s.gross_vega_per_vol_point,
        net_theta_per_day=s.net_theta_per_day,
        net_rho_per_basis_point=s.net_rho_per_basis_point,
        underlying_exposures=s.underlying_exposures,
        positions=[_map_option_position_to_dto(p) for p in s.positions],
        is_complete=s.is_complete,
        warnings=s.warnings,
    )


def _map_bond_cash_flow_schedule_to_dto(s: BondCashFlowSchedule) -> BondCashFlowScheduleDTO:
    return BondCashFlowScheduleDTO(
        instrument_id=s.instrument_id,
        face_value=s.face_value,
        coupon_rate=s.coupon_rate,
        coupon_frequency=s.coupon_frequency,
        day_count_convention=s.day_count_convention,
        settlement_date=s.settlement_date.isoformat(),
        maturity_date=s.maturity_date.isoformat(),
        cash_flows=[
            BondCashFlowItemDTO(
                period_index=c.period_index,
                payment_date=c.payment_date.isoformat(),
                year_fraction=c.year_fraction,
                coupon_amount=c.coupon_amount,
                principal_amount=c.principal_amount,
                total_cash_flow=c.total_cash_flow,
                discount_factor=c.discount_factor,
                present_value=c.present_value,
            )
            for c in s.cash_flows
        ],
        accrued_interest=s.accrued_interest,
        clean_price=s.clean_price,
        dirty_price=s.dirty_price,
    )


def _map_bond_sensitivities_to_dto(s: BondSensitivitiesResult) -> BondSensitivitiesResultDTO:
    return BondSensitivitiesResultDTO(
        clean_price=s.clean_price,
        accrued_interest=s.accrued_interest,
        dirty_price=s.dirty_price,
        yield_to_maturity=s.yield_to_maturity,
        macaulay_duration=s.macaulay_duration,
        modified_duration=s.modified_duration,
        convexity=s.convexity,
        dv01_per_100_face=s.dv01_per_100_face,
        effective_duration=s.effective_duration,
        effective_convexity=s.effective_convexity,
        key_rate_durations=[
            KeyRateSensitivityItemDTO(
                tenor_name=k.tenor_name,
                tenor_years=k.tenor_years,
                key_rate_duration=k.key_rate_duration,
                key_rate_dv01=k.key_rate_dv01,
            )
            for k in s.key_rate_durations
        ],
        pricing_model=str(s.pricing_model),
    )


def _map_bond_position_to_dto(p: BondPositionRiskResult) -> BondPositionRiskDTO:
    return BondPositionRiskDTO(
        position_id=p.position_id,
        instrument_id=p.instrument_id,
        issuer_name=p.issuer_name,
        face_value=p.face_value,
        quantity=p.quantity,
        currency=p.currency,
        base_currency=p.base_currency,
        fx_rate_to_base=p.fx_rate_to_base,
        market_value=p.market_value,
        sensitivities=_map_bond_sensitivities_to_dto(p.sensitivities),
        position_dv01=p.position_dv01,
        base_currency_dv01=p.base_currency_dv01,
        cash_flow_schedule=_map_bond_cash_flow_schedule_to_dto(p.cash_flow_schedule) if p.cash_flow_schedule else None,
    )


def _map_portfolio_fixed_income_summary_to_dto(s: PortfolioFixedIncomeRiskSummary) -> PortfolioFixedIncomeRiskSummaryDTO:
    return PortfolioFixedIncomeRiskSummaryDTO(
        portfolio_id=s.portfolio_id,
        as_of=s.as_of.isoformat(),
        base_currency=s.base_currency,
        total_fixed_income_market_value=s.total_fixed_income_market_value,
        bonds_count=s.bonds_count,
        portfolio_weighted_modified_duration=s.portfolio_weighted_modified_duration,
        portfolio_weighted_macaulay_duration=s.portfolio_weighted_macaulay_duration,
        portfolio_weighted_convexity=s.portfolio_weighted_convexity,
        portfolio_weighted_yield=s.portfolio_weighted_yield,
        portfolio_total_dv01=s.portfolio_total_dv01,
        key_rate_dv01_profile=s.key_rate_dv01_profile,
        positions=[_map_bond_position_to_dto(p) for p in s.positions],
        is_complete=s.is_complete,
        warnings=s.warnings,
    )


def _map_yield_curve_to_dto(c: InterestRateCurveDefinition) -> InterestRateCurveDefinitionDTO:
    return InterestRateCurveDefinitionDTO(
        curve_id=c.curve_id,
        currency=c.currency,
        as_of=c.as_of.isoformat(),
        interpolation_method=c.interpolation_method,
        points=[
            YieldCurvePointDTO(
                tenor_years=pt.tenor_years,
                rate=pt.rate,
                label=pt.label,
                discount_factor=pt.discount_factor,
            )
            for pt in c.points
        ],
    )


def _map_instrument_sensitivities_to_dto(s: PortfolioInstrumentSensitivitiesSummary) -> PortfolioInstrumentSensitivitiesSummaryDTO:
    return PortfolioInstrumentSensitivitiesSummaryDTO(
        portfolio_id=s.portfolio_id,
        as_of=s.as_of.isoformat(),
        base_currency=s.base_currency,
        total_portfolio_value=s.total_portfolio_value,
        options_summary=_map_portfolio_options_summary_to_dto(s.options_summary) if s.options_summary else None,
        fixed_income_summary=_map_portfolio_fixed_income_summary_to_dto(s.fixed_income_summary) if s.fixed_income_summary else None,
        net_equity_delta_equivalent=s.net_equity_delta_equivalent,
        net_fixed_income_dv01=s.net_fixed_income_dv01,
    )


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



# ---------------------------------------------------------------------------
# STAGE 117: DTO MAPPERS
# ---------------------------------------------------------------------------

def _map_factor_definition_to_dto(f: RiskFactorDefinition) -> RiskFactorDefinitionDTO:
    return RiskFactorDefinitionDTO(
        factor_id=f.factor_id,
        factor_code=f.factor_code,
        factor_name=f.factor_name,
        family=f.family,
        description=f.description,
        methodology=f.methodology,
        geographical_scope=f.geographical_scope,
        currency=f.currency,
        return_basis=f.return_basis,
        version=f.version,
    )


def _map_security_factor_exposure_to_dto(s: SecurityFactorExposure) -> SecurityFactorExposureDTO:
    return SecurityFactorExposureDTO(
        symbol=s.symbol,
        factor_betas=s.factor_betas,
        intercept=s.intercept,
        residual_variance=s.residual_variance,
        r_squared=s.r_squared,
        t_stats=s.t_stats,
    )


def _map_factor_contribution_to_dto(c: FactorRiskContribution) -> FactorRiskContributionDTO:
    return FactorRiskContributionDTO(
        factor_id=c.factor_id,
        factor_name=c.factor_name,
        portfolio_exposure=c.portfolio_exposure,
        variance_contribution=c.variance_contribution,
        volatility_contribution=c.volatility_contribution,
        percentage_of_variance=c.percentage_of_variance,
    )


def _map_factor_diagnostics_to_dto(d: FactorModelDiagnostics) -> FactorModelDiagnosticsDTO:
    return FactorModelDiagnosticsDTO(
        observation_count=d.observation_count,
        factor_count=d.factor_count,
        design_matrix_rank=d.design_matrix_rank,
        condition_number=d.condition_number,
        is_rank_deficient=d.is_rank_deficient,
        is_collinear=d.is_collinear,
        status=d.status,
        warnings=d.warnings,
    )


def _map_factor_run_to_dto(run: FactorRiskRun) -> FactorRiskRunDTO:
    return FactorRiskRunDTO(
        run_id=run.run_id,
        portfolio_id=run.portfolio_id,
        as_of=run.as_of.isoformat() if hasattr(run.as_of, "isoformat") else str(run.as_of),
        model_id="FAMA_FRENCH_6",
        model_version="1.0.0",
        factor_ids=run.factor_ids,
        factor_exposures=run.portfolio_exposures,
        benchmark_exposures={fid: (1.0 if "MKT" in fid else 0.0) for fid in run.factor_ids},
        active_exposures=run.active_factor_exposures,
        systematic_variance=run.systematic_variance,
        specific_variance=run.specific_variance,
        total_variance=run.total_variance,
        total_volatility=run.portfolio_volatility,
        factor_contributions=[_map_factor_contribution_to_dto(c) for c in run.factor_contributions],
        specific_risk_contribution=run.specific_risk_contribution,
        specific_variance_contribution=run.specific_variance,
        security_exposures=[_map_security_factor_exposure_to_dto(se) for se in run.security_exposures],
        factor_covariance_matrix=run.factor_covariance_matrix,
        diagnostics=_map_factor_diagnostics_to_dto(run.diagnostics),
        is_reconciled=run.is_reconciled,
        reconciliation_diff=run.reconciliation_diff,
        created_at=run.created_at.isoformat() if hasattr(run.created_at, "isoformat") else str(run.created_at),
    )


def _map_concentration_snapshot_to_dto(c: ConcentrationSnapshot) -> ConcentrationSnapshotDTO:
    return ConcentrationSnapshotDTO(
        portfolio_id=c.portfolio_id,
        as_of=c.as_of.isoformat() if hasattr(c.as_of, "isoformat") else str(c.as_of),
        dimension=c.dimension,
        hhi=c.hhi,
        effective_number_of_holdings=c.effective_number_of_holdings,
        top_1_weight=c.top_1_weight,
        top_3_weight=c.top_3_weight,
        top_5_weight=c.top_5_weight,
        top_10_weight=c.top_10_weight,
        items=[
            ConcentrationItemDTO(
                identifier=it.identifier,
                name=it.name,
                dimension=it.dimension,
                weight=it.weight,
                market_value=it.market_value,
                rank=it.rank,
                securities_count=it.securities_count,
                security_symbols=it.security_symbols,
            )
            for it in c.items
        ],
        total_positions_count=c.total_positions_count,
        total_issuers_count=c.total_issuers_count,
        coverage_ratio=c.coverage_ratio,
    )


def _map_currency_snapshot_to_dto(c: CurrencyRiskSnapshot) -> CurrencyRiskSnapshotDTO:
    return CurrencyRiskSnapshotDTO(
        portfolio_id=c.portfolio_id,
        as_of=c.as_of.isoformat() if hasattr(c.as_of, "isoformat") else str(c.as_of),
        reporting_currency=c.reporting_currency,
        exposures=[
            CurrencyExposureItemDTO(
                currency=exp.currency,
                weight=exp.weight,
                market_value=exp.market_value,
                cash_market_value=exp.cash_market_value,
                exposure_type=exp.exposure_type,
                historical_fx_volatility=exp.historical_fx_volatility,
                fx_sensitivity_beta=exp.fx_sensitivity_beta,
            )
            for exp in c.exposures
        ],
        foreign_currency_weight=c.foreign_currency_weight,
        foreign_currency_market_value=c.foreign_currency_market_value,
        base_local_interaction=c.base_local_interaction,
        cross_currency_correlations=c.cross_currency_correlations,
    )


def _map_sector_snapshot_to_dto(s: SectorRiskSnapshot) -> SectorRiskSnapshotDTO:
    return SectorRiskSnapshotDTO(
        portfolio_id=s.portfolio_id,
        as_of=s.as_of.isoformat() if hasattr(s.as_of, "isoformat") else str(s.as_of),
        portfolio_variance=s.portfolio_variance,
        portfolio_volatility=s.portfolio_volatility,
        sectors=[
            SectorRiskItemDTO(
                sector_name=sec.sector_name,
                weight=sec.weight,
                standalone_volatility=sec.standalone_volatility,
                variance_contribution=sec.variance_contribution,
                volatility_contribution=sec.volatility_contribution,
                percentage_of_variance=sec.percentage_of_variance,
                benchmark_weight=sec.benchmark_weight,
                active_weight=sec.active_weight,
            )
            for sec in s.sectors
        ],
        industries=[
            IndustryRiskItemDTO(
                sector_name=ind.sector_name,
                industry_name=ind.industry_name,
                weight=ind.weight,
                variance_contribution=ind.variance_contribution,
                volatility_contribution=ind.volatility_contribution,
            )
            for ind in s.industries
        ],
        sector_correlation_matrix=s.sector_correlation_matrix,
        is_reconciled=s.is_reconciled,
        reconciliation_diff=s.reconciliation_diff,
    )


def _map_cross_exposure_matrix_to_dto(m: CrossExposureMatrix) -> CrossExposureMatrixDTO:
    return CrossExposureMatrixDTO(
        row_dimension=m.row_dimension,
        col_dimension=m.col_dimension,
        row_keys=m.row_keys,
        col_keys=m.col_keys,
        cells=[
            CrossExposureCellDTO(
                row_key=c.row_key,
                col_key=c.col_key,
                value=c.value,
                unit=c.unit,
            )
            for c in m.cells
        ],
        unit=m.unit,
    )


# ============================================================================
# STAGE 117: MULTI-FACTOR, CONCENTRATION, CURRENCY, AND SECTOR RISK ENDPOINTS
# ============================================================================

@router.get("/factors", response_model=List[RiskFactorDefinitionDTO])
def list_risk_factors(
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[RiskFactorDefinitionDTO]:
    """Lists canonical economic and style risk factors in the platform registry."""
    try:
        factors = service.list_factors()
        return [_map_factor_definition_to_dto(f) for f in factors]
    except Exception as e:
        _handle_error(e)


@router.get("/factors/{factor_id}", response_model=RiskFactorDefinitionDTO)
def get_risk_factor(
    factor_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> RiskFactorDefinitionDTO:
    """Retrieves definition and methodology for a specific risk factor."""
    try:
        factor = service.get_factor(factor_id)
        return _map_factor_definition_to_dto(factor)
    except Exception as e:
        _handle_error(e)


@router.post("/factor-models/calculate", response_model=FactorRiskRunDTO)
def calculate_factor_risk(
    request: CalculateFactorRiskRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> FactorRiskRunDTO:
    """Executes multi-factor regression, covariance estimation, and Euler risk decomposition."""
    try:
        run = service.calculate_factor_risk(
            portfolio_id=request.portfolio_id,
            request=request,
            user_id=current_user.sub,
        )
        return _map_factor_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/factors", response_model=FactorRiskRunDTO)
def get_portfolio_factors(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> FactorRiskRunDTO:
    """Retrieves the latest multi-factor risk run and Euler decomposition for a portfolio."""
    try:
        run = service.get_latest_factor_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        if not run:
            run = service.calculate_factor_risk(
                portfolio_id=portfolio_id,
                request=CalculateFactorRiskRequest(portfolio_id=portfolio_id),
                user_id=current_user.sub,
            )
        return _map_factor_run_to_dto(run)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/factors/exposures", response_model=List[SecurityFactorExposureDTO])
def get_portfolio_factor_exposures(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[SecurityFactorExposureDTO]:
    """Retrieves security-level factor loadings, intercepts, and R-squared metrics."""
    try:
        run = service.get_latest_factor_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        if not run:
            run = service.calculate_factor_risk(
                portfolio_id=portfolio_id,
                request=CalculateFactorRiskRequest(portfolio_id=portfolio_id),
                user_id=current_user.sub,
            )
        return [_map_security_factor_exposure_to_dto(se) for se in run.security_exposures]
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/factors/contributions", response_model=List[FactorRiskContributionDTO])
def get_portfolio_factor_contributions(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[FactorRiskContributionDTO]:
    """Retrieves systematic Euler factor variance and volatility contributions."""
    try:
        run = service.get_latest_factor_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        if not run:
            run = service.calculate_factor_risk(
                portfolio_id=portfolio_id,
                request=CalculateFactorRiskRequest(portfolio_id=portfolio_id),
                user_id=current_user.sub,
            )
        return [_map_factor_contribution_to_dto(c) for c in run.factor_contributions]
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/factors/diagnostics", response_model=FactorModelDiagnosticsDTO)
def get_portfolio_factor_diagnostics(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> FactorModelDiagnosticsDTO:
    """Retrieves regression health, rank check, condition number, and collinearity diagnostics."""
    try:
        run = service.get_latest_factor_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        if not run:
            run = service.calculate_factor_risk(
                portfolio_id=portfolio_id,
                request=CalculateFactorRiskRequest(portfolio_id=portfolio_id),
                user_id=current_user.sub,
            )
        return _map_factor_diagnostics_to_dto(run.diagnostics)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/concentration", response_model=ConcentrationSnapshotDTO)
def get_portfolio_concentration(
    portfolio_id: str,
    dimension: ConcentrationDimension = ConcentrationDimension.SECURITY,
    service: Annotated[RiskService, Depends(get_risk_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
) -> ConcentrationSnapshotDTO:
    """Retrieves HHI, Effective Holdings, and Top-N concentration for the selected dimension."""
    try:
        snap = service.get_portfolio_concentration(
            portfolio_id=portfolio_id,
            dimension=dimension,
            user_id=current_user.sub,
        )
        return _map_concentration_snapshot_to_dto(snap)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/concentration/issuers", response_model=ConcentrationSnapshotDTO)
def get_portfolio_issuer_concentration(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ConcentrationSnapshotDTO:
    """Retrieves consolidated issuer concentration, aggregating share classes and ADRs."""
    try:
        snap = service.get_portfolio_concentration(
            portfolio_id=portfolio_id,
            dimension=ConcentrationDimension.ISSUER,
            user_id=current_user.sub,
        )
        return _map_concentration_snapshot_to_dto(snap)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/currencies", response_model=CurrencyRiskSnapshotDTO)
def get_portfolio_currency_risk(
    portfolio_id: str,
    reporting_currency: Optional[str] = None,
    service: Annotated[RiskService, Depends(get_risk_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
) -> CurrencyRiskSnapshotDTO:
    """Retrieves currency denomination exposures, FX volatilities, and base/local decomposition."""
    try:
        snap = service.get_portfolio_currency_risk(
            portfolio_id=portfolio_id,
            reporting_currency=reporting_currency,
            user_id=current_user.sub,
        )
        return _map_currency_snapshot_to_dto(snap)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/currencies/exposures", response_model=List[CurrencyExposureItemDTO])
def get_portfolio_currency_exposures(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[CurrencyExposureItemDTO]:
    """Retrieves granular currency denomination exposure items and FX betas."""
    try:
        snap = service.get_portfolio_currency_risk(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
        )
        dto = _map_currency_snapshot_to_dto(snap)
        return dto.exposures
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/currencies/sensitivity")
def get_portfolio_currency_sensitivity(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Retrieves base vs local return interaction and empirical FX sensitivities."""
    try:
        snap = service.get_portfolio_currency_risk(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
        )
        return {
            "portfolio_id": portfolio_id,
            "reporting_currency": snap.reporting_currency,
            "foreign_currency_weight": snap.foreign_currency_weight,
            "base_local_interaction": snap.base_local_interaction,
            "sensitivities": {
                exp.currency: {
                    "fx_sensitivity_beta": exp.fx_sensitivity_beta,
                    "historical_fx_volatility": exp.historical_fx_volatility,
                    "market_value": exp.market_value,
                    "weight": exp.weight,
                }
                for exp in snap.exposures
                if exp.currency != snap.reporting_currency
            },
        }
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/sectors", response_model=SectorRiskSnapshotDTO)
def get_portfolio_sector_risk(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> SectorRiskSnapshotDTO:
    """Retrieves sector and industry Euler variance/volatility risk attribution."""
    try:
        snap = service.get_portfolio_sector_risk(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
        )
        return _map_sector_snapshot_to_dto(snap)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/sectors/contributions", response_model=List[SectorRiskItemDTO])
def get_portfolio_sector_contributions(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[SectorRiskItemDTO]:
    """Retrieves sector Euler variance and volatility contributions."""
    try:
        snap = service.get_portfolio_sector_risk(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
        )
        dto = _map_sector_snapshot_to_dto(snap)
        return dto.sectors
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/cross-exposures", response_model=CrossExposureMatrixDTO)
def get_portfolio_cross_exposure(
    portfolio_id: str,
    row_dimension: str = "FACTOR",
    col_dimension: str = "SECTOR",
    service: Annotated[RiskService, Depends(get_risk_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
) -> CrossExposureMatrixDTO:
    """Retrieves 2D cross-exposure matrix (e.g. Factor x Sector, Currency x Sector)."""
    try:
        matrix = service.get_portfolio_cross_exposure(
            portfolio_id=portfolio_id,
            row_dimension=row_dimension,
            col_dimension=col_dimension,
            user_id=current_user.sub,
        )
        return _map_cross_exposure_matrix_to_dto(matrix)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/factor-benchmark")
def get_portfolio_factor_benchmark(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Retrieves portfolio vs benchmark active factor exposures."""
    try:
        run = service.get_latest_factor_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        if not run:
            run = service.calculate_factor_risk(
                portfolio_id=portfolio_id,
                request=CalculateFactorRiskRequest(portfolio_id=portfolio_id),
                user_id=current_user.sub,
            )
        return {
            "portfolio_id": portfolio_id,
            "portfolio_exposures": run.portfolio_exposures,
            "benchmark_exposures": {fid: (1.0 if "MKT" in fid else 0.0) for fid in run.factor_ids},
            "active_factor_exposures": run.active_factor_exposures,
        }
    except Exception as e:
        _handle_error(e)



# -------------------------------------------------------------------------
# Stage 118: Options and Fixed-Income Risk Endpoints
# -------------------------------------------------------------------------


@router.get("/options/models")
def get_options_models(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[Dict[str, Any]]:
    """Returns available options pricing models and supported exercise styles."""
    return [
        {
            "model_id": OptionsPricingModelId.EUROPEAN_BLACK_SCHOLES_MERTON,
            "display_name": "Black-Scholes-Merton (European)",
            "supported_styles": ["EUROPEAN"],
            "description": "Standard continuous-time analytical option pricing and closed-form Greeks.",
        },
        {
            "model_id": OptionsPricingModelId.EUROPEAN_BLACK_76,
            "display_name": "Black-76 (Futures & Commodity Options)",
            "supported_styles": ["EUROPEAN"],
            "description": "Black-76 model for European options on futures and commodity indices.",
        },
        {
            "model_id": OptionsPricingModelId.NUMERICAL_BUMP_REPRICE,
            "display_name": "Numerical Bump & Reprice",
            "supported_styles": ["EUROPEAN", "AMERICAN"],
            "description": "Finite-difference perturbation across spot, implied volatility, rate, and time.",
        },
    ]


@router.post("/options/calculate", response_model=OptionGreeksResultDTO)
def calculate_options_risk(
    request: CalculateOptionsRiskRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> OptionGreeksResultDTO:
    """Computes theoretical price, Greeks, and intrinsic/time values for an option contract."""
    try:
        res = service.calculate_options_risk(request)
        return _map_option_greeks_to_dto(res)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/options", response_model=PortfolioOptionsRiskSummaryDTO)
def get_portfolio_options_risk(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> PortfolioOptionsRiskSummaryDTO:
    """Retrieves portfolio-level aggregated options risk and underlying exposures."""
    try:
        summary = service.get_portfolio_options_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        return _map_portfolio_options_summary_to_dto(summary)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/options/greeks", response_model=List[OptionPositionRiskDTO])
def get_portfolio_options_greeks(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[OptionPositionRiskDTO]:
    """Retrieves position-level options Greeks with multiplier scaling."""
    try:
        summary = service.get_portfolio_options_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        dto = _map_portfolio_options_summary_to_dto(summary)
        return dto.positions
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/options/underlyings")
def get_portfolio_options_underlyings(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Dict[str, float]]:
    """Retrieves aggregated options Greeks partitioned by underlying asset."""
    try:
        summary = service.get_portfolio_options_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        return summary.underlying_exposures
    except Exception as e:
        _handle_error(e)


@router.get("/fixed-income/models")
def get_fixed_income_models(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[Dict[str, Any]]:
    """Returns available fixed-income pricing models and yield solvers."""
    return [
        {
            "model_id": BondPricingModelId.DISCOUNTED_CASHFLOW,
            "display_name": "Discounted Cash Flow (DCF)",
            "description": "Standard multi-period coupon discounting, accrued interest, and yield-to-maturity root solving.",
        },
        {
            "model_id": BondPricingModelId.YIELD_DURATION_CONVEXITY,
            "display_name": "Duration & Convexity Taylor Expansion",
            "description": "First and second order yield sensitivities with DV01 calculation.",
        },
        {
            "model_id": BondPricingModelId.CURVE_BUMP_REPRICE,
            "display_name": "Key-Rate Curve Bump & Reprice",
            "description": "Tenor vertex bumping along the calibrated sovereign yield curve.",
        },
    ]


@router.post("/fixed-income/calculate", response_model=BondSensitivitiesResultDTO)
def calculate_fixed_income_risk(
    request: CalculateFixedIncomeRiskRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> BondSensitivitiesResultDTO:
    """Computes standalone bond clean/dirty price, YTM, Macaulay/Modified duration, and DV01."""
    try:
        res = service.calculate_fixed_income_risk(request)
        return _map_bond_sensitivities_to_dto(res)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/fixed-income", response_model=PortfolioFixedIncomeRiskSummaryDTO)
def get_portfolio_fixed_income_risk(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> PortfolioFixedIncomeRiskSummaryDTO:
    """Retrieves aggregated portfolio fixed-income duration, convexity, and total DV01."""
    try:
        summary = service.get_portfolio_fixed_income_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        return _map_portfolio_fixed_income_summary_to_dto(summary)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/fixed-income/cashflows", response_model=BondCashFlowScheduleDTO)
def get_portfolio_bond_cashflows(
    portfolio_id: str,
    instrument_id: str = "US_10Y_BENCHMARK",
    service: Annotated[RiskService, Depends(get_risk_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
) -> BondCashFlowScheduleDTO:
    """Retrieves projected coupon and principal schedule for a bond instrument."""
    try:
        sched = service.get_bond_cash_flows(portfolio_id=portfolio_id, instrument_id=instrument_id, user_id=current_user.sub)
        return _map_bond_cash_flow_schedule_to_dto(sched)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/fixed-income/dv01")
def get_portfolio_fixed_income_dv01(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Retrieves total portfolio DV01 and key-rate tenor distribution."""
    try:
        summary = service.get_portfolio_fixed_income_risk(portfolio_id=portfolio_id, user_id=current_user.sub)
        return {
            "portfolio_id": portfolio_id,
            "total_dv01": summary.portfolio_total_dv01,
            "weighted_modified_duration": summary.portfolio_weighted_modified_duration,
            "weighted_yield": summary.portfolio_weighted_yield,
            "key_rate_dv01_profile": summary.key_rate_dv01_profile,
        }
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/fixed-income/curves", response_model=InterestRateCurveDefinitionDTO)
def get_portfolio_fixed_income_curves(
    portfolio_id: str,
    curve_id: str = "US_TREASURY_SOVEREIGN",
    service: Annotated[RiskService, Depends(get_risk_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
) -> InterestRateCurveDefinitionDTO:
    """Retrieves calibrated benchmark sovereign yield curve points and discount factors."""
    try:
        curve = service.get_yield_curve_risk(portfolio_id=portfolio_id, curve_id=curve_id, user_id=current_user.sub)
        return _map_yield_curve_to_dto(curve)
    except Exception as e:
        _handle_error(e)


@router.get("/portfolios/{portfolio_id}/instrument-sensitivities", response_model=PortfolioInstrumentSensitivitiesSummaryDTO)
def get_portfolio_instrument_sensitivities(
    portfolio_id: str,
    service: Annotated[RiskService, Depends(get_risk_service)],
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> PortfolioInstrumentSensitivitiesSummaryDTO:
    """Retrieves cross-asset risk synthesis across equity delta, options Greeks, and bond DV01."""
    try:
        summary = service.get_instrument_sensitivities(portfolio_id=portfolio_id, user_id=current_user.sub)
        return _map_instrument_sensitivities_to_dto(summary)
    except Exception as e:
        _handle_error(e)
