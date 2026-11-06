"""
Custom Tool Registry and Testing Lab Service for Stage 149.
Enables developers to define, validate, test, version, and execute custom tools
under zero-trust schemas and financial safety constraints.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple

from atlas.ecosystem.domain import (
    CustomToolDefinition,
    CustomToolTestFixture,
    CustomToolTestResult,
    ToolExecutionAdapter,
    ToolSideEffectClass,
    utc_now,
)
from atlas.ecosystem.errors import (
    CustomToolExecutionError,
    CustomToolNotFoundError,
    CustomToolValidationError,
    FinancialSafetyViolationError,
)

PROHIBITED_TOOL_REGEX = re.compile(r".*(broker|trade|order|buy|sell|transact|wire).*", re.IGNORECASE)


def validate_schema_dict(schema: Dict[str, Any], name: str = "schema") -> None:
    """Validates that a dictionary conforms to basic JSON Schema structure."""
    if not isinstance(schema, dict):
        raise CustomToolValidationError(f"Invalid {name}: must be a dictionary.")
    if "type" not in schema:
        raise CustomToolValidationError(f"Invalid {name}: missing required top-level 'type' field.")
    valid_types = ("object", "array", "string", "number", "integer", "boolean", "null")
    if schema["type"] not in valid_types:
        raise CustomToolValidationError(f"Invalid {name} type '{schema['type']}': must be one of {valid_types}.")


def validate_payload_against_schema(payload: Any, schema: Dict[str, Any]) -> None:
    """Performs lightweight structural JSON Schema validation."""
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(payload, dict):
            raise CustomToolValidationError(f"Schema violation: expected object, got {type(payload).__name__}.")
        required = schema.get("required", [])
        for field in required:
            if field not in payload:
                raise CustomToolValidationError(f"Schema violation: missing required field '{field}'.")
    elif expected_type == "array":
        if not isinstance(payload, list):
            raise CustomToolValidationError(f"Schema violation: expected array, got {type(payload).__name__}.")
    elif expected_type == "string":
        if not isinstance(payload, str):
            raise CustomToolValidationError(f"Schema violation: expected string, got {type(payload).__name__}.")
    elif expected_type in ("number", "integer"):
        if not isinstance(payload, (int, float)):
            raise CustomToolValidationError(f"Schema violation: expected number, got {type(payload).__name__}.")


class CustomToolRegistryService:
    """
    Manages custom tool definitions, versions, and verification test executions.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, CustomToolDefinition] = {}
        self._versions: Dict[str, List[CustomToolDefinition]] = {}
        self._seed_default_tools()

    def _seed_default_tools(self) -> None:
        """Seeds trusted baseline custom tools."""
        default_tools = [
            CustomToolDefinition(
                tool_id="atlas.custom.discounted_cash_flow",
                publisher_id="atlas-official",
                name="DCF Valuation Calculator",
                description="Computes enterprise value and implied equity value from free cash flow projections.",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "fcf_projections": {"type": "array"},
                        "discount_rate": {"type": "number"},
                        "terminal_growth_rate": {"type": "number"},
                        "net_debt": {"type": "number"},
                        "shares_outstanding": {"type": "number"},
                    },
                    "required": ["fcf_projections", "discount_rate", "terminal_growth_rate"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "enterprise_value": {"type": "number"},
                        "implied_share_price": {"type": "number"},
                        "pv_projected_fcf": {"type": "number"},
                        "pv_terminal_value": {"type": "number"},
                    },
                    "required": ["enterprise_value", "implied_share_price"],
                },
                required_scopes=("tools:calculate",),
                side_effect_class=ToolSideEffectClass.READ_ONLY,
                execution_adapter=ToolExecutionAdapter.TRANSFORMATION,
                is_published=True,
            ),
            CustomToolDefinition(
                tool_id="atlas.custom.wacc_calculator",
                publisher_id="atlas-official",
                name="Weighted Average Cost of Capital (WACC)",
                description="Calculates firm WACC given cost of equity, after-tax cost of debt, and capital weights.",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "cost_of_equity": {"type": "number"},
                        "cost_of_debt": {"type": "number"},
                        "tax_rate": {"type": "number"},
                        "equity_weight": {"type": "number"},
                        "debt_weight": {"type": "number"},
                    },
                    "required": ["cost_of_equity", "cost_of_debt", "tax_rate", "equity_weight", "debt_weight"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "wacc": {"type": "number"},
                        "after_tax_cost_of_debt": {"type": "number"},
                    },
                    "required": ["wacc"],
                },
                required_scopes=("tools:calculate",),
                side_effect_class=ToolSideEffectClass.READ_ONLY,
                execution_adapter=ToolExecutionAdapter.TRANSFORMATION,
                is_published=True,
            ),
        ]
        for t in default_tools:
            self._tools[t.tool_id] = t
            self._versions[t.tool_id] = [t]

    def register_tool(
        self,
        *,
        tool_id: str,
        publisher_id: str,
        name: str,
        description: str,
        version: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        required_scopes: Tuple[str, ...],
        side_effect_class: ToolSideEffectClass,
        execution_adapter: ToolExecutionAdapter,
        timeout_seconds: int = 15,
        retry_policy: Optional[Dict[str, Any]] = None,
        resource_policy: Optional[Dict[str, Any]] = None,
        declarative_config: Optional[Dict[str, Any]] = None,
    ) -> CustomToolDefinition:
        # Financial safety check
        if PROHIBITED_TOOL_REGEX.match(tool_id) or PROHIBITED_TOOL_REGEX.match(name):
            raise FinancialSafetyViolationError(
                f"Prohibited tool ID or name '{tool_id}': Live broker order execution is barred."
            )

        validate_schema_dict(input_schema, name="input_schema")
        validate_schema_dict(output_schema, name="output_schema")

        tool = CustomToolDefinition(
            tool_id=tool_id,
            publisher_id=publisher_id,
            name=name,
            description=description,
            version=version,
            input_schema=input_schema,
            output_schema=output_schema,
            required_scopes=required_scopes,
            side_effect_class=side_effect_class,
            execution_adapter=execution_adapter,
            timeout_seconds=timeout_seconds,
            retry_policy=retry_policy or {},
            resource_policy=resource_policy or {},
            declarative_config=declarative_config or {},
            is_published=False,
        )
        self._tools[tool_id] = tool
        self._versions.setdefault(tool_id, []).append(tool)
        return tool

    def get_tool(self, tool_id: str) -> CustomToolDefinition:
        tool = self._tools.get(tool_id)
        if not tool:
            raise CustomToolNotFoundError(f"Custom Tool '{tool_id}' was not found.")
        return tool

    def list_tools(self, published_only: bool = False) -> List[CustomToolDefinition]:
        if published_only:
            return [t for t in self._tools.values() if t.is_published]
        return list(self._tools.values())

    def get_tool_versions(self, tool_id: str) -> List[CustomToolDefinition]:
        if tool_id not in self._versions:
            raise CustomToolNotFoundError(f"Custom Tool '{tool_id}' has no registered versions.")
        return list(self._versions[tool_id])

    def publish_tool(self, tool_id: str) -> CustomToolDefinition:
        tool = self.get_tool(tool_id)
        published = CustomToolDefinition(
            tool_id=tool.tool_id,
            publisher_id=tool.publisher_id,
            name=tool.name,
            description=tool.description,
            version=tool.version,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
            required_scopes=tool.required_scopes,
            side_effect_class=tool.side_effect_class,
            execution_adapter=tool.execution_adapter,
            timeout_seconds=tool.timeout_seconds,
            retry_policy=tool.retry_policy,
            resource_policy=tool.resource_policy,
            declarative_config=tool.declarative_config,
            is_published=True,
            created_at=tool.created_at,
            updated_at=utc_now(),
        )
        self._tools[tool_id] = published
        return published

    # -----------------------------------------------------------------------
    # Testing Lab & Execution
    # -----------------------------------------------------------------------

    def test_tool(
        self,
        *,
        test_id: str,
        tool_id: str,
        input_payload: Dict[str, Any],
        mock_responses: Optional[Dict[str, Any]] = None,
    ) -> CustomToolTestResult:
        """Runs fixture test verifying input validation and output schema compliance."""
        tool = self.get_tool(tool_id)
        start = time.perf_counter()

        try:
            # 1. Validate Input Payload against input_schema
            validate_payload_against_schema(input_payload, tool.input_schema)

            # 2. Execute Transformation / Mock
            output_payload = self._execute_tool_logic(tool, input_payload, mock_responses or {})

            # 3. Validate Output Payload against output_schema
            validate_payload_against_schema(output_payload, tool.output_schema)

            duration = round((time.perf_counter() - start) * 1000, 2)
            return CustomToolTestResult(
                test_id=test_id,
                tool_id=tool_id,
                passed=True,
                output_payload=output_payload,
                duration_ms=duration,
            )
        except Exception as exc:
            duration = round((time.perf_counter() - start) * 1000, 2)
            return CustomToolTestResult(
                test_id=test_id,
                tool_id=tool_id,
                passed=False,
                error_message=str(exc),
                duration_ms=duration,
            )

    def _execute_tool_logic(
        self,
        tool: CustomToolDefinition,
        input_payload: Dict[str, Any],
        mock_responses: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Executes transformation algorithms or declarative handlers."""
        if tool.tool_id == "atlas.custom.discounted_cash_flow":
            fcf = input_payload.get("fcf_projections", [100.0, 110.0, 120.0])
            r = float(input_payload.get("discount_rate", 0.09))
            g = float(input_payload.get("terminal_growth_rate", 0.025))
            net_debt = float(input_payload.get("net_debt", 50.0))
            shares = float(input_payload.get("shares_outstanding", 20.0))

            pv_fcf = sum(cf / ((1.0 + r) ** (i + 1)) for i, cf in enumerate(fcf))
            final_fcf = fcf[-1] * (1.0 + g)
            terminal_val = final_fcf / (r - g) if r > g else final_fcf / 0.05
            pv_terminal = terminal_val / ((1.0 + r) ** len(fcf))
            ev = round(pv_fcf + pv_terminal, 2)
            implied_equity = ev - net_debt
            share_price = round(implied_equity / shares, 2) if shares > 0 else 0.0

            return {
                "enterprise_value": ev,
                "implied_share_price": share_price,
                "pv_projected_fcf": round(pv_fcf, 2),
                "pv_terminal_value": round(pv_terminal, 2),
            }

        elif tool.tool_id == "atlas.custom.wacc_calculator":
            ke = float(input_payload["cost_of_equity"])
            kd = float(input_payload["cost_of_debt"])
            t = float(input_payload["tax_rate"])
            we = float(input_payload["equity_weight"])
            wd = float(input_payload["debt_weight"])

            after_tax_kd = round(kd * (1.0 - t), 4)
            wacc = round((we * ke) + (wd * after_tax_kd), 4)
            return {
                "wacc": wacc,
                "after_tax_cost_of_debt": after_tax_kd,
            }

        elif mock_responses:
            return dict(mock_responses)

        else:
            # Default echo transformation for user-registered custom tools
            return {
                "result": "Transformation completed",
                "processed_fields": list(input_payload.keys()),
            }

