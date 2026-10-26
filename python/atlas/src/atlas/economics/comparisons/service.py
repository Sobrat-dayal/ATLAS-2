"""Domain Service for Macroeconomic Comparisons & Benchmarking (Stage 93).

Orchestrates cross-country concept compatibility validation, period alignment,
multi-country comparison matrices, rankings, distribution statistics, historical trends,
divergence/convergence analysis, and pairwise correlations.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .enums import (
    ComparisonMetricKind,
    CompatibilityStatus,
    CorrelationMethod,
    PeriodAlignmentPolicy,
    RankingDirection,
    TieBreakerPolicy,
    WeightingPolicy,
)
from .errors import (
    MacroComparisonIndicatorUnavailableError,
    MacroComparisonInsufficientSampleError,
    MacroComparisonPeriodMismatchError,
    MacroComparisonQueryLimitExceededError,
)
from .models import (
    CountryMetricObservation,
)
from .repository import MacroComparisonsRepository
from .schemas import (
    ComparableIndicatorDTO,
    ComparisonEligibilityRecordDTO,
    ComparisonMatrixRequestDTO,
    ComparisonMatrixResponseDTO,
    CorrelationAnalysisRequestDTO,
    CorrelationAnalysisResponseDTO,
    CorrelationResultDTO,
    CountryRankingRowDTO,
    DistributionStatisticsRequestDTO,
    DistributionSummaryDTO,
    DivergenceAnalysisRequestDTO,
    DivergenceAnalysisResponseDTO,
    DivergencePointDTO,
    EconomicRankingsRequestDTO,
    EconomicRankingsResponseDTO,
    GeographicCohortDTO,
    HistoricalTrendPointDTO,
    HistoricalTrendsRequestDTO,
    HistoricalTrendsResponseDTO,
    MacroCoverageSummaryDTO,
    MatrixCellDTO,
)


class MacroComparisonsService:
    """Service handling institutional macroeconomic benchmarking business logic."""

    def __init__(self, repo: Optional[MacroComparisonsRepository] = None):
        self.repo = repo or MacroComparisonsRepository()

    # -------------------------------------------------------------------------
    # Discovery APIs
    # -------------------------------------------------------------------------

    def list_indicators(self) -> List[ComparableIndicatorDTO]:
        return [ComparableIndicatorDTO.model_validate(ind) for ind in self.repo.list_indicators()]

    def list_geographies(self) -> List[Dict[str, str]]:
        return self.repo.list_supported_geographies()

    def list_cohorts(self) -> List[GeographicCohortDTO]:
        return [GeographicCohortDTO.model_validate(c) for c in self.repo.list_cohorts()]

    # -------------------------------------------------------------------------
    # Eligibility & Compatibility Engine
    # -------------------------------------------------------------------------

    def check_eligibility(
        self, geography_id: str, metric_kind: ComparisonMetricKind
    ) -> ComparisonEligibilityRecordDTO:
        """Evaluate if an indicator and country are statistically comparable."""
        try:
            self.repo.get_indicator(metric_kind)
        except MacroComparisonIndicatorUnavailableError:
            return ComparisonEligibilityRecordDTO(
                geography_id=geography_id,
                metric_kind=metric_kind,
                status=CompatibilityStatus.INCOMPATIBLE,
                is_eligible=False,
                reasons=["Metric definition is not recognized in the canonical registry."],
            )

        # Check if country exists
        supported_ids = [g["geography_id"] for g in self.repo.list_supported_geographies()]
        if geography_id not in supported_ids:
            return ComparisonEligibilityRecordDTO(
                geography_id=geography_id,
                metric_kind=metric_kind,
                status=CompatibilityStatus.INCOMPATIBLE,
                is_eligible=False,
                reasons=[f"Geographic Entity '{geography_id}' is not in the sovereign comparison universe."],
            )

        obs = self.repo.get_observation(geography_id, metric_kind)
        if not obs:
            return ComparisonEligibilityRecordDTO(
                geography_id=geography_id,
                metric_kind=metric_kind,
                status=CompatibilityStatus.INSUFFICIENT_METADATA,
                is_eligible=False,
                reasons=["No published observations exist for this country and metric."],
            )

        status = CompatibilityStatus.DIRECTLY_COMPARABLE
        caveats = list(obs.methodology_qualifications)

        if caveats:
            status = CompatibilityStatus.COMPARABLE_WITH_QUALIFICATION

        return ComparisonEligibilityRecordDTO(
            geography_id=geography_id,
            metric_kind=metric_kind,
            status=status,
            is_eligible=True,
            caveats=caveats,
        )

    # -------------------------------------------------------------------------
    # Comparison Matrix
    # -------------------------------------------------------------------------

    def get_comparison_matrix(self, req: ComparisonMatrixRequestDTO) -> ComparisonMatrixResponseDTO:
        """Generate high-density cross-country comparison matrix."""
        geo_ids = req.geography_ids
        if not geo_ids:
            # Default to G20 or all supported
            geo_ids = [g["geography_id"] for g in self.repo.list_supported_geographies()]

        if len(geo_ids) > 25:
            raise MacroComparisonQueryLimitExceededError("geographies", len(geo_ids), 25)

        metrics = req.metric_kinds
        if not metrics:
            # Default to core headline set
            metrics = [
                ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
                ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY,
                ComparisonMetricKind.UNEMPLOYMENT_RATE,
                ComparisonMetricKind.POLICY_INTEREST_RATE,
                ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP,
                ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP,
            ]

        if len(metrics) > 30:
            raise MacroComparisonQueryLimitExceededError("metrics", len(metrics), 30)

        cells: List[MatrixCellDTO] = []
        eligibility_records: List[ComparisonEligibilityRecordDTO] = []

        for gid in geo_ids:
            geo_meta = next(
                (g for g in self.repo.list_supported_geographies() if g["geography_id"] == gid),
                {"name": gid, "iso_code": gid},
            )

            for m in metrics:
                elig = self.check_eligibility(gid, m)
                eligibility_records.append(elig)

                obs: Optional[CountryMetricObservation] = None
                if req.period_policy == PeriodAlignmentPolicy.EXACT_PERIOD and req.target_period:
                    obs = self.repo.get_observation(gid, m, period=req.target_period)
                else:
                    # Latest per country (or latest common)
                    obs = self.repo.get_observation(gid, m)

                if obs:
                    cells.append(
                        MatrixCellDTO(
                            geography_id=gid,
                            country_name=geo_meta["name"],
                            iso_code=geo_meta["iso_code"],
                            metric_kind=m,
                            raw_value=obs.raw_value,
                            formatted_value=obs.formatted_value,
                            unit=obs.unit,
                            reference_period=obs.reference_period,
                            status=elig.status,
                            source_agency=obs.source_agency,
                            caveats=obs.methodology_qualifications,
                        )
                    )
                else:
                    cells.append(
                        MatrixCellDTO(
                            geography_id=gid,
                            country_name=geo_meta["name"],
                            iso_code=geo_meta["iso_code"],
                            metric_kind=m,
                            raw_value=None,
                            formatted_value="—",
                            unit="—",
                            reference_period="—",
                            status=CompatibilityStatus.INSUFFICIENT_METADATA,
                            source_agency="—",
                            caveats=["Data point not available"],
                        )
                    )

        return ComparisonMatrixResponseDTO(
            geography_ids=geo_ids,
            metric_kinds=metrics,
            period_policy=req.period_policy,
            cells=cells,
            eligibility=eligibility_records,
            total_countries=len(geo_ids),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    # -------------------------------------------------------------------------
    # Economic Rankings
    # -------------------------------------------------------------------------

    def calculate_rankings(self, req: EconomicRankingsRequestDTO) -> EconomicRankingsResponseDTO:
        """Compute sovereign rankings for a single compatible metric."""
        metric_def = self.repo.get_indicator(req.metric_kind)

        geo_ids = req.geography_ids
        if req.cohort_id:
            cohort = self.repo.get_cohort(req.cohort_id)
            if cohort:
                geo_ids = cohort.member_geography_ids

        if not geo_ids:
            geo_ids = [g["geography_id"] for g in self.repo.list_supported_geographies()]

        eligible_items: List[Tuple[str, str, str, float, str, str, str]] = []
        excluded_count = 0

        target_period = req.period or "2024"

        for gid in geo_ids:
            obs = self.repo.get_observation(gid, req.metric_kind, period=target_period)
            if not obs and not req.period:
                # Fallback to latest available
                obs = self.repo.get_observation(gid, req.metric_kind)

            if obs and obs.raw_value is not None:
                eligible_items.append(
                    (
                        gid,
                        obs.country_name,
                        obs.iso_code,
                        obs.raw_value,
                        obs.formatted_value,
                        obs.unit,
                        obs.reference_period,
                    )
                )
            else:
                excluded_count += 1

        # Sort based on direction
        reverse_sort = req.direction == RankingDirection.DESCENDING
        eligible_items.sort(key=lambda x: x[3], reverse=reverse_sort)

        ranking_rows: List[CountryRankingRowDTO] = []
        current_rank = 1

        for i, item in enumerate(eligible_items):
            is_tied = False
            if i > 0 and math.isclose(item[3], eligible_items[i - 1][3], rel_tol=1e-5):
                is_tied = True
                if req.tie_policy == TieBreakerPolicy.STANDARD_COMPETITION:
                    # Same rank as previous
                    rank = ranking_rows[-1].rank
                else:
                    # Dense rank
                    rank = ranking_rows[-1].rank
            else:
                if req.tie_policy == TieBreakerPolicy.STANDARD_COMPETITION:
                    rank = i + 1
                else:
                    rank = current_rank
                    current_rank += 1

            ranking_rows.append(
                CountryRankingRowDTO(
                    rank=rank,
                    geography_id=item[0],
                    country_name=item[1],
                    iso_code=item[2],
                    metric_kind=req.metric_kind,
                    raw_value=item[3],
                    formatted_value=item[4],
                    unit=item[5],
                    reference_period=item[6],
                    is_tied=is_tied,
                )
            )

        notes = [
            f"Ranked {len(ranking_rows)} sovereign economies by {metric_def.name}.",
            "Rankings represent numerical ordering only. Higher or lower numerical rank does not imply economic superiority without policy context.",
        ]

        return EconomicRankingsResponseDTO(
            metric_kind=req.metric_kind,
            direction=req.direction,
            reference_period=target_period,
            total_eligible=len(ranking_rows),
            total_excluded=excluded_count,
            rankings=ranking_rows,
            notes=notes,
        )

    # -------------------------------------------------------------------------
    # Statistical Distributions
    # -------------------------------------------------------------------------

    def calculate_distributions(self, req: DistributionStatisticsRequestDTO) -> DistributionSummaryDTO:
        """Calculate mean, median, quartiles, and standard deviation for a cohort."""
        metric_def = self.repo.get_indicator(req.metric_kind)

        geo_ids = req.geography_ids
        if req.cohort_id:
            cohort = self.repo.get_cohort(req.cohort_id)
            if cohort:
                geo_ids = cohort.member_geography_ids

        if not geo_ids:
            geo_ids = [g["geography_id"] for g in self.repo.list_supported_geographies()]

        target_period = req.period or "2024"
        values: List[float] = []
        weights: List[float] = []
        excluded_ids: List[str] = []

        for gid in geo_ids:
            obs = self.repo.get_observation(gid, req.metric_kind, period=target_period)
            if not obs and not req.period:
                obs = self.repo.get_observation(gid, req.metric_kind)

            if obs and obs.raw_value is not None:
                values.append(obs.raw_value)
                # Resolve weight if requested
                if req.weighting_policy == WeightingPolicy.POPULATION_WEIGHT:
                    pop_obs = self.repo.get_observation(gid, ComparisonMetricKind.POPULATION_MILLIONS)
                    weights.append(pop_obs.raw_value if pop_obs else 1.0)
                elif req.weighting_policy == WeightingPolicy.GDP_WEIGHT:
                    gdp_obs = self.repo.get_observation(gid, ComparisonMetricKind.GDP_NOMINAL_USD)
                    weights.append(gdp_obs.raw_value if gdp_obs else 1.0)
                else:
                    weights.append(1.0)
            else:
                excluded_ids.append(gid)

        n = len(values)
        if n < 2:
            raise MacroComparisonInsufficientSampleError("distribution analysis", n, 2)

        # Sort values for quantile analysis
        sorted_vals = sorted(values)

        # Weighted Mean
        total_weight = sum(weights)
        if total_weight > 0:
            mean_val = sum(v * w for v, w in zip(values, weights)) / total_weight
        else:
            mean_val = sum(values) / n

        # Median
        if n % 2 == 1:
            median_val = sorted_vals[n // 2]
        else:
            median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        min_val = sorted_vals[0]
        max_val = sorted_vals[-1]

        # Quartiles (Q1 = 25th percentile, Q3 = 75th percentile)
        def _percentile(data: List[float], p: float) -> float:
            k = (len(data) - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return data[int(k)]
            return data[f] * (c - k) + data[c] * (k - f)

        q1_val = _percentile(sorted_vals, 0.25)
        q3_val = _percentile(sorted_vals, 0.75)

        # Sample Standard Deviation (Bessel-corrected N-1)
        unweighted_mean = sum(values) / n
        variance = sum((x - unweighted_mean) ** 2 for x in values) / (n - 1)
        std_dev = math.sqrt(variance)

        return DistributionSummaryDTO(
            metric_kind=req.metric_kind,
            reference_period=target_period,
            sample_size=n,
            total_eligible_geographies=len(geo_ids),
            mean=round(mean_val, 4),
            median=round(median_val, 4),
            minimum=round(min_val, 4),
            maximum=round(max_val, 4),
            q1=round(q1_val, 4),
            q3=round(q3_val, 4),
            standard_deviation=round(std_dev, 4),
            weighting_policy=req.weighting_policy,
            unit=metric_def.default_unit,
            excluded_geography_ids=excluded_ids,
        )

    # -------------------------------------------------------------------------
    # Historical Trends & Normalization
    # -------------------------------------------------------------------------

    def get_historical_trends(self, req: HistoricalTrendsRequestDTO) -> HistoricalTrendsResponseDTO:
        """Fetch time-aligned multi-country time series with optional base rebasing."""
        geo_ids = req.geography_ids
        if not geo_ids:
            geo_ids = ["geo-us", "geo-ea", "geo-cn"]

        points: List[HistoricalTrendPointDTO] = []
        period_sets: List[set] = []

        base_values: Dict[str, float] = {}

        for gid in geo_ids:
            geo_meta = next(
                (g for g in self.repo.list_supported_geographies() if g["geography_id"] == gid),
                {"name": gid, "iso_code": gid},
            )
            series = self.repo.get_historical_series(gid, req.metric_kind)
            current_periods = set()

            for obs in series:
                # Filter by start/end if provided
                if req.start_period and obs.reference_period < req.start_period:
                    continue
                if req.end_period and obs.reference_period > req.end_period:
                    continue

                current_periods.add(obs.reference_period)

                if req.base_period and obs.reference_period == req.base_period:
                    base_values[gid] = obs.raw_value

            period_sets.append(current_periods)

        # Intersection of common periods across all selected countries
        common_periods = sorted(list(set.intersection(*period_sets))) if period_sets else []

        for gid in geo_ids:
            geo_meta = next(
                (g for g in self.repo.list_supported_geographies() if g["geography_id"] == gid),
                {"name": gid, "iso_code": gid},
            )
            series = self.repo.get_historical_series(gid, req.metric_kind)

            base_val = base_values.get(gid)

            for obs in series:
                if req.start_period and obs.reference_period < req.start_period:
                    continue
                if req.end_period and obs.reference_period > req.end_period:
                    continue

                indexed_val: Optional[float] = None
                if req.base_period and base_val is not None and not math.isclose(base_val, 0.0):
                    indexed_val = round((obs.raw_value / base_val) * 100.0, 2)

                points.append(
                    HistoricalTrendPointDTO(
                        geography_id=gid,
                        country_name=geo_meta["name"],
                        reference_period=obs.reference_period,
                        raw_value=obs.raw_value,
                        indexed_value=indexed_val,
                    )
                )

        return HistoricalTrendsResponseDTO(
            metric_kind=req.metric_kind,
            geography_ids=geo_ids,
            base_period=req.base_period,
            points=points,
            common_periods=common_periods,
        )

    # -------------------------------------------------------------------------
    # Pairwise Divergence / Convergence
    # -------------------------------------------------------------------------

    def calculate_divergence(self, req: DivergenceAnalysisRequestDTO) -> DivergenceAnalysisResponseDTO:
        """Calculate historical differential and ratios between two sovereign series."""
        metric_def = self.repo.get_indicator(req.metric_kind)

        series_a = self.repo.get_historical_series(req.geography_a_id, req.metric_kind)
        series_b = self.repo.get_historical_series(req.geography_b_id, req.metric_kind)

        dict_a = {obs.reference_period: obs.raw_value for obs in series_a}
        dict_b = {obs.reference_period: obs.raw_value for obs in series_b}

        common_periods = sorted(list(set(dict_a.keys()) & set(dict_b.keys())))
        if not common_periods:
            raise MacroComparisonPeriodMismatchError("Common history", [req.geography_a_id, req.geography_b_id])

        points: List[DivergencePointDTO] = []

        for p in common_periods:
            if req.start_period and p < req.start_period:
                continue
            if req.end_period and p > req.end_period:
                continue

            val_a = dict_a[p]
            val_b = dict_b[p]
            diff = round(val_a - val_b, 4)
            ratio = round(val_a / val_b, 4) if not math.isclose(val_b, 0.0) else None

            points.append(
                DivergencePointDTO(
                    reference_period=p,
                    country_a_value=val_a,
                    country_b_value=val_b,
                    differential_value=diff,
                    unit=metric_def.default_unit,
                    ratio=ratio,
                )
            )

        geo_a_info = next(
            (g for g in self.repo.list_supported_geographies() if g["geography_id"] == req.geography_a_id),
            {"name": req.geography_a_id},
        )
        geo_b_info = next(
            (g for g in self.repo.list_supported_geographies() if g["geography_id"] == req.geography_b_id),
            {"name": req.geography_b_id},
        )

        latest_diff = points[-1].differential_value if points else 0.0

        return DivergenceAnalysisResponseDTO(
            metric_kind=req.metric_kind,
            geography_a_id=req.geography_a_id,
            country_a_name=geo_a_info["name"],
            geography_b_id=req.geography_b_id,
            country_b_name=geo_b_info["name"],
            points=points,
            latest_differential=latest_diff,
            unit=metric_def.default_unit,
        )

    # -------------------------------------------------------------------------
    # Correlation Analysis
    # -------------------------------------------------------------------------

    def calculate_correlations(self, req: CorrelationAnalysisRequestDTO) -> CorrelationAnalysisResponseDTO:
        """Compute pairwise Pearson or Spearman correlation over matching dates."""
        results: List[CorrelationResultDTO] = []

        for pair in req.series_pairs:
            geo_a = pair.get("geo_a", "")
            metric_a_str = pair.get("metric_a", "")
            geo_b = pair.get("geo_b", "")
            metric_b_str = pair.get("metric_b", "")

            try:
                metric_a = ComparisonMetricKind(metric_a_str)
                metric_b = ComparisonMetricKind(metric_b_str)
            except ValueError:
                continue

            series_a = self.repo.get_historical_series(geo_a, metric_a)
            series_b = self.repo.get_historical_series(geo_b, metric_b)

            dict_a = {obs.reference_period: obs.raw_value for obs in series_a}
            dict_b = {obs.reference_period: obs.raw_value for obs in series_b}

            common_periods = sorted(list(set(dict_a.keys()) & set(dict_b.keys())))
            n = len(common_periods)

            geo_a_info = next(
                (g for g in self.repo.list_supported_geographies() if g["geography_id"] == geo_a),
                {"name": geo_a},
            )
            geo_b_info = next(
                (g for g in self.repo.list_supported_geographies() if g["geography_id"] == geo_b),
                {"name": geo_b},
            )

            warnings: List[str] = [
                "Correlation does not establish economic causality.",
                "Non-stationary macroeconomic level series may exhibit spurious correlation.",
            ]

            if n < 4:
                results.append(
                    CorrelationResultDTO(
                        metric_a=metric_a,
                        geography_a_id=geo_a,
                        country_a_name=geo_a_info["name"],
                        metric_b=metric_b,
                        geography_b_id=geo_b,
                        country_b_name=geo_b_info["name"],
                        method=req.method,
                        sample_size=n,
                        coefficient=0.0,
                        is_valid=False,
                        warnings=warnings + [f"Insufficient paired sample size: {n} (minimum 4 required)."],
                    )
                )
                continue

            x = [dict_a[p] for p in common_periods]
            y = [dict_b[p] for p in common_periods]

            # Zero variance guard
            var_x = sum((val - (sum(x) / n)) ** 2 for val in x)
            var_y = sum((val - (sum(y) / n)) ** 2 for val in y)

            if math.isclose(var_x, 0.0) or math.isclose(var_y, 0.0):
                results.append(
                    CorrelationResultDTO(
                        metric_a=metric_a,
                        geography_a_id=geo_a,
                        country_a_name=geo_a_info["name"],
                        metric_b=metric_b,
                        geography_b_id=geo_b,
                        country_b_name=geo_b_info["name"],
                        method=req.method,
                        sample_size=n,
                        coefficient=0.0,
                        is_valid=False,
                        warnings=warnings + ["One or both series has zero variance (constant values)."],
                    )
                )
                continue

            if req.method == CorrelationMethod.SPEARMAN:
                # Rank transform
                def _rank(arr: List[float]) -> List[float]:
                    sorted_indices = sorted(range(len(arr)), key=lambda k: arr[k])
                    ranks = [0.0] * len(arr)
                    for r, idx in enumerate(sorted_indices):
                        ranks[idx] = float(r + 1)
                    return ranks

                rx = _rank(x)
                ry = _rank(y)
                mean_rx = sum(rx) / n
                mean_ry = sum(ry) / n
                num = sum((a - mean_rx) * (b - mean_ry) for a, b in zip(rx, ry))
                den = math.sqrt(sum((a - mean_rx) ** 2 for a in rx) * sum((b - mean_ry) ** 2 for b in ry))
                coeff = round(num / den, 4) if den > 0 else 0.0
            else:
                # Pearson
                mean_x = sum(x) / n
                mean_y = sum(y) / n
                num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
                den = math.sqrt(var_x * var_y)
                coeff = round(num / den, 4) if den > 0 else 0.0

            results.append(
                CorrelationResultDTO(
                    metric_a=metric_a,
                    geography_a_id=geo_a,
                    country_a_name=geo_a_info["name"],
                    metric_b=metric_b,
                    geography_b_id=geo_b,
                    country_b_name=geo_b_info["name"],
                    method=req.method,
                    sample_size=n,
                    coefficient=coeff,
                    is_valid=True,
                    warnings=warnings,
                )
            )

        return CorrelationAnalysisResponseDTO(results=results)

    # -------------------------------------------------------------------------
    # Coverage
    # -------------------------------------------------------------------------

    def get_coverage_summary(self) -> MacroCoverageSummaryDTO:
        supported_geos = [g["name"] for g in self.repo.list_supported_geographies()]
        supported_metrics = [m.metric_kind.value for m in self.repo.list_indicators()]
        cohorts = [c.name for c in self.repo.list_cohorts()]

        total_obs = sum(len(series) for series in self.repo._historical_series.values())

        return MacroCoverageSummaryDTO(
            supported_geographies=supported_geos,
            supported_metrics=supported_metrics,
            cohorts=cohorts,
            total_observations_count=total_obs,
            harmonized_sources=[
                "U.S. Bureau of Economic Analysis (BEA)",
                "U.S. Bureau of Labor Statistics (BLS)",
                "Eurostat (HICP, ESA 2010)",
                "UK Office for National Statistics (ONS)",
                "Statistics Bureau of Japan",
                "MoSPI (Ministry of Statistics, India)",
                "National Bureau of Statistics (China)",
                "World Bank / IMF International Comparison Program (ICP)",
                "IMF Government Finance Statistics (GFS)",
            ],
            methodology_qualifications=[
                "GDP market exchange rates vs purchasing power parity (PPP) international dollars are kept strictly distinct.",
                "Euro Area statistics represent the unified monetary union and must not be naively summed with member countries to avoid double counting.",
                "Policy rate differentials are measured in basis points against operational targets or midpoints.",
                "Inflation indices adhere to national official baskets; Euro Area uses the Harmonised Index of Consumer Prices (HICP).",
            ],
        )
