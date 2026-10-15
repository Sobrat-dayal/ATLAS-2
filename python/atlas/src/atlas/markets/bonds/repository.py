"""Repository layer for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61).

Provides in-memory catalog query, deterministic keyset pagination, multi-dimensional filtering,
and coverage computation.
"""

import base64
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from .config import (
    CANONICAL_BOND_ISSUERS,
    CANONICAL_BOND_SECURITIES,
    BondIssuerConfig,
    BondTypeEnum,
    CanonicalBondSecurityConfig,
    CouponTypeEnum,
    IssuerCategoryEnum,
    MaturityBucketEnum,
)
from .models import BondCoverageSummary, BondFilterOptionsResponse

# Reference valuation date for deterministic calendar calculations in test/reference data
REFERENCE_DATE = date(2024, 6, 1)


def calculate_maturity_bucket(
    maturity_date_str: Optional[str], is_perpetual: bool
) -> Tuple[Optional[Decimal], MaturityBucketEnum]:
    """Calculate approximate calendar years to maturity and maturity bucket."""
    if is_perpetual or not maturity_date_str:
        return None, MaturityBucketEnum.PERPETUAL

    try:
        mat_date = datetime.strptime(maturity_date_str, "%Y-%m-%d").date()
    except ValueError:
        return None, MaturityBucketEnum.PERPETUAL

    delta_days = (mat_date - REFERENCE_DATE).days
    years = Decimal(str(round(delta_days / 365.25, 2)))

    if years < Decimal("1.0"):
        bucket = MaturityBucketEnum.UNDER_1_YEAR
    elif years < Decimal("3.0"):
        bucket = MaturityBucketEnum.ONE_TO_THREE_YEARS
    elif years < Decimal("5.0"):
        bucket = MaturityBucketEnum.THREE_TO_FIVE_YEARS
    elif years < Decimal("10.0"):
        bucket = MaturityBucketEnum.FIVE_TO_TEN_YEARS
    else:
        bucket = MaturityBucketEnum.OVER_TEN_YEARS

    return years, bucket


