"""ScreenerService: Query planning, validation, server-side filtering, sorting, pagination, and provenance enrichment (Stage 94)."""

import base64
import json
import math
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Set, Tuple

from atlas.screeners.enums import (
    FilterCategory,
    FilterOperator,
    ListingStatus,
    MetricAvailabilityStatus,
    SecurityType,
    SortDirection,
    UnitKind,
    ValueType,
)
from atlas.screeners.errors import (
    ScreenerCursorInvalidError,
    ScreenerFilterNotFoundError,
    ScreenerOperatorNotSupportedError,
    ScreenerQueryLimitExceededError,
    ScreenerRangeInvalidError,
    ScreenerSortUnsupportedError,
    ScreenerUniverseNotFoundError,
    ScreenerValueTypeInvalidError,
)
from atlas.screeners.models import (
    ScreenerColumnDefinition,
    ScreenerFilterDefinition,
    ScreenerObservationRecord,
    ScreenerUniverseDefinition,
)
from atlas.screeners.repository import ScreenerRepository
from atlas.screeners.schemas import (
    CountryOptionDTO,
    ExchangeOptionDTO,
    FilterCriterionDTO,
    ScreenerCoverageResponseDTO,
    ScreenerMetricCellDTO,
    ScreenerResultRowDTO,
    ScreenerRunRequestDTO,
    ScreenerRunResponseDTO,
    SectorOptionDTO,
    SortCriterionDTO,
    ValidationResponseDTO,
)

# Execution budget constants
MAX_ACTIVE_FILTERS = 20
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


