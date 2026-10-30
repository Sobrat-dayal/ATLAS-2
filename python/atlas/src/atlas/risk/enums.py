"""ATLAS Financial Risk Foundation — Enums (Stage 115).

Controlled vocabularies for institutional market-risk measurement,
metric types, estimation models, annualization policies, and calculation statuses.
"""

from enum import Enum


class RiskSubjectType(str, Enum):
    """Scope of the risk measurement."""
    PORTFOLIO = "PORTFOLIO"
    ACCOUNT = "ACCOUNT"
    INSTRUMENT = "INSTRUMENT"


class RiskMetricCode(str, Enum):
    """Canonical risk metric codes."""
    HISTORICAL_REALIZED_VOLATILITY = "HISTORICAL_REALIZED_VOLATILITY"
    HISTORICAL_RETURN_VARIANCE = "HISTORICAL_RETURN_VARIANCE"
    ROLLING_REALIZED_VOLATILITY = "ROLLING_REALIZED_VOLATILITY"
    HISTORICAL_MAX_DRAWDOWN = "HISTORICAL_MAX_DRAWDOWN"
    CURRENT_DRAWDOWN = "CURRENT_DRAWDOWN"
    DRAWDOWN_DURATION = "DRAWDOWN_DURATION"
    BENCHMARK_BETA = "BENCHMARK_BETA"
    BENCHMARK_CORRELATION = "BENCHMARK_CORRELATION"
    HISTORICAL_TRACKING_ERROR = "HISTORICAL_TRACKING_ERROR"
    MODEL_ESTIMATED_PORTFOLIO_VOLATILITY = "MODEL_ESTIMATED_PORTFOLIO_VOLATILITY"
    MODEL_ESTIMATED_PORTFOLIO_VARIANCE = "MODEL_ESTIMATED_PORTFOLIO_VARIANCE"
    MODEL_VOLATILITY_CONTRIBUTION = "MODEL_VOLATILITY_CONTRIBUTION"
    MODEL_VARIANCE_CONTRIBUTION = "MODEL_VARIANCE_CONTRIBUTION"
    DIVERSIFICATION_RATIO = "DIVERSIFICATION_RATIO"
    VALUE_AT_RISK_HISTORICAL = "VALUE_AT_RISK_HISTORICAL"
    VALUE_AT_RISK_PARAMETRIC = "VALUE_AT_RISK_PARAMETRIC"
    VALUE_AT_RISK_MONTE_CARLO = "VALUE_AT_RISK_MONTE_CARLO"
    EXPECTED_SHORTFALL_HISTORICAL = "EXPECTED_SHORTFALL_HISTORICAL"
    EXPECTED_SHORTFALL_PARAMETRIC = "EXPECTED_SHORTFALL_PARAMETRIC"
    EXPECTED_SHORTFALL_MONTE_CARLO = "EXPECTED_SHORTFALL_MONTE_CARLO"
    SCENARIO_PNL = "SCENARIO_PNL"
    SCENARIO_RETURN = "SCENARIO_RETURN"
    VAR_EXCEPTION_RATE = "VAR_EXCEPTION_RATE"
    FACTOR_EXPOSURE = "FACTOR_EXPOSURE"
    FACTOR_VARIANCE_CONTRIBUTION = "FACTOR_VARIANCE_CONTRIBUTION"
    FACTOR_VOLATILITY_CONTRIBUTION = "FACTOR_VOLATILITY_CONTRIBUTION"
    SYSTEMATIC_VARIANCE = "SYSTEMATIC_VARIANCE"
    SPECIFIC_VARIANCE = "SPECIFIC_VARIANCE"
    HERFINDAHL_HIRSCHMAN_INDEX = "HERFINDAHL_HIRSCHMAN_INDEX"
    EFFECTIVE_NUMBER_HOLDINGS = "EFFECTIVE_NUMBER_HOLDINGS"
    TOP_N_CONCENTRATION = "TOP_N_CONCENTRATION"
    ISSUER_CONCENTRATION = "ISSUER_CONCENTRATION"
    FX_VOLATILITY = "FX_VOLATILITY"
    FX_SENSITIVITY_BETA = "FX_SENSITIVITY_BETA"
    SECTOR_VARIANCE_CONTRIBUTION = "SECTOR_VARIANCE_CONTRIBUTION"
    SECTOR_VOLATILITY_CONTRIBUTION = "SECTOR_VOLATILITY_CONTRIBUTION"
    OPTION_DELTA = "OPTION_DELTA"
    OPTION_GAMMA = "OPTION_GAMMA"
    OPTION_VEGA = "OPTION_VEGA"
    OPTION_THETA = "OPTION_THETA"
    OPTION_RHO = "OPTION_RHO"
    BOND_MACAULAY_DURATION = "BOND_MACAULAY_DURATION"
    BOND_MODIFIED_DURATION = "BOND_MODIFIED_DURATION"
    BOND_CONVEXITY = "BOND_CONVEXITY"
    BOND_DV01 = "BOND_DV01"
    BOND_KEY_RATE_DURATION = "BOND_KEY_RATE_DURATION"
    BOND_YTM = "BOND_YTM"


