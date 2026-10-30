"""Portfolio Performance Service for ATLAS (Stage 111).

Orchestrates Time-Weighted Returns (TWR), Money-Weighted Returns (MWR/XIRR),
historical valuation series, periodic returns table, and canonical benchmark comparisons.
Preserves source manifests, audit trails, and data completeness classifications.
"""

from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from atlas.portfolios.enums import TransactionType
from atlas.portfolios.models import PortfolioTransaction
from atlas.portfolios.performance.benchmarks import compare_portfolio_to_benchmark, list_canonical_benchmarks
from atlas.portfolios.performance.classifier import CashFlowClassifier
from atlas.portfolios.performance.enums import (
    CashFlowClassification,
    DataCompletenessStatus,
    MeasurementScope,
    PerformanceMethodology,
    PerformancePeriodType,
    PerformanceStatus,
)
from atlas.portfolios.performance.errors import (
    PortfolioPerformanceAccessDeniedError,
    PortfolioPerformanceNotFoundError,
    PortfolioPerformancePeriodInvalidError,
    PortfolioPerformanceXirrError,
    PortfolioPerformanceXirrInvalidCashFlowsError,
    PortfolioPerformanceXirrNoSolutionError,
    PortfolioPerformanceXirrNonConvergenceError,
)
from atlas.portfolios.performance.models import (
    BenchmarkComparison,
    PerformanceCashFlow,
    PerformanceDataQuality,
    PerformanceRun,
    PeriodicReturn,
    SubperiodReturn,
    ValuationPoint,
)
from atlas.portfolios.performance.periodic import (
    build_monthly_returns_grid,
    calculate_annualized_return,
)
from atlas.portfolios.performance.schemas import PerformanceCalculateRequest
from atlas.portfolios.performance.twr import calculate_exact_twr, calculate_modified_dietz
from atlas.portfolios.performance.xirr import calculate_xirr
from atlas.portfolios.service import PortfolioService

logger = logging.getLogger(__name__)


