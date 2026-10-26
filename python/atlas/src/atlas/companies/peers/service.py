"""Domain Service Layer for Company Peers and Comparable Company Analysis (Stage 87)."""

from typing import Dict, List, Optional

from .calculator import calculate_peer_statistics
from .enums import (
    ComparisonMetricCategory,
    MetricObservationStatus,
    PeerRelationshipType,
)
from .errors import (
    PeerCompanyNotFoundError,
)
from .models import ComparableMetricObservation
from .repository import CompanyPeersRepository
from .schemas import (
    CandidatesResponseDTO,
    CompanyPeerCandidateDTO,
    ComparableObservationDTO,
    CreatePeerGroupRequestDTO,
    HistoricalComparisonRequestDTO,
    HistoricalComparisonResponseDTO,
    HistoricalDataPointDTO,
    HistoricalPeerTrendSeriesDTO,
    IndustryClassificationDTO,
    MetricCatalogResponseDTO,
    PeerBenchmarkStatisticsDTO,
    PeerCompanySummaryDTO,
    PeerComparisonRequestDTO,
    PeerComparisonResponseDTO,
    PeerMethodologyResponseDTO,
    PeerMetricDefinitionDTO,
    PeersOverviewResponseDTO,
    UpdatePeerGroupRequestDTO,
    UserPeerGroupDTO,
)