class BondMarketRepository:
    """Repository accessing the canonical ATLAS Fixed-Income catalog."""

    def __init__(
        self,
        securities: Optional[List[CanonicalBondSecurityConfig]] = None,
        issuers: Optional[Dict[UUID, BondIssuerConfig]] = None,
    ) -> None:
        self._securities = list(securities or CANONICAL_BOND_SECURITIES)
        self._issuers = dict(issuers or CANONICAL_BOND_ISSUERS)

    def get_by_id(self, instrument_entity_id: UUID) -> Optional[CanonicalBondSecurityConfig]:
        """Lookup canonical bond by its Financial Instrument UUID."""
        for sec in self._securities:
            if sec.instrument_entity_id == instrument_entity_id:
                return sec
        return None

    def get_issuer_by_id(self, issuer_entity_id: UUID) -> Optional[BondIssuerConfig]:
        """Lookup legal issuer by Organization Entity UUID."""
        return self._issuers.get(issuer_entity_id)

    def list_issuers(self) -> List[BondIssuerConfig]:
        """Return all canonical bond issuers."""
        return list(self._issuers.values())

    def list_bonds(
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
    ) -> Tuple[List[CanonicalBondSecurityConfig], int, Optional[str], bool]:
        """Filter and paginate canonical bond securities using keyset cursor pagination."""
        items = list(self._securities)

        # Filter by search query (security name, symbol, isin, cusip, issuer name)
        if query and query.strip():
            q = query.strip().lower()
            filtered = []
            for sec in items:
                match = (
                    q in sec.name.lower()
                    or q in sec.symbol.lower()
                    or (sec.isin and q in sec.isin.lower())
                    or (sec.cusip and q in sec.cusip.lower())
                    or q in sec.issuer_name.lower()
                )
                if match:
                    filtered.append(sec)
            items = filtered

        # Filter by issuer category (sovereign, corporate, supranational)
        if issuer_type and issuer_type.strip():
            it = issuer_type.strip().lower()
            items = [sec for sec in items if sec.issuer_category.value.lower() == it]

        # Filter by issuer entity UUID
        if issuer_entity_id:
            items = [sec for sec in items if sec.issuer_entity_id == issuer_entity_id]

        # Filter by bond debt type (sovereign, corporate, treasury_bill, etc.)
        if bond_type and bond_type.strip():
            bt = bond_type.strip().lower()
            items = [sec for sec in items if sec.bond_type.value.lower() == bt]

        # Filter by currency
        if currency and currency.strip():
            c = currency.strip().upper()
            items = [sec for sec in items if sec.currency == c]

        # Filter by coupon type
        if coupon_type and coupon_type.strip():
            ct = coupon_type.strip().lower()
            items = [sec for sec in items if sec.coupon_type.value.lower() == ct]

        # Filter by maturity bucket
        if maturity_bucket and maturity_bucket.strip():
            mb = maturity_bucket.strip().lower()
            bucket_filtered = []
            for sec in items:
                _, bucket = calculate_maturity_bucket(sec.maturity_date, sec.is_perpetual)
                if bucket.value.lower() == mb:
                    bucket_filtered.append(sec)
            items = bucket_filtered

        # Deterministic sorting by (issuer_name, maturity_date or '9999-12-31', symbol, id)
        items.sort(
            key=lambda x: (
                x.issuer_name.lower(),
                x.maturity_date or "9999-12-31",
                x.symbol.lower(),
                str(x.instrument_entity_id),
            )
        )

        total_matched = len(items)

        # Keyset Cursor decoding
        start_idx = 0
        if cursor:
            try:
                decoded = base64.b64decode(cursor.encode("utf-8")).decode("utf-8")
                cursor_data = json.loads(decoded)
                cursor_id = cursor_data.get("instrument_id")
                if cursor_id:
                    for idx, sec in enumerate(items):
                        if str(sec.instrument_entity_id) == cursor_id:
                            start_idx = idx + 1
                            break
            except Exception:
                start_idx = 0

        limit = max(1, min(limit, 100))
        page_items = items[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < total_matched

        next_cursor = None
        if has_more and page_items:
            last_item = page_items[-1]
            payload = {
                "instrument_id": str(last_item.instrument_entity_id),
                "issuer_name": last_item.issuer_name,
                "maturity_date": last_item.maturity_date or "9999-12-31",
            }
            encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
            next_cursor = encoded

        return page_items, total_matched, next_cursor, has_more

    def get_coverage_summary(self) -> BondCoverageSummary:
        """Calculate verified fixed-income coverage metrics."""
        issuers_set = set()
        currencies_set = set()
        sovereign_count = 0
        corporate_count = 0
        other_count = 0
        prices_count = 0
        yields_count = 0
        accrued_count = 0

        for sec in self._securities:
            issuers_set.add(sec.issuer_entity_id)
            currencies_set.add(sec.currency)

            is_sov = (
                sec.bond_type == BondTypeEnum.SOVEREIGN
                or sec.bond_type == BondTypeEnum.TREASURY_BILL
            )
            if is_sov:
                sovereign_count += 1
            elif sec.bond_type == BondTypeEnum.CORPORATE:
                corporate_count += 1
            else:
                other_count += 1

            if sec.default_clean_price is not None:
                prices_count += 1
            if sec.default_yield_value is not None:
                yields_count += 1
            if sec.default_accrued_interest is not None:
                accrued_count += 1

        return BondCoverageSummary(
            total_bonds=len(self._securities),
            total_issuers=len(issuers_set),
            sovereign_bonds=sovereign_count,
            corporate_bonds=corporate_count,
            other_bonds=other_count,
            bonds_with_prices=prices_count,
            bonds_with_yields=yields_count,
            bonds_with_accrued_interest=accrued_count,
            currencies=sorted(list(currencies_set)),
        )

    def get_filter_options(self) -> BondFilterOptionsResponse:
        """Return available filter options and coverage summary."""
        currencies = sorted(list({sec.currency for sec in self._securities}))
        issuer_categories = [e.value for e in IssuerCategoryEnum]
        bond_types = [e.value for e in BondTypeEnum]
        coupon_types = [e.value for e in CouponTypeEnum]
        maturity_buckets = [e.value for e in MaturityBucketEnum]

        issuers_list = []
        for issuer in self._issuers.values():
            issuers_list.append(
                {
                    "issuer_entity_id": str(issuer.issuer_entity_id),
                    "name": issuer.name,
                    "category": issuer.issuer_category.value,
                    "country": issuer.country_code,
                }
            )
        issuers_list.sort(key=lambda x: x["name"].lower())

        coverage = self.get_coverage_summary()

        return BondFilterOptionsResponse(
            issuer_categories=issuer_categories,
            bond_types=bond_types,
            currencies=currencies,
            coupon_types=coupon_types,
            maturity_buckets=maturity_buckets,
            issuers=issuers_list,
            coverage=coverage,
        )
