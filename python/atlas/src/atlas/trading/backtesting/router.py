"""FastAPI REST Router for NautilusTrader Backtesting Engine (Stage 143)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from atlas.auth import AuthPrincipal
from atlas.trading.backtesting.domain import (
    AtlasBacktestConfig,
    AtlasBacktestResult,
    FeeModelType,
    FillModelType,
    LatencyModelType,
    ParameterExperimentConfig,
    SlippagePolicy,
)
from atlas.trading.backtesting.errors import (
    BacktestDatasetIneligibleError,
    BacktestDatasetNotFoundError,
    BacktestDomainError,
    BacktestInvalidParameterError,
    BacktestLicenseRevokedError,
    BacktestLookAheadError,
    BacktestMultiTenantAccessDeniedError,
    BacktestResourceQuotaExceededError,
    BacktestStrategyNotFoundError,
)
from atlas.trading.backtesting.service import AtlasBacktestingService


def get_current_principal() -> AuthPrincipal:
    return AuthPrincipal(sub="DEFAULT_USER", raw_claims={"tenant_id": "default_tenant"})


router = APIRouter(prefix="/trading/backtests", tags=["trading-backtests"])

_backtesting_service = AtlasBacktestingService()


def get_backtesting_service() -> AtlasBacktestingService:
    return _backtesting_service


# Request Models
class ExecuteBacktestRequest(BaseModel):
    strategy_id: str
    strategy_version: str = "1.0.0"
    strategy_parameters: Dict[str, Any] = Field(default_factory=dict)
    dataset_id: str = "ds_spy_daily_2024"
    instrument_ids: List[str] = Field(default_factory=lambda: ["SPY.SIM"])
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    initial_cash: float = 100_000.0
    base_currency: str = "USD"
    account_type: str = "MARGIN"
    fill_model: str = "TOUCHED_BID_ASK"
    slippage_policy: str = "NONE"
    slippage_value: float = 0.0
    fee_model: str = "PER_SHARE"
    commission_rate: float = 0.005
    latency_model: str = "ZERO_LATENCY"
    latency_ms: float = 0.0
    max_position_size: Optional[float] = None
    random_seed: int = 42
    is_private: bool = True
    custom_bars: Optional[List[Dict[str, Any]]] = None


class RunExperimentRequest(BaseModel):
    experiment_id: Optional[str] = None
    strategy_id: str
    dataset_id: str = "ds_spy_daily_2024"
    parameter_grid: Dict[str, List[Any]]
    base_backtest_params: Dict[str, Any] = Field(default_factory=dict)
    objective_metric: str = "sharpe_ratio"
    max_combinations: int = 50
    custom_bars: Optional[List[Dict[str, Any]]] = None


class RunWalkForwardRequest(BaseModel):
    walk_forward_id: Optional[str] = None
    strategy_id: str
    dataset_id: str = "ds_spy_daily_2024"
    fold_windows: List[Dict[str, str]]
    param_candidates: List[Dict[str, Any]]
    base_backtest_params: Dict[str, Any] = Field(default_factory=dict)


class CompareRunsRequest(BaseModel):
    run_ids: List[str]


@router.get("/capabilities")
def get_capabilities(
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Retrieve supported backtesting engine capabilities, Nautilus version, and policies."""
    return service.get_capabilities()


