"""FastAPI Router for Portfolios V1 (Stage 110).

Exposes institutional portfolio accounting, investment accounts, transaction journal,
security positions, FIFO tax lots, multi-currency cash balances, marked valuation,
and ledger reconciliation.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, List, Optional

from atlas.auth import AuthPrincipal
from atlas.portfolios import (
    AccountCreateRequest,
    AccountListResponse,
    AccountResponse,
    AccountUpdateRequest,
    CashBalanceResponse,
    CashLedgerEntryResponse,
    CashValuationResponse,
    LotListResponse,
    LotResponse,
    PortfolioCreateRequest,
    PortfolioError,
    PortfolioListResponse,
    PortfolioResponse,
    PortfolioService,
    PortfolioUpdateRequest,
    PositionListResponse,
    PositionResponse,
    PositionValuationResponse,
    ReconciliationResponse,
    TransactionCorrectRequest,
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionPreviewResponse,
    TransactionResponse,
    TransactionReverseRequest,
    TransactionType,
    ValuationResponse,
)
from atlas.portfolios.performance import (
    BenchmarkComparisonDTO,
    BenchmarkDefinitionDTO,
    BenchmarkListResponse,
    PerformanceCalculateRequest,
    PerformanceCashFlowDTO,
    PerformanceDataQualityDTO,
    PerformanceMethodology,
    PerformancePeriodType,
    PerformanceResponse,
    PerformanceRun,
    PerformanceRunListResponse,
    PerformanceSeriesPointDTO,
    PerformanceSeriesResponse,
    PeriodicReturnDTO,
    PeriodicReturnsResponse,
    PortfolioPerformanceError,
    PortfolioPerformanceService,
    SubperiodReturnDTO,
    list_canonical_benchmarks,
)
from atlas.portfolios.exposure import (
    AllocationChangeItem,
    AllocationChangeResponse,
    CalculateExposureRequest,
    ConcentrationSummary,
    ConcentrationSummaryResponse,
    CrossFundOverlapItem,
    CrossFundOverlapResponse,
    ExposureBasis,
    ExposureCategoryRow,
    ExposureCategoryResponse,
    ExposureDataQuality,
    ExposureDataQualityResponse,
    ExposureDimension,
    ExposureDimensionResponse,
    ExposureDimensionResult,
    FundConstituentItem,
    FundConstituentResponse,
    FundLookThroughResponse,
    FundLookThroughResult,
    GeographyPolicy,
    HistoricalAllocationPoint,
    HistoricalAllocationPointResponse,
    IssuerWeightItem,
    IssuerWeightResponse,
    PortfolioExposureError,
    PortfolioExposureRun,
    PortfolioExposureRunResponse,
    PortfolioExposureService,
    SecurityWeightItem,
    SecurityWeightResponse,
)
from atlas.portfolios.attribution import (
    AttributionBenchmarkSummaryResponse,
    AttributionCategoryResponse,
    AttributionDataQualityResponse,
    AttributionReconciliationResponse,
    AttributionRunsListResponse,
    CalculateAttributionRequest,
    CurrencyEffectResponse,
    HistoricalPeriodResponse,
    MultiPeriodLinkedResponse,
    PortfolioAttributionError,
    PortfolioAttributionRun,
    PortfolioAttributionRunResponse,
    PortfolioAttributionService,
    SecurityContributionResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

# Singleton service instances for in-memory persistence across requests
_service_instance: Optional[PortfolioService] = None
_perf_service_instance: Optional[PortfolioPerformanceService] = None
_exposure_service_instance: Optional[PortfolioExposureService] = None
_attribution_service_instance: Optional[PortfolioAttributionService] = None


def get_portfolio_service(request: Request) -> PortfolioService:
    global _service_instance
    if _service_instance is None:
        _service_instance = PortfolioService()
    return _service_instance


def get_performance_service(
    portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)]
) -> PortfolioPerformanceService:
    global _perf_service_instance
    if _perf_service_instance is None or _perf_service_instance.portfolio_service is not portfolio_service:
        _perf_service_instance = PortfolioPerformanceService(portfolio_service)
    return _perf_service_instance


def get_exposure_service(
    portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)]
) -> PortfolioExposureService:
    global _exposure_service_instance
    if _exposure_service_instance is None or _exposure_service_instance.portfolio_service is not portfolio_service:
        _exposure_service_instance = PortfolioExposureService(portfolio_service)
    return _exposure_service_instance


def get_attribution_service(
    portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)]
) -> PortfolioAttributionService:
    global _attribution_service_instance
    if _attribution_service_instance is None or _attribution_service_instance.portfolio_service is not portfolio_service:
        _attribution_service_instance = PortfolioAttributionService(portfolio_service)
    return _attribution_service_instance


def _handle_error(e: Exception) -> None:
    if isinstance(e, (PortfolioError, PortfolioPerformanceError, PortfolioExposureError, PortfolioAttributionError)):
        code = getattr(e, "code", e.__class__.__name__)
        message = getattr(e, "message", str(e))
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": code, "message": message},
        )
    logger.exception("Unexpected error in portfolios router: %s", e)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "INTERNAL_SERVER_ERROR", "message": str(e)},
    )


def _map_category_to_response(c: ExposureCategoryRow) -> ExposureCategoryResponse:
    return ExposureCategoryResponse(
        category_id=c.category_id,
        category_label=c.category_label,
        base_value=c.base_value,
        weight=c.weight,
        percentage=c.percentage,
        position_count=c.position_count,
        direct_value=c.direct_value,
        look_through_value=c.look_through_value,
        is_residual=c.is_residual,
        is_unclassified=c.is_unclassified,
        parent_category_id=c.parent_category_id,
        subcategories=[_map_category_to_response(sub) for sub in c.subcategories],
    )


def _map_dim_to_response(d: ExposureDimensionResult) -> ExposureDimensionResponse:
    return ExposureDimensionResponse(
        dimension=d.dimension,
        total_base_value=d.total_base_value,
        total_weight=d.total_weight,
        reconciled=d.reconciled,
        reconciliation_discrepancy=d.reconciliation_discrepancy,
        categories=[_map_category_to_response(c) for c in d.categories],
    )


def _map_sec_weight_to_response(s: SecurityWeightItem) -> SecurityWeightResponse:
    return SecurityWeightResponse(
        instrument_id=s.instrument_id,
        symbol=s.symbol,
        name=s.name,
        asset_class=s.asset_class,
        base_value=s.base_value,
        weight=s.weight,
        percentage=s.percentage,
        direct_weight=s.direct_weight,
        look_through_weight=s.look_through_weight,
        effective_shares=s.effective_shares,
        rank=s.rank,
    )


def _map_issuer_weight_to_response(i: IssuerWeightItem) -> IssuerWeightResponse:
    return IssuerWeightResponse(
        issuer_id=i.issuer_id,
        issuer_name=i.issuer_name,
        country_code=i.country_code,
        base_value=i.base_value,
        weight=i.weight,
        percentage=i.percentage,
        constituent_instruments=i.constituent_instruments,
        rank=i.rank,
    )


def _map_concentration_to_response(c: ConcentrationSummary) -> ConcentrationSummaryResponse:
    return ConcentrationSummaryResponse(
        top1_weight=c.top1_weight,
        top3_weight=c.top3_weight,
        top5_weight=c.top5_weight,
        top10_weight=c.top10_weight,
        top20_weight=c.top20_weight,
        herfindahl_index=c.herfindahl_index,
        herfindahl_index_normalized=c.herfindahl_index_normalized,
        effective_number_of_holdings=c.effective_number_of_holdings,
        total_positions=c.total_positions,
        direct_holdings_count=c.direct_holdings_count,
        look_through_holdings_count=c.look_through_holdings_count,
    )


def _map_constituent_to_response(fc: FundConstituentItem) -> FundConstituentResponse:
    return FundConstituentResponse(
        parent_fund_id=fc.parent_fund_id,
        constituent_instrument_id=fc.constituent_instrument_id,
        constituent_symbol=fc.constituent_symbol,
        constituent_name=fc.constituent_name,
        constituent_asset_class=fc.constituent_asset_class,
        constituent_sector=fc.constituent_sector,
        constituent_country=fc.constituent_country,
        constituent_currency=fc.constituent_currency,
        constituent_weight_in_fund=fc.constituent_weight_in_fund,
        effective_base_value=fc.effective_base_value,
        effective_portfolio_weight=fc.effective_portfolio_weight,
        is_residual=fc.is_residual,
    )


def _map_fund_to_response(f: FundLookThroughResult) -> FundLookThroughResponse:
    return FundLookThroughResponse(
        fund_instrument_id=f.fund_instrument_id,
        fund_symbol=f.fund_symbol,
        fund_name=f.fund_name,
        fund_base_value=f.fund_base_value,
        fund_weight_in_portfolio=f.fund_weight_in_portfolio,
        as_of_date=f.as_of_date,
        status=f.status,
        coverage_ratio=f.coverage_ratio,
        residual_weight=f.residual_weight,
        residual_base_value=f.residual_base_value,
        constituents=[_map_constituent_to_response(c) for c in f.constituents],
    )


def _map_overlap_to_response(o: CrossFundOverlapItem) -> CrossFundOverlapResponse:
    return CrossFundOverlapResponse(
        constituent_symbol=o.constituent_symbol,
        constituent_name=o.constituent_name,
        total_effective_weight=o.total_effective_weight,
        total_effective_value=o.total_effective_value,
        funds_involved=o.funds_involved,
        weights_by_fund=o.weights_by_fund,
    )


def _map_quality_to_response(q: ExposureDataQuality) -> ExposureDataQualityResponse:
    return ExposureDataQualityResponse(
        completeness=q.completeness,
        total_positions=q.total_positions,
        classified_positions=q.classified_positions,
        unclassified_positions=q.unclassified_positions,
        classification_coverage_ratio=q.classification_coverage_ratio,
        valuation_coverage_ratio=q.valuation_coverage_ratio,
        fx_coverage_ratio=q.fx_coverage_ratio,
        warnings=q.warnings,
        errors=q.errors,
        reconciled=q.reconciled,
        reconciliation_discrepancy=q.reconciliation_discrepancy,
    )


def _map_run_to_response(run: PortfolioExposureRun) -> PortfolioExposureRunResponse:
    return PortfolioExposureRunResponse(
        run_id=run.run_id,
        portfolio_id=run.portfolio_id,
        account_ids=run.account_ids,
        as_of_date=run.as_of_date,
        calculated_at=run.calculated_at,
        base_currency=run.base_currency,
        exposure_basis=run.exposure_basis,
        geography_policy=run.geography_policy,
        look_through_applied=run.look_through_applied,
        total_nav=run.total_nav,
        gross_exposure=run.gross_exposure,
        cash_value=run.cash_value,
        cash_weight=run.cash_weight,
        input_hash=run.input_hash,
        calculation_version=run.calculation_version,
        reconciled=run.reconciled,
        data_quality=_map_quality_to_response(run.data_quality),
        asset_classes=_map_dim_to_response(run.asset_classes),
        sectors=_map_dim_to_response(run.sectors),
        industries=_map_dim_to_response(run.industries),
        countries=_map_dim_to_response(run.countries),
        currencies=_map_dim_to_response(run.currencies),
        concentration=_map_concentration_to_response(run.concentration),
        security_weights=[_map_sec_weight_to_response(s) for s in run.security_weights],
        issuer_weights=[_map_issuer_weight_to_response(i) for i in run.issuer_weights],
        funds=[_map_fund_to_response(f) for f in run.funds],
        cross_fund_overlap=[_map_overlap_to_response(o) for o in run.cross_fund_overlap],
    )


def _convert_run_to_response(run: PerformanceRun) -> PerformanceResponse:
    subperiods_dto = [
        SubperiodReturnDTO(
            subperiod_index=s.subperiod_index,
            start_time=s.start_time,
            end_time=s.end_time,
            start_value=f"{s.start_value:.2f}",
            end_value_pre_flow=f"{s.end_value_pre_flow:.2f}",
            net_external_flow=f"{s.net_external_flow:.2f}",
            end_value_post_flow=f"{s.end_value_post_flow:.2f}",
            subperiod_return=f"{s.subperiod_return:.4f}",
            cumulative_twr_linked=f"{s.cumulative_twr_linked:.4f}",
        )
        for s in run.subperiods
    ]

    flows_dto = [
        PerformanceCashFlowDTO(
            id=str(f.id),
            flow_date=f.flow_date,
            classification=f.classification.value,
            native_amount=f"{f.native_amount:.2f}",
            native_currency=f.native_currency,
            base_amount=f"{f.base_amount:.2f}",
            base_currency=f.base_currency,
            fx_rate=f"{f.fx_rate:.4f}",
            investor_flow_amount=f"{f.investor_flow_amount:.2f}",
            portfolio_flow_amount=f"{f.portfolio_flow_amount:.2f}",
            description=f.description,
        )
        for f in run.dated_flows
    ]

    bench_dto = None
    if run.benchmark_comparison:
        b = run.benchmark_comparison
        bench_dto = BenchmarkComparisonDTO(
            benchmark_id=b.benchmark_id,
            benchmark_name=b.benchmark_name,
            return_basis=b.return_basis.value,
            currency=b.currency,
            portfolio_return=f"{b.portfolio_return:.4f}",
            benchmark_return=f"{b.benchmark_return:.4f}",
            arithmetic_difference=f"{b.arithmetic_difference:.4f}",
            period_start=b.period_start,
            period_end=b.period_end,
            rebased_portfolio_index_end=f"{b.rebased_portfolio_index_end:.2f}",
            rebased_benchmark_index_end=f"{b.rebased_benchmark_index_end:.2f}",
            warning=b.warning,
        )

    dq_dto = PerformanceDataQualityDTO(
        completeness=run.data_quality.completeness.value,
        missing_valuations=run.data_quality.missing_valuations,
        missing_market_prices=run.data_quality.missing_market_prices,
        missing_fx_rates=run.data_quality.missing_fx_rates,
        stale_market_prices=run.data_quality.stale_market_prices,
        warnings=run.data_quality.warnings,
        source_manifest=run.data_quality.source_manifest,
    )

    return PerformanceResponse(
        run_id=str(run.run_id),
        portfolio_id=str(run.portfolio_id),
        account_id=str(run.account_id) if run.account_id else None,
        methodology=run.methodology.value,
        period_type=run.period_type.value,
        scope=run.scope.value,
        period_start=run.period_start,
        period_end=run.period_end,
        base_currency=run.base_currency,
        status=run.status.value,
        twr_cumulative=f"{run.twr_cumulative:.4f}" if run.twr_cumulative is not None else None,
        twr_annualized=f"{run.twr_annualized:.4f}" if run.twr_annualized is not None else None,
        mwr_xirr=f"{run.mwr_xirr:.4f}" if run.mwr_xirr is not None else None,
        beginning_value=f"{run.beginning_value:.2f}",
        ending_value=f"{run.ending_value:.2f}",
        net_external_flows=f"{run.net_external_flows:.2f}",
        total_contributions=f"{run.total_contributions:.2f}",
        total_withdrawals=f"{run.total_withdrawals:.2f}",
        total_dividends=f"{run.total_dividends:.2f}",
        total_fees=f"{run.total_fees:.2f}",
        investment_gain=f"{run.investment_gain:.2f}",
        subperiods=subperiods_dto,
        dated_flows=flows_dto,
        benchmark_comparison=bench_dto,
        data_quality=dq_dto,
        calculation_version=run.calculation_version,
        input_hash=run.input_hash,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


# ---------------------------------------------------------------------------
# Canonical Benchmarks (Static route preceding dynamic /{portfolio_id})
# ---------------------------------------------------------------------------


@router.get("/benchmarks", response_model=BenchmarkListResponse)
async def list_benchmarks(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> BenchmarkListResponse:
    """List canonical market index benchmarks."""
    benchmarks = list_canonical_benchmarks()
    return BenchmarkListResponse(
        benchmarks=[
            BenchmarkDefinitionDTO(
                benchmark_id=b.benchmark_id,
                name=b.name,
                symbol=b.symbol,
                benchmark_type=b.benchmark_type,
                return_basis=b.return_basis.value,
                currency=b.currency,
                description=b.description,
            )
            for b in benchmarks
        ],
        total=len(benchmarks),
    )


# ---------------------------------------------------------------------------
# Portfolio CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=PortfolioListResponse)
async def list_portfolios(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PortfolioListResponse:
    """List all active portfolios owned by the authenticated principal."""
    try:
        ports, total = service.list_portfolios(current_user.sub, limit=limit, offset=offset)
        items = []
        for p in ports:
            accs = service.list_accounts(p.id, current_user.sub)
            items.append(
                PortfolioResponse(
                    id=p.id,
                    user_id=p.user_id,
                    name=p.name,
                    portfolio_type=p.portfolio_type,
                    base_currency=p.base_currency,
                    status=p.status,
                    cost_basis_method=p.cost_basis_method,
                    description=p.description,
                    account_count=len(accs),
                    revision=p.revision,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
            )
        return PortfolioListResponse(items=items, total=total)
    except Exception as e:
        _handle_error(e)


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: PortfolioCreateRequest,
) -> PortfolioResponse:
    """Create a new portfolio with a primary investment account."""
    try:
        p = service.create_portfolio(current_user.sub, payload)
        accs = service.list_accounts(p.id, current_user.sub)
        return PortfolioResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            base_currency=p.base_currency,
            status=p.status,
            cost_basis_method=p.cost_basis_method,
            description=p.description,
            account_count=len(accs),
            revision=p.revision,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PortfolioResponse:
    """Retrieve details for an owned portfolio."""
    try:
        p = service.get_portfolio(portfolio_id, current_user.sub)
        accs = service.list_accounts(p.id, current_user.sub)
        return PortfolioResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            base_currency=p.base_currency,
            status=p.status,
            cost_basis_method=p.cost_basis_method,
            description=p.description,
            account_count=len(accs),
            revision=p.revision,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    except Exception as e:
        _handle_error(e)


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: PortfolioUpdateRequest,
) -> PortfolioResponse:
    """Update portfolio metadata with optimistic revision protection."""
    try:
        p = service.update_portfolio(portfolio_id, current_user.sub, payload)
        accs = service.list_accounts(p.id, current_user.sub)
        return PortfolioResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            base_currency=p.base_currency,
            status=p.status,
            cost_basis_method=p.cost_basis_method,
            description=p.description,
            account_count=len(accs),
            revision=p.revision,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    except Exception as e:
        _handle_error(e)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> None:
    """Archive a portfolio if it does not have unarchived accounts with active transactions."""
    try:
        service.delete_portfolio(portfolio_id, current_user.sub)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Account Endpoints
# ---------------------------------------------------------------------------


@router.get("/{portfolio_id}/accounts", response_model=AccountListResponse)
async def list_accounts(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> AccountListResponse:
    """List all investment accounts in a portfolio."""
    try:
        accs = service.list_accounts(portfolio_id, current_user.sub)
        items = [AccountResponse.model_validate(a) for a in accs]
        return AccountListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: AccountCreateRequest,
) -> AccountResponse:
    """Create a new investment account in a portfolio."""
    try:
        acc = service.create_account(portfolio_id, current_user.sub, payload)
        return AccountResponse.model_validate(acc)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> AccountResponse:
    """Retrieve details for a specific investment account."""
    try:
        acc = service.get_account(account_id, current_user.sub)
        return AccountResponse.model_validate(acc)
    except Exception as e:
        _handle_error(e)


@router.patch("/{portfolio_id}/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: AccountUpdateRequest,
) -> AccountResponse:
    """Update investment account details."""
    try:
        acc = service.update_account(account_id, current_user.sub, payload)
        return AccountResponse.model_validate(acc)
    except Exception as e:
        _handle_error(e)


@router.delete("/{portfolio_id}/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> None:
    """Archive an investment account if it has no posted transactions."""
    try:
        service.delete_account(account_id, current_user.sub)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Transaction Endpoints
# ---------------------------------------------------------------------------


def _fmt_2(val: Optional[Decimal]) -> str:
    if val is None:
        return "0.00"
    return f"{Decimal(str(val)):.2f}"


def _map_tx_to_response(t) -> TransactionResponse:
    return TransactionResponse(
        id=t.id,
        portfolio_id=t.portfolio_id,
        account_id=t.account_id,
        user_id=t.user_id,
        transaction_type=t.transaction_type,
        status=t.status,
        cash_currency=t.cash_currency,
        trade_date=t.trade_date,
        settlement_date=t.settlement_date,
        instrument_id=t.instrument_id,
        symbol=t.symbol,
        exchange=t.exchange,
        company_name=t.company_name,
        quantity=str(t.quantity) if t.quantity is not None else None,
        unit_price=str(t.unit_price) if t.unit_price is not None else None,
        gross_amount=_fmt_2(t.gross_amount) if t.gross_amount is not None else None,
        fee=_fmt_2(t.fee),
        tax=_fmt_2(t.tax),
        net_cash_amount=_fmt_2(t.net_cash_amount),
        idempotency_key=t.idempotency_key,
        notes=t.notes,
        reverses_transaction_id=t.reverses_transaction_id,
        reversed_by_transaction_id=t.reversed_by_transaction_id,
        created_at=t.created_at,
    )


@router.get("/{portfolio_id}/transactions", response_model=TransactionListResponse)
async def list_transactions(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    account_id: Optional[str] = Query(default=None),
    instrument_id: Optional[str] = Query(default=None),
    tx_type: Optional[TransactionType] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> TransactionListResponse:
    """List transaction history with optional filters."""
    try:
        txs, total = service.list_transactions(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            account_id=account_id,
            instrument_id=instrument_id,
            tx_type=tx_type,
            limit=limit,
            offset=offset,
        )
        items = [_map_tx_to_response(t) for t in txs]
        return TransactionListResponse(items=items, total=total)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions/preview", response_model=TransactionPreviewResponse)
async def preview_transaction(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionCreateRequest,
) -> TransactionPreviewResponse:
    """Preview accounting and cash effects of a candidate transaction without posting."""
    try:
        return service.preview_transaction(portfolio_id, current_user.sub, payload)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def post_transaction(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionCreateRequest,
) -> TransactionResponse:
    """Post an immutable transaction to the portfolio ledger."""
    try:
        tx = service.post_transaction(portfolio_id, current_user.sub, payload)
        return _map_tx_to_response(tx)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    portfolio_id: str,
    transaction_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> TransactionResponse:
    """Retrieve details for a single posted transaction."""
    try:
        tx = service.get_transaction(portfolio_id, transaction_id, current_user.sub)
        return _map_tx_to_response(tx)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions/{transaction_id}/reverse", response_model=TransactionResponse)
async def reverse_transaction(
    portfolio_id: str,
    transaction_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionReverseRequest,
) -> TransactionResponse:
    """Controlled reversal of a posted transaction."""
    try:
        reversal = service.reverse_transaction(
            portfolio_id, transaction_id, current_user.sub, payload
        )
        return _map_tx_to_response(reversal)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions/{transaction_id}/correct", response_model=TransactionResponse)
async def correct_transaction(
    portfolio_id: str,
    transaction_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionCorrectRequest,
) -> TransactionResponse:
    """Controlled correction: atomically reverses original and posts replacement."""
    try:
        replacement = service.correct_transaction(
            portfolio_id, transaction_id, current_user.sub, payload
        )
        return _map_tx_to_response(replacement)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Holdings & Lots Endpoints
# ---------------------------------------------------------------------------


def _map_pos_to_response(p) -> PositionResponse:
    return PositionResponse(
        portfolio_id=p.portfolio_id,
        account_id=p.account_id,
        instrument_id=p.instrument_id,
        symbol=p.symbol,
        exchange=p.exchange,
        company_name=p.company_name,
        quantity=str(p.quantity),
        open_lot_count=p.open_lot_count,
        remaining_cost_basis=str(p.remaining_cost_basis),
        cost_basis_currency=p.cost_basis_currency,
        average_unit_cost=str(p.average_unit_cost) if p.average_unit_cost is not None else None,
        realized_pnl=str(p.realized_pnl),
        unrealized_pnl=str(p.unrealized_pnl) if p.unrealized_pnl is not None else None,
        as_of=p.as_of,
    )


@router.get("/{portfolio_id}/positions", response_model=PositionListResponse)
async def get_portfolio_positions(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PositionListResponse:
    """Get security positions derived deterministically from the transaction ledger."""
    try:
        positions = service.get_positions(portfolio_id, current_user.sub)
        items = [_map_pos_to_response(p) for p in positions]
        return PositionListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}/positions", response_model=PositionListResponse)
async def get_account_positions(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PositionListResponse:
    """Get security positions for an individual account."""
    try:
        positions = service.get_positions(portfolio_id, current_user.sub, account_id=account_id)
        items = [_map_pos_to_response(p) for p in positions]
        return PositionListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/positions/{instrument_id}/lots", response_model=LotListResponse)
async def get_instrument_lots(
    portfolio_id: str,
    instrument_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    account_id: Optional[str] = Query(default=None),
) -> LotListResponse:
    """Get individual FIFO tax-lots for an instrument."""
    try:
        lots = service.get_lots(portfolio_id, current_user.sub, instrument_id, account_id=account_id)
        items = [
            LotResponse(
                id=l.id,
                portfolio_id=l.portfolio_id,
                account_id=l.account_id,
                instrument_id=l.instrument_id,
                acquisition_transaction_id=l.acquisition_transaction_id,
                acquisition_date=l.acquisition_date,
                original_quantity=str(l.original_quantity),
                remaining_quantity=str(l.remaining_quantity),
                unit_cost_basis=str(l.unit_cost_basis),
                total_cost_basis=str(l.total_cost_basis),
                currency=l.currency,
                is_fully_disposed=l.is_fully_disposed,
                disposed_at=l.disposed_at,
            )
            for l in lots
        ]
        return LotListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Cash Endpoints
# ---------------------------------------------------------------------------


def _map_cb_to_response(c) -> CashBalanceResponse:
    return CashBalanceResponse(
        account_id=c.account_id,
        currency=c.currency,
        posted_cash=_fmt_2(c.posted_cash),
        settled_cash=_fmt_2(c.settled_cash),
        unsettled_receivable=_fmt_2(c.unsettled_receivable),
        unsettled_payable=_fmt_2(c.unsettled_payable),
        available_cash=_fmt_2(c.available_cash),
        as_of=c.as_of,
    )


@router.get("/{portfolio_id}/cash", response_model=list[CashBalanceResponse])
async def get_portfolio_cash(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> list[CashBalanceResponse]:
    """Get cash balances across all accounts in a portfolio."""
    try:
        bals = service.get_cash_balances(portfolio_id, current_user.sub)
        return [_map_cb_to_response(b) for b in bals]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}/cash", response_model=list[CashBalanceResponse])
async def get_account_cash(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> list[CashBalanceResponse]:
    """Get cash balances for a specific account."""
    try:
        bals = service.get_cash_balances(portfolio_id, current_user.sub, account_id=account_id)
        return [_map_cb_to_response(b) for b in bals]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}/cash-ledger", response_model=list[CashLedgerEntryResponse])
async def get_account_cash_ledger(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> list[CashLedgerEntryResponse]:
    """Get detailed cash ledger audit entries for an account."""
    try:
        entries = service.get_cash_ledger(portfolio_id, current_user.sub, account_id=account_id)
        return [
            CashLedgerEntryResponse(
                id=e.id,
                account_id=e.account_id,
                transaction_id=e.transaction_id,
                currency=e.currency,
                amount=str(e.amount),
                balance_type=e.balance_type.value,
                effective_date=e.effective_date,
                description=e.description,
                created_at=e.created_at,
            )
            for e in entries
        ]
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Valuation Endpoints
# ---------------------------------------------------------------------------


def _map_val_to_response(val) -> ValuationResponse:
    pos_vals = [
        PositionValuationResponse(
            instrument_id=pv.instrument_id,
            symbol=pv.symbol,
            exchange=pv.exchange,
            quantity=str(pv.quantity),
            remaining_basis=str(pv.remaining_basis),
            basis_currency=pv.basis_currency,
            valuation_status=pv.valuation_status,
            quote_freshness=pv.quote_freshness,
            account_id=pv.account_id,
            company_name=pv.company_name,
            mark_price=str(pv.mark_price) if pv.mark_price is not None else None,
            price_currency=pv.price_currency,
            mark_as_of=pv.mark_as_of,
            mark_source=pv.mark_source,
            native_market_value=str(pv.native_market_value) if pv.native_market_value is not None else None,
            fx_rate_to_base=str(pv.fx_rate_to_base) if pv.fx_rate_to_base is not None else None,
            fx_pair=pv.fx_pair,
            fx_as_of=pv.fx_as_of,
            base_market_value=str(pv.base_market_value) if pv.base_market_value is not None else None,
            unrealized_pnl=str(pv.unrealized_pnl) if pv.unrealized_pnl is not None else None,
        )
        for pv in val.position_valuations
    ]
    cash_vals = [
        CashValuationResponse(
            account_id=cv.account_id,
            currency=cv.currency,
            posted_cash=str(cv.posted_cash),
            settled_cash=str(cv.settled_cash),
            unsettled_receivable=str(cv.unsettled_receivable),
            unsettled_payable=str(cv.unsettled_payable),
            available_cash=str(cv.available_cash),
            fx_rate_to_base=str(cv.fx_rate_to_base),
            base_cash_value=str(cv.base_cash_value),
            as_of=cv.as_of,
        )
        for cv in val.cash_valuations
    ]
    return ValuationResponse(
        id=val.id,
        portfolio_id=val.portfolio_id,
        as_of=val.as_of,
        base_currency=val.base_currency,
        valuation_status=val.valuation_status,
        known_valued_subtotal=str(val.known_valued_subtotal),
        verified_total_portfolio_value=str(val.verified_total_portfolio_value) if val.verified_total_portfolio_value is not None else None,
        total_positions_market_value=str(val.total_positions_market_value) if val.total_positions_market_value is not None else None,
        total_cash_market_value=str(val.total_cash_market_value),
        total_cost_basis=str(val.total_cost_basis),
        total_unrealized_pnl=str(val.total_unrealized_pnl) if val.total_unrealized_pnl is not None else None,
        total_realized_pnl=str(val.total_realized_pnl),
        missing_prices_count=val.missing_prices_count,
        missing_fx_count=val.missing_fx_count,
        stale_quotes_count=val.stale_quotes_count,
        position_valuations=pos_vals,
        cash_valuations=cash_vals,
        source_manifest=val.source_manifest,
        calculation_version=val.calculation_version,
        created_at=val.created_at,
    )


@router.get("/{portfolio_id}/valuation", response_model=ValuationResponse)
async def get_valuation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ValuationResponse:
    """Retrieve the latest marked portfolio valuation."""
    try:
        val = service.get_latest_valuation(portfolio_id, current_user.sub)
        return _map_val_to_response(val)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/valuations", response_model=ValuationResponse, status_code=status.HTTP_201_CREATED)
async def recalculate_valuation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ValuationResponse:
    """Trigger an explicit recomputation of portfolio valuation."""
    try:
        val = service.calculate_portfolio_valuation(portfolio_id, current_user.sub)
        return _map_val_to_response(val)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/valuations/{valuation_id}", response_model=ValuationResponse)
async def get_valuation_snapshot(
    portfolio_id: str,
    valuation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ValuationResponse:
    """Retrieve a specific historical valuation snapshot."""
    try:
        val = service.repository.get_valuation(valuation_id, current_user.sub)
        if not val or val.portfolio_id != portfolio_id:
            raise HTTPException(status_code=404, detail="Valuation snapshot not found.")
        return _map_val_to_response(val)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Reconciliation Endpoints
# ---------------------------------------------------------------------------


@router.get("/{portfolio_id}/reconciliation", response_model=ReconciliationResponse)
async def get_reconciliation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ReconciliationResponse:
    """Audit and verify ledger integrity and position balances."""
    try:
        rec = service.reconcile_portfolio(portfolio_id, current_user.sub)
        return ReconciliationResponse(
            portfolio_id=rec.portfolio_id,
            status=rec.status,
            reconciliation_timestamp=rec.reconciliation_timestamp,
            total_transactions_checked=rec.total_transactions_checked,
            total_lots_checked=rec.total_lots_checked,
            total_positions_checked=rec.total_positions_checked,
            total_cash_entries_checked=rec.total_cash_entries_checked,
            discrepancies=rec.discrepancies,
            warnings=rec.warnings,
            is_balanced=rec.is_balanced,
        )
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/reconciliation/check", response_model=ReconciliationResponse)
async def check_reconciliation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ReconciliationResponse:
    """Trigger explicit ledger reconciliation audit."""
    try:
        rec = service.reconcile_portfolio(portfolio_id, current_user.sub)
        return ReconciliationResponse(
            portfolio_id=rec.portfolio_id,
            status=rec.status,
            reconciliation_timestamp=rec.reconciliation_timestamp,
            total_transactions_checked=rec.total_transactions_checked,
            total_lots_checked=rec.total_lots_checked,
            total_positions_checked=rec.total_positions_checked,
            total_cash_entries_checked=rec.total_cash_entries_checked,
            discrepancies=rec.discrepancies,
            warnings=rec.warnings,
            is_balanced=rec.is_balanced,
        )
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Portfolio Performance Analytics (Stage 111)
# ---------------------------------------------------------------------------


@router.get("/{portfolio_id}/performance", response_model=PerformanceResponse)
async def get_performance_summary(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
    period_type: PerformancePeriodType = Query(default=PerformancePeriodType.YEAR_TO_DATE),
    methodology: PerformanceMethodology = Query(default=PerformanceMethodology.TIME_WEIGHTED_RETURN),
    reporting_currency: Optional[str] = Query(default=None),
    account_id: Optional[str] = Query(default=None),
    benchmark_id: Optional[str] = Query(default="BENCHMARK_SP500"),
) -> PerformanceResponse:
    """Retrieve or compute latest eligible portfolio performance summary."""
    try:
        run = perf_service.get_performance_summary(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            period_type=period_type,
            methodology=methodology,
            reporting_currency=reporting_currency,
            account_id=account_id,
            benchmark_id=benchmark_id,
        )
        return _convert_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/performance/calculate", response_model=PerformanceResponse)
async def calculate_performance(
    portfolio_id: str,
    request: PerformanceCalculateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
) -> PerformanceResponse:
    """Trigger a versioned, reproducible portfolio performance calculation run."""
    try:
        request.portfolio_id = portfolio_id
        run = perf_service.calculate_performance(portfolio_id, current_user.sub, request)
        return _convert_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/performance/runs", response_model=PerformanceRunListResponse)
async def list_performance_runs(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PerformanceRunListResponse:
    """List historical performance calculation runs for auditability."""
    try:
        runs, total = perf_service.list_performance_runs(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            limit=limit,
            offset=offset,
        )
        return PerformanceRunListResponse(
            runs=[_convert_run_to_response(r) for r in runs],
            total=total,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/performance/runs/{run_id}", response_model=PerformanceResponse)
async def get_performance_run(
    portfolio_id: str,
    run_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
) -> PerformanceResponse:
    """Retrieve an immutable performance run by UUID."""
    try:
        run = perf_service.get_performance_run(run_id=run_id, user_id=current_user.sub)
        return _convert_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/performance/series", response_model=PerformanceSeriesResponse)
async def get_performance_series(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
    period_type: PerformancePeriodType = Query(default=PerformancePeriodType.YEAR_TO_DATE),
    account_id: Optional[str] = Query(default=None),
) -> PerformanceSeriesResponse:
    """Retrieve historical valuation series and indexed TWR growth curve (Index = 100)."""
    try:
        perf = perf_service.get_performance_summary(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            period_type=period_type,
            account_id=account_id,
        )
        raw_points = perf_service.get_performance_series(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            period_type=period_type,
            account_id=account_id,
        )
        points = [
            PerformanceSeriesPointDTO(
                timestamp=p["timestamp"],  # type: ignore
                portfolio_value=str(p["portfolio_value"]),
                indexed_twr=str(p["indexed_twr"]),
                benchmark_indexed=str(p["benchmark_indexed"]) if p["benchmark_indexed"] else None,
                cash_flow_amount=str(p["cash_flow_amount"]) if p["cash_flow_amount"] else None,
                cash_flow_type=str(p["cash_flow_type"]) if p["cash_flow_type"] else None,
            )
            for p in raw_points
        ]
        return PerformanceSeriesResponse(
            portfolio_id=portfolio_id,
            base_currency=perf.base_currency,
            period_start=perf.period_start,
            period_end=perf.period_end,
            points=points,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/performance/periodic", response_model=PeriodicReturnsResponse)
async def get_periodic_returns(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
    account_id: Optional[str] = Query(default=None),
) -> PeriodicReturnsResponse:
    """Retrieve calendar monthly and full-year geometrically compounded returns table."""
    try:
        portfolio = perf_service.portfolio_service.repository.get_portfolio(portfolio_id, current_user.sub)
        periodic = perf_service.get_periodic_returns(portfolio_id, current_user.sub, account_id=account_id)
        return PeriodicReturnsResponse(
            portfolio_id=portfolio_id,
            base_currency=portfolio.base_currency,
            returns=[
                PeriodicReturnDTO(
                    period_label=p.period_label,
                    period_type=p.period_type,
                    start_date=p.start_date,
                    end_date=p.end_date,
                    return_value=f"{p.return_value:.4f}" if p.return_value is not None else None,
                    beginning_value=f"{p.beginning_value:.2f}",
                    ending_value=f"{p.ending_value:.2f}",
                    net_external_flows=f"{p.net_external_flows:.2f}",
                    investment_gain=f"{p.investment_gain:.2f}",
                    is_partial=p.is_partial,
                    completeness=p.completeness.value,
                )
                for p in periodic
            ],
        )
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/performance/cash-flows", response_model=List[PerformanceCashFlowDTO])
async def list_cash_flows(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
    period_type: PerformancePeriodType = Query(default=PerformancePeriodType.SINCE_INCEPTION),
    account_id: Optional[str] = Query(default=None),
) -> List[PerformanceCashFlowDTO]:
    """Retrieve list of classified cash flows relative to portfolio/account boundaries."""
    try:
        flows = perf_service.list_classified_cash_flows(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            period_type=period_type,
            account_id=account_id,
        )
        return [
            PerformanceCashFlowDTO(
                id=str(f.id),
                flow_date=f.flow_date,
                classification=f.classification.value,
                native_amount=f"{f.native_amount:.2f}",
                native_currency=f.native_currency,
                base_amount=f"{f.base_amount:.2f}",
                base_currency=f.base_currency,
                fx_rate=f"{f.fx_rate:.4f}",
                investor_flow_amount=f"{f.investor_flow_amount:.2f}",
                portfolio_flow_amount=f"{f.portfolio_flow_amount:.2f}",
                description=f.description,
            )
            for f in flows
        ]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/performance/data-quality", response_model=PerformanceDataQualityDTO)
async def get_performance_data_quality(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    perf_service: Annotated[PortfolioPerformanceService, Depends(get_performance_service)],
    period_type: PerformancePeriodType = Query(default=PerformancePeriodType.YEAR_TO_DATE),
    account_id: Optional[str] = Query(default=None),
) -> PerformanceDataQualityDTO:
    """Retrieve input coverage, quote freshness diagnostics, and calculation warnings."""
    try:
        perf = perf_service.get_performance_summary(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            period_type=period_type,
            account_id=account_id,
        )
        return PerformanceDataQualityDTO(
            completeness=perf.data_quality.completeness.value,
            missing_valuations=perf.data_quality.missing_valuations,
            missing_market_prices=perf.data_quality.missing_market_prices,
            missing_fx_rates=perf.data_quality.missing_fx_rates,
            stale_market_prices=perf.data_quality.stale_market_prices,
            warnings=perf.data_quality.warnings,
            source_manifest=perf.data_quality.source_manifest,
        )
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Stage 112: Portfolio Allocation, Exposure, and Concentration Endpoints
# ---------------------------------------------------------------------------


@router.post("/{portfolio_id}/exposures/calculate", response_model=PortfolioExposureRunResponse)
async def calculate_portfolio_exposure(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    payload: CalculateExposureRequest,
) -> PortfolioExposureRunResponse:
    """Calculate multi-dimensional allocation and exposure decomposition."""
    try:
        run = exposure_service.calculate_portfolio_exposure(portfolio_id, current_user.sub, payload)
        return _map_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/exposures", response_model=PortfolioExposureRunResponse)
async def get_latest_exposure(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    geography_policy: GeographyPolicy = Query(default=GeographyPolicy.ISSUER_DOMICILE),
    enable_look_through: bool = Query(default=True),
    force_recalculate: bool = Query(default=False),
) -> PortfolioExposureRunResponse:
    """Retrieve the latest exposure run or trigger a fresh calculation."""
    try:
        run = exposure_service.get_latest_exposure(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            geography_policy=geography_policy,
            enable_look_through=enable_look_through,
            force_recalculate=force_recalculate,
        )
        return _map_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/exposures/runs", response_model=List[PortfolioExposureRunResponse])
async def list_exposure_runs(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
) -> List[PortfolioExposureRunResponse]:
    """List all calculated exposure runs for a portfolio."""
    try:
        runs = exposure_service.list_exposure_runs(portfolio_id, current_user.sub)
        return [_map_run_to_response(r) for r in runs]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/exposures/runs/{run_id}", response_model=PortfolioExposureRunResponse)
async def get_exposure_run(
    portfolio_id: str,
    run_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
) -> PortfolioExposureRunResponse:
    """Retrieve a specific historical exposure run by run ID."""
    try:
        run = exposure_service.get_exposure_run(portfolio_id, run_id, current_user.sub)
        return _map_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/allocations/asset-classes", response_model=ExposureDimensionResponse)
async def get_asset_class_allocation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> ExposureDimensionResponse:
    """Retrieve canonical asset-class allocation breakdown."""
    try:
        dim = exposure_service.get_asset_class_allocation(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return _map_dim_to_response(dim)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/allocations/sectors", response_model=ExposureDimensionResponse)
async def get_sector_exposure(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> ExposureDimensionResponse:
    """Retrieve GICS sector classification breakdown."""
    try:
        dim = exposure_service.get_sector_exposure(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return _map_dim_to_response(dim)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/allocations/industries", response_model=ExposureDimensionResponse)
async def get_industry_exposure(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> ExposureDimensionResponse:
    """Retrieve GICS industry group/industry classification breakdown."""
    try:
        dim = exposure_service.get_industry_exposure(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return _map_dim_to_response(dim)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/allocations/countries", response_model=ExposureDimensionResponse)
async def get_country_exposure(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    geography_policy: GeographyPolicy = Query(default=GeographyPolicy.ISSUER_DOMICILE),
    enable_look_through: bool = Query(default=True),
) -> ExposureDimensionResponse:
    """Retrieve geographic allocation and country exposure breakdown."""
    try:
        dim = exposure_service.get_country_exposure(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            geography_policy=geography_policy,
            enable_look_through=enable_look_through,
        )
        return _map_dim_to_response(dim)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/allocations/currencies", response_model=ExposureDimensionResponse)
async def get_currency_exposure(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> ExposureDimensionResponse:
    """Retrieve currency denomination exposure breakdown."""
    try:
        dim = exposure_service.get_currency_exposure(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return _map_dim_to_response(dim)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/concentration/securities", response_model=List[SecurityWeightResponse])
async def get_security_weights(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> List[SecurityWeightResponse]:
    """Retrieve individual security-level weights and effective exposures."""
    try:
        weights = exposure_service.get_security_weights(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return [_map_sec_weight_to_response(s) for s in weights]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/concentration/issuers", response_model=List[IssuerWeightResponse])
async def get_issuer_weights(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> List[IssuerWeightResponse]:
    """Retrieve consolidated ultimate economic issuer concentration."""
    try:
        issuers = exposure_service.get_issuer_weights(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return [_map_issuer_weight_to_response(i) for i in issuers]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/concentration/summary", response_model=ConcentrationSummaryResponse)
async def get_concentration_summary(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    exposure_basis: ExposureBasis = Query(default=ExposureBasis.NET_ASSET_VALUE),
    enable_look_through: bool = Query(default=True),
) -> ConcentrationSummaryResponse:
    """Retrieve concentration statistics (Top 1/3/5/10/20, HHI, and Effective Number of Holdings)."""
    try:
        summary = exposure_service.get_concentration_summary(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            exposure_basis=exposure_basis,
            enable_look_through=enable_look_through,
        )
        return _map_concentration_to_response(summary)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/lookthrough", response_model=List[FundLookThroughResponse])
async def get_look_through_details(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
) -> List[FundLookThroughResponse]:
    """Retrieve decomposed constituent look-through for all funds in portfolio."""
    try:
        funds = exposure_service.get_look_through_details(portfolio_id, current_user.sub)
        return [_map_fund_to_response(f) for f in funds]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/lookthrough/funds/{instrument_id}", response_model=FundLookThroughResponse)
async def get_fund_look_through(
    portfolio_id: str,
    instrument_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
) -> FundLookThroughResponse:
    """Retrieve constituent look-through decomposition for a specific fund."""
    try:
        fund = exposure_service.get_fund_look_through(portfolio_id, instrument_id, current_user.sub)
        if not fund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FUND_NOT_FOUND", "message": f"Fund '{instrument_id}' not found in portfolio."},
            )
        return _map_fund_to_response(fund)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/lookthrough/overlap", response_model=List[CrossFundOverlapResponse])
async def get_cross_fund_overlap(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
) -> List[CrossFundOverlapResponse]:
    """Retrieve cross-fund constituent overlap analysis across all ETF/fund holdings."""
    try:
        overlaps = exposure_service.get_cross_fund_overlap(portfolio_id, current_user.sub)
        return [_map_overlap_to_response(o) for o in overlaps]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/exposures/history", response_model=List[HistoricalAllocationPointResponse])
async def get_historical_exposures(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    dimension: ExposureDimension = Query(default=ExposureDimension.ASSET_CLASS),
) -> List[HistoricalAllocationPointResponse]:
    """Retrieve historical allocation trajectory for a specified dimension."""
    try:
        points = exposure_service.get_historical_exposures(portfolio_id, current_user.sub, dimension)
        return [
            HistoricalAllocationPointResponse(
                as_of_date=p.as_of_date,
                dimension=p.dimension,
                category_id=p.category_id,
                category_label=p.category_label,
                weight=p.weight,
                base_value=p.base_value,
                base_currency=p.base_currency,
            )
            for p in points
        ]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/exposures/changes", response_model=List[AllocationChangeResponse])
async def get_allocation_changes(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
    start_date: date = Query(...),
    end_date: date = Query(...),
    dimension: ExposureDimension = Query(default=ExposureDimension.ASSET_CLASS),
) -> List[AllocationChangeResponse]:
    """Calculate date-to-date allocation drift and weight changes (delta_w = w_t2 - w_t1)."""
    try:
        changes = exposure_service.get_allocation_changes(
            portfolio_id, current_user.sub, dimension, start_date, end_date
        )
        return [
            AllocationChangeResponse(
                dimension=c.dimension,
                category_id=c.category_id,
                category_label=c.category_label,
                start_date=c.start_date,
                end_date=c.end_date,
                start_weight=c.start_weight,
                end_weight=c.end_weight,
                weight_change_pct=c.weight_change_pct,
                weight_change_bps=c.weight_change_bps,
                start_value=c.start_value,
                end_value=c.end_value,
                value_change=c.value_change,
            )
            for c in changes
        ]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/exposures/data-quality", response_model=ExposureDataQualityResponse)
async def get_exposure_data_quality(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    exposure_service: Annotated[PortfolioExposureService, Depends(get_exposure_service)],
) -> ExposureDataQualityResponse:
    """Retrieve classification coverage, valuation audit, and reconciliation status."""
    try:
        quality = exposure_service.get_data_quality(portfolio_id, current_user.sub)
        return _map_quality_to_response(quality)
    except Exception as e:
        _handle_error(e)


# ===========================================================================
# STAGE 113: PORTFOLIO PERFORMANCE ATTRIBUTION ENDPOINTS
# ===========================================================================

def _map_attribution_category_to_response(c: Any) -> AttributionCategoryResponse:
    return AttributionCategoryResponse(
        category_id=c.category_id,
        category_label=c.category_label,
        portfolio_weight=c.portfolio_weight,
        benchmark_weight=c.benchmark_weight,
        portfolio_return=c.portfolio_return,
        benchmark_return=c.benchmark_return,
        allocation_effect=c.allocation_effect,
        selection_effect=c.selection_effect,
        interaction_effect=c.interaction_effect,
        total_effect=c.total_effect,
        sub_industries=[_map_attribution_category_to_response(s) for s in c.sub_industries] if c.sub_industries else None,
    )


def _map_security_contribution_to_response(s: Any) -> SecurityContributionResponse:
    return SecurityContributionResponse(
        instrument_id=s.instrument_id,
        symbol=s.symbol,
        name=s.name,
        weight=s.weight,
        security_return=s.security_return,
        contribution=s.contribution,
        sector=s.sector,
        industry=s.industry,
        currency=s.currency,
        is_sold=s.is_sold,
    )


def _map_currency_effect_to_response(c: Any) -> CurrencyEffectResponse:
    return CurrencyEffectResponse(
        currency=c.currency,
        weight=c.weight,
        local_return=c.local_return,
        fx_return=c.fx_return,
        interaction_return=c.interaction_return,
        base_currency_return=c.base_currency_return,
        contribution_to_base=c.contribution_to_base,
    )


def _map_historical_period_to_response(p: Any) -> HistoricalPeriodResponse:
    return HistoricalPeriodResponse(
        period_label=p.period_label,
        period_start=p.period_start,
        period_end=p.period_end,
        portfolio_return=p.portfolio_return,
        benchmark_return=p.benchmark_return,
        active_return=p.active_return,
        allocation_effect=p.allocation_effect,
        selection_effect=p.selection_effect,
        interaction_effect=p.interaction_effect,
        total_attributed=p.total_attributed,
        residual=p.residual,
        category_effects=p.category_effects,
    )


def _map_multi_period_linked_to_response(m: Any) -> MultiPeriodLinkedResponse:
    return MultiPeriodLinkedResponse(
        linking_method=m.linking_method,
        cumulative_portfolio_return=m.cumulative_portfolio_return,
        cumulative_benchmark_return=m.cumulative_benchmark_return,
        cumulative_active_return=m.cumulative_active_return,
        total_allocation_effect=m.total_allocation_effect,
        total_selection_effect=m.total_selection_effect,
        total_interaction_effect=m.total_interaction_effect,
        total_attributed=m.total_attributed,
        reconciliation_residual=m.reconciliation_residual,
        category_results=[_map_attribution_category_to_response(c) for c in m.category_results],
        periods=[_map_historical_period_to_response(p) for p in m.periods],
    )


def _map_attribution_reconciliation_to_response(r: Any) -> AttributionReconciliationResponse:
    return AttributionReconciliationResponse(
        portfolio_return=r.portfolio_return,
        reconstructed_portfolio_return=r.reconstructed_portfolio_return,
        portfolio_return_reconciled=r.portfolio_return_reconciled,
        benchmark_return=r.benchmark_return,
        reconstructed_benchmark_return=r.reconstructed_benchmark_return,
        benchmark_return_reconciled=r.benchmark_return_reconciled,
        active_return=r.active_return,
        total_attributed=r.total_attributed,
        attribution_reconciled=r.attribution_reconciled,
        residual=r.residual,
        security_contributions_sum=r.security_contributions_sum,
        security_contributions_reconciled=r.security_contributions_reconciled,
        status=r.status,
        tolerance=r.tolerance,
    )


def _map_attribution_data_quality_to_response(q: Any) -> AttributionDataQualityResponse:
    return AttributionDataQualityResponse(
        completeness=q.completeness,
        portfolio_holdings_coverage_ratio=q.portfolio_holdings_coverage_ratio,
        benchmark_constituent_coverage_ratio=q.benchmark_constituent_coverage_ratio,
        taxonomy_coverage_ratio=q.taxonomy_coverage_ratio,
        missing_securities_count=q.missing_securities_count,
        unmapped_sector_weight=q.unmapped_sector_weight,
        input_hash=q.input_hash,
        warnings=q.warnings,
    )


def _map_attribution_run_to_response(run: PortfolioAttributionRun) -> PortfolioAttributionRunResponse:
    return PortfolioAttributionRunResponse(
        id=run.id,
        portfolio_id=run.portfolio_id,
        account_id=run.account_id,
        benchmark_id=run.benchmark_id,
        benchmark_name=run.benchmark_name,
        period_start=run.period_start,
        period_end=run.period_end,
        reporting_currency=run.reporting_currency,
        attribution_method=run.attribution_method,
        methodology_version=run.methodology_version,
        classification_dimension=run.classification_dimension,
        taxonomy_id=run.taxonomy_id,
        taxonomy_version=run.taxonomy_version,
        portfolio_return=run.portfolio_return,
        benchmark_return=run.benchmark_return,
        active_return=run.active_return,
        total_allocation_effect=run.total_allocation_effect,
        total_selection_effect=run.total_selection_effect,
        total_interaction_effect=run.total_interaction_effect,
        total_attributed=run.total_attributed,
        reconciliation_residual=run.reconciliation_residual,
        category_results=[_map_attribution_category_to_response(c) for c in run.category_results],
        security_contributions=[_map_security_contribution_to_response(s) for s in run.security_contributions],
        top_contributors=[_map_security_contribution_to_response(s) for s in run.top_contributors],
        top_detractors=[_map_security_contribution_to_response(s) for s in run.top_detractors],
        currency_effects=[_map_currency_effect_to_response(c) for c in run.currency_effects],
        reconciliation=_map_attribution_reconciliation_to_response(run.reconciliation),
        data_quality=_map_attribution_data_quality_to_response(run.data_quality),
        multi_period=_map_multi_period_linked_to_response(run.multi_period) if run.multi_period else None,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


@router.get("/{portfolio_id}/attribution", response_model=PortfolioAttributionRunResponse)
async def get_portfolio_attribution(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> PortfolioAttributionRunResponse:
    """Retrieve the latest valid performance attribution run for a portfolio."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return _map_attribution_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/attribution/calculate", response_model=PortfolioAttributionRunResponse)
