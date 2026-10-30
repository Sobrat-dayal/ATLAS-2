"""ATLAS Portfolios V1 — Optimization Orchestration Service (Stage 114).

Coordinates portfolio optimization studies, runs, universe construction,
expected return and covariance estimation, numerical solving, frontier building,
rebalancing calculations, and tenant isolation.
"""

from datetime import datetime
from decimal import Decimal
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
import uuid

import numpy as np

from atlas.portfolios.exposure.registry import get_instrument_classification
from atlas.portfolios.optimization.constraints import ConstraintEngine
from atlas.portfolios.optimization.enums import (
    ConstraintType,
    CovarianceModel,
    ExpectedReturnModel,
    FeasibilityStatus,
    OptimizationObjective,
    SolverStatus,
    StudyStatus,
)
from atlas.portfolios.optimization.errors import (
    PortfolioOptimizationAccessDeniedError,
    PortfolioOptimizationError,
    PortfolioOptimizationNavInvalidError,
    PortfolioOptimizationRunNotFoundError,
    PortfolioOptimizationStudyNotFoundError,
    PortfolioOptimizationUniverseEmptyError,
)
from atlas.portfolios.optimization.estimation import CovarianceEngine, ExpectedReturnEngine
from atlas.portfolios.optimization.frontier import EfficientFrontierBuilder
from atlas.portfolios.optimization.models import (
    CandidatePortfolio,
    CovarianceEstimate,
    ExpectedReturnEstimate,
    OptimizationConstraintItem,
    OptimizationStudy,
    PortfolioOptimizationRun,
    SolverDiagnostics,
)
from atlas.portfolios.optimization.rebalancing import RebalancingEngine
from atlas.portfolios.optimization.sensitivity import SensitivityEngine
from atlas.portfolios.optimization.solvers import ConvexOptimizationSolver
from atlas.portfolios.service import PortfolioService

logger = logging.getLogger("atlas.portfolios.optimization.service")


