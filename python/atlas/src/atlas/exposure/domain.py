"""Domain Definitions for Financial and Economic Exposure Engine (Stage 137).

Institutional-grade typed models for:
- Multi-domain financial exposure (Company, Portfolio, Geographic, Sector, Commodity, Supply Chain, Infrastructure)
- Quantitative measurement bases, evidence classes, and uncertainty classifications
- Exact decimal precision for currency amounts, ratios, and percentages
- Lineage manifests, coverage ratios, and immutable analysis runs
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType


class ExposureDomain(str, Enum):
    """Primary operational domains for financial and economic exposure."""
    COMPANY = "COMPANY"
    PORTFOLIO = "PORTFOLIO"
    GEOGRAPHIC = "GEOGRAPHIC"
    SECTOR = "SECTOR"
    COMMODITY = "COMMODITY"
    CORPORATE_GROUP = "CORPORATE_GROUP"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    DERIVATIVES = "DERIVATIVES"
    MACRO_ECONOMIC = "MACRO_ECONOMIC"


class ExposureType(str, Enum):
    """Canonical exposure classifications."""
    EQUITY_POSITION_EXPOSURE = "EQUITY_POSITION_EXPOSURE"
    DEBT_POSITION_EXPOSURE = "DEBT_POSITION_EXPOSURE"
    PORTFOLIO_WEIGHT_EXPOSURE = "PORTFOLIO_WEIGHT_EXPOSURE"
    DERIVATIVE_NOTIONAL_EXPOSURE = "DERIVATIVE_NOTIONAL_EXPOSURE"
    DERIVATIVE_DELTA_EQUIVALENT_EXPOSURE = "DERIVATIVE_DELTA_EQUIVALENT_EXPOSURE"
    DERIVATIVE_SENSITIVITY_EXPOSURE = "DERIVATIVE_SENSITIVITY_EXPOSURE"
    REVENUE_GEOGRAPHIC_EXPOSURE = "REVENUE_GEOGRAPHIC_EXPOSURE"
    REVENUE_SEGMENT_EXPOSURE = "REVENUE_SEGMENT_EXPOSURE"
    REVENUE_CUSTOMER_EXPOSURE = "REVENUE_CUSTOMER_EXPOSURE"
    ASSET_GEOGRAPHIC_EXPOSURE = "ASSET_GEOGRAPHIC_EXPOSURE"
    CAPEX_GEOGRAPHIC_EXPOSURE = "CAPEX_GEOGRAPHIC_EXPOSURE"
    SECTOR_ALLOCATION_EXPOSURE = "SECTOR_ALLOCATION_EXPOSURE"
    INDUSTRY_ALLOCATION_EXPOSURE = "INDUSTRY_ALLOCATION_EXPOSURE"
    COMMODITY_PRICE_EXPOSURE = "COMMODITY_PRICE_EXPOSURE"
    COMMODITY_OPERATIONAL_EXPOSURE = "COMMODITY_OPERATIONAL_EXPOSURE"
    FOREIGN_EXCHANGE_EXPOSURE = "FOREIGN_EXCHANGE_EXPOSURE"
    INTEREST_RATE_EXPOSURE = "INTEREST_RATE_EXPOSURE"
    SUPPLY_CHAIN_DEPENDENCY = "SUPPLY_CHAIN_DEPENDENCY"
    INFRASTRUCTURE_ASSET_ASSOCIATION = "INFRASTRUCTURE_ASSET_ASSOCIATION"
    FACILITY_GEOGRAPHIC_PRESENCE = "FACILITY_GEOGRAPHIC_PRESENCE"
    CORPORATE_GROUP_EXPOSURE = "CORPORATE_GROUP_EXPOSURE"
    ECONOMIC_INDICATOR_SENSITIVITY = "ECONOMIC_INDICATOR_SENSITIVITY"
    SCENARIO_EXPOSURE = "SCENARIO_EXPOSURE"


class ExposureEvidenceClass(str, Enum):
    """Institutional evidence and derivation classifications."""
    REPORTED = "REPORTED"
    DETERMINISTICALLY_CALCULATED = "DETERMINISTICALLY_CALCULATED"
    MODEL_ESTIMATED = "MODEL_ESTIMATED"
    USER_DEFINED_SCENARIO = "USER_DEFINED_SCENARIO"
    SOURCE_REPORTED_QUALITATIVE = "SOURCE_REPORTED_QUALITATIVE"
    UNAVAILABLE = "UNAVAILABLE"


class ExposureRelationshipStrength(str, Enum):
    """Qualitative strength of connection between subject and exposure target."""
    DIRECT_MEASURED = "DIRECT_MEASURED"
    DIRECT_REPORTED = "DIRECT_REPORTED"
    DERIVED_FROM_VERIFIED_DATA = "DERIVED_FROM_VERIFIED_DATA"
    INDIRECT_DOCUMENTED = "INDIRECT_DOCUMENTED"
    QUALITATIVE_REPORTED = "QUALITATIVE_REPORTED"
    ASSUMPTION_DEPENDENT = "ASSUMPTION_DEPENDENT"
    UNRESOLVED = "UNRESOLVED"


class CoverageStatus(str, Enum):
    """Completeness status of measured population."""
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNALLOCATED_RESIDUAL = "UNALLOCATED_RESIDUAL"
    UNCOVERED = "UNCOVERED"
    UNKNOWN = "UNKNOWN"


class UncertaintyClass(str, Enum):
    """Source-grounded uncertainty and limitation categorization."""
    SOURCE_INCOMPLETE = "SOURCE_INCOMPLETE"
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    ENTITY_IDENTITY_AMBIGUITY = "ENTITY_IDENTITY_AMBIGUITY"
    GEOGRAPHIC_PRECISION_LIMITATION = "GEOGRAPHIC_PRECISION_LIMITATION"
    QUANTITATIVE_ESTIMATION = "QUANTITATIVE_ESTIMATION"
    SCENARIO_ASSUMPTION = "SCENARIO_ASSUMPTION"
    DATA_STALENESS = "DATA_STALENESS"
    INCONSISTENT_REPORTING = "INCONSISTENT_REPORTING"
    VERIFIED_DETERMINISTIC = "VERIFIED_DETERMINISTIC"


class ConsolidationBasis(str, Enum):
    """Accounting consolidation status for corporate group metrics."""
    CONSOLIDATED = "CONSOLIDATED"
    SUBSIDIARY_STANDALONE = "SUBSIDIARY_STANDALONE"
    EQUITY_METHOD = "EQUITY_METHOD"
    PROPORTIONAL = "PROPORTIONAL"
    NOT_CONSOLIDATED = "NOT_CONSOLIDATED"


class CountryExposureBasis(str, Enum):
    """Basis used for attributing country exposure."""
    ISSUER_DOMICILE = "ISSUER_DOMICILE"
    EXCHANGE_LOCATION = "EXCHANGE_LOCATION"
    REVENUE_GEOGRAPHY = "REVENUE_GEOGRAPHY"
    ASSET_GEOGRAPHY = "ASSET_GEOGRAPHY"
    COUNTRY_OF_RISK = "COUNTRY_OF_RISK"


class AnalysisRunStatus(str, Enum):
    """Execution status for exposure analysis runs."""
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    RESOLVING = "RESOLVING"
    CALCULATING = "CALCULATING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# -----------------------------------------------------------------------------
# Core Exposure Models
# -----------------------------------------------------------------------------
class ExposureMeasureDefinition(BaseModel):
    """Typed definition of an authorized financial exposure metric."""
    measure_id: str
    measure_version: str = "v1.0"
    display_name: str
    domain: ExposureDomain
    unit_dimension: str  # e.g., "CURRENCY", "PERCENT", "RATIO", "COUNT", "MW", "BPS"
    financial_basis: str
    numerator_definition: str
    denominator_definition: Optional[str] = None
    aggregation_rule: str = "SUM"
    missing_data_policy: str = "EXCLUDE_WITH_UNCOVERED_DISCLOSURE"
    required_sources: List[str] = Field(default_factory=list)
    allowed_derivation_methods: List[str] = Field(default_factory=list)
    description: str = ""


class ExposureCoverageSummary(BaseModel):
    """Explicit accounting of measured coverage and unallocated residuals."""
    total_relevant_denominator: Decimal
    eligible_covered_denominator: Decimal
    coverage_ratio: Decimal  # eligible_covered / total_relevant
    covered_dimensions: List[str] = Field(default_factory=list)
    uncovered_dimensions: List[str] = Field(default_factory=list)
    unallocated_residual_amount: Optional[Decimal] = None
    unallocated_residual_percentage: Optional[Decimal] = None
    coverage_status: CoverageStatus = CoverageStatus.COMPLETE
    notes: List[str] = Field(default_factory=list)


class AtlasExposureResult(BaseModel):
    """Canonical quantitative or qualitative exposure result."""
    exposure_id: str
    analysis_run_id: str
    subject_entity_ref: CanonicalGraphNodeRef
    target_entity_ref: CanonicalGraphNodeRef
    related_event_id: Optional[str] = None
    exposure_domain: ExposureDomain
    exposure_type: ExposureType
    exposure_measure_id: str
    evidence_class: ExposureEvidenceClass
    relationship_strength: ExposureRelationshipStrength
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    unit: str = "USD"
    percentage: Optional[Decimal] = None  # 0.0 to 100.0 or signed if net
    numerator_value: Optional[Decimal] = None
    denominator_value: Optional[Decimal] = None
    denominator_reference: Optional[str] = None
    reporting_period: Optional[str] = None  # e.g., "FY2024", "2024Q3"
    market_data_as_of: Optional[datetime] = None
    valid_at: Optional[datetime] = None
    known_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    calculation_method_id: str
    calculation_version: str = "v1.0"
    assumption_set_id: Optional[str] = None
    source_manifest_id: Optional[str] = None
    input_lineage_ids: List[str] = Field(default_factory=list)
    graph_path_ids: List[str] = Field(default_factory=list)
    coverage_status: CoverageStatus = CoverageStatus.COMPLETE
    coverage_ratio: Optional[Decimal] = None
    uncertainty_class: UncertaintyClass = UncertaintyClass.VERIFIED_DETERMINISTIC
    explanation: str = ""
    limitations_disclaimer: str = (
        "Calculated exposure represents verified financial/economic relationship topology. "
        "It does not constitute a prediction of future market outcomes, realized asset damage, or economic loss."
    )
    warnings: List[str] = Field(default_factory=list)
    tenant_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExposureScenarioShock(BaseModel):
    """Explicit user-defined hypothetical shock input for scenario calculation."""
    shock_id: str
    target_dimension: str  # e.g., "SECTOR", "COUNTRY", "COMMODITY", "INTEREST_RATE", "SECURITY"
    target_identifier: str  # e.g., "Information Technology", "US", "BRENT", "USD_RATE_BPS"
    shock_value: Decimal  # percentage shock (e.g. -10.0 for -10%) or absolute (e.g. 25 for +25bps)
    shock_unit: str = "PERCENT"  # "PERCENT", "BPS", "CURRENCY_AMOUNT"
    description: Optional[str] = None


class ExposureScenarioDefinition(BaseModel):
    """Scenario specification defining hypothetical assumptions."""
    scenario_id: str
    scenario_name: str
    owner_id: str
    shocks: List[ExposureScenarioShock] = Field(default_factory=list)
    methodology_version: str = "v1.0"
    market_data_as_of: Optional[datetime] = None
    financial_data_as_of: Optional[datetime] = None
    known_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExposureScenarioRun(BaseModel):
    """Immutable execution record for a scenario evaluation."""
    run_id: str
    scenario_id: str
    status: AnalysisRunStatus = AnalysisRunStatus.COMPLETED
    subject_entity_ref: CanonicalGraphNodeRef
    results: List[AtlasExposureResult] = Field(default_factory=list)
    total_conditional_pnl: Decimal = Decimal("0.0")
    base_currency: str = "USD"
    warnings: List[str] = Field(default_factory=list)
    assumptions_notice: str = (
        "HYPOTHETICAL SCENARIO RESULT. Computed strictly from user-supplied assumptions. "
        "Does not constitute a financial forecast, probability estimate, or realized market outcome."
    )
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExposureAnalysisRun(BaseModel):
    """Immutable record of an exposure analysis run."""
    run_id: str
    subject_ref: CanonicalGraphNodeRef
    event_id: Optional[str] = None
    exposure_domains: List[ExposureDomain] = Field(default_factory=list)
    status: AnalysisRunStatus = AnalysisRunStatus.COMPLETED
    results: List[AtlasExposureResult] = Field(default_factory=list)
    coverage_summary: Optional[ExposureCoverageSummary] = None
    graph_revision: Optional[str] = None
    financial_data_revision: Optional[str] = None
    known_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_at: Optional[datetime] = None
    calculation_versions: Dict[str, str] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    tenant_id: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
