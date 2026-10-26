"""Repository Layer for Company Peers and Comparable Company Analysis (Stage 87).

Maintains authoritative canonical company classification registries, verified
peer relationships, financial metric observations, and user-scoped peer group persistence.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from .enums import (
    ComparisonMetricCategory,
    IndustryTaxonomy,
    MetricObservationStatus,
    PeerRelationshipType,
)
from .errors import (
    PeerCompanyNotFoundError,
    PeerDuplicateCompanyError,
    PeerGroupNotAuthorizedError,
    PeerGroupNotFoundError,
    PeerGroupRevisionConflictError,
    PeerGroupSizeExceededError,
    PeerSelfSelectionNotAllowedError,
)
from .models import (
    CompanyPeerCandidate,
    ComparableMetricObservation,
    HistoricalDataPoint,
    IndustryClassification,
    UserCompanyPeerGroup,
)


class CompanyPeersRepository:
    """Authoritative repository for company classifications, candidate discovery, and peer groups."""

    def __init__(self):
        # Canonical Apple Company ID and Reference Universe IDs
        self.apple_id = "c0000000-0000-0000-0000-000000000001"
        self.msft_id = "c0000000-0000-0000-0000-000000000002"
        self.googl_id = "c0000000-0000-0000-0000-000000000003"
        self.samsung_id = "c0000000-0000-0000-0000-000000000004"
        self.dell_id = "c0000000-0000-0000-0000-000000000005"
        self.hp_id = "c0000000-0000-0000-0000-000000000006"
        self.sony_id = "c0000000-0000-0000-0000-000000000007"
        self.nvda_id = "c0000000-0000-0000-0000-000000000008"

        # Company directory: ID -> Profile dict
        self._companies: Dict[str, dict] = {}

        # User Peer Groups: group_id -> UserCompanyPeerGroup
        self._user_groups: Dict[str, UserCompanyPeerGroup] = {}

        # Multi-Company Metric Store: (company_id, metric_id, period_id) -> ComparableMetricObservation
        self._metric_store: Dict[tuple, ComparableMetricObservation] = {}

        # Historical series: (company_id, metric_id) -> List[HistoricalDataPoint]
        self._history_store: Dict[tuple, List[HistoricalDataPoint]] = {}

        self._init_reference_universe()
        self._init_financial_and_valuation_data()
        self._init_default_groups()

    def _init_reference_universe(self):
        """Initializes canonical reference companies and verified industry classifications."""
        self._companies[self.apple_id] = {
            "company_id": self.apple_id,
            "ticker": "AAPL",
            "display_name": "Apple Inc.",
            "headquarters_country": "United States",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Information Technology",
                industry_group="Technology Hardware & Equipment",
                industry="Technology Hardware, Storage & Peripherals",
                sub_industry="Technology Hardware, Storage & Peripherals",
                code="45202030",
            ),
            "market_cap": Decimal("3520000000000"),
            "formatted_market_cap": "$3.52T",
            "revenue": Decimal("391035000000"),
            "formatted_revenue": "$391.04B",
            "reporting_currency": "USD",
        }

        self._companies[self.msft_id] = {
            "company_id": self.msft_id,
            "ticker": "MSFT",
            "display_name": "Microsoft Corporation",
            "headquarters_country": "United States",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Information Technology",
                industry_group="Software & Services",
                industry="Software",
                sub_industry="Systems Software",
                code="45103020",
            ),
            "market_cap": Decimal("3150000000000"),
            "formatted_market_cap": "$3.15T",
            "revenue": Decimal("245120000000"),
            "formatted_revenue": "$245.12B",
            "reporting_currency": "USD",
            "relationship_type": PeerRelationshipType.VERIFIED_COMPETITOR,
            "relevance_score": 0.94,
            "selection_reasons": [
                "Commercial competitor in personal computing operating systems, tablets, and AI productivity platforms",
                "Mega-cap technology peer ($3.15T market capitalization)",
                "Same primary geographic market (United States / Global)",
            ],
            "is_competitor": True,
        }

        self._companies[self.googl_id] = {
            "company_id": self.googl_id,
            "ticker": "GOOGL",
            "display_name": "Alphabet Inc.",
            "headquarters_country": "United States",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Communication Services",
                industry_group="Media & Entertainment",
                industry="Interactive Media & Services",
                sub_industry="Interactive Media & Services",
                code="50203010",
            ),
            "market_cap": Decimal("2180000000000"),
            "formatted_market_cap": "$2.18T",
            "revenue": Decimal("349600000000"),
            "formatted_revenue": "$349.60B",
            "reporting_currency": "USD",
            "relationship_type": PeerRelationshipType.VERIFIED_COMPETITOR,
            "relevance_score": 0.92,
            "selection_reasons": [
                "Ecosystem competitor across mobile OS (Android vs iOS), app store distribution, and browser default search",
                "Mega-cap technology peer ($2.18T market capitalization)",
                "Comparable global revenue scale ($349.60B)",
            ],
            "is_competitor": True,
        }

        self._companies[self.samsung_id] = {
            "company_id": self.samsung_id,
            "ticker": "005930.KS",
            "display_name": "Samsung Electronics Co., Ltd.",
            "headquarters_country": "South Korea",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Information Technology",
                industry_group="Technology Hardware & Equipment",
                industry="Technology Hardware, Storage & Peripherals",
                sub_industry="Consumer Electronics",
                code="45202010",
            ),
            "market_cap": Decimal("380000000000"),
            "formatted_market_cap": "$380.00B",
            "revenue": Decimal("225400000000"),
            "formatted_revenue": "$225.40B",
            "reporting_currency": "KRW",
            "relationship_type": PeerRelationshipType.VERIFIED_COMPETITOR,
            "relevance_score": 0.96,
            "selection_reasons": [
                "Direct commercial competitor in global smartphones (Galaxy vs iPhone), tablets, smartwatches, and consumer audio",
                "Same primary GICS Industry Group (Technology Hardware & Equipment)",
                "Large-scale global consumer electronics operations ($225.40B revenue)",
            ],
            "is_competitor": True,
        }

        self._companies[self.dell_id] = {
            "company_id": self.dell_id,
            "ticker": "DELL",
            "display_name": "Dell Technologies Inc.",
            "headquarters_country": "United States",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Information Technology",
                industry_group="Technology Hardware & Equipment",
                industry="Technology Hardware, Storage & Peripherals",
                sub_industry="Technology Hardware, Storage & Peripherals",
                code="45202030",
            ),
            "market_cap": Decimal("85000000000"),
            "formatted_market_cap": "$85.00B",
            "revenue": Decimal("92500000000"),
            "formatted_revenue": "$92.50B",
            "reporting_currency": "USD",
            "relationship_type": PeerRelationshipType.VERIFIED_COMPETITOR,
            "relevance_score": 0.89,
            "selection_reasons": [
                "Identical verified GICS Sub-Industry (Technology Hardware, Storage & Peripherals - 45202030)",
                "Direct product competitor in commercial and consumer personal computers and laptops (XPS vs MacBook)",
                "Same geographic listing market (United States)",
            ],
            "is_competitor": True,
        }

        self._companies[self.hp_id] = {
            "company_id": self.hp_id,
            "ticker": "HPQ",
            "display_name": "HP Inc.",
            "headquarters_country": "United States",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Information Technology",
                industry_group="Technology Hardware & Equipment",
                industry="Technology Hardware, Storage & Peripherals",
                sub_industry="Technology Hardware, Storage & Peripherals",
                code="45202030",
            ),
            "market_cap": Decimal("34000000000"),
            "formatted_market_cap": "$34.00B",
            "revenue": Decimal("53600000000"),
            "formatted_revenue": "$53.60B",
            "reporting_currency": "USD",
            "relationship_type": PeerRelationshipType.COMPARABLE_CANDIDATE,
            "relevance_score": 0.84,
            "selection_reasons": [
                "Identical verified GICS Sub-Industry (Technology Hardware, Storage & Peripherals - 45202030)",
                "Comparable hardware business model (personal systems, notebooks, workstations)",
                "Same geographic headquarters (United States)",
            ],
            "is_competitor": False,
        }

        self._companies[self.sony_id] = {
            "company_id": self.sony_id,
            "ticker": "SONY",
            "display_name": "Sony Group Corporation",
            "headquarters_country": "Japan",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Consumer Discretionary",
                industry_group="Consumer Durables & Apparel",
                industry="Household Durables",
                sub_industry="Consumer Electronics",
                code="25201010",
            ),
            "market_cap": Decimal("118000000000"),
            "formatted_market_cap": "$118.00B",
            "revenue": Decimal("88200000000"),
            "formatted_revenue": "$88.20B",
            "reporting_currency": "JPY",
            "relationship_type": PeerRelationshipType.SOURCE_DEFINED_PEER,
            "relevance_score": 0.79,
            "selection_reasons": [
                "Source-defined peer in consumer electronics, digital imaging, and subscription digital entertainment",
                "Global hardware brand recognition with proprietary ecosystem components",
            ],
            "is_competitor": False,
        }

        self._companies[self.nvda_id] = {
            "company_id": self.nvda_id,
            "ticker": "NVDA",
            "display_name": "NVIDIA Corporation",
            "headquarters_country": "United States",
            "classification": IndustryClassification(
                taxonomy=IndustryTaxonomy.GICS,
                sector="Information Technology",
                industry_group="Semiconductors & Semiconductor Equipment",
                industry="Semiconductors",
                sub_industry="Semiconductors",
                code="45301010",
            ),
            "market_cap": Decimal("3450000000000"),
            "formatted_market_cap": "$3.45T",
            "revenue": Decimal("96300000000"),
            "formatted_revenue": "$96.30B",
            "reporting_currency": "USD",
            "relationship_type": PeerRelationshipType.COMPARABLE_CANDIDATE,
            "relevance_score": 0.78,
            "selection_reasons": [
                "Mega-cap technology peer ($3.45T market capitalization)",
                "Advanced silicon architecture, custom microprocessors, and AI compute systems",
                "Same primary geographic listing (United States)",
            ],
            "is_competitor": False,
        }

    def _init_financial_and_valuation_data(self):
        """Registers canonical financial observations across the reference universe."""
        data_table = {
            self.apple_id: {
                # Scale
                "scale.revenue": (Decimal("391035000000"), "$391.04B", "$"),
                "scale.gross_profit": (Decimal("180683000000"), "$180.68B", "$"),
                "scale.operating_income": (Decimal("123184000000"), "$123.18B", "$"),
                "scale.net_income": (Decimal("93725000000"), "$93.73B", "$"),
                "scale.total_assets": (Decimal("364980000000"), "$364.98B", "$"),
                "scale.total_debt": (Decimal("106629000000"), "$106.63B", "$"),
                "scale.total_equity": (Decimal("66658000000"), "$66.66B", "$"),
                "scale.market_cap": (Decimal("3520000000000"), "$3.52T", "$"),
                "scale.enterprise_value": (Decimal("3596700000000"), "$3.60T", "$"),
                # Growth
                "growth.revenue_growth": (Decimal("2.02"), "2.02%", "%"),
                # Profitability
                "profitability.gross_margin": (Decimal("46.21"), "46.21%", "%"),
                "profitability.operating_margin": (Decimal("31.50"), "31.50%", "%"),
                "profitability.ebitda_margin": (Decimal("34.43"), "34.43%", "%"),
                "profitability.net_margin": (Decimal("23.97"), "23.97%", "%"),
                "profitability.roe": (Decimal("147.25"), "147.25%", "%"),
                "profitability.roa": (Decimal("26.42"), "26.42%", "%"),
                "profitability.roic": (Decimal("61.34"), "61.34%", "%"),
                # Liquidity & Solvency
                "liquidity.current_ratio": (Decimal("0.89"), "0.89x", "x"),
                "solvency.debt_to_equity": (Decimal("1.60"), "1.60x", "x"),
                # Valuation
                "valuation.pe": (Decimal("37.56"), "37.56x", "x"),
                "valuation.forward_pe": (Decimal("31.20"), "31.20x", "x"),
                "valuation.pb": (Decimal("52.81"), "52.81x", "x"),
                "valuation.ps": (Decimal("9.00"), "9.00x", "x"),
                "valuation.ev_to_ebitda": (Decimal("26.71"), "26.71x", "x"),
                "valuation.ev_to_revenue": (Decimal("9.20"), "9.20x", "x"),
                "cashflow.free_cash_flow_yield": (Decimal("3.09"), "3.09%", "%"),
            },
            self.msft_id: {
                "scale.revenue": (Decimal("245120000000"), "$245.12B", "$"),
                "scale.gross_profit": (Decimal("170720000000"), "$170.72B", "$"),
                "scale.operating_income": (Decimal("109430000000"), "$109.43B", "$"),
                "scale.net_income": (Decimal("88140000000"), "$88.14B", "$"),
                "scale.total_assets": (Decimal("512160000000"), "$512.16B", "$"),
                "scale.total_debt": (Decimal("49800000000"), "$49.80B", "$"),
                "scale.total_equity": (Decimal("268480000000"), "$268.48B", "$"),
                "scale.market_cap": (Decimal("3150000000000"), "$3.15T", "$"),
                "scale.enterprise_value": (Decimal("3124500000000"), "$3.12T", "$"),
                "growth.revenue_growth": (Decimal("15.67"), "15.67%", "%"),
                "profitability.gross_margin": (Decimal("69.65"), "69.65%", "%"),
                "profitability.operating_margin": (Decimal("44.64"), "44.64%", "%"),
                "profitability.ebitda_margin": (Decimal("52.12"), "52.12%", "%"),
                "profitability.net_margin": (Decimal("35.96"), "35.96%", "%"),
                "profitability.roe": (Decimal("35.88"), "35.88%", "%"),
                "profitability.roa": (Decimal("18.82"), "18.82%", "%"),
                "profitability.roic": (Decimal("28.45"), "28.45%", "%"),
                "liquidity.current_ratio": (Decimal("1.25"), "1.25x", "x"),
                "solvency.debt_to_equity": (Decimal("0.19"), "0.19x", "x"),
                "valuation.pe": (Decimal("35.74"), "35.74x", "x"),
                "valuation.forward_pe": (Decimal("29.40"), "29.40x", "x"),
                "valuation.pb": (Decimal("11.73"), "11.73x", "x"),
                "valuation.ps": (Decimal("12.85"), "12.85x", "x"),
                "valuation.ev_to_ebitda": (Decimal("24.46"), "24.46x", "x"),
                "valuation.ev_to_revenue": (Decimal("12.75"), "12.75x", "x"),
                "cashflow.free_cash_flow_yield": (Decimal("2.35"), "2.35%", "%"),
            },
            self.googl_id: {
                "scale.revenue": (Decimal("349600000000"), "$349.60B", "$"),
                "scale.gross_profit": (Decimal("201200000000"), "$201.20B", "$"),
                "scale.operating_income": (Decimal("112300000000"), "$112.30B", "$"),
                "scale.net_income": (Decimal("94200000000"), "$94.20B", "$"),
                "scale.total_assets": (Decimal("432500000000"), "$432.50B", "$"),
                "scale.total_debt": (Decimal("28400000000"), "$28.40B", "$"),
                "scale.total_equity": (Decimal("312000000000"), "$312.00B", "$"),
                "scale.market_cap": (Decimal("2180000000000"), "$2.18T", "$"),
                "scale.enterprise_value": (Decimal("2085000000000"), "$2.09T", "$"),
                "growth.revenue_growth": (Decimal("13.80"), "13.80%", "%"),
                "profitability.gross_margin": (Decimal("57.55"), "57.55%", "%"),
                "profitability.operating_margin": (Decimal("32.12"), "32.12%", "%"),
                "profitability.ebitda_margin": (Decimal("38.40"), "38.40%", "%"),
                "profitability.net_margin": (Decimal("26.95"), "26.95%", "%"),
                "profitability.roe": (Decimal("31.85"), "31.85%", "%"),
                "profitability.roa": (Decimal("22.50"), "22.50%", "%"),
                "profitability.roic": (Decimal("30.12"), "30.12%", "%"),
                "liquidity.current_ratio": (Decimal("2.10"), "2.10x", "x"),
                "solvency.debt_to_equity": (Decimal("0.09"), "0.09x", "x"),
                "valuation.pe": (Decimal("23.14"), "23.14x", "x"),
                "valuation.forward_pe": (Decimal("20.10"), "20.10x", "x"),
                "valuation.pb": (Decimal("6.99"), "6.99x", "x"),
                "valuation.ps": (Decimal("6.24"), "6.24x", "x"),
                "valuation.ev_to_ebitda": (Decimal("15.53"), "15.53x", "x"),
                "valuation.ev_to_revenue": (Decimal("5.96"), "5.96x", "x"),
                "cashflow.free_cash_flow_yield": (Decimal("3.85"), "3.85%", "%"),
            },
            self.samsung_id: {
                "scale.revenue": (Decimal("225400000000"), "$225.40B", "$"),
                "scale.gross_profit": (Decimal("72100000000"), "$72.10B", "$"),
                "scale.operating_income": (Decimal("23800000000"), "$23.80B", "$"),
                "scale.net_income": (Decimal("20100000000"), "$20.10B", "$"),
                "scale.total_assets": (Decimal("350000000000"), "$350.00B", "$"),
                "scale.total_debt": (Decimal("14200000000"), "$14.20B", "$"),
                "scale.total_equity": (Decimal("275000000000"), "$275.00B", "$"),
                "scale.market_cap": (Decimal("380000000000"), "$380.00B", "$"),
                "scale.enterprise_value": (Decimal("312000000000"), "$312.00B", "$"),
                "growth.revenue_growth": (Decimal("12.40"), "12.40%", "%"),
                "profitability.gross_margin": (Decimal("31.99"), "31.99%", "%"),
                "profitability.operating_margin": (Decimal("10.56"), "10.56%", "%"),
                "profitability.ebitda_margin": (Decimal("24.10"), "24.10%", "%"),
                "profitability.net_margin": (Decimal("8.92"), "8.92%", "%"),
                "profitability.roe": (Decimal("7.65"), "7.65%", "%"),
                "profitability.roa": (Decimal("5.85"), "5.85%", "%"),
                "profitability.roic": (Decimal("9.20"), "9.20%", "%"),
                "liquidity.current_ratio": (Decimal("2.45"), "2.45x", "x"),
                "solvency.debt_to_equity": (Decimal("0.05"), "0.05x", "x"),
                "valuation.pe": (Decimal("18.91"), "18.91x", "x"),
                "valuation.forward_pe": (Decimal("13.40"), "13.40x", "x"),
                "valuation.pb": (Decimal("1.38"), "1.38x", "x"),
                "valuation.ps": (Decimal("1.69"), "1.69x", "x"),
                "valuation.ev_to_ebitda": (Decimal("5.74"), "5.74x", "x"),
                "valuation.ev_to_revenue": (Decimal("1.38"), "1.38x", "x"),
                "cashflow.free_cash_flow_yield": (Decimal("5.20"), "5.20%", "%"),
            },
            self.dell_id: {
                "scale.revenue": (Decimal("92500000000"), "$92.50B", "$"),
                "scale.gross_profit": (Decimal("20400000000"), "$20.40B", "$"),
                "scale.operating_income": (Decimal("6400000000"), "$6.40B", "$"),
                "scale.net_income": (Decimal("3750000000"), "$3.75B", "$"),
                "scale.total_assets": (Decimal("83500000000"), "$83.50B", "$"),
                "scale.total_debt": (Decimal("26100000000"), "$26.10B", "$"),
                "scale.total_equity": (Decimal("-1200000000"), "-$1.20B", "$"),
                "scale.market_cap": (Decimal("85000000000"), "$85.00B", "$"),
                "scale.enterprise_value": (Decimal("104200000000"), "$104.20B", "$"),
                "growth.revenue_growth": (Decimal("4.50"), "4.50%", "%"),
                "profitability.gross_margin": (Decimal("22.05"), "22.05%", "%"),
                "profitability.operating_margin": (Decimal("6.92"), "6.92%", "%"),
                "profitability.ebitda_margin": (Decimal("9.80"), "9.80%", "%"),
                "profitability.net_margin": (Decimal("4.05"), "4.05%", "%"),
                "profitability.roe": (None, "N/M", "%"),  # Negative equity -> Not Meaningful
                "profitability.roa": (Decimal("4.62"), "4.62%", "%"),
                "profitability.roic": (Decimal("16.85"), "16.85%", "%"),
                "liquidity.current_ratio": (Decimal("0.78"), "0.78x", "x"),
                "solvency.debt_to_equity": (None, "N/M", "x"),  # Negative equity
                "valuation.pe": (Decimal("22.67"), "22.67x", "x"),
                "valuation.forward_pe": (Decimal("14.50"), "14.50x", "x"),
                "valuation.pb": (None, "N/M", "x"),  # Negative book value
                "valuation.ps": (Decimal("0.92"), "0.92x", "x"),
                "valuation.ev_to_ebitda": (Decimal("11.50"), "11.50x", "x"),
                "valuation.ev_to_revenue": (Decimal("1.13"), "1.13x", "x"),
                "cashflow.free_cash_flow_yield": (Decimal("6.10"), "6.10%", "%"),
            },
            self.hp_id: {
                "scale.revenue": (Decimal("53600000000"), "$53.60B", "$"),
                "scale.gross_profit": (Decimal("11700000000"), "$11.70B", "$"),
                "scale.operating_income": (Decimal("4100000000"), "$4.10B", "$"),
                "scale.net_income": (Decimal("2800000000"), "$2.80B", "$"),
                "scale.total_assets": (Decimal("37800000000"), "$37.80B", "$"),
                "scale.total_debt": (Decimal("10900000000"), "$10.90B", "$"),
                "scale.total_equity": (Decimal("-750000000"), "-$750M", "$"),
                "scale.market_cap": (Decimal("34000000000"), "$34.00B", "$"),
                "scale.enterprise_value": (Decimal("41800000000"), "$41.80B", "$"),
                "growth.revenue_growth": (Decimal("-1.20"), "-1.20%", "%"),
                "profitability.gross_margin": (Decimal("21.83"), "21.83%", "%"),
                "profitability.operating_margin": (Decimal("7.65"), "7.65%", "%"),
                "profitability.ebitda_margin": (Decimal("9.50"), "9.50%", "%"),
                "profitability.net_margin": (Decimal("5.22"), "5.22%", "%"),
                "profitability.roe": (None, "N/M", "%"),
                "profitability.roa": (Decimal("7.41"), "7.41%", "%"),
                "profitability.roic": (Decimal("22.10"), "22.10%", "%"),
                "liquidity.current_ratio": (Decimal("0.72"), "0.72x", "x"),
                "solvency.debt_to_equity": (None, "N/M", "x"),
                "valuation.pe": (Decimal("12.14"), "12.14x", "x"),
                "valuation.forward_pe": (Decimal("9.80"), "9.80x", "x"),
                "valuation.pb": (None, "N/M", "x"),
                "valuation.ps": (Decimal("0.63"), "0.63x", "x"),
                "valuation.ev_to_ebitda": (Decimal("8.21"), "8.21x", "x"),
                "valuation.ev_to_revenue": (Decimal("0.78"), "0.78x", "x"),
                "cashflow.free_cash_flow_yield": (Decimal("9.45"), "9.45%", "%"),
            },
        }

        metric_names = {
            "scale.revenue": ("Total Revenue", ComparisonMetricCategory.SCALE),
            "scale.gross_profit": ("Gross Profit", ComparisonMetricCategory.SCALE),
            "scale.operating_income": ("Operating Income (EBIT)", ComparisonMetricCategory.SCALE),
            "scale.net_income": ("Net Income", ComparisonMetricCategory.SCALE),
            "scale.total_assets": ("Total Assets", ComparisonMetricCategory.SCALE),
            "scale.total_debt": ("Total Debt", ComparisonMetricCategory.SCALE),
            "scale.total_equity": ("Total Equity", ComparisonMetricCategory.SCALE),
            "scale.market_cap": ("Market Capitalization", ComparisonMetricCategory.SCALE),
            "scale.enterprise_value": ("Enterprise Value (EV)", ComparisonMetricCategory.SCALE),
            "growth.revenue_growth": ("Revenue Growth YoY", ComparisonMetricCategory.GROWTH),
            "profitability.gross_margin": ("Gross Margin", ComparisonMetricCategory.PROFITABILITY),
            "profitability.operating_margin": (
                "Operating Margin",
                ComparisonMetricCategory.PROFITABILITY,
            ),
            "profitability.ebitda_margin": (
                "EBITDA Margin",
                ComparisonMetricCategory.PROFITABILITY,
            ),
            "profitability.net_margin": ("Net Margin", ComparisonMetricCategory.PROFITABILITY),
            "profitability.roe": ("Return on Equity (ROE)", ComparisonMetricCategory.PROFITABILITY),
            "profitability.roa": ("Return on Assets (ROA)", ComparisonMetricCategory.PROFITABILITY),
            "profitability.roic": (
                "Return on Invested Capital (ROIC)",
                ComparisonMetricCategory.PROFITABILITY,
            ),
            "liquidity.current_ratio": ("Current Ratio", ComparisonMetricCategory.LIQUIDITY),
            "solvency.debt_to_equity": ("Debt-to-Equity", ComparisonMetricCategory.SOLVENCY),
            "valuation.pe": ("P/E (Trailing)", ComparisonMetricCategory.VALUATION),
            "valuation.forward_pe": ("Forward P/E", ComparisonMetricCategory.VALUATION),
            "valuation.pb": ("Price-to-Book (P/B)", ComparisonMetricCategory.VALUATION),
            "valuation.ps": ("Price-to-Sales (P/S)", ComparisonMetricCategory.VALUATION),
            "valuation.ev_to_ebitda": ("EV / EBITDA", ComparisonMetricCategory.VALUATION),
            "valuation.ev_to_revenue": ("EV / Revenue", ComparisonMetricCategory.VALUATION),
            "cashflow.free_cash_flow_yield": (
                "Free Cash Flow Yield",
                ComparisonMetricCategory.CASH_FLOW,
            ),
        }

        for comp_id, m_dict in data_table.items():
            comp_info = self._companies.get(comp_id, {})
            c_name = comp_info.get("display_name", "Unknown")
            ticker = comp_info.get("ticker", "UNK")
            is_sub = comp_id == self.apple_id

            for m_id, (val, fmt_val, unit) in m_dict.items():
                m_name, cat = metric_names.get(m_id, (m_id, ComparisonMetricCategory.SCALE))
                status = (
                    MetricObservationStatus.AVAILABLE
                    if val is not None
                    else MetricObservationStatus.NOT_MEANINGFUL
                )

                self._metric_store[(comp_id, m_id, "FY2024")] = ComparableMetricObservation(
                    company_id=comp_id,
                    company_name=c_name,
                    ticker=ticker,
                    metric_id=m_id,
                    metric_name=m_name,
                    category=cat,
                    exact_value=val,
                    formatted_value=fmt_val,
                    unit=unit,
                    currency="USD",
                    period_id="FY2024",
                    period_end="2024-09-28" if comp_id == self.apple_id else "2024-12-31",
                    status=status,
                    is_subject=is_sub,
                    source_filing_ref="Form 10-K / Annual Regulatory Filing",
                )

        # Historical multi-period data for Apple, Microsoft, Alphabet, Samsung
        # Years: FY2021, FY2022, FY2023, FY2024
        history_table = {
            self.apple_id: {
                "growth.revenue_growth": [
                    ("FY2021", "2021-09-25", 2021, Decimal("33.26"), "33.26%"),
                    ("FY2022", "2022-09-24", 2022, Decimal("7.79"), "7.79%"),
                    ("FY2023", "2023-09-30", 2023, Decimal("-2.80"), "-2.80%"),
                    ("FY2024", "2024-09-28", 2024, Decimal("2.02"), "2.02%"),
                ],
                "profitability.operating_margin": [
                    ("FY2021", "2021-09-25", 2021, Decimal("29.78"), "29.78%"),
                    ("FY2022", "2022-09-24", 2022, Decimal("30.29"), "30.29%"),
                    ("FY2023", "2023-09-30", 2023, Decimal("29.82"), "29.82%"),
                    ("FY2024", "2024-09-28", 2024, Decimal("31.50"), "31.50%"),
                ],
                "valuation.pe": [
                    ("FY2021", "2021-09-25", 2021, Decimal("28.40"), "28.40x"),
                    ("FY2022", "2022-09-24", 2022, Decimal("24.10"), "24.10x"),
                    ("FY2023", "2023-09-30", 2023, Decimal("30.20"), "30.20x"),
                    ("FY2024", "2024-09-28", 2024, Decimal("37.56"), "37.56x"),
                ],
            },
            self.msft_id: {
                "growth.revenue_growth": [
                    ("FY2021", "2021-06-30", 2021, Decimal("17.53"), "17.53%"),
                    ("FY2022", "2022-06-30", 2022, Decimal("17.96"), "17.96%"),
                    ("FY2023", "2023-06-30", 2023, Decimal("6.88"), "6.88%"),
                    ("FY2024", "2024-06-30", 2024, Decimal("15.67"), "15.67%"),
                ],
                "profitability.operating_margin": [
                    ("FY2021", "2021-06-30", 2021, Decimal("41.59"), "41.59%"),
                    ("FY2022", "2022-06-30", 2022, Decimal("42.06"), "42.06%"),
                    ("FY2023", "2023-06-30", 2023, Decimal("41.77"), "41.77%"),
                    ("FY2024", "2024-06-30", 2024, Decimal("44.64"), "44.64%"),
                ],
                "valuation.pe": [
                    ("FY2021", "2021-06-30", 2021, Decimal("35.10"), "35.10x"),
                    ("FY2022", "2022-06-30", 2022, Decimal("27.40"), "27.40x"),
                    ("FY2023", "2023-06-30", 2023, Decimal("33.80"), "33.80x"),
                    ("FY2024", "2024-06-30", 2024, Decimal("35.74"), "35.74x"),
                ],
            },
            self.googl_id: {
                "growth.revenue_growth": [
                    ("FY2021", "2021-12-31", 2021, Decimal("41.15"), "41.15%"),
                    ("FY2022", "2022-12-31", 2022, Decimal("9.78"), "9.78%"),
                    ("FY2023", "2023-12-31", 2023, Decimal("8.68"), "8.68%"),
                    ("FY2024", "2024-12-31", 2024, Decimal("13.80"), "13.80%"),
                ],
                "profitability.operating_margin": [
                    ("FY2021", "2021-12-31", 2021, Decimal("30.55"), "30.55%"),
                    ("FY2022", "2022-12-31", 2022, Decimal("26.46"), "26.46%"),
                    ("FY2023", "2023-12-31", 2023, Decimal("27.42"), "27.42%"),
                    ("FY2024", "2024-12-31", 2024, Decimal("32.12"), "32.12%"),
                ],
                "valuation.pe": [
                    ("FY2021", "2021-12-31", 2021, Decimal("26.80"), "26.80x"),
                    ("FY2022", "2022-12-31", 2022, Decimal("18.20"), "18.20x"),
                    ("FY2023", "2023-12-31", 2023, Decimal("25.10"), "25.10x"),
                    ("FY2024", "2024-12-31", 2024, Decimal("23.14"), "23.14x"),
                ],
            },
        }

        for comp_id, metrics in history_table.items():
            for m_id, points in metrics.items():
                self._history_store[(comp_id, m_id)] = [
                    HistoricalDataPoint(
                        period_id=pid,
                        period_end=pend,
                        fiscal_year=fy,
                        fiscal_quarter="FY",
                        value=v,
                        formatted_value=fv,
                    )
                    for pid, pend, fy, v, fv in points
                ]

    def _init_default_groups(self):
        """Initializes default peer group for Apple Inc."""
        def_group_id = "pg-apple-core-peers"
        self._user_groups[def_group_id] = UserCompanyPeerGroup(
            id=def_group_id,
            owner_user_id="system_default",
            subject_company_id=self.apple_id,
            name="Core Hardware & Platform Peers",
            description="Institutional comparable peer group: Microsoft, Alphabet, Samsung, Dell, and HP",
            peer_company_ids=[
                self.msft_id,
                self.googl_id,
                self.samsung_id,
                self.dell_id,
                self.hp_id,
            ],
            revision=1,
        )

    # -------------------------------------------------------------------------
    # Company Profile and Classification Queries
    # -------------------------------------------------------------------------

    def get_company(self, company_id: str) -> Optional[dict]:
        """Resolves canonical company profile and industry classification."""
        return self._companies.get(company_id)

    def get_candidates_for_company(
        self,
        company_id: str,
        limit: int = 20,
        competitors_only: bool = False,
    ) -> List[CompanyPeerCandidate]:
        """Resolves qualified peer candidates for a subject company with explainable selection reasons."""
        if company_id not in self._companies:
            raise PeerCompanyNotFoundError(company_id)

        candidates: List[CompanyPeerCandidate] = []
        for c_id, profile in self._companies.items():
            if c_id == company_id:
                continue  # Never include subject company as candidate

            is_comp = profile.get("is_competitor", False)
            if competitors_only and not is_comp:
                continue

            rel_type = profile.get("relationship_type", PeerRelationshipType.COMPARABLE_CANDIDATE)
            score = profile.get("relevance_score", 0.5)
            reasons = profile.get("selection_reasons", ["Industry similarity"])

            candidates.append(
                CompanyPeerCandidate(
                    candidate_company_id=c_id,
                    ticker=profile["ticker"],
                    display_name=profile["display_name"],
                    relationship_type=rel_type,
                    classification=profile["classification"],
                    headquarters_country=profile["headquarters_country"],
                    market_cap=profile.get("market_cap"),
                    formatted_market_cap=profile.get("formatted_market_cap"),
                    revenue=profile.get("revenue"),
                    formatted_revenue=profile.get("formatted_revenue"),
                    relevance_score=score,
                    selection_reasons=reasons,
                    is_competitor=is_comp,
                )
            )

        # Sort candidates deterministically by relevance score descending
        candidates.sort(key=lambda c: c.relevance_score, reverse=True)
        return candidates[:limit]

    # -------------------------------------------------------------------------
    # User Peer Group Persistence with Tenant Isolation
    # -------------------------------------------------------------------------

    def get_peer_groups_for_company(
        self, company_id: str, user_id: str
    ) -> List[UserCompanyPeerGroup]:
        """Returns all peer groups owned by user or system default for the subject company."""
        return [
            g
            for g in self._user_groups.values()
            if (
                g.subject_company_id == company_id
                and (g.owner_user_id == user_id or g.owner_user_id == "system_default")
            )
        ]

    def get_peer_group(self, group_id: str, user_id: str) -> UserCompanyPeerGroup:
        """Retrieves specific peer group, verifying user authorization."""
        group = self._user_groups.get(group_id)
        if not group:
            raise PeerGroupNotFoundError(group_id)
        if group.owner_user_id != user_id and group.owner_user_id != "system_default":
            raise PeerGroupNotAuthorizedError(group_id)
        return group

    def create_peer_group(
        self,
        owner_user_id: str,
        subject_company_id: str,
        name: str,
        peer_company_ids: List[str],
        description: Optional[str] = None,
    ) -> UserCompanyPeerGroup:
        """Creates a new user-scoped peer group with strict validation."""
        if subject_company_id not in self._companies:
            raise PeerCompanyNotFoundError(subject_company_id)

        # Disallow self-peer
        if subject_company_id in peer_company_ids:
            raise PeerSelfSelectionNotAllowedError(subject_company_id)

        # Disallow duplicates
        if len(peer_company_ids) != len(set(peer_company_ids)):
            raise PeerDuplicateCompanyError("Duplicate companies in peer group list")

        # Disallow exceeding maximum size
        if len(peer_company_ids) > 25:
            raise PeerGroupSizeExceededError(len(peer_company_ids), 25)

        # Validate existence of each peer
        for pid in peer_company_ids:
            if pid not in self._companies:
                raise PeerCompanyNotFoundError(pid)

        new_id = f"pg-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        group = UserCompanyPeerGroup(
            id=new_id,
            owner_user_id=owner_user_id,
            subject_company_id=subject_company_id,
            name=name.strip(),
            description=description.strip() if description else None,
            peer_company_ids=list(peer_company_ids),
            created_at=now,
            updated_at=now,
            revision=1,
        )
        self._user_groups[new_id] = group
        return group

    def update_peer_group(
        self,
        group_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        peer_company_ids: Optional[List[str]] = None,
        expected_revision: Optional[int] = None,
    ) -> UserCompanyPeerGroup:
        """Updates an existing peer group with revision concurrency checking."""
        group = self.get_peer_group(group_id, user_id)
        if group.owner_user_id == "system_default":
            raise PeerGroupNotAuthorizedError(
                f"Cannot mutate system default peer group '{group_id}'"
            )

        if expected_revision is not None and group.revision != expected_revision:
            raise PeerGroupRevisionConflictError(group_id, expected_revision, group.revision)

        if peer_company_ids is not None:
            if group.subject_company_id in peer_company_ids:
                raise PeerSelfSelectionNotAllowedError(group.subject_company_id)
            if len(peer_company_ids) != len(set(peer_company_ids)):
                raise PeerDuplicateCompanyError("Duplicate companies in updated peer list")
            if len(peer_company_ids) > 25:
                raise PeerGroupSizeExceededError(len(peer_company_ids), 25)
            for pid in peer_company_ids:
                if pid not in self._companies:
                    raise PeerCompanyNotFoundError(pid)
            group.peer_company_ids = list(peer_company_ids)

        if name is not None:
            group.name = name.strip()
        if description is not None:
            group.description = description.strip() if description else None

        group.updated_at = datetime.now(timezone.utc)
        group.revision += 1
        return group

    def delete_peer_group(self, group_id: str, user_id: str) -> None:
        """Deletes a user-owned peer group."""
        group = self.get_peer_group(group_id, user_id)
        if group.owner_user_id == "system_default":
            raise PeerGroupNotAuthorizedError(
                f"Cannot delete system default peer group '{group_id}'"
            )
        del self._user_groups[group_id]

    # -------------------------------------------------------------------------
    # Comparable Metric Observations & Historical Queries
    # -------------------------------------------------------------------------

    def get_observation(
        self, company_id: str, metric_id: str, period_id: str = "FY2024"
    ) -> Optional[ComparableMetricObservation]:
        """Fetches an individual metric observation."""
        return self._metric_store.get((company_id, metric_id, period_id))

    def get_historical_series(self, company_id: str, metric_id: str) -> List[HistoricalDataPoint]:
        """Fetches multi-period historical series for a company and metric."""
        return self._history_store.get((company_id, metric_id), [])
