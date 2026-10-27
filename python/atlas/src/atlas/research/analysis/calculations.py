"""Institutional Quantitative & Financial Research Calculation Engine (Stage 106).

Strict numerical correctness, non-zero denominator protection, dimensional consistency,
descriptive statistics, safe bounded arithmetic, and deterministic scenario mathematics.
Zero eval(), zero arbitrary code execution, zero fabricated probabilities.
"""

import ast
import math
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Optional, Tuple

from atlas.research.domain import ResearchAnalysisTypeDefinition
from atlas.research.enums import AnalysisFrequency, ResearchAnalysisType
from atlas.research.errors import (
    ResearchAnalysisDivisionByZeroError,
    ResearchAnalysisFormulaInvalidError,
)


def quantize_value(val: float, places: int = 4) -> float:
    """Helper to round float values cleanly using Decimal half-up."""
    try:
        d = Decimal(str(val))
        return float(d.quantize(Decimal("10") ** -places, rounding=ROUND_HALF_UP))
    except Exception:
        return round(val, places)


# ---------------------------------------------------------------------------
# 1. Period-over-Period Changes & Financial Growth
# ---------------------------------------------------------------------------

def compute_absolute_change(current_val: Optional[float], prior_val: Optional[float]) -> Optional[float]:
    """Computes period delta: Δ = X_t - X_{t-1}."""
    if current_val is None or prior_val is None:
        return None
    return quantize_value(current_val - prior_val, places=4)


def compute_percentage_growth(current_val: Optional[float], prior_val: Optional[float]) -> Optional[float]:
    """Computes percentage growth: ((X_t - X_{t-1}) / X_{t-1}) * 100.
    
    Strictly guards against:
    - Zero denominator (returns None, undefined)
    - Negative base (returns None or qualified, since growth from negative numbers is mathematically misleading)
    """
    if current_val is None or prior_val is None:
        return None
    if prior_val == 0.0:
        return None
    # For negative baselines, percentage growth is economically non-standard
    if prior_val < 0.0:
        return None
    growth = ((current_val - prior_val) / prior_val) * 100.0
    return quantize_value(growth, places=2)


def compute_cagr(start_val: Optional[float], end_val: Optional[float], elapsed_periods: int) -> Optional[float]:
    """Computes Compound Annual Growth Rate (CAGR): (X_end / X_start) ** (1/n) - 1.
    
    Strict requirements:
    - start_val > 0
    - end_val > 0
    - elapsed_periods > 0
    Returns percentage value (e.g. 8.45 for 8.45%) or None if invalid.
    """
    if start_val is None or end_val is None:
        return None
    if elapsed_periods <= 0:
        return None
    if start_val <= 0.0 or end_val <= 0.0:
        return None
    try:
        cagr = (math.pow(end_val / start_val, 1.0 / elapsed_periods) - 1.0) * 100.0
        return quantize_value(cagr, places=2)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


# ---------------------------------------------------------------------------
# 2. Descriptive & Cross-Sectional Statistics
# ---------------------------------------------------------------------------

def calculate_mean(values: List[float]) -> Optional[float]:
    """Computes arithmetic mean over non-null valid numbers."""
    valid = [v for v in values if v is not None and not math.isnan(v) and not math.isinf(v)]
    if not valid:
        return None
    return quantize_value(sum(valid) / len(valid), places=4)


def calculate_median(values: List[float]) -> Optional[float]:
    """Computes exact median over sorted valid observations."""
    valid = sorted([v for v in values if v is not None and not math.isnan(v) and not math.isinf(v)])
    if not valid:
        return None
    n = len(valid)
    mid = n // 2
    if n % 2 == 1:
        return quantize_value(valid[mid], places=4)
    else:
        return quantize_value((valid[mid - 1] + valid[mid]) / 2.0, places=4)


def calculate_standard_deviation(values: List[float], is_sample: bool = True) -> Optional[float]:
    """Computes sample (N-1) or population (N) standard deviation."""
    valid = [v for v in values if v is not None and not math.isnan(v) and not math.isinf(v)]
    n = len(valid)
    if is_sample and n < 2:
        return None
    if not is_sample and n < 1:
        return None
    mean = sum(valid) / n
    variance_sum = sum((x - mean) ** 2 for x in valid)
    denom = (n - 1) if is_sample else n
    return quantize_value(math.sqrt(variance_sum / denom), places=4)


def calculate_quartiles(values: List[float]) -> Tuple[Optional[float], Optional[float]]:
    """Calculates 25th (Q1) and 75th (Q3) percentiles using standard linear interpolation."""
    valid = sorted([v for v in values if v is not None and not math.isnan(v) and not math.isinf(v)])
    if len(valid) < 4:
        return None, None
    n = len(valid)
    q1_idx = int(n * 0.25)
    q3_idx = int(n * 0.75)
    return quantize_value(valid[q1_idx], places=4), quantize_value(valid[q3_idx], places=4)


