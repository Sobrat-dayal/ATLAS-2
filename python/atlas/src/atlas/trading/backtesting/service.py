"""Master NautilusTrader Backtesting and Strategy Research Service (Stage 143)."""

from __future__ import annotations

import copy
import uuid
from typing import Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.trading.backtesting.data.catalog import AtlasDataCatalog
from atlas.trading.backtesting.data.manifests import HistoricalDatasetRegistry
from atlas.trading.backtesting.domain import (
    AtlasBacktestConfig,
    AtlasBacktestResult,
    AtlasStrategyDefinition,
    HistoricalDatasetManifest,
    ParameterExperimentConfig,
    ParameterExperimentResult,
    STAGE_143_DISCLAIMERS,
    WalkForwardResult,
)
from atlas.trading.backtesting.nautilus.runner import IsolatedBacktestRunner
from atlas.trading.backtesting.persistence.repository import BacktestRunRepository
from atlas.trading.backtesting.research.comparisons import compare_backtest_runs
from atlas.trading.backtesting.research.experiments import ParameterExperimentEngine
from atlas.trading.backtesting.research.walk_forward import WalkForwardEngine
from atlas.trading.backtesting.strategies.registry import StrategyRegistry


class AtlasBacktestingService:
    """Master institutional backtesting and quantitative strategy research orchestrator."""

    def __init__(
        self,
        strategy_registry: Optional[StrategyRegistry] = None,
        dataset_registry: Optional[HistoricalDatasetRegistry] = None,
        catalog: Optional[AtlasDataCatalog] = None,
        repository: Optional[BacktestRunRepository] = None,
    ):
        self.strategy_registry = strategy_registry or StrategyRegistry()
        self.dataset_registry = dataset_registry or HistoricalDatasetRegistry()
        self.catalog = catalog or AtlasDataCatalog(dataset_registry=self.dataset_registry)
        self.repository = repository or BacktestRunRepository()

        self.runner = IsolatedBacktestRunner(catalog=self.catalog)
        self.experiment_engine = ParameterExperimentEngine(runner=self.runner)
        self.walk_forward_engine = WalkForwardEngine(runner=self.runner)

    def get_capabilities(self) -> Dict[str, Any]:
        """Return supported backtesting features, NautilusTrader version, and disclaimers."""
        return {
            "stage": 143,
            "system_name": "ATLAS NautilusTrader Historical Backtesting Engine",
            "nautilus_version": "1.231.0",
            "supported_instruments": ["EQUITY", "ETF", "OPTION", "FUTURES", "FX"],
            "registered_strategies_count": len(self.strategy_registry.list_strategies()),
            "datasets_count": len(self.dataset_registry.list_manifests()),
            "disclaimers": STAGE_143_DISCLAIMERS,
            "security_policies": {
                "tenant_isolation_enforced": True,
                "zero_fabrication_enforced": True,
                "no_look_ahead_enforced": True,
                "paper_trading_allowed": False,  # Reserved for Stage 144
                "broker_order_routing_allowed": False,  # Reserved for Stage 145
            },
        }

    # Strategy Management
    def list_strategies(self) -> List[AtlasStrategyDefinition]:
        return self.strategy_registry.list_strategies()

    def get_strategy(self, strategy_id: str) -> AtlasStrategyDefinition:
        return self.strategy_registry.get_strategy(strategy_id)

    # Dataset Management
    def list_datasets(self) -> List[HistoricalDatasetManifest]:
        return self.dataset_registry.list_manifests()

    def get_dataset(self, dataset_id: str) -> HistoricalDatasetManifest:
        return self.dataset_registry.get_manifest(dataset_id)

    # Run Execution
    def execute_backtest(
        self,
        config: AtlasBacktestConfig,
        custom_bars: Optional[List[Dict[str, Any]]] = None,
        principal: Optional[AuthPrincipal] = None,
    ) -> AtlasBacktestResult:
        """Validate parameters and execute an isolated historical simulation run."""
        # 1. Validate parameters against strategy schema
        config.strategy_parameters = self.strategy_registry.validate_parameters(
            config.strategy_id,
            config.strategy_parameters,
        )

        # 2. Run simulation
        result = self.runner.run_backtest(config, custom_bars=custom_bars)

        # 3. Save to repository with tenant context
        return self.repository.save_run(result, principal=principal)

    def get_run(
        self,
        run_id: str,
        principal: Optional[AuthPrincipal] = None,
    ) -> Optional[AtlasBacktestResult]:
        """Retrieve run enforcing multi-tenant RLS checks (Test V)."""
        return self.repository.get_run(run_id, principal=principal)

    def list_runs(
        self,
        principal: AuthPrincipal,
    ) -> List[AtlasBacktestResult]:
        return self.repository.list_runs_for_user(principal)

    # Research & Optimization
    def run_parameter_experiment(
        self,
        exp_config: ParameterExperimentConfig,
        custom_bars: Optional[List[Dict[str, Any]]] = None,
        principal: Optional[AuthPrincipal] = None,
    ) -> ParameterExperimentResult:
        """Execute multi-parameter sweep."""
        res = self.experiment_engine.run_parameter_sweep(exp_config, custom_bars=custom_bars)
        self.repository.save_experiment(res)
        return res

    def run_walk_forward_validation(
        self,
        walk_forward_id: str,
        base_config: AtlasBacktestConfig,
        fold_windows: List[Dict[str, str]],
        param_candidates: List[Dict[str, Any]],
        principal: Optional[AuthPrincipal] = None,
    ) -> WalkForwardResult:
        """Execute chronological sliding walk-forward validation (Test R)."""
        res = self.walk_forward_engine.run_walk_forward(
            walk_forward_id=walk_forward_id,
            base_config=base_config,
            fold_windows=fold_windows,
            param_candidates=param_candidates,
        )
        self.repository.save_walk_forward(res)
        return res

    def compare_runs(
        self,
        run_ids: List[str],
        principal: Optional[AuthPrincipal] = None,
    ) -> List[Dict[str, Any]]:
        """Compare multiple runs side-by-side."""
        resolved: List[AtlasBacktestResult] = []
        for r_id in run_ids:
            run = self.get_run(r_id, principal=principal)
            if run:
                resolved.append(run)
        return compare_backtest_runs(resolved)