@router.get("/strategies")
def list_strategies(
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """List registered canonical and custom trading strategies."""
    return {"strategies": service.list_strategies()}


@router.get("/strategies/{strategy_id}")
def get_strategy(
    strategy_id: str,
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Retrieve single strategy definition and parameter schema."""
    try:
        return service.get_strategy(strategy_id)
    except BacktestStrategyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/datasets")
def list_datasets(
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """List licensed historical market datasets and coverage manifests."""
    return {"datasets": service.list_datasets()}


@router.get("/datasets/{dataset_id}")
def get_dataset(
    dataset_id: str,
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Retrieve historical dataset manifest by ID."""
    try:
        return service.get_dataset(dataset_id)
    except BacktestDatasetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except BacktestLicenseRevokedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.post("/runs")
def execute_backtest_run(
    req: ExecuteBacktestRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Execute a single historical backtest simulation."""
    run_id = f"run_bt_{uuid.uuid4().hex[:10]}"
    try:
        config = AtlasBacktestConfig(
            run_id=run_id,
            owner_id=principal.sub,
            strategy_id=req.strategy_id,
            strategy_version=req.strategy_version,
            strategy_parameters=req.strategy_parameters,
            instrument_ids=req.instrument_ids,
            dataset_id=req.dataset_id,
            start_date=req.start_date,
            end_date=req.end_date,
            initial_cash=req.initial_cash,
            base_currency=req.base_currency,
            account_type=req.account_type,
            fill_model=FillModelType(req.fill_model),
            slippage_policy=SlippagePolicy(req.slippage_policy),
            slippage_value=req.slippage_value,
            fee_model=FeeModelType(req.fee_model),
            commission_rate=req.commission_rate,
            latency_model=LatencyModelType(req.latency_model),
            latency_ms=req.latency_ms,
            max_position_size=req.max_position_size,
            random_seed=req.random_seed,
            tenant_id=principal.raw_claims.get("tenant_id") or "default_tenant",
            is_private=req.is_private,
        )

        return service.execute_backtest(config, custom_bars=req.custom_bars, principal=principal)
    except (BacktestDatasetNotFoundError, BacktestStrategyNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except BacktestLicenseRevokedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except (BacktestDatasetIneligibleError, BacktestInvalidParameterError, BacktestLookAheadError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
    except BacktestResourceQuotaExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)


@router.get("/runs/{run_id}")
def get_backtest_run(
    run_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Retrieve full completed backtest result enforcing multi-tenant RLS checks."""
    try:
        res = service.get_run(run_id, principal=principal)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found.")
        return res
    except BacktestMultiTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("/runs")
def list_user_backtest_runs(
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """List historical backtest runs accessible to authenticated principal."""
    runs = service.list_runs(principal)
    return {
        "runs": [
            {
                "run_id": r.run_id,
                "strategy_id": r.config.strategy_id,
                "dataset_id": r.config.dataset_id,
                "total_return_pct": r.performance.total_return_pct,
                "sharpe_ratio": r.performance.sharpe_ratio,
                "max_drawdown_pct": r.performance.drawdown.max_drawdown_pct,
                "trades_count": r.performance.total_trades_count,
                "completed_at": r.execution_time_seconds,
            }
            for r in runs
        ]
    }


@router.post("/experiments")
def run_parameter_experiment(
    req: RunExperimentRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Execute multi-parameter sweep experiment."""
    exp_id = req.experiment_id or f"exp_{uuid.uuid4().hex[:10]}"
    try:
        base_cfg = AtlasBacktestConfig(
            run_id=f"{exp_id}_base",
            owner_id=principal.sub,
            strategy_id=req.strategy_id,
            dataset_id=req.dataset_id,
            tenant_id=principal.raw_claims.get("tenant_id") or "default_tenant",
        )
        exp_cfg = ParameterExperimentConfig(
            experiment_id=exp_id,
            strategy_id=req.strategy_id,
            dataset_id=req.dataset_id,
            parameter_grid=req.parameter_grid,
            base_config=base_cfg,
            objective_metric=req.objective_metric,
            max_combinations=req.max_combinations,
        )
        return service.run_parameter_experiment(exp_cfg, custom_bars=req.custom_bars, principal=principal)
    except BacktestResourceQuotaExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)


@router.post("/walk-forward")
def run_walk_forward_validation(
    req: RunWalkForwardRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Execute chronological sliding walk-forward validation (Test R)."""
    wf_id = req.walk_forward_id or f"wf_{uuid.uuid4().hex[:10]}"
    base_cfg = AtlasBacktestConfig(
        run_id=f"{wf_id}_base",
        owner_id=principal.sub,
        strategy_id=req.strategy_id,
        dataset_id=req.dataset_id,
        tenant_id=principal.raw_claims.get("tenant_id") or "default_tenant",
    )
    return service.run_walk_forward_validation(
        walk_forward_id=wf_id,
        base_config=base_cfg,
        fold_windows=req.fold_windows,
        param_candidates=req.param_candidates,
        principal=principal,
    )


@router.post("/compare")
def compare_completed_runs(
    req: CompareRunsRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasBacktestingService = Depends(get_backtesting_service),
):
    """Compare multiple completed backtest runs across standardized metrics."""
    return {"comparison": service.compare_runs(req.run_ids, principal=principal)}
