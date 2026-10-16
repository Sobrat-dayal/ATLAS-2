"""Business Logic and Market Read Services for ATLAS Futures & Commodities Markets V1 (Stage 62)."""

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID

from .config import (
    CanonicalFuturesContractConfig,
    CommodityCategoryEnum,
    ContractLifecycleEnum,
    VolumeWindowEnum,
)
from .models import (
    CommodityDirectoryItem,
    CommodityDirectoryResponse,
    CommoditySpotBenchmarkView,
    CommoditySummary,
    FuturesContractDirectoryItem,
    FuturesContractDirectoryResponse,
    FuturesContractOverviewResponse,
    FuturesContractSpecificationView,
    FuturesPriceChangeView,
    FuturesPriceObservationView,
    FuturesProductSummary,
    FuturesSettlementObservationView,
    FuturesVolumeOpenInterestView,
    SpotBenchmarkDirectoryResponse,
)
from .repository import FuturesMarketRepository

logger = logging.getLogger(__name__)


class FuturesMarketReadService:
    """Service providing market observations, price change analytics, and spread validation."""

    def __init__(self, repository: FuturesMarketRepository) -> None:
        self._repo = repository

    def build_price_observation(
        self, contract: CanonicalFuturesContractConfig
    ) -> FuturesPriceObservationView:
        """Construct validated price observation view with spread and crossed market guards."""
        bid = contract.bid
        ask = contract.ask
        spread: Optional[Decimal] = None

        if bid is not None and ask is not None:
            if ask >= bid:
                spread = ask - bid
            else:
                logger.warning(
                    f"Crossed market observed for contract {contract.symbol}: bid {bid} > ask {ask}"
                )
                spread = None

        return FuturesPriceObservationView(
            last=contract.latest_trade_price,
            bid=bid,
            ask=ask,
            spread=spread,
            quote_unit=contract.quote_unit,
            quote_currency=contract.quote_currency,
            source_timestamp=contract.source_timestamp,
            received_at=contract.received_at,
            freshness_status=contract.freshness_status,
            delay_status=contract.delay_status,
            provider=contract.provider,
        )

    def build_settlement_observation(
        self, contract: CanonicalFuturesContractConfig
    ) -> FuturesSettlementObservationView:
        """Construct official clearing settlement observation view."""
        return FuturesSettlementObservationView(
            settlement_price=contract.official_settlement,
            settlement_status=contract.settlement_status,
            trade_date=contract.settlement_trade_date,
            publication_timestamp=contract.source_timestamp,
            quote_unit=contract.quote_unit,
            provider=contract.provider,
        )

    def build_price_change(
        self, contract: CanonicalFuturesContractConfig
    ) -> FuturesPriceChangeView:
        """Compute price movement against same-contract previous settlement.

        Strict rule: If the reference price is <= 0 (e.g. negative or zero),
        ordinary percentage change is suppressed (returns None) to avoid misleading
        or undefined arithmetic.
        """
        ref_price = contract.previous_settlement
        current_price = (
            contract.latest_trade_price
            if contract.latest_trade_price is not None
            else contract.official_settlement
        )

        change_abs: Optional[Decimal] = None
        change_pct: Optional[Decimal] = None
        change_ticks: Optional[Decimal] = None

        if current_price is not None and ref_price is not None:
            change_abs = current_price - ref_price

            # Strict guard against nonpositive reference denominators
            if ref_price > Decimal("0"):
                change_pct = (change_abs / ref_price) * Decimal("100")
            else:
                # Reference is <= 0 (e.g. negative WTI oil reference)
                change_pct = None

            if contract.tick_size is not None and contract.tick_size > Decimal("0"):
                change_ticks = change_abs / contract.tick_size

        return FuturesPriceChangeView(
            change_absolute=change_abs,
            change_percent=change_pct,
            reference_price=ref_price,
            reference_type="PREVIOUS_SETTLEMENT",
            change_ticks=change_ticks,
        )

    def build_volume_open_interest(
        self, contract: CanonicalFuturesContractConfig
    ) -> FuturesVolumeOpenInterestView:
        """Construct volume and reported open interest observation view."""
        return FuturesVolumeOpenInterestView(
            volume=contract.volume,
            volume_window=VolumeWindowEnum.SESSION,
            open_interest=contract.open_interest,
            open_interest_as_of=contract.open_interest_as_of,
            provider=contract.provider,
        )