class RiskModelType(str, Enum):
    """Underlying risk calculation methodologies."""
    HISTORICAL_RETURN_STATISTICS = "HISTORICAL_RETURN_STATISTICS"
    HISTORICAL_DRAWDOWN = "HISTORICAL_DRAWDOWN"
    BENCHMARK_SENSITIVITY = "BENCHMARK_SENSITIVITY"
    COVARIANCE_BASED_PORTFOLIO_RISK = "COVARIANCE_BASED_PORTFOLIO_RISK"
    HISTORICAL_SIMULATION_VAR = "HISTORICAL_SIMULATION_VAR"
    PARAMETRIC_NORMAL_VAR = "PARAMETRIC_NORMAL_VAR"
    MONTE_CARLO_VAR = "MONTE_CARLO_VAR"
    SCENARIO_ANALYSIS = "SCENARIO_ANALYSIS"
    MULTI_FACTOR_EQUITY = "MULTI_FACTOR_EQUITY"
    CONCENTRATION_HERFINDAHL = "CONCENTRATION_HERFINDAHL"
    CURRENCY_DENOMINATION_SENSITIVITY = "CURRENCY_DENOMINATION_SENSITIVITY"
    SECTOR_EULER_DECOMPOSITION = "SECTOR_EULER_DECOMPOSITION"
    BLACK_SCHOLES_MERTON = "BLACK_SCHOLES_MERTON"
    BOND_DISCOUNTED_CASHFLOW = "BOND_DISCOUNTED_CASHFLOW"


class RiskCalculationStatus(str, Enum):
    """Lifecycle status of a risk run."""
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    INCOMPLETE = "INCOMPLETE"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class RiskMetricStatus(str, Enum):
    """Operational status of an individual calculated metric."""
    AVAILABLE = "AVAILABLE"
    AVAILABLE_WITH_WARNINGS = "AVAILABLE_WITH_WARNINGS"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    MISSING_PRICE_DATA = "MISSING_PRICE_DATA"
    MISSING_FX_DATA = "MISSING_FX_DATA"
    MISSING_BENCHMARK_DATA = "MISSING_BENCHMARK_DATA"
    INVALID_NUMERICAL_DOMAIN = "INVALID_NUMERICAL_DOMAIN"
    UNSUPPORTED_INSTRUMENT = "UNSUPPORTED_INSTRUMENT"
    SOURCE_RESTRICTED = "SOURCE_RESTRICTED"
    UNAVAILABLE = "UNAVAILABLE"