class PortfolioOptimizationService:
    """Institutional-grade portfolio optimization and quantitative asset allocation service."""

    def __init__(
        self,
        portfolio_service: Optional[PortfolioService] = None,
    ) -> None:
        self.portfolio_service = portfolio_service or PortfolioService()
        self.return_engine = ExpectedReturnEngine()
        self.covariance_engine = CovarianceEngine()
        self.constraint_engine = ConstraintEngine()
        self.solver = ConvexOptimizationSolver()
        self.frontier_builder = EfficientFrontierBuilder(self.solver)
        self.rebalancing_engine = RebalancingEngine()
        self.sensitivity_engine = SensitivityEngine(self.solver)

        self._studies: Dict[str, OptimizationStudy] = {}
        self._portfolio_studies: Dict[str, List[str]] = {}
        self._runs: Dict[str, PortfolioOptimizationRun] = {}
        self._portfolio_runs: Dict[str, List[str]] = {}

    def create_study(
        self,
        portfolio_id: str,
        user_id: str,
        name: str,
        description: str = "",
        default_objective: OptimizationObjective = OptimizationObjective.MINIMUM_VARIANCE,
        universe_symbols: Optional[List[str]] = None,
    ) -> OptimizationStudy:
        """Creates a persistent portfolio optimization study."""
        portfolio = self.portfolio_service.get_portfolio(portfolio_id, user_id)
        study_id = f"opt_std_{uuid.uuid4().hex[:12]}"

        study = OptimizationStudy(
            study_id=study_id,
            portfolio_id=portfolio_id,
            owner_user_id=user_id,
            name=name,
            description=description,
            status=StudyStatus.ACTIVE,
            default_objective=default_objective,
            universe_symbols=universe_symbols or [],
            base_currency=portfolio.base_currency,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._studies[study_id] = study
        if portfolio_id not in self._portfolio_studies:
            self._portfolio_studies[portfolio_id] = []
        self._portfolio_studies[portfolio_id].append(study_id)

        return study

    def get_study(
        self,
        portfolio_id: str,
        study_id: str,
        user_id: str,
    ) -> OptimizationStudy:
        """Retrieves an authorized optimization study."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        study = self._studies.get(study_id)
        if not study or study.portfolio_id != portfolio_id:
            raise PortfolioOptimizationStudyNotFoundError(f"Optimization study {study_id} not found")
        if study.owner_user_id != user_id:
            raise PortfolioOptimizationAccessDeniedError("Unauthorized access to optimization study")
        return study

    def archive_study(
        self,
        portfolio_id: str,
        study_id: str,
        user_id: str,
    ) -> OptimizationStudy:
        """Archives a portfolio optimization study."""
        study = self.get_study(portfolio_id, study_id, user_id)
        study.status = StudyStatus.ARCHIVED
        study.updated_at = datetime.utcnow()
        return study

    def list_studies(
        self,
        portfolio_id: str,
        user_id: str,
    ) -> List[OptimizationStudy]:
        """Lists active optimization studies for a portfolio."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        study_ids = self._portfolio_studies.get(portfolio_id, [])
        return [
            self._studies[sid]
            for sid in study_ids
            if sid in self._studies and self._studies[sid].status == StudyStatus.ACTIVE
        ]

    def execute_optimization(
        self,
        portfolio_id: str,
        user_id: str,
        study_id: Optional[str] = None,
        objective_type: OptimizationObjective = OptimizationObjective.MINIMUM_VARIANCE,
        universe_symbols: Optional[List[str]] = None,
        expected_return_model: ExpectedReturnModel = ExpectedReturnModel.HISTORICAL_ARITHMETIC_MEAN,
        covariance_model: CovarianceModel = CovarianceModel.SAMPLE_COVARIANCE,
        user_return_assumptions: Optional[Dict[str, Decimal]] = None,
        constraints: Optional[List[OptimizationConstraintItem]] = None,
        risk_aversion: float = 2.0,
        risk_free_rate: float = 0.045,
        target_return: Optional[float] = None,
        max_turnover: Optional[float] = None,
        proportional_cost_rate: Decimal = Decimal("0.0010"),
        is_long_only: bool = True,
    ) -> PortfolioOptimizationRun:
        """Executes full mathematical portfolio optimization and produces candidate allocation."""
        # 1. Enforce portfolio access control
        portfolio = self.portfolio_service.get_portfolio(portfolio_id, user_id)

        # 2. Retrieve actual positions, cash, and NAV from Stage 110
        val = self.portfolio_service.get_latest_valuation(portfolio_id, user_id)
        if not val:
            val = self.portfolio_service.calculate_portfolio_valuation(portfolio_id, user_id)
        positions = self.portfolio_service.get_positions(portfolio_id, user_id)
        cash_balances = self.portfolio_service.get_cash_balances(portfolio_id, user_id)

        pos_val_map = {pv.symbol: pv for pv in (val.position_valuations if val else [])}
        total_positions_val = Decimal("0.00")
        for pos in positions:
            pv = pos_val_map.get(pos.symbol)
            mkt_val = (
                pv.base_market_value
                if pv and pv.base_market_value is not None and pv.base_market_value > Decimal("0.00")
                else pos.remaining_cost_basis
            )
            total_positions_val += mkt_val

        cash_total = (
            val.total_cash_market_value
            if val and val.total_cash_market_value > Decimal("0.00")
            else sum((c.available_cash for c in cash_balances), Decimal("0.00"))
        )

        nav = total_positions_val + cash_total
        if nav <= Decimal("0.00"):
            nav = Decimal("100000.00")

        # 3. Establish Baseline Weights
        baseline_weights: Dict[str, Decimal] = {}
        for pos in positions:
            pv = pos_val_map.get(pos.symbol)
            mkt_val = (
                pv.base_market_value
                if pv and pv.base_market_value is not None and pv.base_market_value > Decimal("0.00")
                else pos.remaining_cost_basis
            )
            baseline_weights[pos.symbol] = mkt_val / nav

        if cash_total > Decimal("0.00"):
            baseline_weights["CASH"] = cash_total / nav
        elif "CASH" not in baseline_weights:
            baseline_weights["CASH"] = Decimal("0.00")

        # 4. Resolve Eligible Universe
        symbols: List[str] = []
        if universe_symbols and len(universe_symbols) > 0:
            symbols = list(dict.fromkeys(universe_symbols))
        else:
            symbols = list(baseline_weights.keys())

        if "CASH" not in symbols and "CASH" in baseline_weights:
            symbols.append("CASH")

        if len(symbols) == 0:
            raise PortfolioOptimizationUniverseEmptyError("Investment universe contains no eligible instruments")

        n = len(symbols)

        # 5. Estimate Expected Returns & Covariance Matrix
        exp_return_est = self.return_engine.estimate(
            symbols=symbols,
            model=expected_return_model,
            user_assumptions=user_return_assumptions,
        )
        cov_est = self.covariance_engine.estimate(
            symbols=symbols,
            model=covariance_model,
        )

        mu_vec = np.array([float(exp_return_est.estimates.get(s, Decimal("0.08"))) for s in symbols])
        sigma_mat = np.array(cov_est.matrix, dtype=float)

        # 6. Compile Constraints and Precheck Feasibility
        applied_constraints = constraints or []
        self.constraint_engine.precheck_feasibility(
            symbols=symbols,
            constraints=applied_constraints,
            is_long_only=is_long_only,
        )

        bounds, scipy_constraints = self.constraint_engine.build_scipy_bounds_and_constraints(
            symbols=symbols,
            constraints=applied_constraints,
            expected_returns=mu_vec,
            target_return=target_return,
            baseline_weights=baseline_weights,
            max_turnover=max_turnover,
            is_long_only=is_long_only,
        )

        # 7. Numerical Solver Execution
        opt_weights_vec, diagnostics = self.solver.solve(
            symbols=symbols,
            objective_type=objective_type,
            cov_matrix=sigma_mat,
            expected_returns=mu_vec,
            bounds=bounds,
            constraints=scipy_constraints,
            risk_aversion=risk_aversion,
            risk_free_rate=risk_free_rate,
            target_return=target_return,
            initial_weights=np.array([float(baseline_weights.get(s, Decimal("0.0"))) for s in symbols]),
        )

        # 8. Post-Solution Feasibility and Slack Verification
        candidate_weights_dict = {
            symbols[i]: Decimal(str(round(float(opt_weights_vec[i]), 6))) for i in range(n)
        }
        feas_status, slacks, active_cons = self.constraint_engine.verify_solution(
            symbols=symbols,
            weights=candidate_weights_dict,
            constraints=applied_constraints,
        )
        diagnostics.active_constraints = active_cons

        # 9. Compute Portfolio Candidate Metrics
        cand_return = Decimal(str(round(float(np.dot(mu_vec, opt_weights_vec)), 6)))
        cand_var = Decimal(str(round(float(np.dot(opt_weights_vec, np.dot(sigma_mat, opt_weights_vec))), 6)))
        cand_vol = Decimal(str(round(float(np.sqrt(max(float(cand_var), 1e-9))), 6)))
        rf_dec = Decimal(str(risk_free_rate))
        cand_sharpe = (cand_return - rf_dec) / cand_vol if cand_vol > Decimal("0.0001") else Decimal("0.00")

        # 10. Rebalancing & Turnover Comparisons
        comparisons, one_way_to, est_cost = self.rebalancing_engine.compute_comparisons(
            symbols=symbols,
            current_weights=baseline_weights,
            candidate_weights=candidate_weights_dict,
            portfolio_nav=nav,
            proportional_cost_rate=proportional_cost_rate,
        )

        cash_weight = candidate_weights_dict.get("CASH", Decimal("0.00"))

        candidate = CandidatePortfolio(
            weights=candidate_weights_dict,
            cash_weight=cash_weight,
            estimated_return=cand_return,
            estimated_variance=cand_var,
            estimated_volatility=cand_vol,
            estimated_sharpe=cand_sharpe,
            estimated_turnover=one_way_to,
            estimated_cost=est_cost,
            feasibility_status=feas_status,
            constraint_slacks=slacks,
        )

        # 11. Efficient Frontier Construction
        frontier_points = self.frontier_builder.construct_frontier(
            symbols=symbols,
            cov_matrix=sigma_mat,
            expected_returns=mu_vec,
            bounds=bounds,
            base_constraints=scipy_constraints,
            num_points=12,
            risk_free_rate=risk_free_rate,
        )

        # 12. Sensitivity Scenarios
        sensitivity_results = self.sensitivity_engine.run_scenarios(
            symbols=symbols,
            base_cov=sigma_mat,
            base_returns=mu_vec,
            base_bounds=bounds,
            base_constraints=scipy_constraints,
            baseline_weights=baseline_weights,
            risk_aversion=risk_aversion,
        )

        # 13. Deterministic SHA-256 Provenance Hash
        hasher = hashlib.sha256()
        hasher.update(portfolio_id.encode())
        hasher.update(objective_type.value.encode())
        hasher.update("".join(symbols).encode())
        hasher.update(str(cand_return).encode())
        hasher.update(str(cand_var).encode())
        input_hash = hasher.hexdigest()

        run_id = f"opt_run_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        run = PortfolioOptimizationRun(
            run_id=run_id,
            study_id=study_id,
            portfolio_id=portfolio_id,
            owner_user_id=user_id,
            objective_type=objective_type,
            base_currency=portfolio.base_currency,
            universe_symbols=symbols,
            baseline_nav=nav,
            baseline_weights=baseline_weights,
            expected_returns=exp_return_est,
            covariance=cov_est,
            constraints=applied_constraints,
            candidate=candidate,
            frontier_points=frontier_points,
            comparisons=comparisons,
            diagnostics=diagnostics,
            sensitivity_results=sensitivity_results,
            input_hash=input_hash,
            created_at=now,
            completed_at=now,
        )

        self._runs[run_id] = run
        if portfolio_id not in self._portfolio_runs:
            self._portfolio_runs[portfolio_id] = []
        self._portfolio_runs[portfolio_id].append(run_id)

        return run

    def get_run(
        self,
        portfolio_id: str,
        run_id: str,
        user_id: str,
    ) -> PortfolioOptimizationRun:
        """Retrieves an immutable optimization calculation run."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        run = self._runs.get(run_id)
        if not run or run.portfolio_id != portfolio_id:
            raise PortfolioOptimizationRunNotFoundError(f"Optimization run {run_id} not found")
        if run.owner_user_id != user_id:
            raise PortfolioOptimizationAccessDeniedError("Unauthorized access to optimization run")
        return run

    def get_latest_run(
        self,
        portfolio_id: str,
        user_id: str,
    ) -> PortfolioOptimizationRun:
        """Retrieves the latest valid optimization run or computes a default one."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        run_ids = self._portfolio_runs.get(portfolio_id, [])
        if run_ids:
            latest_id = run_ids[-1]
            if latest_id in self._runs:
                return self._runs[latest_id]

        return self.execute_optimization(
            portfolio_id=portfolio_id,
            user_id=user_id,
            objective_type=OptimizationObjective.MINIMUM_VARIANCE,
        )

    def list_runs(
        self,
        portfolio_id: str,
        user_id: str,
        study_id: Optional[str] = None,
    ) -> List[PortfolioOptimizationRun]:
        """Lists historical optimization runs for a portfolio."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        run_ids = self._portfolio_runs.get(portfolio_id, [])
        runs = [self._runs[rid] for rid in run_ids if rid in self._runs]
        if study_id:
            runs = [r for r in runs if r.study_id == study_id]
        return runs

    def get_eligible_universe(
        self,
        portfolio_id: str,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Returns eligible universe assets including current holdings and liquid instruments."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        positions = self.portfolio_service.get_positions(portfolio_id, user_id)

        expanded = [
            {"symbol": "AAPL", "name": "Apple Inc.", "asset_class": "EQUITY", "sector": "Information Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "asset_class": "EQUITY", "sector": "Information Technology"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "asset_class": "EQUITY", "sector": "Information Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "asset_class": "EQUITY", "sector": "Consumer Discretionary"},
            {"symbol": "GOOGL", "name": "Alphabet Inc. Cl A", "asset_class": "EQUITY", "sector": "Communication Services"},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "asset_class": "ETF", "sector": "Broad Market"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "asset_class": "ETF", "sector": "Technology"},
            {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "asset_class": "FIXED_INCOME", "sector": "Aggregate Bond"},
            {"symbol": "GLD", "name": "SPDR Gold Shares", "asset_class": "COMMODITY", "sector": "Precious Metals"},
            {"symbol": "CASH", "name": "Cash & Cash Equivalents", "asset_class": "CASH", "sector": "Cash"},
        ]

        res: List[Dict[str, Any]] = []
        seen = set()
        for p in positions:
            sym = p.symbol
            seen.add(sym)
            res.append({
                "symbol": sym,
                "name": getattr(p, "company_name", None) or sym,
                "asset_class": "EQUITY",
                "sector": "Broad Market",
                "is_current_holding": True,
            })
        if "CASH" not in seen:
            res.append({
                "symbol": "CASH",
                "name": "Cash & Cash Equivalents",
                "asset_class": "CASH",
                "sector": "Cash",
                "is_current_holding": True,
            })
            seen.add("CASH")
        for item in expanded:
            if item["symbol"] not in seen:
                seen.add(item["symbol"])
                res.append({
                    "symbol": item["symbol"],
                    "name": item["name"],
                    "asset_class": item["asset_class"],
                    "sector": item["sector"],
                    "is_current_holding": False,
                })
        return res

    def validate_constraints(
        self,
        portfolio_id: str,
        user_id: str,
        constraints: List[OptimizationConstraintItem],
        universe_symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Validates constraints for mutual consistency and budget feasibility."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        positions = self.portfolio_service.get_positions(portfolio_id, user_id)
        symbols = universe_symbols or ([p.symbol for p in positions] + ["CASH"])
        symbols = list(dict.fromkeys(symbols))
        try:
            self.constraint_engine.precheck_feasibility(constraints, symbols)
            return {
                "is_feasible": True,
                "message": "All constraints are mathematically feasible and consistent with portfolio budget.",
                "constraint_count": len(constraints),
                "conflicts": [],
            }
        except PortfolioOptimizationError as err:
            return {
                "is_feasible": False,
                "message": err.message if hasattr(err, "message") else str(err),
                "constraint_count": len(constraints),
                "conflicts": [err.message if hasattr(err, "message") else str(err)],
            }

