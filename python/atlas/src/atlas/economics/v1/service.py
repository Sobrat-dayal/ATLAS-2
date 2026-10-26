"""Domain Service for Institutional Economics V1 (Stage 89).

Provides macroeconomic overview snapshots, canonical indicator discovery,
source-qualified time-series queries, statistical transformations, point-in-time
vintage awareness, and coverage boundary reporting.
"""

from datetime import date
from typing import List, Optional

from .enums import IndicatorCategory, TransformationType
from .errors import (
    EconomicIndicatorNotFoundError,
    EconomicSeriesNotFoundError,
)
from .repository import EconomicsV1Repository
from .schemas import (
    EconomicCoverageResponseDTO,
    EconomicGeographyDTO,
    EconomicIndicatorDTO,
    EconomicObservationDTO,
    EconomicSeriesDTO,
    EconomicSeriesObservationsResponseDTO,
    EconomicVintageDTO,
    GlobalMacroOverviewResponseDTO,
    MajorEconomyMacroSummaryDTO,
    TransformationDefinitionDTO,
)
from .transformations import SUPPORTED_TRANSFORMATIONS, apply_transformation


class EconomicsV1Service:
    """Core domain service for Economics V1."""

    def __init__(self, repository: Optional[EconomicsV1Repository] = None) -> None:
        self.repository = repository or EconomicsV1Repository()

    def get_overview(
        self, geography_ids: Optional[List[str]] = None
    ) -> GlobalMacroOverviewResponseDTO:
        summaries = self.repository.get_major_economies_summary()
        if geography_ids:
            geo_set = set(geography_ids)
            summaries = [s for s in summaries if s.geography_id in geo_set]

        categories = [c.value for c in IndicatorCategory]
        indicators = self.repository.get_indicators()
        series_list = self.repository.get_series_list()

        return GlobalMacroOverviewResponseDTO(
            major_economies=[MajorEconomyMacroSummaryDTO.model_validate(s) for s in summaries],
            indicator_categories=categories,
            total_indicators=len(indicators),
            total_series=len(series_list),
            freshness_statement="All headline statistics reflect latest official releases with exact reporting periods and statutory source citations.",
        )

    def get_categories(self) -> List[str]:
        return [c.value for c in IndicatorCategory]

    def get_indicators(
        self, category: Optional[str] = None, search: Optional[str] = None
    ) -> List[EconomicIndicatorDTO]:
        cat_enum = None
        if category:
            try:
                cat_enum = IndicatorCategory(category)
            except ValueError:
                cat_enum = None

        indicators = self.repository.get_indicators(category=cat_enum)
        if search:
            q = search.lower().strip()
            indicators = [
                i
                for i in indicators
                if q in i.name.lower() or q in i.code.lower() or q in i.description.lower()
            ]

        return [EconomicIndicatorDTO.model_validate(i) for i in indicators]

    def get_indicator_detail(self, indicator_id: str) -> EconomicIndicatorDTO:
        indicator = self.repository.get_indicator(indicator_id)
        if not indicator:
            raise EconomicIndicatorNotFoundError(indicator_id)
        return EconomicIndicatorDTO.model_validate(indicator)

    def get_series(
        self,
        indicator_id: Optional[str] = None,
        geography_id: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[EconomicSeriesDTO]:
        cat_enum = None
        if category:
            try:
                cat_enum = IndicatorCategory(category)
            except ValueError:
                cat_enum = None

        series_list = self.repository.get_series_list(
            indicator_id=indicator_id,
            geography_id=geography_id,
            category=cat_enum,
        )
        return [EconomicSeriesDTO.model_validate(s) for s in series_list]

    def get_series_detail(self, series_id: str) -> EconomicSeriesDTO:
        series = self.repository.get_series(series_id)
        if not series:
            raise EconomicSeriesNotFoundError(series_id)
        return EconomicSeriesDTO.model_validate(series)

    def get_observations(
        self,
        series_id: str,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None,
        transformation: TransformationType = TransformationType.SOURCE_REPORTED,
        vintage_policy: Optional[str] = None,
        as_of_date: Optional[date] = None,
        limit: int = 100,
        page: int = 1,
    ) -> EconomicSeriesObservationsResponseDTO:
        series = self.repository.get_series(series_id)
        if not series:
            raise EconomicSeriesNotFoundError(series_id)

        raw_observations = self.repository.get_observations(series_id)

        # Apply point-in-time filter if as_of_date specified (no look-ahead leakage)
        if as_of_date:
            raw_observations = [
                obs
                for obs in raw_observations
                if obs.published_at and obs.published_at.date() <= as_of_date
            ]

        # Apply start/end period bounds
        if start_period:
            raw_observations = [obs for obs in raw_observations if obs.period >= start_period]
        if end_period:
            raw_observations = [obs for obs in raw_observations if obs.period <= end_period]

        # Sort ascending by reference_date for transformation math
        raw_observations.sort(key=lambda x: x.reference_date)

        # Apply statistical transformation
        transformed_obs, effective_unit = apply_transformation(
            observations=raw_observations,
            transformation=transformation,
            frequency=series.frequency,
            source_unit=series.unit,
        )

        total_count = len(transformed_obs)
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_obs = transformed_obs[start_idx:end_idx]

        return EconomicSeriesObservationsResponseDTO(
            series=EconomicSeriesDTO.model_validate(series),
            transformation=transformation,
            effective_unit=effective_unit,
            observations=[EconomicObservationDTO.model_validate(o) for o in paginated_obs],
            total_count=total_count,
            page=page,
            limit=limit,
        )

    def get_vintages(self, series_id: str) -> List[EconomicVintageDTO]:
        series = self.repository.get_series(series_id)
        if not series:
            raise EconomicSeriesNotFoundError(series_id)
        vintages = self.repository.get_vintages(series_id)
        return [EconomicVintageDTO.model_validate(v) for v in vintages]

    def get_geographies(self) -> List[EconomicGeographyDTO]:
        geos = self.repository.get_geographies()
        return [EconomicGeographyDTO.model_validate(g) for g in geos]

    def get_coverage(self) -> EconomicCoverageResponseDTO:
        providers = [
            "BEA (U.S. Bureau of Economic Analysis)",
            "BLS (U.S. Bureau of Labor Statistics)",
            "Federal Reserve Board",
            "Eurostat (Statistical Office of the European Union)",
            "European Central Bank (ECB)",
            "NBS (National Bureau of Statistics of China)",
            "People's Bank of China (PBOC)",
            "MoSPI (Ministry of Statistics and Programme Implementation, India)",
            "Reserve Bank of India (RBI)",
            "Statistics Bureau of Japan",
            "Bank of Japan (BOJ)",
            "Cabinet Office of Japan (ESRI)",
            "ONS (Office for National Statistics, United Kingdom)",
            "Bank of England (BOE)",
            "OECD Economic Outlook",
            "World Bank World Development Indicators",
        ]
        geos = [g.name for g in self.repository.get_geographies()]
        cats = [c.value for c in IndicatorCategory]

        return EconomicCoverageResponseDTO(
            supported_providers=providers,
            covered_geographies=geos,
            covered_categories=cats,
            vintage_support_enabled=True,
            coverage_statement="ATLAS Economics V1 provides authoritative macroeconomic series for G6 economies (United States, Euro Area, China, India, Japan, United Kingdom) across core indicators.",
            limitations=[
                "National accounting calendars differ across jurisdictions (e.g. India fiscal year April-March vs calendar year).",
                "CPI definitions reflect country-specific representative consumption baskets and population coverages.",
                "Unemployment rates from labor force surveys (ILO definitions) may differ in survey frequency and collection methodology.",
                "Statistical releases are subject to official revision schedules by government statistical agencies.",
                "Global averages are not artificially synthesized; only verified official multi-country aggregates are reported.",
            ],
        )

    def get_transformations(self) -> List[TransformationDefinitionDTO]:
        return [TransformationDefinitionDTO.model_validate(t) for t in SUPPORTED_TRANSFORMATIONS]