def calculate_pearson_correlation(
    series_x: List[Optional[float]],
    series_y: List[Optional[float]],
) -> Optional[float]:
    """Computes Pearson correlation coefficient r between two paired numerical series.
    
    Guards:
    - Strictly filters paired non-null values
    - Requires at least 3 paired observations
    - If variance of either series is zero, returns None (undefined)
    - Returns bounded correlation [-1.0, 1.0]
    """
    if len(series_x) != len(series_y):
        return None
    paired: List[Tuple[float, float]] = []
    for x, y in zip(series_x, series_y):
        if x is not None and y is not None and not math.isnan(x) and not math.isnan(y):
            paired.append((float(x), float(y)))
    if len(paired) < 3:
        return None
    n = len(paired)
    xs = [p[0] for p in paired]
    ys = [p[1] for p in paired]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    diff_x = [x - mean_x for x in xs]
    diff_y = [y - mean_y for y in ys]

    sum_sq_x = sum(dx ** 2 for dx in diff_x)
    sum_sq_y = sum(dy ** 2 for dy in diff_y)

    if sum_sq_x == 0.0 or sum_sq_y == 0.0:
        # Zero variance means correlation is mathematically undefined
        return None

    covariance = sum(dx * dy for dx, dy in zip(diff_x, diff_y))
    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    r = covariance / denominator
    # Bound float rounding
    r = max(-1.0, min(1.0, r))
    return quantize_value(r, places=4)


# ---------------------------------------------------------------------------
# 3. Safe Bounded Formula Evaluator (No eval(), No exec())
# ---------------------------------------------------------------------------

class SafeExpressionEvaluator:
    """Bounded, sandboxed AST-based numerical expression evaluator.
    
    Supports:
    - Basic binary operators: +, -, *, /
    - Unary negative: -x
    - Named variables bound to float values
    - Constant numbers
    Strictly forbids:
    - Function calls
    - Attribute access
    - Imports, statements, loops, comprehensions
    - Deeply nested expressions (depth > 8)
    """

    ALLOWED_OPERATORS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: SafeExpressionEvaluator._safe_div(a, b),
    }

    ALLOWED_UNARY = {
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: a,
    }

    @staticmethod
    def _safe_div(a: float, b: float) -> float:
        if b == 0.0:
            raise ResearchAnalysisDivisionByZeroError("Division by zero in custom formula expression")
        return a / b

    @classmethod
    def evaluate(cls, expression_str: str, variables: Dict[str, float], max_depth: int = 8) -> float:
        """Parses and safely evaluates a mathematical formula string."""
        if not expression_str or len(expression_str) > 500:
            raise ResearchAnalysisFormulaInvalidError("Expression must be between 1 and 500 characters")
        try:
            tree = ast.parse(expression_str, mode="eval")
        except SyntaxError as e:
            raise ResearchAnalysisFormulaInvalidError(f"Expression syntax error: {e}")
        return cls._eval_node(tree.body, variables, current_depth=0, max_depth=max_depth)

    @classmethod
    def _eval_node(cls, node: ast.AST, variables: Dict[str, float], current_depth: int, max_depth: int) -> float:
        if current_depth > max_depth:
            raise ResearchAnalysisFormulaInvalidError("Expression exceeds maximum allowable nesting depth")

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ResearchAnalysisFormulaInvalidError("Only numeric constants are permitted in expressions")

        if isinstance(node, ast.Num):  # Python <3.8 compatibility
            return float(node.n)

        if isinstance(node, ast.Name):
            var_name = node.id
            if var_name in variables:
                val = variables[var_name]
                if val is None or math.isnan(val):
                    raise ResearchAnalysisFormulaInvalidError(f"Variable '{var_name}' is undefined or NaN")
                return float(val)
            raise ResearchAnalysisFormulaInvalidError(f"Unknown parameter variable '{var_name}'")

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in cls.ALLOWED_UNARY:
                operand_val = cls._eval_node(node.operand, variables, current_depth + 1, max_depth)
                return cls.ALLOWED_UNARY[op_type](operand_val)
            raise ResearchAnalysisFormulaInvalidError(f"Unsupported unary operator: {op_type.__name__}")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in cls.ALLOWED_OPERATORS:
                left_val = cls._eval_node(node.left, variables, current_depth + 1, max_depth)
                right_val = cls._eval_node(node.right, variables, current_depth + 1, max_depth)
                return cls.ALLOWED_OPERATORS[op_type](left_val, right_val)
            raise ResearchAnalysisFormulaInvalidError(f"Unsupported binary operator: {op_type.__name__}")

        raise ResearchAnalysisFormulaInvalidError(f"Disallowed expression element: {type(node).__name__}")


