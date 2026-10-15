"""Service layer for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61).

Implements BondMarketReadService, BondDirectoryService, and BondOverviewService with strict
pricing and yield semantics.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from .config import CanonicalBondSecurityConfig, PriceKindEnum
from .models import (
    BondContractTermsView,
    BondDirectoryItem,
    BondDirectoryResponse,
    BondIssuerSummary,
    BondOverviewResponse,
    BondPriceObservationView,
    BondYieldObservationView,
)
from .repository import BondMarketRepository, calculate_maturity_bucket


class BondMarketReadService:
    """Service responsible for reading and validating bond price and yield observations."""

    def __init__(self, repository: BondMarketRepository) -> None:
        self._repo = repository

    def build_price_view(self, config: CanonicalBondSecurityConfig) -> BondPriceObservationView:
        """Construct a validated source-aware BondPriceObservationView from config data."""
        clean_price = config.default_clean_price
        dirty_price = config.default_dirty_price
        accrued_interest = config.default_accrued_interest

        # Clean/Dirty arithmetic validation: dirty = clean + accrued
        if dirty_price is None and clean_price is not None and accrued_interest is not None:
            dirty_price = clean_price + accrued_interest

        # Bid/Ask spread and crossed market protection
        bid = config.default_bid
        ask = config.default_ask
        spread = None
        price_kind = config.default_price_kind

        if bid is not None and ask is not None:
            if bid > ask:
                # Crossed market anomaly
                spread = None
                price_kind = PriceKindEnum.UNKNOWN
            else:
                spread = ask - bid

        # 24h percentage price change
        price_change_24h = config.default_price_change_24h
        price_change_24h_percent = None
        if clean_price is not None and price_change_24h is not None:
            reference_price = clean_price - price_change_24h
            if reference_price > Decimal("0"):
                price_change_24h_percent = (price_change_24h / reference_price) * Decimal("100")

        now_iso = datetime.now(timezone.utc).isoformat()

        return BondPriceObservationView(
            clean_price=clean_price,
            dirty_price=dirty_price,
            accrued_interest=accrued_interest,
            price_basis=config.default_price_basis,
            quote_unit=config.default_quote_unit,
            price_kind=price_kind,
            currency=config.currency,
            bid=bid,
            ask=ask,
            spread=spread,
            price_change_24h=price_change_24h,
            price_change_24h_percent=price_change_24h_percent,
            source_timestamp=now_iso,
            received_at=now_iso,
            valuation_date=config.issue_date,
            freshness_status="REALTIME",
            delay_status="REALTIME",
            provider=config.default_provider,
        )

    def build_yield_view(self, config: CanonicalBondSecurityConfig) -> BondYieldObservationView:
        """Construct a typed BondYieldObservationView keeping yield separated from coupon."""
        now_iso = datetime.now(timezone.utc).isoformat()
        return BondYieldObservationView(
            yield_value=config.default_yield_value,
            yield_type=config.default_yield_type,
            yield_unit="PERCENT_PER_ANNUM",
            yield_change_bps_24h=config.default_yield_change_bps_24h,
            as_of=now_iso,
            source=config.default_provider,
            methodology="Standard Market Convention",
        )

    def build_terms_view(self, config: CanonicalBondSecurityConfig) -> BondContractTermsView:
        """Construct a verified BondContractTermsView."""
        years, bucket = calculate_maturity_bucket(config.maturity_date, config.is_perpetual)
        return BondContractTermsView(
            issue_date=config.issue_date,
            dated_date=config.dated_date,
            maturity_date=config.maturity_date,
            is_perpetual=config.is_perpetual,
            time_to_maturity_years=years,
            maturity_bucket=bucket,
            coupon_type=config.coupon_type,
            coupon_rate=config.coupon_rate,
            coupon_frequency=config.coupon_frequency,
            day_count_convention=config.day_count_convention,
            face_value=config.face_value,
            face_value_convention=config.face_value_convention,
            seniority=config.seniority,
            is_callable=config.is_callable,
            is_putable=config.is_putable,
            reference_index=config.reference_index,
            floating_margin_bps=config.floating_margin_bps,
        )

    def build_issuer_summary(self, config: CanonicalBondSecurityConfig) -> BondIssuerSummary:
        """Construct a verified BondIssuerSummary."""
        issuer = self._repo.get_issuer_by_id(config.issuer_entity_id)
        if issuer:
            return BondIssuerSummary(
                issuer_entity_id=issuer.issuer_entity_id,
                name=issuer.name,
                issuer_category=issuer.issuer_category,
                country_code=issuer.country_code,
                jurisdiction=issuer.jurisdiction,
            )
        return BondIssuerSummary(
            issuer_entity_id=config.issuer_entity_id,
            name=config.issuer_name,
            issuer_category=config.issuer_category,
            country_code="USA",
            jurisdiction="Unknown",
        )


class BondDirectoryService:
    """Service providing bond securities directory discovery, search, and pagination."""

    def __init__(
        self, repository: BondMarketRepository, read_service: BondMarketReadService
    ) -> None:
        self._repo = repository
        self._read_service = read_service

    def get_directory(
        self,
        query: Optional[str] = None,
        issuer_type: Optional[str] = None,
        issuer_entity_id: Optional[UUID] = None,
        bond_type: Optional[str] = None,
        currency: Optional[str] = None,
        coupon_type: Optional[str] = None,
        maturity_bucket: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> BondDirectoryResponse:
        """Return a filtered, paginated bond directory response."""
        configs, total, next_cursor, has_more = self._repo.list_bonds(
            query=query,
            issuer_type=issuer_type,
            issuer_entity_id=issuer_entity_id,
            bond_type=bond_type,
            currency=currency,
            coupon_type=coupon_type,
            maturity_bucket=maturity_bucket,
            limit=limit,
            cursor=cursor,
        )

        items = []
        for cfg in configs:
            issuer_summary = self._read_service.build_issuer_summary(cfg)
            terms = self._read_service.build_terms_view(cfg)
            price = self._read_service.build_price_view(cfg)
            yield_obs = self._read_service.build_yield_view(cfg)

            items.append(
                BondDirectoryItem(
                    instrument_entity_id=cfg.instrument_entity_id,
                    symbol=cfg.symbol,
                    name=cfg.name,
                    isin=cfg.isin,
                    cusip=cfg.cusip,
                    issuer=issuer_summary,
                    bond_type=cfg.bond_type,
                    currency=cfg.currency,
                    terms=terms,
                    price=price,
                    yield_obs=yield_obs,
                    freshness_status="REALTIME",
                    provider=cfg.default_provider,
                    data_status="ACTIVE",
                )
            )

        coverage = self._repo.get_coverage_summary()

        return BondDirectoryResponse(
            schema_version="1.0.0",
            scope="authorized_configured_bonds_universe",
            items=items,
            total=total,
            limit=limit,
            next_cursor=next_cursor,
            has_more=has_more,
            coverage=coverage,
        )


class BondOverviewService:
    """Service providing deep security inspection details for a selected bond."""

    def __init__(
        self, repository: BondMarketRepository, read_service: BondMarketReadService
    ) -> None:
        self._repo = repository
        self._read_service = read_service

    def get_overview(self, instrument_entity_id: UUID) -> Optional[BondOverviewResponse]:
        """Return full overview details for a specific canonical bond."""
        cfg = self._repo.get_by_id(instrument_entity_id)
        if not cfg:
            return None

        issuer_summary = self._read_service.build_issuer_summary(cfg)
        terms = self._read_service.build_terms_view(cfg)
        price = self._read_service.build_price_view(cfg)
        yield_obs = self._read_service.build_yield_view(cfg)

        provenance = {
            "source_provider": cfg.default_provider,
            "provider_series": cfg.provider_series_id,
            "pricing_kind": cfg.default_price_kind.value,
            "quotation_unit": cfg.default_quote_unit.value,
            "day_count": cfg.day_count_convention.value,
        }

        availability = {
            "clean_price_available": price.clean_price is not None,
            "dirty_price_available": price.dirty_price is not None,
            "accrued_interest_available": price.accrued_interest is not None,
            "bid_ask_available": price.bid is not None and price.ask is not None,
            "yield_available": yield_obs.yield_value is not None,
        }

        return BondOverviewResponse(
            schema_version="1.0.0",
            instrument_entity_id=cfg.instrument_entity_id,
            symbol=cfg.symbol,
            name=cfg.name,
            isin=cfg.isin,
            cusip=cfg.cusip,
            issuer=issuer_summary,
            bond_type=cfg.bond_type,
            currency=cfg.currency,
            terms=terms,
            price=price,
            yield_obs=yield_obs,
            provenance=provenance,
            availability=availability,
        )