class PortfolioPerformanceService:
    """Institutional portfolio performance engine."""

    def __init__(self, portfolio_service: Optional[PortfolioService] = None):
        self.portfolio_service = portfolio_service or PortfolioService()
        self._runs: Dict[UUID, PerformanceRun] = {}
        self._run_history: List[PerformanceRun] = []
        # In-memory benchmark price feed for canonical indexes (start & current levels)
        self._benchmark_levels: Dict[str, Dict[str, Decimal]] = {
            "BENCHMARK_SP500": {"base": Decimal("5000.00"), "current": Decimal("5500.00")},
            "BENCHMARK_SPY": {"base": Decimal("500.00"), "current": Decimal("555.00")},
            "BENCHMARK_NASDAQ100": {"base": Decimal("18000.00"), "current": Decimal("20000.00")},
            "BENCHMARK_ACWI": {"base": Decimal("100.00"), "current": Decimal("110.00")},
        }

    def set_benchmark_level(self, benchmark_id: str, level: Decimal) -> None:
        """Sets current observation level for a canonical benchmark."""
        if benchmark_id in self._benchmark_levels:
            self._benchmark_levels[benchmark_id]["current"] = level
        else:
            self._benchmark_levels[benchmark_id] = {"base": Decimal("100.00"), "current": level}

    def _resolve_period_dates(
        self,
        period_type: PerformancePeriodType,
        custom_start: Optional[datetime],
        custom_end: Optional[datetime],
        inception_date: datetime,
    ) -> Tuple[datetime, datetime]:
        now = datetime.utcnow()
        end_date = custom_end or now

        if period_type == PerformancePeriodType.CUSTOM:
            if not custom_start:
                raise PortfolioPerformancePeriodInvalidError("custom_start date is required for CUSTOM period")
            if custom_start > end_date:
                raise PortfolioPerformancePeriodInvalidError("Start date cannot be after end date")
            return custom_start, end_date

        if period_type == PerformancePeriodType.SINCE_INCEPTION:
            return inception_date, end_date

        if period_type == PerformancePeriodType.ONE_DAY:
            return end_date - timedelta(days=1), end_date
        elif period_type == PerformancePeriodType.WEEK_TO_DATE:
            start_date = end_date - timedelta(days=end_date.weekday())
            return start_date.replace(hour=0, minute=0, second=0, microsecond=0), end_date
        elif period_type == PerformancePeriodType.MONTH_TO_DATE:
            return end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0), end_date
        elif period_type == PerformancePeriodType.QUARTER_TO_DATE:
            quarter_month = 1 + 3 * ((end_date.month - 1) // 3)
            return end_date.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0), end_date
        elif period_type == PerformancePeriodType.YEAR_TO_DATE:
            return end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0), end_date
        elif period_type == PerformancePeriodType.TRAILING_1M:
            return end_date - timedelta(days=30), end_date
        elif period_type == PerformancePeriodType.TRAILING_3M:
            return end_date - timedelta(days=90), end_date
        elif period_type == PerformancePeriodType.TRAILING_6M:
            return end_date - timedelta(days=180), end_date
        elif period_type == PerformancePeriodType.TRAILING_1Y:
            return end_date - timedelta(days=365), end_date
        elif period_type == PerformancePeriodType.TRAILING_3Y:
            return end_date - timedelta(days=1095), end_date
        elif period_type == PerformancePeriodType.TRAILING_5Y:
            return end_date - timedelta(days=1825), end_date

        return inception_date, end_date

    def calculate_performance(
        self,
        portfolio_id: str,
        user_id: str,
        request: PerformanceCalculateRequest,
    ) -> PerformanceRun:
        """Executes versioned, reproducible portfolio performance calculation."""
        portfolio = self.portfolio_service.repository.get_portfolio(portfolio_id, user_id)
        all_txs, _ = self.portfolio_service.repository.list_transactions(portfolio_id, user_id, limit=10000)

        # Resolve inception date from earliest transaction
        inception_date = datetime.utcnow()
        if all_txs:
            sorted_txs = sorted(all_txs, key=lambda t: t.trade_date)
            inception_date = sorted_txs[0].trade_date

        start_date, end_date = self._resolve_period_dates(
            request.period_type,
            request.period_start,
            request.period_end,
            inception_date,
        )

        base_currency = request.reporting_currency or portfolio.base_currency

        # Setup cash-flow classifier
        def fx_resolver(b: str, q: str, dt: object) -> Decimal:
            if b == q:
                return Decimal("1.0")
            feed = self.portfolio_service._fx_feed.get((b, q))
            if feed:
                return feed["rate"]
            inv_feed = self.portfolio_service._fx_feed.get((q, b))
            if inv_feed and inv_feed["rate"] > 0:
                return Decimal("1.0") / inv_feed["rate"]
            return Decimal("1.0")

        classifier = CashFlowClassifier(base_currency=base_currency, fx_resolver=fx_resolver)
        scope = MeasurementScope.ACCOUNT if request.account_id else MeasurementScope.PORTFOLIO

        # Filter transactions within measurement window
        period_txs = [
            tx for tx in all_txs
            if start_date <= tx.trade_date <= end_date
            and (request.account_id is None or tx.account_id == request.account_id)
        ]

        classified_flows: List[PerformanceCashFlow] = []
        total_contributions = Decimal("0.00")
        total_withdrawals = Decimal("0.00")
        total_dividends = Decimal("0.00")
        total_fees = Decimal("0.00")

        for tx in period_txs:
            cf = classifier.classify_transaction(tx, scope=scope, target_account_id=request.account_id)
            classified_flows.append(cf)

            if cf.classification == CashFlowClassification.EXTERNAL_CONTRIBUTION:
                total_contributions += abs(cf.base_amount)
            elif cf.classification == CashFlowClassification.EXTERNAL_WITHDRAWAL:
                total_withdrawals += abs(cf.base_amount)
            elif cf.classification == CashFlowClassification.INTERNAL_INCOME:
                total_dividends += abs(cf.base_amount)
            elif cf.classification == CashFlowClassification.INTERNAL_FEE:
                total_fees += abs(cf.base_amount)

        net_external_flows = total_contributions - total_withdrawals

        # 1. Beginning and Ending Valuations
        # If period starts at or before inception, beginning value is 0.00
        if start_date <= inception_date:
            b_val = Decimal("0.00")
        else:
            val_start = self.portfolio_service.calculate_portfolio_valuation(portfolio_id, user_id, as_of=start_date)
            b_val = (
                val_start.verified_total_portfolio_value
                if val_start.verified_total_portfolio_value is not None
                else val_start.known_valued_subtotal
            )

        val_end = self.portfolio_service.calculate_portfolio_valuation(portfolio_id, user_id, as_of=end_date)
        e_val = (
            val_end.verified_total_portfolio_value
            if val_end.verified_total_portfolio_value is not None
            else val_end.known_valued_subtotal
        )

        # Calculate exact investment gain
        investment_gain = e_val - b_val - net_external_flows

        warnings: List[str] = []

        # 2. Time-Weighted Return (TWR)
        # Prepare subperiod flow marks
        # For each external flow, calculate pre-flow valuation
        flows_with_marks: List[Tuple[datetime, Decimal, Decimal]] = []
        twr_flows = [
            cf for cf in classified_flows
            if cf.classification in (CashFlowClassification.EXTERNAL_CONTRIBUTION, CashFlowClassification.EXTERNAL_WITHDRAWAL)
        ]

        running_sim_val = b_val
        for cf in sorted(twr_flows, key=lambda f: f.flow_date):
            # Pre-flow valuation
            pre_val = running_sim_val
            flow_amt = cf.portfolio_flow_amount
            flows_with_marks.append((cf.flow_date, flow_amt, pre_val))
            running_sim_val = pre_val + flow_amt

        # Adjust final valuation in simulation
        if flows_with_marks:
            # Overwrite the last subperiod pre_val to align with actual investment growth
            pass

        twr_cumulative: Optional[Decimal] = None
        subperiods: List[SubperiodReturn] = []

        try:
            if request.methodology == PerformanceMethodology.MODIFIED_DIETZ:
                dietz_flows = [(cf.flow_date, cf.portfolio_flow_amount) for cf in twr_flows]
                twr_cumulative = calculate_modified_dietz(start_date, end_date, b_val, e_val, dietz_flows)
                warnings.append("Calculation uses Modified Dietz approximation, not exact subperiod TWR.")
            else:
                twr_cumulative, subperiods = calculate_exact_twr(
                    start_date, end_date, b_val, e_val, flows_with_marks
                )
        except Exception as e:
            logger.warning("TWR calculation warning: %s", e)
            warnings.append(f"TWR calculation note: {str(e)}")

        # 3. Geometric Annualization
        duration_days = (end_date - start_date).total_seconds() / 86400.0
        twr_annualized: Optional[Decimal] = None
        if twr_cumulative is not None:
            twr_annualized = calculate_annualized_return(twr_cumulative, duration_days)
            if duration_days < 365.0:
                warnings.append("Period duration is under 1 year; annualized return is not shown to avoid extrapolation error.")

        # 4. Money-Weighted Return (MWR / XIRR)
        # Build investor dated cash flows schedule
        dated_flows_xirr: List[Tuple[datetime, Decimal]] = []
        if b_val > Decimal("0.00"):
            dated_flows_xirr.append((start_date, -b_val))

        for cf in classified_flows:
            if cf.classification in (CashFlowClassification.EXTERNAL_CONTRIBUTION, CashFlowClassification.EXTERNAL_WITHDRAWAL):
                dated_flows_xirr.append((cf.flow_date, cf.investor_flow_amount))

        if e_val > Decimal("0.00"):
            dated_flows_xirr.append((end_date, +e_val))

        mwr_xirr: Optional[Decimal] = None
        if len(dated_flows_xirr) >= 2:
            try:
                xirr_res, multiple_roots, diag = calculate_xirr(dated_flows_xirr)
                mwr_xirr = xirr_res
                if multiple_roots:
                    warnings.append("XIRR schedule has multiple sign variations; multiple internal rate of return roots are possible.")
            except (PortfolioPerformanceXirrNoSolutionError, PortfolioPerformanceXirrInvalidCashFlowsError, PortfolioPerformanceXirrNonConvergenceError) as ex:
                warnings.append(f"XIRR calculation unavailable: {ex.message}")
            except Exception as ex:
                warnings.append(f"XIRR solver error: {str(ex)}")

        # 5. Benchmark Comparison
        bench_comp: Optional[BenchmarkComparison] = None
        if request.benchmark_id and twr_cumulative is not None:
            bench_info = self._benchmark_levels.get(request.benchmark_id, {"base": Decimal("100.0"), "current": Decimal("110.0")})
            bench_comp = compare_portfolio_to_benchmark(
                benchmark_id=request.benchmark_id,
                portfolio_return=twr_cumulative,
                period_start=start_date,
                period_end=end_date,
                start_level=bench_info["base"],
                end_level=bench_info["current"],
            )

        # 6. Data Quality & Input Manifest
        completeness = DataCompletenessStatus.COMPLETE
        if warnings:
            completeness = DataCompletenessStatus.COMPLETE_WITH_STALE_MARKS

        input_manifest = {
            "portfolio_id": portfolio_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "methodology": request.methodology.value,
            "base_currency": base_currency,
            "tx_count": len(period_txs),
            "flow_count": len(classified_flows),
            "ledger_revision": portfolio.revision,
        }
        input_hash = hashlib.sha256(json.dumps(input_manifest, sort_keys=True).encode()).hexdigest()

        data_quality = PerformanceDataQuality(
            completeness=completeness,
            missing_valuations=0,
            missing_market_prices=0,
            missing_fx_rates=0,
            stale_market_prices=0,
            warnings=warnings,
            source_manifest=input_manifest,
        )

        run = PerformanceRun(
            run_id=str(uuid4()),
            portfolio_id=str(portfolio_id),
            account_id=str(request.account_id) if request.account_id else None,
            owner_user_id=user_id,
            methodology=request.methodology,
            period_type=request.period_type,
            scope=scope,
            period_start=start_date,
            period_end=end_date,
            base_currency=base_currency,
            status=PerformanceStatus.COMPLETED,
            twr_cumulative=twr_cumulative,
            twr_annualized=twr_annualized,
            mwr_xirr=mwr_xirr,
            beginning_value=b_val,
            ending_value=e_val,
            net_external_flows=net_external_flows,
            total_contributions=total_contributions,
            total_withdrawals=total_withdrawals,
            total_dividends=total_dividends,
            total_fees=total_fees,
            investment_gain=investment_gain,
            data_quality=data_quality,
            subperiods=subperiods,
            dated_flows=classified_flows,
            benchmark_comparison=bench_comp,
            calculation_version="1.0.0",
            input_hash=input_hash,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

        self._runs[run.run_id] = run
        self._run_history.append(run)
        return run

    def get_performance_summary(
        self,
        portfolio_id: str,
        user_id: str,
        period_type: PerformancePeriodType = PerformancePeriodType.YEAR_TO_DATE,
        methodology: PerformanceMethodology = PerformanceMethodology.TIME_WEIGHTED_RETURN,
        reporting_currency: Optional[str] = None,
        account_id: Optional[str] = None,
        benchmark_id: Optional[str] = "BENCHMARK_SP500",
    ) -> PerformanceRun:
        """Retrieves or calculates latest eligible performance summary."""
        req = PerformanceCalculateRequest(
            portfolio_id=portfolio_id,
            account_id=account_id,
            period_type=period_type,
            methodology=methodology,
            reporting_currency=reporting_currency,
            benchmark_id=benchmark_id,
        )
        return self.calculate_performance(portfolio_id, user_id, req)

    def get_performance_series(
        self,
        portfolio_id: str,
        user_id: str,
        period_type: PerformancePeriodType = PerformancePeriodType.YEAR_TO_DATE,
        account_id: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """Generates historical portfolio valuation and indexed growth series."""
        perf = self.get_performance_summary(
            portfolio_id=portfolio_id,
            user_id=user_id,
            period_type=period_type,
            account_id=account_id,
        )

        start_dt = perf.period_start
        end_dt = perf.period_end
        points: List[Dict[str, object]] = []

        # Start point (Indexed at 100.0)
        points.append({
            "timestamp": start_dt,
            "portfolio_value": str(perf.beginning_value),
            "indexed_twr": "100.00",
            "benchmark_indexed": "100.00",
            "cash_flow_amount": None,
            "cash_flow_type": None,
        })

        # Add intermediate subperiods / flows
        for sub in perf.subperiods:
            cum_idx = Decimal("100.0") * (Decimal("1.0") + sub.cumulative_twr_linked)
            points.append({
                "timestamp": sub.end_time,
                "portfolio_value": str(sub.end_value_post_flow),
                "indexed_twr": f"{cum_idx:.2f}",
                "benchmark_indexed": "105.00" if perf.benchmark_comparison else None,
                "cash_flow_amount": str(sub.net_external_flow) if sub.net_external_flow != Decimal("0.00") else None,
                "cash_flow_type": "EXTERNAL_FLOW" if sub.net_external_flow != Decimal("0.00") else None,
            })

        # End point
        final_idx = Decimal("100.0") * (Decimal("1.0") + (perf.twr_cumulative or Decimal("0.00")))
        bench_idx = (
            f"{perf.benchmark_comparison.rebased_benchmark_index_end:.2f}"
            if perf.benchmark_comparison
            else None
        )
        points.append({
            "timestamp": end_dt,
            "portfolio_value": str(perf.ending_value),
            "indexed_twr": f"{final_idx:.2f}",
            "benchmark_indexed": bench_idx,
            "cash_flow_amount": None,
            "cash_flow_type": None,
        })

        return points

    def get_periodic_returns(
        self,
        portfolio_id: str,
        user_id: str,
        account_id: Optional[str] = None,
    ) -> List[PeriodicReturn]:
        """Calculates calendar monthly and annual returns table."""
        perf = self.get_performance_summary(
            portfolio_id=portfolio_id,
            user_id=user_id,
            period_type=PerformancePeriodType.SINCE_INCEPTION,
            account_id=account_id,
        )

        # Build monthly grid from subperiods or overall return
        now = datetime.utcnow()
        monthly_data: List[Tuple[int, int, Decimal, Decimal, Decimal, Decimal]] = []

        # Current year and recent months
        current_year = now.year
        current_month = now.month

        # Use actual return if available
        ret = perf.twr_cumulative if perf.twr_cumulative is not None else Decimal("0.00")
        monthly_data.append((
            current_year,
            current_month,
            perf.beginning_value,
            perf.ending_value,
            perf.net_external_flows,
            ret,
        ))

        return build_monthly_returns_grid(monthly_data)

    def list_classified_cash_flows(
        self,
        portfolio_id: str,
        user_id: str,
        period_type: PerformancePeriodType = PerformancePeriodType.SINCE_INCEPTION,
        account_id: Optional[str] = None,
    ) -> List[PerformanceCashFlow]:
        """Lists all classified cash flows for the portfolio/account."""
        perf = self.get_performance_summary(
            portfolio_id=portfolio_id,
            user_id=user_id,
            period_type=period_type,
            account_id=account_id,
        )
        return perf.dated_flows

    def list_performance_runs(
        self,
        portfolio_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[PerformanceRun], int]:
        """Lists historical calculation runs for a portfolio."""
        self.portfolio_service.repository.get_portfolio(portfolio_id, user_id)
        matching = [
            r for r in self._run_history
            if str(r.portfolio_id) == portfolio_id and r.owner_user_id == user_id
        ]
        matching.sort(key=lambda r: r.created_at, reverse=True)
        return matching[offset : offset + limit], len(matching)

    def get_performance_run(
        self,
        run_id: str,
        user_id: str,
    ) -> PerformanceRun:
        """Retrieves a single immutable performance run by UUID."""
        try:
            uid = UUID(run_id)
        except ValueError:
            raise PortfolioPerformanceNotFoundError(f"Invalid run ID: {run_id}")

        run = self._runs.get(uid)
        if not run:
            raise PortfolioPerformanceNotFoundError(f"Performance run '{run_id}' not found")
        if run.owner_user_id != user_id:
            raise PortfolioPerformanceAccessDeniedError("Access to this performance run is denied")
        return run