class CompanyPeersService:
    """Service orchestrating candidate discovery, user peer groups, financial comparison, and statistics."""

    def __init__(self, repository: Optional[CompanyPeersRepository] = None):
        self.repository = repository or CompanyPeersRepository()

        # Catalog of standard supported comparison metrics
        self._metric_catalog: List[PeerMetricDefinitionDTO] = [
            # Scale
            PeerMetricDefinitionDTO(
                metric_id="scale.revenue",
                name="Total Revenue",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Total Operating Revenue",
                description="Total revenue reported on the income statement for the fiscal period.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.gross_profit",
                name="Gross Profit",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Revenue - Cost of Revenue",
                description="Gross income generated before operating expenses.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.operating_income",
                name="Operating Income (EBIT)",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Gross Profit - Operating Expenses",
                description="Earnings before interest and tax generated from core business operations.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.net_income",
                name="Net Income",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Income Before Tax - Income Tax Expense",
                description="Bottom-line accounting net profit attributable to ordinary shareholders.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.total_assets",
                name="Total Assets",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Total Current Assets + Total Non-Current Assets",
                description="Total economic resources controlled by the company at period end.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.total_debt",
                name="Total Debt",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Short-Term Debt + Long-Term Debt",
                description="Total contractual debt obligations on the balance sheet.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.total_equity",
                name="Total Equity",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Total Assets - Total Liabilities",
                description="Book value of total shareholders' equity.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.market_cap",
                name="Market Capitalization",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Share Price × Total Diluted Shares Outstanding",
                description="Total equity market valuation as of the valuation observation timestamp.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="scale.enterprise_value",
                name="Enterprise Value (EV)",
                category=ComparisonMetricCategory.SCALE,
                unit="$",
                formula_display="Market Cap + Total Debt - Cash & Cash Equivalents",
                description="Theoretical takeover cost of the core operating business.",
            ),
            # Growth
            PeerMetricDefinitionDTO(
                metric_id="growth.revenue_growth",
                name="Revenue Growth YoY",
                category=ComparisonMetricCategory.GROWTH,
                unit="%",
                formula_display="(Revenue_t - Revenue_{t-1}) / |Revenue_{t-1}| × 100",
                description="Year-over-year revenue expansion rate.",
            ),
            # Profitability
            PeerMetricDefinitionDTO(
                metric_id="profitability.gross_margin",
                name="Gross Margin",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="Gross Profit / Revenue × 100",
                description="Gross profit as a percentage of total revenue.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="profitability.operating_margin",
                name="Operating Margin",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="Operating Income (EBIT) / Revenue × 100",
                description="Operating profitability margin generated from revenue.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="profitability.ebitda_margin",
                name="EBITDA Margin",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="EBITDA / Revenue × 100",
                description="Cash earnings before interest, tax, depreciation, and amortization relative to revenue.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="profitability.net_margin",
                name="Net Margin",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="Net Income / Revenue × 100",
                description="Net profit conversion efficiency per dollar of revenue.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="profitability.roe",
                name="Return on Equity (ROE)",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="Net Income / Average Shareholders' Equity × 100",
                description="Net earnings generated relative to book equity capital.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="profitability.roa",
                name="Return on Assets (ROA)",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="Net Income / Average Total Assets × 100",
                description="Operational efficiency at deploying total company assets.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="profitability.roic",
                name="Return on Invested Capital (ROIC)",
                category=ComparisonMetricCategory.PROFITABILITY,
                unit="%",
                formula_display="NOPAT / Invested Capital × 100",
                description="Net operating profit after tax relative to total invested debt and equity capital.",
            ),
            # Liquidity & Solvency
            PeerMetricDefinitionDTO(
                metric_id="liquidity.current_ratio",
                name="Current Ratio",
                category=ComparisonMetricCategory.LIQUIDITY,
                unit="x",
                formula_display="Current Assets / Current Liabilities",
                description="Coverage of short-term liabilities with liquid current assets.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="solvency.debt_to_equity",
                name="Debt-to-Equity (D/E)",
                category=ComparisonMetricCategory.SOLVENCY,
                unit="x",
                formula_display="Total Debt / Total Shareholders' Equity",
                description="Financial leverage ratio of debt obligations relative to book equity.",
            ),
            # Valuation
            PeerMetricDefinitionDTO(
                metric_id="valuation.pe",
                name="Price-to-Earnings (P/E)",
                category=ComparisonMetricCategory.VALUATION,
                unit="x",
                formula_display="Market Capitalization / Net Income",
                description="Trailing twelve months price to earnings multiple.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="valuation.forward_pe",
                name="Forward P/E",
                category=ComparisonMetricCategory.VALUATION,
                unit="x",
                formula_display="Market Price / Forward Consensus EPS",
                description="Market multiple relative to consensus forward earnings expectations.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="valuation.pb",
                name="Price-to-Book (P/B)",
                category=ComparisonMetricCategory.VALUATION,
                unit="x",
                formula_display="Market Capitalization / Total Equity",
                description="Market capitalization multiple relative to net balance sheet book value.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="valuation.ps",
                name="Price-to-Sales (P/S)",
                category=ComparisonMetricCategory.VALUATION,
                unit="x",
                formula_display="Market Capitalization / Total Revenue",
                description="Equity market multiple relative to total annual revenue.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="valuation.ev_to_ebitda",
                name="EV / EBITDA",
                category=ComparisonMetricCategory.VALUATION,
                unit="x",
                formula_display="Enterprise Value / EBITDA",
                description="Capital structure-neutral operating enterprise valuation multiple.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="valuation.ev_to_revenue",
                name="EV / Revenue",
                category=ComparisonMetricCategory.VALUATION,
                unit="x",
                formula_display="Enterprise Value / Total Revenue",
                description="Total enterprise multiple relative to sales scale.",
            ),
            PeerMetricDefinitionDTO(
                metric_id="cashflow.free_cash_flow_yield",
                name="Free Cash Flow Yield",
                category=ComparisonMetricCategory.CASH_FLOW,
                unit="%",
                formula_display="Free Cash Flow / Market Capitalization × 100",
                description="Free cash flow generation yield relative to total equity market cap.",
            ),
        ]

    # -------------------------------------------------------------------------
    # Overview & Candidate Discovery
    # -------------------------------------------------------------------------

    def get_overview(self, company_id: str, user_id: str) -> PeersOverviewResponseDTO:
        """Constructs top-level overview response for the company peers workspace."""
        company = self.repository.get_company(company_id)
        if not company:
            raise PeerCompanyNotFoundError(company_id)

        c_class = company["classification"]
        class_dto = IndustryClassificationDTO(
            taxonomy=c_class.taxonomy,
            sector=c_class.sector,
            industry_group=c_class.industry_group,
            industry=c_class.industry,
            sub_industry=c_class.sub_industry,
            code=c_class.code,
            taxonomy_version=c_class.taxonomy_version,
        )

        # Get default peer group if present
        user_groups = self.repository.get_peer_groups_for_company(company_id, user_id)
        def_group = user_groups[0] if user_groups else None
        def_group_dto = (
            UserPeerGroupDTO(
                id=def_group.id,
                owner_user_id=def_group.owner_user_id,
                subject_company_id=def_group.subject_company_id,
                name=def_group.name,
                description=def_group.description,
                peer_company_ids=def_group.peer_company_ids,
                created_at=def_group.created_at,
                updated_at=def_group.updated_at,
                revision=def_group.revision,
            )
            if def_group
            else None
        )

        candidates = self.repository.get_candidates_for_company(company_id, limit=20)

        # Pull key highlights from observations
        pe_obs = self.repository.get_observation(company_id, "valuation.pe", "FY2024")
        om_obs = self.repository.get_observation(
            company_id, "profitability.operating_margin", "FY2024"
        )
        rg_obs = self.repository.get_observation(company_id, "growth.revenue_growth", "FY2024")

        highlights = {
            "subject_ticker": company["ticker"],
            "subject_market_cap": company.get("formatted_market_cap", "N/A"),
            "subject_pe": pe_obs.formatted_value if pe_obs else "N/A",
            "subject_operating_margin": om_obs.formatted_value if om_obs else "N/A",
            "subject_revenue_growth": rg_obs.formatted_value if rg_obs else "N/A",
        }

        return PeersOverviewResponseDTO(
            subject_company_id=company_id,
            subject_company_name=company["display_name"],
            classification=class_dto,
            default_peer_group=def_group_dto,
            total_candidates=len(candidates),
            available_metrics_count=len(self._metric_catalog),
            key_highlights=highlights,
        )

    def get_candidates(
        self,
        company_id: str,
        limit: int = 20,
        competitors_only: bool = False,
    ) -> CandidatesResponseDTO:
        """Retrieves verified comparable candidates with selection rationale."""
        candidates = self.repository.get_candidates_for_company(
            company_id=company_id, limit=limit, competitors_only=competitors_only
        )

        items = [
            CompanyPeerCandidateDTO(
                candidate_company_id=c.candidate_company_id,
                ticker=c.ticker,
                display_name=c.display_name,
                relationship_type=c.relationship_type,
                classification=IndustryClassificationDTO(
                    taxonomy=c.classification.taxonomy,
                    sector=c.classification.sector,
                    industry_group=c.classification.industry_group,
                    industry=c.classification.industry,
                    sub_industry=c.classification.sub_industry,
                    code=c.classification.code,
                    taxonomy_version=c.classification.taxonomy_version,
                ),
                headquarters_country=c.headquarters_country,
                market_cap=c.market_cap,
                formatted_market_cap=c.formatted_market_cap,
                revenue=c.revenue,
                formatted_revenue=c.formatted_revenue,
                relevance_score=c.relevance_score,
                selection_reasons=c.selection_reasons,
                is_competitor=c.is_competitor,
            )
            for c in candidates
        ]

        return CandidatesResponseDTO(
            subject_company_id=company_id,
            total_candidates=len(items),
            items=items,
        )

    def get_available_metrics(self) -> MetricCatalogResponseDTO:
        """Returns the complete catalog of comparable financial and valuation metrics."""
        return MetricCatalogResponseDTO(
            total_metrics=len(self._metric_catalog),
            items=self._metric_catalog,
        )

    # -------------------------------------------------------------------------
    # Peer Comparison Calculation Service
    # -------------------------------------------------------------------------

    def compare_peers(
        self,
        company_id: str,
        user_id: str,
        request: PeerComparisonRequestDTO,
    ) -> PeerComparisonResponseDTO:
        """Executes batched multi-company comparable financial and valuation analysis."""
        subject_info = self.repository.get_company(company_id)
        if not subject_info:
            raise PeerCompanyNotFoundError(company_id)

        # 1. Resolve peer company IDs
        if request.peer_company_ids:
            peer_ids = list(request.peer_company_ids)
        elif request.peer_group_id:
            group = self.repository.get_peer_group(request.peer_group_id, user_id)
            peer_ids = list(group.peer_company_ids)
        else:
            # Fallback to default peer group
            def_groups = self.repository.get_peer_groups_for_company(company_id, user_id)
            if def_groups:
                peer_ids = list(def_groups[0].peer_company_ids)
            else:
                candidates = self.repository.get_candidates_for_company(company_id, limit=5)
                peer_ids = [c.candidate_company_id for c in candidates]

        # Filter out self if accidentally provided
        peer_ids = [pid for pid in peer_ids if pid != company_id]

        # 2. Resolve companies
        all_company_ids = [company_id] + peer_ids
        company_summaries: List[PeerCompanySummaryDTO] = []
        for cid in all_company_ids:
            c_data = self.repository.get_company(cid)
            if c_data:
                c_class = c_data["classification"]
                company_summaries.append(
                    PeerCompanySummaryDTO(
                        company_id=cid,
                        ticker=c_data["ticker"],
                        display_name=c_data["display_name"],
                        relationship_type=c_data.get(
                            "relationship_type", PeerRelationshipType.COMPARABLE_CANDIDATE
                        ),
                        sector=c_class.sector,
                        industry=c_class.industry or c_class.sector,
                        country=c_data["headquarters_country"],
                        is_subject=(cid == company_id),
                    )
                )

        # 3. Resolve metric IDs
        metric_ids = request.metric_ids or [m.metric_id for m in self._metric_catalog]
        fiscal_period = request.fiscal_period or "FY2024"

        observations_matrix: Dict[str, Dict[str, ComparableObservationDTO]] = {}
        statistics_map: Dict[str, PeerBenchmarkStatisticsDTO] = {}

        for m_id in metric_ids:
            m_def = next((m for m in self._metric_catalog if m.metric_id == m_id), None)
            if not m_def:
                continue

            observations_matrix[m_id] = {}
            raw_obs_list: List[ComparableMetricObservation] = []

            for cid in all_company_ids:
                obs = self.repository.get_observation(cid, m_id, fiscal_period)
                c_info = self.repository.get_company(cid)
                c_name = c_info["display_name"] if c_info else "Unknown"
                ticker = c_info["ticker"] if c_info else "UNK"

                if not obs:
                    obs = ComparableMetricObservation(
                        company_id=cid,
                        company_name=c_name,
                        ticker=ticker,
                        metric_id=m_id,
                        metric_name=m_def.name,
                        category=m_def.category,
                        exact_value=None,
                        formatted_value="—",
                        unit=m_def.unit,
                        period_id=fiscal_period,
                        period_end="—",
                        status=MetricObservationStatus.MISSING,
                        is_subject=(cid == company_id),
                        explanation="No observation cataloged for this fiscal period",
                    )

                raw_obs_list.append(obs)
                observations_matrix[m_id][cid] = ComparableObservationDTO(
                    company_id=cid,
                    company_name=c_name,
                    ticker=ticker,
                    metric_id=m_id,
                    metric_name=m_def.name,
                    category=m_def.category,
                    exact_value=obs.exact_value,
                    formatted_value=obs.formatted_value,
                    unit=obs.unit,
                    currency=obs.currency,
                    period_id=obs.period_id,
                    period_end=obs.period_end,
                    status=obs.status,
                    is_subject=obs.is_subject,
                    source_filing_ref=obs.source_filing_ref,
                    explanation=obs.explanation,
                )

            # Compute statistics across eligible observations
            stats = calculate_peer_statistics(
                observations=raw_obs_list,
                subject_id=company_id,
                outlier_policy=request.outlier_policy,
                subject_policy=request.subject_inclusion_policy,
            )

            statistics_map[m_id] = PeerBenchmarkStatisticsDTO(
                metric_id=stats.metric_id,
                metric_name=stats.metric_name,
                category=stats.category,
                unit=stats.unit,
                mean=stats.mean,
                median=stats.median,
                min_value=stats.min_value,
                max_value=stats.max_value,
                sample_count=stats.sample_count,
                total_count=stats.total_count,
                coverage_ratio=stats.coverage_ratio,
                subject_value=stats.subject_value,
                subject_diff_vs_median_pct=stats.subject_diff_vs_median_pct,
                subject_diff_vs_median_pp=stats.subject_diff_vs_median_pp,
                subject_percentile=stats.subject_percentile,
                outliers_detected=stats.outliers_detected,
            )

        return PeerComparisonResponseDTO(
            subject_company_id=company_id,
            subject_company_name=subject_info["display_name"],
            period_alignment_mode=request.period_alignment_mode,
            fiscal_period=fiscal_period,
            companies=company_summaries,
            observations=observations_matrix,
            statistics=statistics_map,
        )

    def compare_history(
        self,
        company_id: str,
        user_id: str,
        request: HistoricalComparisonRequestDTO,
    ) -> HistoricalComparisonResponseDTO:
        """Builds multi-period time-series trend data for subject and peers."""
        subject_info = self.repository.get_company(company_id)
        if not subject_info:
            raise PeerCompanyNotFoundError(company_id)

        # 1. Resolve peer company IDs
        if request.peer_company_ids:
            peer_ids = list(request.peer_company_ids)
        elif request.peer_group_id:
            group = self.repository.get_peer_group(request.peer_group_id, user_id)
            peer_ids = list(group.peer_company_ids)
        else:
            def_groups = self.repository.get_peer_groups_for_company(company_id, user_id)
            peer_ids = list(def_groups[0].peer_company_ids) if def_groups else []

        all_company_ids = [company_id] + [p for p in peer_ids if p != company_id]
        series_list: List[HistoricalPeerTrendSeriesDTO] = []

        for m_id in request.metric_ids:
            m_def = next((m for m in self._metric_catalog if m.metric_id == m_id), None)
            m_name = m_def.name if m_def else m_id

            for cid in all_company_ids:
                c_data = self.repository.get_company(cid)
                if not c_data:
                    continue

                raw_points = self.repository.get_historical_series(cid, m_id)
                points_dto = [
                    HistoricalDataPointDTO(
                        period_id=p.period_id,
                        period_end=p.period_end,
                        fiscal_year=p.fiscal_year,
                        fiscal_quarter=p.fiscal_quarter,
                        value=p.value,
                        formatted_value=p.formatted_value,
                    )
                    for p in raw_points[: request.max_periods]
                ]

                series_list.append(
                    HistoricalPeerTrendSeriesDTO(
                        metric_id=m_id,
                        metric_name=m_name,
                        company_id=cid,
                        company_name=c_data["display_name"],
                        ticker=c_data["ticker"],
                        is_subject=(cid == company_id),
                        points=points_dto,
                    )
                )

        return HistoricalComparisonResponseDTO(
            subject_company_id=company_id,
            series=series_list,
        )

    # -------------------------------------------------------------------------
    # Peer Group CRUD Operations
    # -------------------------------------------------------------------------

    def get_user_peer_groups(self, company_id: str, user_id: str) -> List[UserPeerGroupDTO]:
        """Lists user-owned and system default peer groups for the subject company."""
        groups = self.repository.get_peer_groups_for_company(company_id, user_id)
        return [
            UserPeerGroupDTO(
                id=g.id,
                owner_user_id=g.owner_user_id,
                subject_company_id=g.subject_company_id,
                name=g.name,
                description=g.description,
                peer_company_ids=g.peer_company_ids,
                created_at=g.created_at,
                updated_at=g.updated_at,
                revision=g.revision,
            )
            for g in groups
        ]

    def get_peer_group(self, group_id: str, user_id: str) -> UserPeerGroupDTO:
        """Retrieves a single peer group verifying ownership."""
        g = self.repository.get_peer_group(group_id, user_id)
        return UserPeerGroupDTO(
            id=g.id,
            owner_user_id=g.owner_user_id,
            subject_company_id=g.subject_company_id,
            name=g.name,
            description=g.description,
            peer_company_ids=g.peer_company_ids,
            created_at=g.created_at,
            updated_at=g.updated_at,
            revision=g.revision,
        )

    def create_peer_group(
        self,
        company_id: str,
        user_id: str,
        request: CreatePeerGroupRequestDTO,
    ) -> UserPeerGroupDTO:
        """Creates a new private user peer group."""
        g = self.repository.create_peer_group(
            owner_user_id=user_id,
            subject_company_id=company_id,
            name=request.name,
            description=request.description,
            peer_company_ids=request.peer_company_ids,
        )
        return UserPeerGroupDTO(
            id=g.id,
            owner_user_id=g.owner_user_id,
            subject_company_id=g.subject_company_id,
            name=g.name,
            description=g.description,
            peer_company_ids=g.peer_company_ids,
            created_at=g.created_at,
            updated_at=g.updated_at,
            revision=g.revision,
        )

    def update_peer_group(
        self,
        group_id: str,
        user_id: str,
        request: UpdatePeerGroupRequestDTO,
    ) -> UserPeerGroupDTO:
        """Updates name, description, or peer membership with revision checking."""
        g = self.repository.update_peer_group(
            group_id=group_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            peer_company_ids=request.peer_company_ids,
            expected_revision=request.expected_revision,
        )
        return UserPeerGroupDTO(
            id=g.id,
            owner_user_id=g.owner_user_id,
            subject_company_id=g.subject_company_id,
            name=g.name,
            description=g.description,
            peer_company_ids=g.peer_company_ids,
            created_at=g.created_at,
            updated_at=g.updated_at,
            revision=g.revision,
        )

    def delete_peer_group(self, group_id: str, user_id: str) -> None:
        """Deletes an authorized peer group."""
        self.repository.delete_peer_group(group_id, user_id)

    def get_methodology(self) -> PeerMethodologyResponseDTO:
        """Exposes the transparent peer selection and benchmarking methodology rules."""
        return PeerMethodologyResponseDTO(
            version="Stage87.v1",
            candidate_discovery={
                "primary_matching": "Exact GICS 8-digit Sub-Industry matching (Weight: 40%)",
                "scale_scoring": "Logarithmic Market Cap proximity within 0.2x to 5.0x range (Weight: 25%)",
                "geographic_matching": "Headquarters region & primary listing market parity (Weight: 15%)",
                "relationship_evidence": "Source-defined 10-K itemized competitor disclosures (Weight: 20%)",
            },
            period_alignment_rules={
                "LATEST_COMMON_FISCAL_YEAR": "Aligns latest completed fiscal year (e.g. FY2024)",
                "LATEST_AVAILABLE": "Compares most recently filed quarterly or annual disclosure",
                "QUALIFIED_TTM": "Trailing twelve months sum from 4 consecutive filed quarters",
            },
            valuation_definitions={
                "market_cap": "Diluted shares outstanding × official closing price on valuation observation date",
                "enterprise_value": "Market Cap + Short/Long-Term Debt - Cash & Cash Equivalents",
                "pe_negative_policy": "Flagged as NOT_MEANINGFUL (N/M) if trailing earnings are negative",
            },
            statistical_methodology={
                "median": "Exact middle value for odd samples, average of two middle values for even samples",
                "mean": "Arithmetic mean computed strictly over eligible AVAILABLE observations",
                "outlier_detection": "Tukey's fences: values beyond Q1 - 1.5*IQR or Q3 + 1.5*IQR",
                "percentile_rank": "Strictly below count + 0.5 * equal count divided by eligible sample count",
            },
        )