class RiskReturnFrequency(str, Enum):
    """Sampling frequency for return observations."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class AnnualizationPolicy(str, Enum):
    """Policy for square-root-of-time scaling convention."""
    DAYS_252 = "DAYS_252"      # sqrt(252)
    DAYS_260 = "DAYS_260"      # sqrt(260)
    WEEKS_52 = "WEEKS_52"      # sqrt(52)
    MONTHS_12 = "MONTHS_12"    # sqrt(12)
    NONE = "NONE"              # sqrt(1) = 1.0


class DataCoverageStatus(str, Enum):
    """Completeness rating for observation input data."""
    FULL_COVERAGE = "FULL_COVERAGE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    MISSING_DATA = "MISSING_DATA"


class ReturnBasis(str, Enum):
    """Return computation basis."""
    TOTAL_RETURN = "TOTAL_RETURN"
    PRICE_RETURN = "PRICE_RETURN"


class DrawdownEpisodeStatus(str, Enum):
    """Drawdown episode recovery state."""
    RECOVERED = "RECOVERED"
    ONGOING = "ONGOING"


class VaRModelType(str, Enum):
    """Methodology for estimating Value at Risk."""
    HISTORICAL_SIMULATION = "HISTORICAL_SIMULATION"
    PARAMETRIC_NORMAL = "PARAMETRIC_NORMAL"
    MONTE_CARLO_GAUSSIAN = "MONTE_CARLO_GAUSSIAN"


class ExpectedShortfallMethod(str, Enum):
    """Methodology for estimating Expected Shortfall."""
    EMPIRICAL_TAIL_MEAN = "EMPIRICAL_TAIL_MEAN"
    PARAMETRIC_NORMAL = "PARAMETRIC_NORMAL"
    MONTE_CARLO = "MONTE_CARLO"


class ScenarioType(str, Enum):
    """Classification of risk test scenario."""
    HISTORICAL_REPLAY = "HISTORICAL_REPLAY"
    HYPOTHETICAL_USER_DEFINED = "HYPOTHETICAL_USER_DEFINED"


class ScenarioShockType(str, Enum):
    """Nature of shock perturbation applied."""
    SECURITY_PRICE_PERCENT_SHOCK = "SECURITY_PRICE_PERCENT_SHOCK"
    ELIGIBLE_GROUP_PERCENT_SHOCK = "ELIGIBLE_GROUP_PERCENT_SHOCK"
    FX_RATE_PERCENT_SHOCK = "FX_RATE_PERCENT_SHOCK"
    PORTFOLIO_WIDE_ELIGIBLE_SHOCK = "PORTFOLIO_WIDE_ELIGIBLE_SHOCK"


class ShockTargetType(str, Enum):
    """Target category receiving a shock perturbation."""
    SECURITY = "SECURITY"
    SECTOR = "SECTOR"
    CURRENCY = "CURRENCY"
    PORTFOLIO = "PORTFOLIO"


class KupiecTestStatus(str, Enum):
    """Statistical outcome of the Kupiec Unconditional Coverage test."""
    ACCEPT_UNCONDITIONAL_COVERAGE = "ACCEPT_UNCONDITIONAL_COVERAGE"
    REJECT_TOO_MANY_EXCEPTIONS = "REJECT_TOO_MANY_EXCEPTIONS"
    REJECT_TOO_FEW_EXCEPTIONS = "REJECT_TOO_FEW_EXCEPTIONS"
    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"




# ---------------------------------------------------------------------------
# Stage 117: Factor, Concentration, Currency, and Sector Risk Enums
# ---------------------------------------------------------------------------


class FactorFamily(str, Enum):
    """Classification family for systematic economic risk factors."""
    MARKET = "MARKET"
    STYLE = "STYLE"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    COUNTRY = "COUNTRY"
    CURRENCY = "CURRENCY"
    MACROECONOMIC = "MACROECONOMIC"


class FactorReturnBasis(str, Enum):
    """Basis of factor returns."""
    EXCESS_RETURN = "EXCESS_RETURN"
    RAW_RETURN = "RAW_RETURN"


class ConcentrationDimension(str, Enum):
    """Dimension over which concentration is partitioned."""
    SECURITY = "SECURITY"
    ISSUER = "ISSUER"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    ASSET_CLASS = "ASSET_CLASS"
    COUNTRY = "COUNTRY"
    CURRENCY = "CURRENCY"


class CurrencyExposureType(str, Enum):
    """Type of currency exposure classification."""
    DENOMINATION = "DENOMINATION"
    ECONOMIC_SENSITIVITY = "ECONOMIC_SENSITIVITY"
    CASH_BALANCE = "CASH_BALANCE"


class ModelDiagnosticStatus(str, Enum):
    """Statistical health condition of a calibrated risk model."""
    HEALTHY = "HEALTHY"
    WARNING_RANK_DEFICIENT = "WARNING_RANK_DEFICIENT"
    WARNING_COLLINEARITY = "WARNING_COLLINEARITY"
    WARNING_INSUFFICIENT_OBSERVATIONS = "WARNING_INSUFFICIENT_OBSERVATIONS"
    WARNING_NON_PSD_COVARIANCE = "WARNING_NON_PSD_COVARIANCE"



# ---------------------------------------------------------------------------
# Stage 118: Options and Fixed-Income Risk Foundations Enums
# ---------------------------------------------------------------------------


class OptionType(str, Enum):
    """Option contract direction/right."""
    CALL = "CALL"
    PUT = "PUT"


class ExerciseStyle(str, Enum):
    """Option exercise rights schedule."""
    EUROPEAN = "EUROPEAN"
    AMERICAN = "AMERICAN"
    BERMUDAN = "BERMUDAN"


class OptionSettlementType(str, Enum):
    """Settlement mechanism for derivatives."""
    PHYSICAL = "PHYSICAL"
    CASH = "CASH"


class OptionContractStatus(str, Enum):
    """Operational status of an option contract."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    EXERCISED = "EXERCISED"
    ASSIGNED = "ASSIGNED"
    SETTLED = "SETTLED"
    UNSUPPORTED = "UNSUPPORTED"


