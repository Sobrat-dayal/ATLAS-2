"""Canonical Exposure Measure Definitions (Stage 137).

Enforces institutional rigor by explicitly defining numerators, denominators,
aggregation rules, units, and missing data policies.
"""

from typing import Dict
from atlas.exposure.domain import ExposureDomain, ExposureMeasureDefinition

MEASURE_REGISTRY: Dict[str, ExposureMeasureDefinition] = {
    "REV_GEO_SHARE_V1": ExposureMeasureDefinition(
        measure_id="REV_GEO_SHARE_V1",
        measure_version="v1.0",
        display_name="Geographic Revenue Share",
        domain=ExposureDomain.GEOGRAPHIC,
        unit_dimension="PERCENT",
        financial_basis="CONSOLIDATED_REPORTED_REVENUE",
        numerator_definition="Reported segment revenue attributed to target country or region",
        denominator_definition="Total reported consolidated revenue for matching accounting period",
        aggregation_rule="SUM",
        missing_data_policy="EXCLUDE_WITH_UNCOVERED_DISCLOSURE",
        required_sources=["10-K", "10-Q", "ANNUAL_REPORT", "AUDITED_FINANCIAL_STATEMENTS"],
        allowed_derivation_methods=["REPORTED_DISCLOSURE", "RATIO_CALCULATION"],
        description="Share of total company revenue originating from or delivered to a specific geographic territory."
    ),
    "REV_GEO_AMOUNT_V1": ExposureMeasureDefinition(
        measure_id="REV_GEO_AMOUNT_V1",
        measure_version="v1.0",
        display_name="Geographic Revenue Amount",
        domain=ExposureDomain.GEOGRAPHIC,
        unit_dimension="CURRENCY",
        financial_basis="REPORTED_SEGMENT_REVENUE",
        numerator_definition="Reported segment revenue for target country or region in specified currency",
        denominator_definition=None,
        aggregation_rule="SUM",
        missing_data_policy="EXCLUDE_WITH_UNCOVERED_DISCLOSURE",
        required_sources=["10-K", "10-Q", "ANNUAL_REPORT"],
        allowed_derivation_methods=["REPORTED_DISCLOSURE", "POINT_IN_TIME_FX_CONVERSION"],
        description="Absolute reported revenue in currency attributed to target geography."
    ),
    "FACILITY_COUNT_V1": ExposureMeasureDefinition(
        measure_id="FACILITY_COUNT_V1",
        measure_version="v1.0",
        display_name="Facility Operational Presence Count",
        domain=ExposureDomain.INFRASTRUCTURE,
        unit_dimension="COUNT",
        financial_basis="PHYSICAL_ASSET_REGISTRY",
        numerator_definition="Count of verified physical facilities located within the geographic boundary",
        denominator_definition="Total verified company facilities globally",
        aggregation_rule="SUM",
        missing_data_policy="DISCLOSE_PARTIAL",
        required_sources=["STAGE_132_CORPORATE_FACILITIES", "REGULATORY_DISCLOSURES"],
        allowed_derivation_methods=["SPATIAL_COUNT"],
        description="Physical presence metric. Strictly prohibited from being used as a revenue or financial exposure proxy."
    ),
    "PORTFOLIO_NAV_WEIGHT_V1": ExposureMeasureDefinition(
        measure_id="PORTFOLIO_NAV_WEIGHT_V1",
        measure_version="v1.0",
        display_name="Portfolio Position NAV Weight",
        domain=ExposureDomain.PORTFOLIO,
        unit_dimension="PERCENT",
        financial_basis="PORTFOLIO_NET_ASSET_VALUE",
        numerator_definition="Clean market value of verified holding position",
        denominator_definition="Total portfolio net asset value as of the valuation date",
        aggregation_rule="SUM",
        missing_data_policy="EXCLUDE_WITH_UNCOVERED_DISCLOSURE",
        required_sources=["PORTFOLIO_ACCOUNTING_SYSTEM", "CUSTODIAN_FEED", "VERIFIED_HOLDINGS"],
        allowed_derivation_methods=["DETERMINISTIC_VALUATION_RATIO"],
        description="Percentage of total portfolio net assets allocated to this position."
    ),
    "PORTFOLIO_GROSS_EXPOSURE_V1": ExposureMeasureDefinition(
        measure_id="PORTFOLIO_GROSS_EXPOSURE_V1",
        measure_version="v1.0",
        display_name="Portfolio Gross Exposure",
        domain=ExposureDomain.PORTFOLIO,
        unit_dimension="CURRENCY",
        financial_basis="SUM_OF_ABSOLUTE_POSITION_VALUES",
        numerator_definition="Sum of absolute market values of all long and short positions: sum(|V_i|)",
        denominator_definition=None,
        aggregation_rule="SUM_ABS",
        missing_data_policy="DISCLOSE_MISSING",
        required_sources=["PORTFOLIO_POSITIONS"],
        allowed_derivation_methods=["SUM_ABSOLUTE_VALUE"],
        description="Total economic footprint of all long and short positions regardless of direction."
    ),
    "PORTFOLIO_NET_EXPOSURE_V1": ExposureMeasureDefinition(
        measure_id="PORTFOLIO_NET_EXPOSURE_V1",
        measure_version="v1.0",
        display_name="Portfolio Net Exposure",
        domain=ExposureDomain.PORTFOLIO,
        unit_dimension="CURRENCY",
        financial_basis="SUM_OF_SIGNED_POSITION_VALUES",
        numerator_definition="Algebraic sum of signed market values of long and short positions: sum(V_i)",
        denominator_definition=None,
        aggregation_rule="SUM_SIGNED",
        missing_data_policy="DISCLOSE_MISSING",
        required_sources=["PORTFOLIO_POSITIONS"],
        allowed_derivation_methods=["SUM_SIGNED_VALUE"],
        description="Signed directional market exposure. Long positions positive, short positions negative."
    ),
    "FUND_LOOKTHROUGH_WEIGHT_V1": ExposureMeasureDefinition(
        measure_id="FUND_LOOKTHROUGH_WEIGHT_V1",
        measure_version="v1.0",
        display_name="Fund Look-Through Indirect Weight",
        domain=ExposureDomain.PORTFOLIO,
        unit_dimension="PERCENT",
        financial_basis="COMPOUNDED_HOLDINGS_CHAIN",
        numerator_definition="Effective indirect holding allocation calculated by multiplying weights along verified holding chain",
        denominator_definition="Top-level parent portfolio NAV",
        aggregation_rule="COMPOUND_MULTIPLY",
        missing_data_policy="DISCLOSE_PARTIAL_LOOKTHROUGH",
        required_sources=["PORTFOLIO_HOLDINGS", "FUND_CONSTITUENT_DISCLOSURES"],
        allowed_derivation_methods=["BOUNDED_CYCLE_PROTECTED_TRAVERSAL"],
        description="Indirect investment exposure through nested mutual funds or ETFs with strict cycle detection."
    ),
    "CORP_GROUP_CONSOLIDATED_REV_V1": ExposureMeasureDefinition(
        measure_id="CORP_GROUP_CONSOLIDATED_REV_V1",
        measure_version="v1.0",
        display_name="Corporate Group Consolidated Revenue",
        domain=ExposureDomain.CORPORATE_GROUP,
        unit_dimension="CURRENCY",
        financial_basis="GAAP_IFRS_CONSOLIDATED_FINANCIALS",
        numerator_definition="Reported consolidated group revenue of parent entity with internal eliminations",
        denominator_definition=None,
        aggregation_rule="CONSOLIDATED_PARENT_ONLY",
        missing_data_policy="DISCLOSE_UNCONSOLIDATED",
        required_sources=["SEC_EDGAR_10K", "IFRS_ANNUAL_REPORT"],
        allowed_derivation_methods=["CONSOLIDATED_EXTRACTION"],
        description="Parent company consolidated revenue. Never adds subsidiary revenues already consolidated within parent."
    ),
    "DV01_RATE_SENSITIVITY_V1": ExposureMeasureDefinition(
        measure_id="DV01_RATE_SENSITIVITY_V1",
        measure_version="v1.0",
        display_name="DV01 Interest Rate Sensitivity",
        domain=ExposureDomain.MACRO_ECONOMIC,
        unit_dimension="CURRENCY",
        financial_basis="DOLLAR_VALUE_OF_01",
        numerator_definition="-DV01 * Delta_yield_in_basis_points",
        denominator_definition=None,
        aggregation_rule="LINEAR_SENSITIVITY_SUM",
        missing_data_policy="UNAVAILABLE",
        required_sources=["FIXED_INCOME_ANALYTICS", "VERIFIED_DV01_CALCULATOR"],
        allowed_derivation_methods=["LOCAL_LINEAR_APPROXIMATION"],
        description="First-order local dollar sensitivity to interest rate shift. Strictly labeled as scenario approximation."
    ),
    "DERIVATIVE_DELTA_EQUIVALENT_V1": ExposureMeasureDefinition(
        measure_id="DERIVATIVE_DELTA_EQUIVALENT_V1",
        measure_version="v1.0",
        display_name="Derivative Delta-Equivalent Exposure",
        domain=ExposureDomain.DERIVATIVES,
        unit_dimension="CURRENCY",
        financial_basis="DELTA_WEIGHTED_NOTIONAL",
        numerator_definition="Contracts * Multiplier * Underlying_Price * Delta",
        denominator_definition=None,
        aggregation_rule="SUM",
        missing_data_policy="UNAVAILABLE",
        required_sources=["OPTION_ANALYTICS", "MARKET_DATA_SERVICE"],
        allowed_derivation_methods=["BLACK_SCHOLES_DELTA_MAPPING"],
        description="Effective linear dollar exposure of an option or derivative contract."
    ),
    "SUPPLY_CHAIN_QUALITATIVE_V1": ExposureMeasureDefinition(
        measure_id="SUPPLY_CHAIN_QUALITATIVE_V1",
        measure_version="v1.0",
        display_name="Documented Supply Chain Relationship",
        domain=ExposureDomain.SUPPLY_CHAIN,
        unit_dimension="QUALITATIVE",
        financial_basis="DISCLOSED_BUSINESS_RELATIONSHIP",
        numerator_definition="Documented supplier/customer commercial tie in verified regulatory disclosures",
        denominator_definition=None,
        aggregation_rule="RELATIONSHIP_LIST",
        missing_data_policy="AMOUNT_NULL_QUALITATIVE_ONLY",
        required_sources=["10-K_MAJOR_CUSTOMERS", "SUPPLY_CHAIN_DISCLOSURES"],
        allowed_derivation_methods=["QUALITATIVE_DOCUMENTATION"],
        description="Commercial dependency. Monetary exposure is NULL unless specific contract value is explicitly disclosed."
    ),
    "EARTHQUAKE_PROXIMITY_PRESENCE_V1": ExposureMeasureDefinition(
        measure_id="EARTHQUAKE_PROXIMITY_PRESENCE_V1",
        measure_version="v1.0",
        display_name="Geographic Event Proximity Presence",
        domain=ExposureDomain.INFRASTRUCTURE,
        unit_dimension="DISTANCE_KM",
        financial_basis="GEOSPATIAL_DISTANCE",
        numerator_definition="Great-circle distance between verified corporate/infrastructure facility and event epicenter",
        denominator_definition=None,
        aggregation_rule="MIN_DISTANCE",
        missing_data_policy="UNAVAILABLE",
        required_sources=["USGS_SEISMIC_FEED", "STAGE_134_LIVE_WORLD", "STAGE_132_FACILITIES"],
        allowed_derivation_methods=["HAVERSINE_SPATIAL_DISTANCE"],
        description="Physical proximity to event. Strictly conveys geographic co-location, NOT asset loss or financial impairment."
    ),
    "COMMODITY_MENTION_QUALITATIVE_V1": ExposureMeasureDefinition(
        measure_id="COMMODITY_MENTION_QUALITATIVE_V1",
        measure_version="v1.0",
        display_name="Commodity Context Mention",
        domain=ExposureDomain.COMMODITY,
        unit_dimension="QUALITATIVE",
        financial_basis="TEXTUAL_CONTEXTUAL_MENTION",
        numerator_definition="Documented mention of commodity in corporate or industry context",
        denominator_definition=None,
        aggregation_rule="PRESENCE_FLAG",
        missing_data_policy="NUMERICAL_UNAVAILABLE",
        required_sources=["FINANCIAL_NEWS", "EARNINGS_CALL_TRANSCRIPTS"],
        allowed_derivation_methods=["TEXTUAL_EXTRACTION"],
        description="Identifies commodity context. Monetary or volumetric exposure is marked UNAVAILABLE without numerical data."
    ),
    "SCENARIO_CONDITIONAL_PNL_V1": ExposureMeasureDefinition(
        measure_id="SCENARIO_CONDITIONAL_PNL_V1",
        measure_version="v1.0",
        display_name="Hypothetical Scenario Conditional P&L",
        domain=ExposureDomain.PORTFOLIO,
        unit_dimension="CURRENCY",
        financial_basis="USER_DEFINED_SHOCK_FACTOR",
        numerator_definition="Subject eligible market value * User shock percentage",
        denominator_definition="Total portfolio net asset value",
        aggregation_rule="SUM",
        missing_data_policy="EXCLUDE_UNCOVERED",
        required_sources=["USER_SCENARIO_SPECIFICATION", "PORTFOLIO_POSITIONS"],
        allowed_derivation_methods=["DETERMINISTIC_SHOCK_APPLICATION"],
        description="Conditional profit/loss under user hypothetical assumptions. Explicitly disclaims market prediction."
    )
}


def get_measure_definition(measure_id: str) -> ExposureMeasureDefinition:
    """Retrieve measure definition by id or raise KeyError."""
    if measure_id not in MEASURE_REGISTRY:
        raise KeyError(f"Measure definition '{measure_id}' is not registered.")
    return MEASURE_REGISTRY[measure_id]