class ScreenerService:
    """Core domain service for Financial Screeners V1."""

    def __init__(self, repository: Optional[ScreenerRepository] = None):
        self._repo = repository or ScreenerRepository()

    # =========================================================================
    # 1. Metadata & Discovery APIs
    # =========================================================================

    def get_universes(self) -> List[ScreenerUniverseDefinition]:
        return self._repo.get_universes()

    def get_filters(self) -> List[ScreenerFilterDefinition]:
        return self._repo.get_filters()

    def get_columns(self) -> List[ScreenerColumnDefinition]:
        return self._repo.get_columns()

    def get_exchanges(self) -> List[ExchangeOptionDTO]:
        """Returns supported exchange options with security counts."""
        records = self._repo.get_records()
        exchanges: Dict[str, Dict[str, Any]] = {}
        for r in records:
            if r.listing_status == ListingStatus.ACTIVE and r.security_type == SecurityType.COMMON_STOCK:
                mic = r.exchange_mic
                if mic not in exchanges:
                    exchanges[mic] = {
                        "mic": mic,
                        "name": r.exchange_name,
                        "country_code": r.listing_country_code,
                        "count": 0,
                    }
                exchanges[mic]["count"] += 1

        return [ExchangeOptionDTO(**item) for item in sorted(exchanges.values(), key=lambda x: x["name"])]

    def get_geographies(self) -> List[CountryOptionDTO]:
        """Returns supported country filter options with security counts."""
        records = self._repo.get_records()
        countries: Dict[str, Dict[str, Any]] = {}
        for r in records:
            if r.listing_status == ListingStatus.ACTIVE and r.security_type == SecurityType.COMMON_STOCK:
                code = r.listing_country_code
                if code not in countries:
                    countries[code] = {
                        "code": code,
                        "name": r.listing_country,
                        "count": 0,
                    }
                countries[code]["count"] += 1

        return [CountryOptionDTO(**item) for item in sorted(countries.values(), key=lambda x: x["name"])]

    def get_industries(self) -> List[SectorOptionDTO]:
        """Returns supported sector & child industry classifications."""
        records = self._repo.get_records()
        sectors: Dict[str, Dict[str, Any]] = {}
        for r in records:
            if r.sector and r.listing_status == ListingStatus.ACTIVE:
                s_name = r.sector
                if s_name not in sectors:
                    sectors[s_name] = {
                        "name": s_name,
                        "count": 0,
                        "industries": set(),
                    }
                sectors[s_name]["count"] += 1
                if r.industry:
                    sectors[s_name]["industries"].add(r.industry)

        result: List[SectorOptionDTO] = []
        for s_name, s_data in sorted(sectors.items(), key=lambda x: x[0]):
            result.append(
                SectorOptionDTO(
                    name=s_name,
                    count=s_data["count"],
                    industries=sorted(list(s_data["industries"])),
                )
            )
        return result

    def get_coverage(self) -> ScreenerCoverageResponseDTO:
        """Computes comprehensive institutional coverage audit."""
        records = self._repo.get_records()
        active = [r for r in records if r.listing_status == ListingStatus.ACTIVE]
        exchanges = {r.exchange_mic for r in records}
        countries = {r.listing_country_code for r in records}
        sectors = {r.sector for r in records if r.sector}

        quotes_count = sum(1 for r in records if r.last_price is not None)
        cap_count = sum(1 for r in records if r.market_cap is not None)
        fundamentals_count = sum(1 for r in records if r.revenue is not None or r.net_income is not None)
        ratios_count = sum(1 for r in records if r.pe_ratio is not None or r.dividend_yield is not None)

        freshness_map: Dict[str, int] = {}
        for r in records:
            key = str(r.price_freshness.value)
            freshness_map[key] = freshness_map.get(key, 0) + 1

        providers = sorted(list({r.provider for r in records}))

        return ScreenerCoverageResponseDTO(
            total_instruments=len(records),
            active_listings=len(active),
            exchanges_count=len(exchanges),
            countries_count=len(countries),
            sectors_count=len(sectors),
            instruments_with_quotes=quotes_count,
            instruments_with_market_cap=cap_count,
            instruments_with_fundamentals=fundamentals_count,
            instruments_with_ratios=ratios_count,
            providers_represented=providers,
            data_freshness_breakdown=freshness_map,
        )

    # =========================================================================
    # 2. Query Validation
    # =========================================================================

    def validate_query(self, request: ScreenerRunRequestDTO) -> ValidationResponseDTO:
        """Validates candidate screener query conditions without executing full search."""
        u_def = self._repo.get_universe(request.universe.universe_id)
        if not u_def:
            raise ScreenerUniverseNotFoundError(request.universe.universe_id)

        if len(request.filters) > MAX_ACTIVE_FILTERS:
            raise ScreenerQueryLimitExceededError(limit=MAX_ACTIVE_FILTERS, actual=len(request.filters))

        accepted_filters: List[FilterCriterionDTO] = []
        rejected_filters: List[Dict[str, Any]] = []
        warnings: List[str] = []

        for f in request.filters:
            f_def = self._repo.get_filter(f.filter_id)
            if not f_def:
                rejected_filters.append({
                    "filter_id": f.filter_id,
                    "reason": f"Filter '{f.filter_id}' is not in approved filter registry.",
                    "code": "SCREENER_FILTER_NOT_FOUND",
                })
                continue

            if f.operator not in f_def.allowed_operators:
                rejected_filters.append({
                    "filter_id": f.filter_id,
                    "reason": f"Operator '{f.operator}' not allowed for '{f.filter_id}'. Allowed: {[op.value for op in f_def.allowed_operators]}.",
                    "code": "SCREENER_OPERATOR_NOT_SUPPORTED",
                })
                continue

            # Validate range
            if f.operator == FilterOperator.BETWEEN:
                if f.secondary_value is None:
                    rejected_filters.append({
                        "filter_id": f.filter_id,
                        "reason": "Operator BETWEEN requires both a lower value and a secondary_value upper bound.",
                        "code": "SCREENER_RANGE_INVALID",
                    })
                    continue
                try:
                    d1 = Decimal(str(f.value))
                    d2 = Decimal(str(f.secondary_value))
                    if d1 > d2:
                        rejected_filters.append({
                            "filter_id": f.filter_id,
                            "reason": f"Range lower bound ({d1}) cannot exceed upper bound ({d2}).",
                            "code": "SCREENER_RANGE_INVALID",
                        })
                        continue
                except (InvalidOperation, TypeError, ValueError):
                    rejected_filters.append({
                        "filter_id": f.filter_id,
                        "reason": "Numeric values could not be parsed for range comparison.",
                        "code": "SCREENER_VALUE_TYPE_INVALID",
                    })
                    continue

            # Validate numeric types
            if f_def.value_type in [ValueType.NUMERIC, ValueType.CURRENCY, ValueType.PERCENTAGE, ValueType.INTEGER]:
                if f.operator != FilterOperator.IN:
                    try:
                        d_val = Decimal(str(f.value))
                        if not math.isfinite(float(d_val)):
                            rejected_filters.append({
                                "filter_id": f.filter_id,
                                "reason": "Non-finite values (NaN / Inf) are prohibited.",
                                "code": "SCREENER_VALUE_TYPE_INVALID",
                            })
                            continue
                    except (InvalidOperation, TypeError, ValueError):
                        rejected_filters.append({
                            "filter_id": f.filter_id,
                            "reason": f"Expected numeric decimal value for '{f.filter_id}', got '{f.value}'.",
                            "code": "SCREENER_VALUE_TYPE_INVALID",
                        })
                        continue

            accepted_filters.append(f)

        # Universe size calculation
        universe_candidates = self._prefilter_universe(request)

        is_valid = len(rejected_filters) == 0
        return ValidationResponseDTO(
            valid=is_valid,
            accepted_filters=accepted_filters,
            rejected_filters=rejected_filters,
            warnings=warnings,
            eligible_universe_size=len(universe_candidates),
        )

    # =========================================================================
    # 3. Screener Query Execution
    # =========================================================================

    def run_screen(self, request: ScreenerRunRequestDTO) -> ScreenerRunResponseDTO:
        """
        Executes server-side screening with universe resolution, indexed filter pushdown,
        deterministic tie-breaker sorting, bounded pagination, and cell provenance formatting.
        Zero external provider RPC fanout.
        """
        start_time = time.perf_counter()

        # 1. Validation & universe check
        val = self.validate_query(request)
        if not val.valid:
            first_err = val.rejected_filters[0]
            if first_err["code"] == "SCREENER_FILTER_NOT_FOUND":
                raise ScreenerFilterNotFoundError(first_err["filter_id"])
            if first_err["code"] == "SCREENER_OPERATOR_NOT_SUPPORTED":
                raise ScreenerOperatorNotSupportedError(first_err["filter_id"], "unsupported")
            if first_err["code"] == "SCREENER_RANGE_INVALID":
                raise ScreenerRangeInvalidError(first_err["filter_id"])
            raise ScreenerValueTypeInvalidError(first_err["filter_id"], first_err["reason"])

        # 2. Universe pre-filtering (asset class, security types, listing status, venue scopes)
        candidates = self._prefilter_universe(request)

        # 3. Server-side predicate evaluation (AND-based composition)
        matching_records = []
        for rec in candidates:
            if self._satisfies_all_filters(rec, request.filters):
                matching_records.append(rec)

        # 4. Sorting with deterministic tie-breaker
        sorted_records = self._sort_records(matching_records, request.sort)

        # 5. Bounded Pagination
        page_size = min(max(1, request.page_size), MAX_PAGE_SIZE)
        page = max(1, request.page)

        # Handle cursor if provided
        if request.cursor:
            page, page_size = self._decode_cursor(request.cursor)

        total_matching = len(sorted_records)
        total_pages = max(1, math.ceil(total_matching / page_size)) if total_matching > 0 else 1
        page = min(page, total_pages)

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_records = sorted_records[start_idx:end_idx]

        # 6. Next cursor generation
        has_next = page < total_pages
        has_prev = page > 1
        next_cursor = self._encode_cursor(page + 1, page_size) if has_next else None

        # 7. Column Selection & Cell Provenance Enrichment
        filter_ids = [f.filter_id for f in request.filters]
        active_columns = self._resolve_columns(request.columns, filter_ids=filter_ids)
        result_rows: List[ScreenerResultRowDTO] = []
        for r in page_records:
            row_dto = self._build_result_row(r, active_columns)
            result_rows.append(row_dto)

        # 8. Source coverage statistics for response
        source_cov = {
            "total_evaluated": len(candidates),
            "total_matching": total_matching,
            "page_returned": len(result_rows),
            "quotes_coverage": sum(1 for r in page_records if r.last_price is not None),
            "fundamentals_coverage": sum(1 for r in page_records if r.revenue is not None),
            "ratios_coverage": sum(1 for r in page_records if r.pe_ratio is not None),
        }

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return ScreenerRunResponseDTO(
            query_id=str(uuid.uuid4()),
            universe_id=request.universe.universe_id,
            evaluated_as_of=datetime.now(timezone.utc),
            total_matching_count=total_matching,
            count_exactness="EXACT",
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next_page=has_next,
            has_previous_page=has_prev,
            next_cursor=next_cursor,
            rows=result_rows,
            applied_filters_count=len(request.filters),
            source_coverage=source_cov,
            execution_duration_ms=round(duration_ms, 2),
            warnings=[],
        )

    # =========================================================================
    # 4. Internal Filter Evaluation Logic
    # =========================================================================

    def _prefilter_universe(self, request: ScreenerRunRequestDTO) -> List[ScreenerObservationRecord]:
        """Reduces universe using indexed eligibility criteria before expensive filtering."""
        u_def = self._repo.get_universe(request.universe.universe_id)
        if not u_def:
            raise ScreenerUniverseNotFoundError(request.universe.universe_id)

        all_records = self._repo.get_records()
        candidates: List[ScreenerObservationRecord] = []

        # Target security types & listing statuses
        allowed_types: Set[SecurityType] = set(u_def.eligible_security_types)
        if request.universe.security_types:
            override_types = set()
            for st in request.universe.security_types:
                parsed = SecurityType._missing_(st)
                if parsed:
                    override_types.add(parsed)
            if override_types:
                allowed_types = override_types

        allowed_statuses: Set[ListingStatus] = set(u_def.eligible_listing_statuses)
        if request.universe.listing_statuses:
            override_statuses = set()
            for ls in request.universe.listing_statuses:
                parsed = ListingStatus._missing_(ls)
                if parsed:
                    override_statuses.add(parsed)
            if override_statuses:
                allowed_statuses = override_statuses

        allowed_mics: Optional[Set[str]] = (
            set(u_def.exchange_scope) if u_def.exchange_scope else None
        )
        if request.universe.exchange_mics:
            req_mics = {m.upper().strip() for m in request.universe.exchange_mics if m.strip()}
            if req_mics:
                allowed_mics = req_mics if allowed_mics is None else (allowed_mics & req_mics)

        allowed_issuer_countries: Optional[Set[str]] = None
        if request.universe.issuer_country_codes:
            allowed_issuer_countries = {c.upper().strip() for c in request.universe.issuer_country_codes if c.strip()}

        allowed_listing_countries: Optional[Set[str]] = None
        if request.universe.listing_country_codes:
            allowed_listing_countries = {c.upper().strip() for c in request.universe.listing_country_codes if c.strip()}

        allowed_sectors: Optional[Set[str]] = None
        if request.universe.sectors:
            allowed_sectors = {s.lower().strip() for s in request.universe.sectors if s.strip()}

        allowed_industries: Optional[Set[str]] = None
        if request.universe.industries:
            allowed_industries = {i.lower().strip() for i in request.universe.industries if i.strip()}

        for r in all_records:
            # 1. Asset class / security type check (e.g. exclude ETF from common equity!)
            if r.security_type not in allowed_types:
                continue

            # 2. Listing status check (e.g. exclude delisted from active screens!)
            if r.listing_status not in allowed_statuses:
                continue

            # 3. Exchange MIC scope
            if allowed_mics and r.exchange_mic.upper() not in allowed_mics:
                continue

            # 4. Issuer Domicile Country scope
            if allowed_issuer_countries and r.issuer_country_code.upper() not in allowed_issuer_countries:
                continue

            # 5. Listing Market Country scope
            if allowed_listing_countries and r.listing_country_code.upper() not in allowed_listing_countries:
                continue

            # 6. Sector scope
            if allowed_sectors:
                if not r.sector or r.sector.lower().strip() not in allowed_sectors:
                    continue

            # 7. Industry scope
            if allowed_industries:
                if not r.industry or r.industry.lower().strip() not in allowed_industries:
                    continue

            candidates.append(r)

        return candidates

    def _satisfies_all_filters(
        self, record: ScreenerObservationRecord, filters: List[FilterCriterionDTO]
    ) -> bool:
        """Evaluates basic AND condition composition with strict NULL semantics."""
        for crit in filters:
            if not self._eval_criterion(record, crit):
                return False
        return True

    def _eval_criterion(self, record: ScreenerObservationRecord, crit: FilterCriterionDTO) -> bool:
        """
        Evaluates a single filter criterion.
        Strict Null Policy: If candidate observation is None, comparison returns False
        for all standard relational operators (GT, GTE, LT, LTE, BETWEEN).
        Missing values NEVER pass numeric comparisons.
        """
        field_name = crit.filter_id
        val = getattr(record, field_name, None)

        # Strict NULL handling
        if val is None:
            return False

        op = crit.operator
        target = crit.value

        # Numeric / Decimal handling
        if isinstance(val, (Decimal, int, float)):
            try:
                dec_val = Decimal(str(val))
                dec_target = Decimal(str(target))

                if op == FilterOperator.EQ:
                    return dec_val == dec_target
                elif op == FilterOperator.NE:
                    return dec_val != dec_target
                elif op == FilterOperator.GT:
                    return dec_val > dec_target
                elif op == FilterOperator.GTE:
                    return dec_val >= dec_target
                elif op == FilterOperator.LT:
                    return dec_val < dec_target
                elif op == FilterOperator.LTE:
                    return dec_val <= dec_target
                elif op == FilterOperator.BETWEEN:
                    dec_upper = Decimal(str(crit.secondary_value))
                    return dec_target <= dec_val <= dec_upper
                elif op == FilterOperator.IN:
                    if isinstance(target, (list, set, tuple)):
                        return dec_val in {Decimal(str(x)) for x in target}
                    return dec_val == dec_target
            except (InvalidOperation, TypeError, ValueError):
                return False

        # String / Enum handling
        str_val = str(val).strip().lower()
        if op == FilterOperator.EQ:
            return str_val == str(target).strip().lower()
        elif op == FilterOperator.NE:
            return str_val != str(target).strip().lower()
        elif op == FilterOperator.IN:
            if isinstance(target, (list, set, tuple)):
                target_set = {str(x).strip().lower() for x in target}
                return str_val in target_set
            return str_val == str(target).strip().lower()

        return False

    # =========================================================================
    # 5. Deterministic Sorting & Pagination
    # =========================================================================

    def _sort_records(
        self, records: List[ScreenerObservationRecord], sort_criteria: List[SortCriterionDTO]
    ) -> List[ScreenerObservationRecord]:
        """
        Sorts candidates deterministically.
        Uses primary requested field (with NULLS LAST policy) and guarantees
        stable tie-breaker ordering on (instrument_entity_id, listing_id).
        """
        if not sort_criteria:
            # Default sorting: Market Cap DESC, tie-breaker instrument UUID ASC
            sort_criteria = [SortCriterionDTO(field_id="market_cap", direction=SortDirection.DESC)]

        primary_sort = sort_criteria[0]
        field_id = primary_sort.field_id
        is_desc = primary_sort.direction == SortDirection.DESC

        # Verify field is sortable
        col_def = self._repo.get_column(field_id)
        if not col_def and not hasattr(ScreenerObservationRecord, field_id):
            raise ScreenerSortUnsupportedError(field_id)

        def sort_key(r: ScreenerObservationRecord):
            raw_val = getattr(r, field_id, None)

            # NULLS LAST policy:
            # In ascending: non-nulls first (0), nulls last (1)
            # In descending: non-nulls first (0), nulls last (1)
            is_null = 1 if raw_val is None else 0

            # Normalization for numeric vs string
            if raw_val is None:
                norm_val = Decimal("-Infinity") if is_desc else Decimal("Infinity")
            elif isinstance(raw_val, (Decimal, int, float)):
                norm_val = Decimal(str(raw_val))
            else:
                norm_val = str(raw_val).lower()

            # Tie-breakers: stable instrument UUID and listing UUID
            tie_breaker_1 = str(r.instrument_entity_id)
            tie_breaker_2 = str(r.listing_id)

            return (is_null, norm_val, tie_breaker_1, tie_breaker_2)

        return sorted(records, key=sort_key, reverse=is_desc)

    def _encode_cursor(self, page: int, page_size: int) -> str:
        payload = {"p": page, "s": page_size, "t": int(time.time())}
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    def _decode_cursor(self, cursor_str: str) -> Tuple[int, int]:
        try:
            raw = base64.urlsafe_b64decode(cursor_str.encode()).decode()
            data = json.loads(raw)
            return int(data.get("p", 1)), int(data.get("s", DEFAULT_PAGE_SIZE))
        except Exception:
            raise ScreenerCursorInvalidError()

    # =========================================================================
    # 6. Column Selection & Cell Formatting
    # =========================================================================

    def _resolve_columns(
        self, requested_columns: Optional[List[str]], filter_ids: Optional[List[str]] = None
    ) -> List[ScreenerColumnDefinition]:
        """Resolves active columns from request, or falls back to default visible columns plus filtered metrics."""
        all_cols = {c.column_id: c for c in self._repo.get_columns()}

        resolved: List[ScreenerColumnDefinition] = []
        if requested_columns:
            for col_id in requested_columns:
                c = all_cols.get(col_id.lower().strip())
                if c and c not in resolved:
                    resolved.append(c)
        else:
            resolved = [c for c in all_cols.values() if c.default_visible]

        # Also ensure any actively filtered column is included in row metrics
        if filter_ids:
            for fid in filter_ids:
                c = all_cols.get(fid.lower().strip())
                if c and c not in resolved:
                    resolved.append(c)

        return resolved

    def _build_result_row(
        self, record: ScreenerObservationRecord, columns: List[ScreenerColumnDefinition]
    ) -> ScreenerResultRowDTO:
        """Assembles a high-density institutional row DTO with cell-level provenance."""
        metrics: Dict[str, ScreenerMetricCellDTO] = {}

        for col in columns:
            col_id = col.column_id
            raw_val = getattr(record, col_id, None)

            # Special field mappings
            if col_id == "symbol":
                raw_val = record.ticker
            elif col_id == "security_name":
                raw_val = record.canonical_security_name

            # Determine availability & format display value
            status, display_val = self._format_cell(raw_val, col, record)

            metrics[col_id] = ScreenerMetricCellDTO(
                metric_id=col_id,
                raw_value=raw_val,
                display_value=display_val,
                unit=col.unit_kind.value,
                currency=record.trading_currency if col.data_type == ValueType.CURRENCY else None,
                status=status.value,
                observation_period=record.fiscal_period if col.category == FilterCategory.FUNDAMENTALS else None,
                freshness=record.price_freshness.value if col.category == FilterCategory.MARKET_DATA else None,
                as_of=record.price_timestamp.isoformat() if record.price_timestamp else None,
                provider=record.provider,
            )

        return ScreenerResultRowDTO(
            instrument_entity_id=record.instrument_entity_id,
            listing_id=record.listing_id,
            issuer_company_entity_id=record.issuer_company_entity_id,
            canonical_security_name=record.canonical_security_name,
            ticker=record.ticker,
            exchange_mic=record.exchange_mic,
            exchange_name=record.exchange_name,
            listing_country_code=record.listing_country_code,
            issuer_country_code=record.issuer_country_code,
            security_type=record.security_type.value,
            share_class_name=record.share_class_name,
            listing_status=record.listing_status.value,
            currency=record.trading_currency,
            sector=record.sector,
            industry=record.industry,
            metrics=metrics,
        )

    def _format_cell(
        self, raw_val: Any, col: ScreenerColumnDefinition, record: ScreenerObservationRecord
    ) -> Tuple[MetricAvailabilityStatus, str]:
        """Formats cell with compact institutional notation and tabular clarity."""
        if raw_val is None:
            # Special case for P/E on negative earnings
            if col.column_id == "pe_ratio" and record.net_income is not None and record.net_income <= Decimal("0"):
                return MetricAvailabilityStatus.NOT_MEANINGFUL, "N/M"
            return MetricAvailabilityStatus.MISSING, "—"

        try:
            if col.unit_kind == UnitKind.MONETARY:
                d = Decimal(str(raw_val))
                curr = record.trading_currency
                sym = "$" if curr == "USD" else ("₹" if curr == "INR" else ("€" if curr == "EUR" else ("£" if curr == "GBP" else f"{curr} ")))
                if col.column_id == "market_cap" or col.column_id in ["revenue", "net_income", "total_assets", "book_equity", "traded_value_latest"]:
                    # Compact scaling for institutional tables
                    abs_d = abs(d)
                    sign = "-" if d < 0 else ""
                    if abs_d >= Decimal("1000000000000"):
                        return MetricAvailabilityStatus.AVAILABLE, f"{sign}{sym}{(abs_d / Decimal('1000000000000')).quantize(Decimal('0.01'))}T"
                    elif abs_d >= Decimal("1000000000"):
                        return MetricAvailabilityStatus.AVAILABLE, f"{sign}{sym}{(abs_d / Decimal('1000000000')).quantize(Decimal('0.01'))}B"
                    elif abs_d >= Decimal("1000000"):
                        return MetricAvailabilityStatus.AVAILABLE, f"{sign}{sym}{(abs_d / Decimal('1000000')).quantize(Decimal('0.01'))}M"
                    return MetricAvailabilityStatus.AVAILABLE, f"{sign}{sym}{abs_d.quantize(Decimal('0.01'))}"
                else:
                    # Last price
                    return MetricAvailabilityStatus.AVAILABLE, f"{sym}{d.quantize(Decimal('0.01'))}"

            elif col.unit_kind == UnitKind.PERCENT:
                d = Decimal(str(raw_val))
                sign = "+" if d > 0 and col.column_id == "price_change_pct" else ""
                return MetricAvailabilityStatus.AVAILABLE, f"{sign}{d.quantize(Decimal('0.01'))}%"

            elif col.unit_kind == UnitKind.MULTIPLE:
                d = Decimal(str(raw_val))
                return MetricAvailabilityStatus.AVAILABLE, f"{d.quantize(Decimal('0.01'))}x"

            elif col.unit_kind == UnitKind.SHARES:
                d = Decimal(str(raw_val))
                if d >= Decimal("1000000"):
                    return MetricAvailabilityStatus.AVAILABLE, f"{(d / Decimal('1000000')).quantize(Decimal('0.1'))}M"
                elif d >= Decimal("1000"):
                    return MetricAvailabilityStatus.AVAILABLE, f"{(d / Decimal('1000')).quantize(Decimal('0.1'))}K"
                return MetricAvailabilityStatus.AVAILABLE, f"{int(d):,}"

            elif col.unit_kind == UnitKind.CURRENCY_PER_SHARE:
                d = Decimal(str(raw_val))
                curr = record.trading_currency
                sym = "$" if curr == "USD" else ("₹" if curr == "INR" else ("€" if curr == "EUR" else ("£" if curr == "GBP" else "")))
                return MetricAvailabilityStatus.AVAILABLE, f"{sym}{d.quantize(Decimal('0.01'))}"

            return MetricAvailabilityStatus.AVAILABLE, str(raw_val)

        except Exception:
            return MetricAvailabilityStatus.AVAILABLE, str(raw_val)