class OptionsPricingModelId(str, Enum):
    """Methodology used for option pricing and Greeks calculation."""
    EUROPEAN_BLACK_SCHOLES_MERTON = "EUROPEAN_BLACK_SCHOLES_MERTON"
    EUROPEAN_BLACK_76 = "EUROPEAN_BLACK_76"
    VENDOR_SOURCED = "VENDOR_SOURCED"
    NUMERICAL_BUMP_REPRICE = "NUMERICAL_BUMP_REPRICE"


class CouponType(str, Enum):
    """Fixed-income coupon structure type."""
    FIXED = "FIXED"
    ZERO_COUPON = "ZERO_COUPON"
    FLOATING = "FLOATING"
    STEP_UP = "STEP_UP"


class CouponFrequency(str, Enum):
    """Annual frequency of coupon payments."""
    ANNUAL = "ANNUAL"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    QUARTERLY = "QUARTERLY"
    MONTHLY = "MONTHLY"

    @property
    def periods_per_year(self) -> int:
        if self == CouponFrequency.ANNUAL:
            return 1
        elif self == CouponFrequency.SEMI_ANNUAL:
            return 2
        elif self == CouponFrequency.QUARTERLY:
            return 4
        elif self == CouponFrequency.MONTHLY:
            return 12
        return 1


class DayCountConvention(str, Enum):
    """Day count convention for bond accrual and year-fraction calculation."""
    ACT_ACT = "ACT_ACT"
    ACT_365F = "ACT_365F"
    ACT_360 = "ACT_360"
    THIRTY_360 = "THIRTY_360"


class BondPricingModelId(str, Enum):
    """Methodology used for bond pricing, yield solving, and duration/convexity."""
    DISCOUNTED_CASHFLOW = "DISCOUNTED_CASHFLOW"
    YIELD_DURATION_CONVEXITY = "YIELD_DURATION_CONVEXITY"
    CURVE_BUMP_REPRICE = "CURVE_BUMP_REPRICE"


class YieldCurveInterpolation(str, Enum):
    """Interpolation method across interest rate curve tenors."""
    LINEAR = "LINEAR"
    CUBIC_SPLINE = "CUBIC_SPLINE"
    FLAT_FORWARD = "FLAT_FORWARD"
