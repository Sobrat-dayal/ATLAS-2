"""
Portfolio Exposure Service for ATLAS (Stage 112).

Orchestrates multi-dimensional allocation, sector/industry classification,
geographic and currency exposures, issuer/security concentration (HHI),
fund and ETF look-through decomposition, historical drift analysis,
and exposure reconciliation audits.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
import logging
from typing import Any, Dict, List, Optional
import uuid

from atlas.portfolios.exposure.engine import PortfolioExposureEngine
from atlas.portfolios.exposure.enums import (
    ExposureBasis,
    ExposureDimension,
    GeographyPolicy,
)
from atlas.portfolios.exposure.errors import (
    PortfolioExposureAccessDeniedError,
    PortfolioExposureNotFoundError,
)
from atlas.portfolios.exposure.historical import HistoricalAllocationEngine
from atlas.portfolios.exposure.lookthrough import FundLookThroughEngine
from atlas.portfolios.exposure.models import (
    AllocationChangeItem,
    ConcentrationSummary,
    CrossFundOverlapItem,
    ExposureDataQuality,
    ExposureDimensionResult,
    FundLookThroughResult,
    HistoricalAllocationPoint,
    IssuerWeightItem,
    PortfolioExposureRun,
    SecurityWeightItem,
)
from atlas.portfolios.exposure.schemas import CalculateExposureRequest
from atlas.portfolios.service import PortfolioService

logger = logging.getLogger("atlas.portfolios.exposure.service")


class PortfolioExposureService:
    """Institutional portfolio allocation, exposure, and concentration service."""

    def __init__(self, portfolio_service: Optional[PortfolioService] = None) -> None:
        self.portfolio_service = portfolio_service or PortfolioService()
        self.engine = PortfolioExposureEngine()
        self._runs: Dict[str, PortfolioExposureRun] = {}
        self._portfolio_runs: Dict[str, List[str]] = {}

    def calculate_portfolio_exposure(
        self,
        portfolio_id: str,
        user_id: str,
        request: Optional[CalculateExposureRequest] = None,
    ) -> PortfolioExposureRun:
        """
        Calculate full multi-dimensional allocation and exposure decomposition for a portfolio.
        """
        req = request or CalculateExposureRequest()
        as_of_date = req.as_of_date or date.today()
        if req.as_of_date and req.as_of_date < date.today():
            as_of_dt = datetime.combine(as_of_date, datetime.max.time())
        else:
            as_of_dt = None

        # 1. Verify portfolio ownership and load base details
        portfolio = self.portfolio_service.get_portfolio(portfolio_id, user_id)

        # 2. Retrieve valuation
        valuation = self.portfolio_service.calculate_portfolio_valuation(portfolio_id, user_id, as_of=as_of_dt)

        account_filter = req.account_ids[0] if (req.account_ids and len(req.account_ids) == 1) else None

        basis = req.exposure_basis
        if basis == ExposureBasis.NET_ASSET_VALUE:
            basis = ExposureBasis.LOOK_THROUGH if req.enable_look_through else ExposureBasis.DIRECT

        # 3. Run calculation engine
        run = self.engine.calculate_exposure_run(
            portfolio=portfolio,
            valuation=valuation,
            exposure_basis=basis,
            geography_policy=req.geography_policy,
            include_cash=True,
            account_id_filter=account_filter,
        )

        # 4. Store run in memory cache
        self._runs[run.run_id] = run
        if portfolio_id not in self._portfolio_runs:
            self._portfolio_runs[portfolio_id] = []
        self._portfolio_runs[portfolio_id].append(run.run_id)

        return run

    def get_latest_exposure(
        self,
        portfolio_id: str,
        user_id: str,
        exposure_basis: ExposureBasis = ExposureBasis.NET_ASSET_VALUE,
        geography_policy: GeographyPolicy = GeographyPolicy.ISSUER_DOMICILE,
        enable_look_through: bool = True,
        force_recalculate: bool = False,
    ) -> PortfolioExposureRun:
        """
        Get the most recent exposure run for a portfolio, calculating if not present.
        """
        # Verify access
        self.portfolio_service.get_portfolio(portfolio_id, user_id)

        if not force_recalculate and portfolio_id in self._portfolio_runs and self._portfolio_runs[portfolio_id]:
            # Look backwards from most recent run
            for run_id in reversed(self._portfolio_runs[portfolio_id]):
                run = self._runs.get(run_id)
                if (
                    run
                    and run.exposure_basis == exposure_basis
                    and run.geography_policy == geography_policy
                    and run.look_through_applied == enable_look_through
                ):
                    return run

        # Calculate anew
        return self.calculate_portfolio_exposure(
            portfolio_id=portfolio_id,
            user_id=user_id,
            request=CalculateExposureRequest(
                exposure_basis=exposure_basis,
                geography_policy=geography_policy,
                enable_look_through=enable_look_through,
                force_recalculate=force_recalculate,
            ),
        )

    def list_exposure_runs(
        self, portfolio_id: str, user_id: str
    ) -> List[PortfolioExposureRun]:
        """List all calculated exposure runs for a portfolio."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        run_ids = self._portfolio_runs.get(portfolio_id, [])
        return [self._runs[rid] for rid in run_ids if rid in self._runs]

    def get_exposure_run(
        self, portfolio_id: str, run_id: str, user_id: str
    ) -> PortfolioExposureRun:
        """Get a specific exposure run by ID with tenant access check."""
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        run = self._runs.get(run_id)
        if not run or run.portfolio_id != portfolio_id:
            raise PortfolioExposureNotFoundError(f"Exposure run '{run_id}' not found for portfolio '{portfolio_id}'.")
        return run

    def get_asset_class_allocation(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ExposureDimensionResult:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.asset_classes

    def get_sector_exposure(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ExposureDimensionResult:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.sectors

    def get_industry_exposure(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ExposureDimensionResult:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.industries

    def get_country_exposure(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ExposureDimensionResult:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.countries

    def get_currency_exposure(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ExposureDimensionResult:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.currencies

    def get_security_weights(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> List[SecurityWeightItem]:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.security_weights

    def get_issuer_weights(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> List[IssuerWeightItem]:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.issuer_weights

    def get_concentration_summary(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ConcentrationSummary:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.concentration

    def get_look_through_details(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> List[FundLookThroughResult]:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.funds

    def get_fund_look_through(
        self, portfolio_id: str, instrument_id: str, user_id: str, **kwargs: Any
    ) -> Optional[FundLookThroughResult]:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        for fund in run.funds:
            if fund.fund_instrument_id == instrument_id or fund.fund_symbol.upper() == instrument_id.upper():
                return fund
        return None

    def get_cross_fund_overlap(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> List[CrossFundOverlapItem]:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.cross_fund_overlap

    def get_historical_exposures(
        self,
        portfolio_id: str,
        user_id: str,
        dimension: ExposureDimension,
    ) -> List[HistoricalAllocationPoint]:
        """
        Extract historical allocation time series across existing runs for this portfolio.
        """
        self.portfolio_service.get_portfolio(portfolio_id, user_id)
        runs = self.list_exposure_runs(portfolio_id, user_id)
        return HistoricalAllocationEngine.extract_time_series(runs, dimension)

    def get_allocation_changes(
        self,
        portfolio_id: str,
        user_id: str,
        dimension: ExposureDimension,
        start_date: date,
        end_date: date,
    ) -> List[AllocationChangeItem]:
        """
        Calculate date-to-date allocation drift between two points in time.
        """
        start_run = self.calculate_portfolio_exposure(
            portfolio_id, user_id, CalculateExposureRequest(as_of_date=start_date)
        )
        end_run = self.calculate_portfolio_exposure(
            portfolio_id, user_id, CalculateExposureRequest(as_of_date=end_date)
        )

        dim_start = getattr(start_run, dimension.value if hasattr(start_run, dimension.value) else "asset_classes")
        dim_end = getattr(end_run, dimension.value if hasattr(end_run, dimension.value) else "asset_classes")

        # Map proper attribute
        if dimension == ExposureDimension.ASSET_CLASS:
            dim_start, dim_end = start_run.asset_classes, end_run.asset_classes
        elif dimension == ExposureDimension.SECTOR:
            dim_start, dim_end = start_run.sectors, end_run.sectors
        elif dimension == ExposureDimension.INDUSTRY:
            dim_start, dim_end = start_run.industries, end_run.industries
        elif dimension == ExposureDimension.COUNTRY:
            dim_start, dim_end = start_run.countries, end_run.countries
        elif dimension == ExposureDimension.CURRENCY:
            dim_start, dim_end = start_run.currencies, end_run.currencies

        return HistoricalAllocationEngine.calculate_allocation_changes(
            dim_start, dim_end, start_date, end_date
        )

    def get_data_quality(
        self, portfolio_id: str, user_id: str, **kwargs: Any
    ) -> ExposureDataQuality:
        run = self.get_latest_exposure(portfolio_id, user_id, **kwargs)
        return run.data_quality