async def calculate_portfolio_attribution(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
    request: Optional[CalculateAttributionRequest] = None,
) -> PortfolioAttributionRunResponse:
    """Execute an on-demand performance attribution calculation with specified methodology and parameters."""
    try:
        run = attribution_service.calculate_attribution(portfolio_id, current_user.sub, request)
        return _map_attribution_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/runs", response_model=AttributionRunsListResponse)
async def list_portfolio_attribution_runs(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> AttributionRunsListResponse:
    """List historical performance attribution calculation runs."""
    try:
        runs = attribution_service.list_attribution_runs(portfolio_id, current_user.sub)
        return AttributionRunsListResponse(
            items=[_map_attribution_run_to_response(r) for r in runs],
            total=len(runs),
        )
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/runs/{run_id}", response_model=PortfolioAttributionRunResponse)
async def get_portfolio_attribution_run_by_id(
    portfolio_id: str,
    run_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> PortfolioAttributionRunResponse:
    """Retrieve a specific historical performance attribution run by ID."""
    try:
        run = attribution_service.get_attribution_run(portfolio_id, run_id, current_user.sub)
        return _map_attribution_run_to_response(run)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/effects", response_model=List[AttributionCategoryResponse])
async def get_attribution_effects(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[AttributionCategoryResponse]:
    """Retrieve category-level allocation, selection, and interaction effects."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return [_map_attribution_category_to_response(c) for c in run.category_results]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/securities", response_model=List[SecurityContributionResponse])
async def get_attribution_securities(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[SecurityContributionResponse]:
    """Retrieve security-level return contributions and contributor rankings."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return [_map_security_contribution_to_response(s) for s in run.security_contributions]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/sectors", response_model=List[AttributionCategoryResponse])
async def get_attribution_sectors(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[AttributionCategoryResponse]:
    """Retrieve GICS sector-level performance attribution decomposition."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return [_map_attribution_category_to_response(c) for c in run.category_results]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/industries", response_model=List[AttributionCategoryResponse])
async def get_attribution_industries(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[AttributionCategoryResponse]:
    """Retrieve industry group-level performance attribution decomposition."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        # Return sub-industries if available, else top-level categories
        industries = []
        for c in run.category_results:
            if c.sub_industries:
                industries.extend(c.sub_industries)
            else:
                industries.append(c)
        return [_map_attribution_category_to_response(i) for i in industries]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/currencies", response_model=List[CurrencyEffectResponse])
async def get_attribution_currencies(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[CurrencyEffectResponse]:
    """Retrieve currency translation and local/FX interaction decomposition."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return [_map_currency_effect_to_response(c) for c in run.currency_effects]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/history", response_model=List[HistoricalPeriodResponse])
async def get_attribution_history(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[HistoricalPeriodResponse]:
    """Retrieve discrete historical period attribution results time series."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        if run.multi_period:
            return [_map_historical_period_to_response(p) for p in run.multi_period.periods]
        return []
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/linked", response_model=Optional[MultiPeriodLinkedResponse])
async def get_attribution_linked(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> Optional[MultiPeriodLinkedResponse]:
    """Retrieve multi-period logarithmic linked attribution results (Carino methodology)."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return _map_multi_period_linked_to_response(run.multi_period) if run.multi_period else None
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/reconciliation", response_model=AttributionReconciliationResponse)
async def get_attribution_reconciliation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> AttributionReconciliationResponse:
    """Retrieve mathematical audit checks, residual verification, and tolerance status."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return _map_attribution_reconciliation_to_response(run.reconciliation)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/data-quality", response_model=AttributionDataQualityResponse)
async def get_attribution_data_quality(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> AttributionDataQualityResponse:
    """Retrieve data completeness, taxonomy coverage, and cryptographic input hash."""
    try:
        run = attribution_service.get_latest_attribution(portfolio_id, current_user.sub)
        return _map_attribution_data_quality_to_response(run.data_quality)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/attribution/benchmarks", response_model=List[AttributionBenchmarkSummaryResponse])
async def list_attribution_benchmarks(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    attribution_service: Annotated[PortfolioAttributionService, Depends(get_attribution_service)],
) -> List[AttributionBenchmarkSummaryResponse]:
    """List supported benchmarks for performance attribution and constituent availability."""
    try:
        benchmarks = list_canonical_benchmarks()
        return [
            AttributionBenchmarkSummaryResponse(
                benchmark_id=b.benchmark_id,
                name=b.name,
                symbol=b.symbol,
                benchmark_type=b.benchmark_type,
                return_basis=b.return_basis.value,
                currency=b.currency,
                description=b.description,
                has_constituent_data=True,
            )
            for b in benchmarks
        ]
    except Exception as e:
        _handle_error(e)