class FuturesDirectoryService:
    """Service handling directory queries, filtering, and pagination for listed contracts."""

    def __init__(
        self,
        repository: FuturesMarketRepository,
        read_service: FuturesMarketReadService,
    ) -> None:
        self._repo = repository
        self._read_service = read_service

    def get_directory(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        exchange: Optional[str] = None,
        product_entity_id: Optional[UUID] = None,
        root_symbol: Optional[str] = None,
        contract_month: Optional[str] = None,
        settlement_type: Optional[str] = None,
        lifecycle_status: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> FuturesContractDirectoryResponse:
        """Retrieve paginated futures contract directory with observations and coverage."""
        contracts, total, next_cursor, has_more = self._repo.list_contracts(
            query=query,
            category=category,
            exchange=exchange,
            product_entity_id=product_entity_id,
            root_symbol=root_symbol,
            contract_month=contract_month,
            settlement_type=settlement_type,
            lifecycle_status=lifecycle_status,
            limit=limit,
            cursor=cursor,
        )

        items: list[FuturesContractDirectoryItem] = []
        for c in contracts:
            prod = self._repo.get_product_by_id(c.product_entity_id)
            und = self._repo.get_commodity_by_id(c.underlying_entity_id)

            prod_name = prod.name if prod else c.name
            und_name = und.name if und else "Underlying Commodity"
            cat = prod.category if prod else CommodityCategoryEnum.ENERGY

            price_obs = self._read_service.build_price_observation(c)
            settle_obs = self._read_service.build_settlement_observation(c)
            change_obs = self._read_service.build_price_change(c)
            vol_oi_obs = self._read_service.build_volume_open_interest(c)

            item = FuturesContractDirectoryItem(
                instrument_entity_id=c.instrument_entity_id,
                product_entity_id=c.product_entity_id,
                underlying_entity_id=c.underlying_entity_id,
                symbol=c.symbol,
                name=c.name,
                product_name=prod_name,
                underlying_name=und_name,
                exchange=c.exchange,
                exchange_mic=c.exchange_mic,
                category=cat,
                contract_year=c.contract_year,
                contract_month_code=c.contract_month_code,
                contract_month=c.contract_month,
                expiration_date=c.expiration_date,
                last_trading_date=c.last_trading_date,
                lifecycle_status=c.lifecycle_status,
                settlement_type=c.settlement_type,
                contract_size=c.contract_size,
                size_unit=c.size_unit,
                tick_size=c.tick_size,
                tick_value=c.tick_value,
                quote_currency=c.quote_currency,
                quote_unit=c.quote_unit,
                price_observation=price_obs,
                settlement_observation=settle_obs,
                price_change=change_obs,
                volume_open_interest=vol_oi_obs,
            )
            items.append(item)

        coverage = self._repo.get_coverage_summary()

        return FuturesContractDirectoryResponse(
            items=items,
            total=total,
            limit=limit,
            cursor=cursor,
            next_cursor=next_cursor,
            has_more=has_more,
            coverage=coverage,
        )


class CommodityDirectoryService:
    """Service providing catalog access to underlying economic commodities."""

    def __init__(self, repository: FuturesMarketRepository) -> None:
        self._repo = repository

    def get_commodities(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> CommodityDirectoryResponse:
        """List canonical commodities with associated futures products and contract counts."""
        commodities = self._repo.list_commodities(category=category, query=query)

        items: list[CommodityDirectoryItem] = []
        for c in commodities:
            prods = self._repo.list_products_for_commodity(c.commodity_entity_id)

            prod_summaries: list[FuturesProductSummary] = []
            active_contracts_count = 0

            for p in prods:
                prod_summaries.append(
                    FuturesProductSummary(
                        product_entity_id=p.product_entity_id,
                        underlying_entity_id=p.underlying_entity_id,
                        root_symbol=p.root_symbol,
                        name=p.name,
                        exchange=p.exchange,
                        exchange_mic=p.exchange_mic,
                        category=p.category,
                        contract_size=p.contract_size,
                        size_unit=p.size_unit,
                        quote_currency=p.quote_currency,
                        quote_unit=p.quote_unit,
                        tick_size=p.tick_size,
                        tick_value=p.tick_value,
                        settlement_type=p.settlement_type,
                        contract_multiplier=p.contract_multiplier,
                    )
                )
                contracts = self._repo.list_contracts_for_product(p.product_entity_id)
                active_contracts_count += sum(
                    1 for ct in contracts if ct.lifecycle_status == ContractLifecycleEnum.ACTIVE
                )

            item = CommodityDirectoryItem(
                commodity_entity_id=c.commodity_entity_id,
                name=c.name,
                slug=c.slug,
                category=c.category,
                grade_specification=c.grade_specification,
                physical_unit=c.physical_unit,
                reference_region=c.reference_region,
                delivery_characteristics=c.delivery_characteristics,
                associated_products_count=len(prods),
                active_contracts_count=active_contracts_count,
                associated_products=prod_summaries,
            )
            items.append(item)

        return CommodityDirectoryResponse(items=items, total=len(items))

    def get_commodity_by_id(self, commodity_entity_id: UUID) -> Optional[CommodityDirectoryItem]:
        """Lookup a single canonical commodity with associated products and contracts."""
        c = self._repo.get_commodity_by_id(commodity_entity_id)
        if not c:
            return None

        prods = self._repo.list_products_for_commodity(c.commodity_entity_id)
        prod_summaries: list[FuturesProductSummary] = []
        active_contracts_count = 0

        for p in prods:
            prod_summaries.append(
                FuturesProductSummary(
                    product_entity_id=p.product_entity_id,
                    underlying_entity_id=p.underlying_entity_id,
                    root_symbol=p.root_symbol,
                    name=p.name,
                    exchange=p.exchange,
                    exchange_mic=p.exchange_mic,
                    category=p.category,
                    contract_size=p.contract_size,
                    size_unit=p.size_unit,
                    quote_currency=p.quote_currency,
                    quote_unit=p.quote_unit,
                    tick_size=p.tick_size,
                    tick_value=p.tick_value,
                    settlement_type=p.settlement_type,
                    contract_multiplier=p.contract_multiplier,
                )
            )
            contracts = self._repo.list_contracts_for_product(p.product_entity_id)
            active_contracts_count += sum(
                1 for ct in contracts if ct.lifecycle_status == ContractLifecycleEnum.ACTIVE
            )

        return CommodityDirectoryItem(
            commodity_entity_id=c.commodity_entity_id,
            name=c.name,
            slug=c.slug,
            category=c.category,
            grade_specification=c.grade_specification,
            physical_unit=c.physical_unit,
            reference_region=c.reference_region,
            delivery_characteristics=c.delivery_characteristics,
            associated_products_count=len(prods),
            active_contracts_count=active_contracts_count,
            associated_products=prod_summaries,
        )


class SpotBenchmarkService:
    """Service providing access to physical commodity spot benchmarks."""

    def __init__(self, repository: FuturesMarketRepository) -> None:
        self._repo = repository

    def get_spot_benchmarks(self) -> SpotBenchmarkDirectoryResponse:
        """List all verified physical commodity spot benchmarks with price changes."""
        benchmarks = self._repo.list_spot_benchmarks()

        items: list[CommoditySpotBenchmarkView] = []
        for b in benchmarks:
            und = self._repo.get_commodity_by_id(b.commodity_entity_id)
            und_name = und.name if und else "Commodity"

            chg_abs: Optional[Decimal] = None
            chg_pct: Optional[Decimal] = None

            if b.latest_price is not None and b.previous_price is not None:
                chg_abs = b.latest_price - b.previous_price
                if b.previous_price > Decimal("0"):
                    chg_pct = (chg_abs / b.previous_price) * Decimal("100")

            item = CommoditySpotBenchmarkView(
                benchmark_entity_id=b.benchmark_entity_id,
                commodity_entity_id=b.commodity_entity_id,
                commodity_name=und_name,
                name=b.name,
                grade=b.grade,
                location=b.location,
                currency=b.currency,
                quote_unit=b.quote_unit,
                assessment_methodology=b.assessment_methodology,
                latest_price=b.latest_price,
                previous_price=b.previous_price,
                change_absolute=chg_abs,
                change_percent=chg_pct,
                as_of_date=b.as_of_date,
                provider=b.provider,
            )
            items.append(item)

        return SpotBenchmarkDirectoryResponse(items=items, total=len(items))


class FuturesOverviewService:
    """Service assembling comprehensive inspection views for a single futures contract."""

    def __init__(
        self,
        repository: FuturesMarketRepository,
        read_service: FuturesMarketReadService,
    ) -> None:
        self._repo = repository
        self._read_service = read_service

    def get_overview(self, instrument_entity_id: UUID) -> Optional[FuturesContractOverviewResponse]:
        """Assemble full contract inspection view including terms and market observations."""
        contract = self._repo.get_contract_by_id(instrument_entity_id)
        if not contract:
            return None

        product = self._repo.get_product_by_id(contract.product_entity_id)
        underlying = self._repo.get_commodity_by_id(contract.underlying_entity_id)

        if not product or not underlying:
            logger.error(f"Missing product or underlying reference for contract {contract.symbol}")
            return None

        und_summary = CommoditySummary(
            commodity_entity_id=underlying.commodity_entity_id,
            name=underlying.name,
            slug=underlying.slug,
            category=underlying.category,
            grade_specification=underlying.grade_specification,
            physical_unit=underlying.physical_unit,
            reference_region=underlying.reference_region,
            delivery_characteristics=underlying.delivery_characteristics,
        )

        prod_summary = FuturesProductSummary(
            product_entity_id=product.product_entity_id,
            underlying_entity_id=product.underlying_entity_id,
            root_symbol=product.root_symbol,
            name=product.name,
            exchange=product.exchange,
            exchange_mic=product.exchange_mic,
            category=product.category,
            contract_size=product.contract_size,
            size_unit=product.size_unit,
            quote_currency=product.quote_currency,
            quote_unit=product.quote_unit,
            tick_size=product.tick_size,
            tick_value=product.tick_value,
            settlement_type=product.settlement_type,
            contract_multiplier=product.contract_multiplier,
        )

        specs = FuturesContractSpecificationView(
            contract_size=contract.contract_size,
            size_unit=contract.size_unit,
            quote_currency=contract.quote_currency,
            quote_unit=contract.quote_unit,
            tick_size=contract.tick_size,
            tick_value=contract.tick_value,
            settlement_type=contract.settlement_type,
            contract_multiplier=contract.contract_multiplier,
            trading_hours=contract.trading_hours,
            expiration_date=contract.expiration_date,
            last_trading_date=contract.last_trading_date,
            first_notice_date=contract.first_notice_date,
            last_notice_date=contract.last_notice_date,
            delivery_start_date=contract.delivery_start_date,
            delivery_end_date=contract.delivery_end_date,
            settlement_date=contract.settlement_date,
        )

        price_obs = self._read_service.build_price_observation(contract)
        settle_obs = self._read_service.build_settlement_observation(contract)
        change_obs = self._read_service.build_price_change(contract)
        vol_oi_obs = self._read_service.build_volume_open_interest(contract)

        return FuturesContractOverviewResponse(
            instrument_entity_id=contract.instrument_entity_id,
            symbol=contract.symbol,
            name=contract.name,
            exchange=contract.exchange,
            exchange_mic=contract.exchange_mic,
            contract_year=contract.contract_year,
            contract_month_code=contract.contract_month_code,
            contract_month=contract.contract_month,
            lifecycle_status=contract.lifecycle_status,
            underlying=und_summary,
            product=prod_summary,
            specifications=specs,
            price_observation=price_obs,
            settlement_observation=settle_obs,
            price_change=change_obs,
            volume_open_interest=vol_oi_obs,
            provider=contract.provider,
            freshness_status=contract.freshness_status,
            delay_status=contract.delay_status,
            source_timestamp=contract.source_timestamp,
            received_at=contract.received_at,
        )
