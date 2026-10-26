"""ScreenerService: Query planning, validation, server-side filtering, sorting, pagination, and provenance enrichment (Stage 94)."""

import base64
import functools
import json
import math
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from atlas.screeners.enums import (
    FilterCategory,
    FilterOperator,
    ListingStatus,
    MetricAvailabilityStatus,
    SecurityType,
    SortDirection,
    SortNullOrder,
    UnitKind,
    ValueType,
)
from atlas.screeners.errors import (
    ScreenerCursorInvalidError,
    ScreenerFilterNotFoundError,
    ScreenerOperatorNotSupportedError,
    ScreenerQueryLimitExceededError,
    ScreenerRangeInvalidError,
    ScreenerSortLimitExceededError,
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
from atlas.screeners.ranking import FactorRankingEngine
from atlas.screeners.repository import ScreenerRepository
from atlas.screeners.schemas import (
    ConditionValidationIssueDTO,
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
from atlas.screeners.technical import (
    compute_ema,
    compute_momentum,
    compute_rsi,
    compute_sma,
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

    def get_filter(self, filter_id: str) -> Optional[ScreenerFilterDefinition]:
        """Lookup a specific factor/filter by ID from the canonical registry."""
        return self._repo.get_filter(filter_id)

    def get_factors(self, category: Optional[str] = None) -> List[ScreenerFilterDefinition]:
        """Returns all approved factors, optionally filtered by category name."""
        all_filters = self._repo.get_filters()
        if not category:
            return all_filters
        cat_upper = category.upper()
        return [f for f in all_filters if f.category.value.upper() == cat_upper or f.category.name == cat_upper]

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
        """Validates candidate screener query conditions without executing full search (Stage 95)."""
        u_def = self._repo.get_universe(request.universe.universe_id)
        if not u_def:
            raise ScreenerUniverseNotFoundError(request.universe.universe_id)

        if len(request.filters) > MAX_ACTIVE_FILTERS:
            raise ScreenerQueryLimitExceededError(limit=MAX_ACTIVE_FILTERS, actual=len(request.filters))

        accepted_filters: List[FilterCriterionDTO] = []
        rejected_filters: List[Dict[str, Any]] = []
        issues: List[ConditionValidationIssueDTO] = []
        warnings: List[str] = []
        contradictions_detected = False

        # 1. Per-condition syntactic and semantic validation
        for f in request.filters:
            f_def = self._repo.get_filter(f.filter_id)
            if not f_def:
                reason = f"Filter '{f.filter_id}' is not in approved filter registry."
                rejected_filters.append({
                    "filter_id": f.filter_id,
                    "condition_id": f.condition_id,
                    "reason": reason,
                    "code": "SCREENER_FILTER_NOT_FOUND",
                })
                issues.append(ConditionValidationIssueDTO(
                    condition_id=f.condition_id,
                    filter_id=f.filter_id,
                    field_path="filter_id",
                    code="SCREENER_FILTER_NOT_FOUND",
                    severity="error",
                    message=reason,
                ))
                continue

            # Check universe eligibility
            if f_def.eligible_security_types:
                overlap = set(f_def.eligible_security_types).intersection(set(u_def.eligible_security_types))
                if not overlap:
                    warning_msg = (
                        f"Metric '{f_def.display_name}' applies to security types {[st.value for st in f_def.eligible_security_types]}, "
                        f"which are not included in selected universe '{u_def.name}'."
                    )
                    warnings.append(warning_msg)
                    issues.append(ConditionValidationIssueDTO(
                        condition_id=f.condition_id,
                        filter_id=f.filter_id,
                        code="SCREENER_UNIVERSE_INCOMPATIBILITY",
                        severity="warning",
                        message=warning_msg,
                    ))

            if f.operator not in f_def.allowed_operators:
                reason = f"Operator '{f.operator}' not allowed for '{f.filter_id}'. Allowed: {[op.value for op in f_def.allowed_operators]}."
                rejected_filters.append({
                    "filter_id": f.filter_id,
                    "condition_id": f.condition_id,
                    "reason": reason,
                    "code": "SCREENER_OPERATOR_NOT_SUPPORTED",
                })
                issues.append(ConditionValidationIssueDTO(
                    condition_id=f.condition_id,
                    filter_id=f.filter_id,
                    field_path="operator",
                    code="SCREENER_OPERATOR_NOT_SUPPORTED",
                    severity="error",
                    message=reason,
                ))
                continue

            # Validate range
            if f.operator == FilterOperator.BETWEEN:
                if f.secondary_value is None or str(f.secondary_value).strip() == "":
                    reason = "Operator BETWEEN requires both a lower value and a secondary_value upper bound."
                    rejected_filters.append({
                        "filter_id": f.filter_id,
                        "condition_id": f.condition_id,
                        "reason": reason,
                        "code": "SCREENER_RANGE_INVALID",
                    })
                    issues.append(ConditionValidationIssueDTO(
                        condition_id=f.condition_id,
                        filter_id=f.filter_id,
                        field_path="secondary_value",
                        code="SCREENER_RANGE_INVALID",
                        severity="error",
                        message=reason,
                    ))
                    continue
                try:
                    d1 = Decimal(str(f.value))
                    d2 = Decimal(str(f.secondary_value))
                    if d1 > d2:
                        reason = f"Range lower bound ({d1}) cannot exceed upper bound ({d2})."
                        rejected_filters.append({
                            "filter_id": f.filter_id,
                            "condition_id": f.condition_id,
                            "reason": reason,
                            "code": "SCREENER_RANGE_INVALID",
                        })
                        issues.append(ConditionValidationIssueDTO(
                            condition_id=f.condition_id,
                            filter_id=f.filter_id,
                            field_path="secondary_value",
                            code="SCREENER_RANGE_INVALID",
                            severity="error",
                            message=reason,
                        ))
                        continue
                except (InvalidOperation, TypeError, ValueError):
                    reason = "Numeric values could not be parsed for range comparison."
                    rejected_filters.append({
                        "filter_id": f.filter_id,
                        "condition_id": f.condition_id,
                        "reason": reason,
                        "code": "SCREENER_VALUE_TYPE_INVALID",
                    })
                    issues.append(ConditionValidationIssueDTO(
                        condition_id=f.condition_id,
                        filter_id=f.filter_id,
                        field_path="value",
                        code="SCREENER_VALUE_TYPE_INVALID",
                        severity="error",
                        message=reason,
                    ))
                    continue

            # Validate numeric types
            if f_def.value_type in [ValueType.NUMERIC, ValueType.CURRENCY, ValueType.PERCENTAGE, ValueType.INTEGER]:
                if f.operator != FilterOperator.IN:
                    try:
                        d_val = Decimal(str(f.value))
                        if not math.isfinite(float(d_val)):
                            reason = "Non-finite values (NaN / Inf) are prohibited."
                            rejected_filters.append({
                                "filter_id": f.filter_id,
                                "condition_id": f.condition_id,
                                "reason": reason,
                                "code": "SCREENER_VALUE_TYPE_INVALID",
                            })
                            issues.append(ConditionValidationIssueDTO(
                                condition_id=f.condition_id,
                                filter_id=f.filter_id,
                                field_path="value",
                                code="SCREENER_VALUE_TYPE_INVALID",
                                severity="error",
                                message=reason,
                            ))
                            continue
                    except (InvalidOperation, TypeError, ValueError):
                        reason = f"Expected numeric decimal value for '{f.filter_id}', got '{f.value}'."
                        rejected_filters.append({
                            "filter_id": f.filter_id,
                            "condition_id": f.condition_id,
                            "reason": reason,
                            "code": "SCREENER_VALUE_TYPE_INVALID",
                        })
                        issues.append(ConditionValidationIssueDTO(
                            condition_id=f.condition_id,
                            filter_id=f.filter_id,
                            field_path="value",
                            code="SCREENER_VALUE_TYPE_INVALID",
                            severity="error",
                            message=reason,
                        ))
                        continue

            # Validate parameters if supplied for parameterized/technical filters
            if f.parameters:
                param_error = None
                if f_def.allowed_parameters:
                    for k, v in f.parameters.items():
                        if k not in f_def.allowed_parameters:
                            param_error = f"Parameter '{k}' is not supported for filter '{f.filter_id}'."
                            break
                        if k == "period":
                            try:
                                p_int = int(v)
                                if p_int < 2 or p_int > 500:
                                    param_error = f"Period parameter must be an integer between 2 and 500, got {v}."
                                    break
                            except (ValueError, TypeError):
                                param_error = f"Period parameter must be an integer, got '{v}'."
                                break
                if param_error:
                    rejected_filters.append({
                        "filter_id": f.filter_id,
                        "condition_id": f.condition_id,
                        "reason": param_error,
                        "code": "SCREENER_PARAMETER_INVALID",
                    })
                    issues.append(ConditionValidationIssueDTO(
                        condition_id=f.condition_id,
                        filter_id=f.filter_id,
                        field_path="parameters",
                        code="SCREENER_PARAMETER_INVALID",
                        severity="error",
                        message=param_error,
                    ))
                    continue

            accepted_filters.append(f)

        # 2. Contradiction Detection across active conditions
        # A. Numeric boundary contradiction detection
        numeric_bounds: Dict[str, Dict[str, Any]] = {}
        for f in accepted_filters:
            f_def = self._repo.get_filter(f.filter_id)
            if not f_def or f_def.value_type not in [ValueType.NUMERIC, ValueType.CURRENCY, ValueType.PERCENTAGE, ValueType.INTEGER]:
                continue
            if f.operator == FilterOperator.IN:
                continue

            fid = f.filter_id
            if fid not in numeric_bounds:
                numeric_bounds[fid] = {
                    "min_val": None,
                    "min_strict": False,
                    "min_condition_id": None,
                    "max_val": None,
                    "max_strict": False,
                    "max_condition_id": None,
                    "eq_val": None,
                    "eq_condition_id": None,
                }
            nb = numeric_bounds[fid]

            try:
                if f.operator in [FilterOperator.GT, FilterOperator.GTE]:
                    val_dec = Decimal(str(f.value))
                    is_strict = f.operator == FilterOperator.GT
                    if nb["min_val"] is None or val_dec > nb["min_val"] or (val_dec == nb["min_val"] and is_strict):
                        nb["min_val"] = val_dec
                        nb["min_strict"] = is_strict
                        nb["min_condition_id"] = f.condition_id
                elif f.operator in [FilterOperator.LT, FilterOperator.LTE]:
                    val_dec = Decimal(str(f.value))
                    is_strict = f.operator == FilterOperator.LT
                    if nb["max_val"] is None or val_dec < nb["max_val"] or (val_dec == nb["max_val"] and is_strict):
                        nb["max_val"] = val_dec
                        nb["max_strict"] = is_strict
                        nb["max_condition_id"] = f.condition_id
                elif f.operator == FilterOperator.EQ:
                    val_dec = Decimal(str(f.value))
                    if nb["eq_val"] is not None and nb["eq_val"] != val_dec:
                        contradictions_detected = True
                        reason = f"Contradictory equality conditions on '{fid}': cannot equal both {nb['eq_val']} and {val_dec}."
                        rejected_filters.append({
                            "filter_id": fid,
                            "condition_id": f.condition_id,
                            "reason": reason,
                            "code": "SCREENER_CONTRADICTORY_CONDITIONS",
                        })
                        issues.append(ConditionValidationIssueDTO(
                            condition_id=f.condition_id,
                            filter_id=fid,
                            code="SCREENER_CONTRADICTORY_CONDITIONS",
                            severity="error",
                            message=reason,
                        ))
                    nb["eq_val"] = val_dec
                    nb["eq_condition_id"] = f.condition_id
                elif f.operator == FilterOperator.BETWEEN and f.secondary_value is not None:
                    d_low = Decimal(str(f.value))
                    d_high = Decimal(str(f.secondary_value))
                    if nb["min_val"] is None or d_low > nb["min_val"]:
                        nb["min_val"] = d_low
                        nb["min_strict"] = False
                        nb["min_condition_id"] = f.condition_id
                    if nb["max_val"] is None or d_high < nb["max_val"]:
                        nb["max_val"] = d_high
                        nb["max_strict"] = False
                        nb["max_condition_id"] = f.condition_id
            except (InvalidOperation, TypeError, ValueError):
                pass

        for fid, nb in numeric_bounds.items():
            if nb["min_val"] is not None and nb["max_val"] is not None:
                if nb["min_val"] > nb["max_val"]:
                    contradictions_detected = True
                    reason = (
                        f"Contradictory conditions on '{fid}': lower bound ({nb['min_val']}) "
                        f"strictly exceeds upper bound ({nb['max_val']}). No securities can satisfy this query."
                    )
                    rejected_filters.append({
                        "filter_id": fid,
                        "condition_id": nb["max_condition_id"],
                        "reason": reason,
                        "code": "SCREENER_CONTRADICTORY_CONDITIONS",
                    })
                    issues.append(ConditionValidationIssueDTO(
                        condition_id=nb["max_condition_id"],
                        filter_id=fid,
                        code="SCREENER_CONTRADICTORY_CONDITIONS",
                        severity="error",
                        message=reason,
                    ))
                elif nb["min_val"] == nb["max_val"] and (nb["min_strict"] or nb["max_strict"]):
                    contradictions_detected = True
                    reason = (
                        f"Contradictory conditions on '{fid}': strict inequality on matching boundary ({nb['min_val']}) "
                        f"renders predicate impossible to satisfy."
                    )
                    rejected_filters.append({
                        "filter_id": fid,
                        "condition_id": nb["max_condition_id"] or nb["min_condition_id"],
                        "reason": reason,
                        "code": "SCREENER_CONTRADICTORY_CONDITIONS",
                    })
                    issues.append(ConditionValidationIssueDTO(
                        condition_id=nb["max_condition_id"] or nb["min_condition_id"],
                        filter_id=fid,
                        code="SCREENER_CONTRADICTORY_CONDITIONS",
                        severity="error",
                        message=reason,
                    ))

        # B. Single-valued Enum contradiction detection
        single_valued_fields = {"sector", "industry", "exchange_mic", "listing_country_code", "issuer_country_code"}
        enum_eq_seen: Dict[str, Tuple[str, Optional[str]]] = {}
        for f in accepted_filters:
            if f.filter_id in single_valued_fields and f.operator == FilterOperator.EQ:
                str_val = str(f.value).strip().lower()
                if f.filter_id in enum_eq_seen:
                    prev_val, prev_cid = enum_eq_seen[f.filter_id]
                    if prev_val != str_val:
                        contradictions_detected = True
                        reason = (
                            f"Contradictory equality conditions on single-valued classification '{f.filter_id}': "
                            f"cannot match both '{prev_val}' and '{str_val}' simultaneously."
                        )
                        rejected_filters.append({
                            "filter_id": f.filter_id,
                            "condition_id": f.condition_id,
                            "reason": reason,
                            "code": "SCREENER_CONTRADICTORY_CONDITIONS",
                        })
                        issues.append(ConditionValidationIssueDTO(
                            condition_id=f.condition_id,
                            filter_id=f.filter_id,
                            code="SCREENER_CONTRADICTORY_CONDITIONS",
                            severity="error",
                            message=reason,
                        ))
                else:
                    enum_eq_seen[f.filter_id] = (str_val, f.condition_id)

        # C. Boolean contradiction detection
        bool_eq_seen: Dict[str, Tuple[bool, Optional[str]]] = {}
        for f in accepted_filters:
            f_def = self._repo.get_filter(f.filter_id)
            if f_def and f_def.value_type == ValueType.BOOLEAN and f.operator == FilterOperator.EQ:
                b_val = f.value if isinstance(f.value, bool) else (str(f.value).strip().lower() in ("true", "1", "yes"))
                if f.filter_id in bool_eq_seen:
                    prev_b, prev_cid = bool_eq_seen[f.filter_id]
                    if prev_b != b_val:
                        contradictions_detected = True
                        reason = f"Contradictory boolean conditions on '{f.filter_id}': cannot require both True and False simultaneously."
                        rejected_filters.append({
                            "filter_id": f.filter_id,
                            "condition_id": f.condition_id,
                            "reason": reason,
                            "code": "SCREENER_CONTRADICTORY_CONDITIONS",
                        })
                        issues.append(ConditionValidationIssueDTO(
                            condition_id=f.condition_id,
                            filter_id=f.filter_id,
                            code="SCREENER_CONTRADICTORY_CONDITIONS",
                            severity="error",
                            message=reason,
                        ))
                else:
                    bool_eq_seen[f.filter_id] = (b_val, f.condition_id)

        # Sector applicability warnings
        if request.universe.sectors and "Financial Services" in request.universe.sectors:
            fin_inapplicable = {"gross_margin", "fcf", "net_debt", "ev_to_ebitda", "current_ratio", "quick_ratio"}
            for f in accepted_filters:
                if f.filter_id in fin_inapplicable:
                    warnings.append(f"Metric '{f.filter_id}' is inapplicable to financial institutions and banks and will evaluate to null/missing.")

        # Universe size calculation
        universe_candidates = self._prefilter_universe(request)

        is_valid = len(rejected_filters) == 0 and not contradictions_detected
        return ValidationResponseDTO(
            valid=is_valid,
            accepted_filters=accepted_filters if is_valid else [],
            rejected_filters=rejected_filters,
            issues=issues,
            warnings=warnings,
            contradictions_detected=contradictions_detected,
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

        # Ranking evaluation if requested (Stage 97)
        ranking_eval = None
        ranking_row_map: Dict[UUID, Any] = {}
        ranking_summary = None

        if request.ranking:
            # Build candidate list for ranking based on cohort policy
            ranking_targets = candidates if request.ranking.cohort_policy == "all_eligible_universe" else matching_records
            cand_dicts = [
                {
                    "instrument_entity_id": rec.instrument_entity_id,
                    "ticker": rec.ticker,
                    "canonical_security_name": rec.canonical_security_name,
                    "record": rec,
                }
                for rec in ranking_targets
            ]
            if len(cand_dicts) >= 2:
                def metric_extractor(cand: Dict[str, Any], factor_id: str) -> Optional[float]:
                    rec = cand["record"]
                    val = getattr(rec, factor_id, None)
                    if val is not None:
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return None
                    return None

                ranking_eval = FactorRankingEngine.evaluate(cand_dicts, request.ranking, metric_extractor)
                for r_row in ranking_eval.results:
                    ranking_row_map[r_row.instrument_entity_id] = r_row

                ranking_summary = {
                    "mode": ranking_eval.mode.value,
                    "method": ranking_eval.method.value,
                    "cohort_policy": ranking_eval.cohort_policy,
                    "eligible_count": ranking_eval.eligible_count,
                    "excluded_count": ranking_eval.excluded_count,
                    "methodology_version": ranking_eval.methodology_version,
                }

        # 4. Sorting with deterministic tie-breaker
        sort_criteria = request.multi_sort if request.multi_sort is not None else request.sort
        if not sort_criteria and request.ranking and ranking_row_map:
            # If ranking was computed and no explicit sort provided, sort by rank ascending
            def _rank_sort_key(r: ScreenerObservationRecord):
                r_dto = ranking_row_map.get(r.instrument_entity_id)
                rank_val = r_dto.rank if r_dto else 999999
                return (rank_val, str(r.instrument_entity_id))

            sorted_records = sorted(matching_records, key=_rank_sort_key)
        else:
            sorted_records = self._sort_records(matching_records, sort_criteria)

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
            ranking_row = ranking_row_map.get(r.instrument_entity_id)
            row_dto = self._build_result_row(r, active_columns, ranking_row=ranking_row)
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
            ranking_evaluation_id=ranking_eval.ranking_evaluation_id if ranking_eval else None,
            ranking_summary=ranking_summary,
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

        # Dynamic indicator evaluation if custom parameters provided and bars available
        if crit.parameters and record.historical_bars:
            closes = [Decimal(str(b["close"])) for b in record.historical_bars]
            p = crit.parameters.get("period")
            if p is not None:
                p_int = int(p)
                if field_name.startswith("sma") or field_name == "sma":
                    val = compute_sma(closes, p_int)
                elif field_name.startswith("ema") or field_name == "ema":
                    val = compute_ema(closes, p_int)
                elif field_name.startswith("rsi") or field_name == "rsi":
                    val = compute_rsi(closes, p_int)
                elif field_name.startswith("momentum") or field_name == "momentum":
                    val = compute_momentum(closes, p_int)

        # Strict NULL handling
        if val is None:
            return False

        op = crit.operator
        target = crit.value

        # Boolean handling
        if isinstance(val, bool):
            target_bool = target if isinstance(target, bool) else (str(target).strip().lower() in ("true", "1", "yes"))
            if op == FilterOperator.EQ:
                return val == target_bool
            elif op == FilterOperator.NE:
                return val != target_bool
            return False

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
        Sorts candidates deterministically using an ordered array of typed sort keys.
        Supports up to 5 sort keys, explicit NULLS_LAST or NULLS_FIRST ordering,
        and guarantees stable tie-breaker ordering on (instrument_entity_id, listing_id).
        """
        if not sort_criteria:
            # Default sorting: Market Cap DESC, NULLS LAST
            sort_criteria = [
                SortCriterionDTO(
                    field_id="market_cap",
                    direction=SortDirection.DESC,
                    null_order=SortNullOrder.NULLS_LAST,
                )
            ]

        if len(sort_criteria) > 5:
            raise ScreenerSortLimitExceededError(limit=5)

        # Verify all fields are sortable
        for crit in sort_criteria:
            col_def = self._repo.get_column(crit.field_id)
            if not col_def and not hasattr(ScreenerObservationRecord, crit.field_id):
                raise ScreenerSortUnsupportedError(crit.field_id)

        def _compare_records(r1: ScreenerObservationRecord, r2: ScreenerObservationRecord) -> int:
            for crit in sort_criteria:
                field_id = crit.field_id
                val1 = getattr(r1, field_id, None)
                val2 = getattr(r2, field_id, None)
                is_desc = (crit.direction == SortDirection.DESC)
                null_order = crit.null_order

                # Handle null values
                if val1 is None and val2 is not None:
                    return 1 if null_order == SortNullOrder.NULLS_LAST else -1
                if val1 is not None and val2 is None:
                    return -1 if null_order == SortNullOrder.NULLS_LAST else 1
                if val1 is None and val2 is None:
                    continue

                # Both non-null: compare values
                if isinstance(val1, (Decimal, int, float)) and isinstance(val2, (Decimal, int, float)):
                    d1 = Decimal(str(val1))
                    d2 = Decimal(str(val2))
                    if d1 != d2:
                        if is_desc:
                            return -1 if d1 > d2 else 1
                        else:
                            return -1 if d1 < d2 else 1
                else:
                    s1 = str(val1).lower()
                    s2 = str(val2).lower()
                    if s1 != s2:
                        if is_desc:
                            return -1 if s1 > s2 else 1
                        else:
                            return -1 if s1 < s2 else 1

            # Deterministic final tie-breakers (always ascending)
            id1 = str(r1.instrument_entity_id)
            id2 = str(r2.instrument_entity_id)
            if id1 != id2:
                return -1 if id1 < id2 else 1

            lid1 = str(r1.listing_id)
            lid2 = str(r2.listing_id)
            if lid1 != lid2:
                return -1 if lid1 < lid2 else 1

            return 0

        return sorted(records, key=functools.cmp_to_key(_compare_records))

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
        self,
        record: ScreenerObservationRecord,
        columns: List[ScreenerColumnDefinition],
        ranking_row: Optional[Any] = None,
    ) -> ScreenerResultRowDTO:
        """Assembles a high-density institutional row DTO with cell-level provenance and factor ranking."""
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
            rank=ranking_row.rank if ranking_row else None,
            composite_score=ranking_row.composite_score if ranking_row else None,
            percentile=ranking_row.percentile if ranking_row else None,
            z_score=ranking_row.z_score if ranking_row else None,
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
            if col.data_type == ValueType.BOOLEAN:
                return MetricAvailabilityStatus.AVAILABLE, ("Yes" if raw_val else "No")

            if col.unit_kind == UnitKind.MONETARY:
                d = Decimal(str(raw_val))
                curr = record.trading_currency
                sym = "$" if curr == "USD" else ("₹" if curr == "INR" else ("€" if curr == "EUR" else ("£" if curr == "GBP" else f"{curr} ")))
                if col.column_id == "market_cap" or col.column_id in [
                    "revenue", "net_income", "total_assets", "book_equity", "traded_value_latest",
                    "operating_cash_flow", "capex", "fcf", "total_debt", "net_debt", "ev"
                ]:
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
                    # Last price / Moving Average / ATR
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