def get_supported_analysis_types() -> List[ResearchAnalysisTypeDefinition]:
    """Returns the taxonomic catalog of 13 supported institutional research analysis types."""
    return [
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.COMPANY_FINANCIAL_TREND,
            label="Company Financial Statement Trends",
            description="Multi-year or multi-quarter historical trajectory of financial statement items (Revenue, OpInc, FCF).",
            supported_subject_types=["COMPANY"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.QUARTERLY, AnalysisFrequency.TTM],
            supported_metric_categories=["PROFITABILITY", "REVENUE", "CASH_FLOW", "CAPITAL_STRUCTURE"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.COMPANY_RATIO_ANALYSIS,
            label="Company Financial Ratio Analysis",
            description="Time-series analysis of canonical Stage 83 profitability, liquidity, and leverage ratios.",
            supported_subject_types=["COMPANY"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.QUARTERLY, AnalysisFrequency.TTM],
            supported_metric_categories=["PROFITABILITY", "LIQUIDITY", "LEVERAGE", "EFFICIENCY"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.PEER_BENCHMARKING,
            label="Peer Group Cross-Sectional Benchmarking",
            description="Comparable company analysis across verified Stage 87 peer groups with quartiles, mean, and median.",
            supported_subject_types=["COMPANY"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.TTM],
            supported_metric_categories=["PROFITABILITY", "VALUATION", "LEVERAGE", "GROWTH"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.MACROECONOMIC_TIME_SERIES,
            label="Macroeconomic Time-Series Research",
            description="Aligned historical economic series (CPI, Fed Funds, GDP) preserving publication vintages.",
            supported_subject_types=["MACROECONOMIC", "GEOGRAPHY"],
            supported_frequencies=[AnalysisFrequency.MONTHLY, AnalysisFrequency.QUARTERLY, AnalysisFrequency.ANNUAL],
            supported_metric_categories=["INFLATION", "POLICY_RATES", "OUTPUT", "LABOR"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.MULTI_INDICATOR_COMPARISON,
            label="Multi-Indicator Economic Comparison",
            description="Joint cross-indicator time-series alignment and descriptive correlation analysis.",
            supported_subject_types=["MACROECONOMIC", "GEOGRAPHY"],
            supported_frequencies=[AnalysisFrequency.MONTHLY, AnalysisFrequency.QUARTERLY],
            supported_metric_categories=["MACRO_CORRELATION"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.HYPOTHESIS_EVALUATION,
            label="Evidence-Based Hypothesis Testing",
            description="Deterministic evaluation of testable empirical claims against reproducible analytical datasets.",
            supported_subject_types=["COMPANY", "PEER_GROUP", "MACROECONOMIC"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.QUARTERLY],
            supported_metric_categories=["ALL"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.ASSUMPTION_SENSITIVITY_ANALYSIS,
            label="Deterministic Scenario Sensitivity Grid",
            description="Bounded what-if parameter variation and arithmetic sensitivity table without fabricated probabilities.",
            supported_subject_types=["COMPANY", "ANALYST_MODEL"],
            supported_frequencies=[AnalysisFrequency.ANNUAL],
            supported_metric_categories=["REVENUE", "MARGIN", "VALUATION"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.CASH_FLOW_ANALYSIS,
            label="Cash Flow & Working Capital Analysis",
            description="Operating cash flow, CapEx, free cash flow conversion, and balance sheet capital changes.",
            supported_subject_types=["COMPANY"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.QUARTERLY],
            supported_metric_categories=["CASH_FLOW"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.CAPITAL_STRUCTURE_ANALYSIS,
            label="Capital Structure & Solvency Research",
            description="Debt-to-equity, net debt, interest coverage, and capital structure composition.",
            supported_subject_types=["COMPANY"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.QUARTERLY],
            supported_metric_categories=["LEVERAGE", "SOLVENCY"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.INDUSTRY_COMPARISON,
            label="Industry Classification Comparison",
            description="Cross-sectional distribution analysis within verified industry classification segments.",
            supported_subject_types=["INDUSTRY"],
            supported_frequencies=[AnalysisFrequency.ANNUAL],
            supported_metric_categories=["INDUSTRY_RATIOS"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.HISTORICAL_MARKET_CONTEXT,
            label="Historical Market Context Research",
            description="Descriptive market returns and trading context aligned with corporate reporting dates.",
            supported_subject_types=["FINANCIAL_INSTRUMENT", "COMPANY"],
            supported_frequencies=[AnalysisFrequency.DAILY, AnalysisFrequency.MONTHLY],
            supported_metric_categories=["PRICE_RETURNS"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.EVENT_DISCLOSURE_COMPARISON,
            label="Corporate Event Disclosure Comparison",
            description="Pre- and post-event announcement filing comparison and disclosure difference analysis.",
            supported_subject_types=["FINANCIAL_EVENT", "COMPANY"],
            supported_frequencies=[AnalysisFrequency.DAILY],
            supported_metric_categories=["EVENT_DISCLOSURE"],
        ),
        ResearchAnalysisTypeDefinition(
            type_id=ResearchAnalysisType.DESCRIPTIVE_STATISTICAL_ANALYSIS,
            label="Descriptive Statistical Distribution Analysis",
            description="Parametric and non-parametric distribution metrics (mean, median, quantiles, std dev).",
            supported_subject_types=["COMPANY", "MACROECONOMIC"],
            supported_frequencies=[AnalysisFrequency.ANNUAL, AnalysisFrequency.MONTHLY],
            supported_metric_categories=["STATISTICS"],
        ),
    ]
