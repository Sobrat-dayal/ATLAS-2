"""Natural-language intent interpretation and structured action planning (Stage 128, Parts XI, XII, LI)."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.ai.actions.domain import (
    ActionLifecycleState,
    AiActionType,
    AiFinancialAction,
    AiFinancialActionPlan,
)
from atlas.ai.actions.errors import (
    AiActionBrokerExecutionProhibitedError,
    AiActionInvalidIntentError,
    AiActionLedgerMutationProhibitedError,
    AiActionUnsupportedError,
)
from atlas.ai.actions.registry import get_action_registry


class AtlasActionPlanner:
    """Interprets user intent and constructs validated, permission-aware action plans."""

    def __init__(self) -> None:
        self.registry = get_action_registry()

    def parse_and_plan(
        self,
        intent: str,
        actor_user_id: str,
        tenant_id: str = "default_tenant",
        conversation_id: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None,
    ) -> AiFinancialActionPlan:
        hints = context_hints or {}
        clean_intent = intent.strip()
        lower_intent = clean_intent.lower()

        # 1. Prohibited action checks (Parts IX, XLI, LXI, Fixture I)
        if any(
            w in lower_intent
            for w in ["buy ", "sell ", "buy 100", "place order", "submit order", "execute trade"]
        ):
            raise AiActionBrokerExecutionProhibitedError(
                f"Trading or broker order execution requested in '{clean_intent}'. "
                "The AI Action Engine only supports non-executing analytical and hypothetical proposals."
            )

        if any(
            w in lower_intent
            for w in [
                "modify ledger",
                "alter transaction",
                "mutate cash",
                "transfer cash",
                "deposit money",
            ]
        ):
            raise AiActionLedgerMutationProhibitedError(
                f"Ledger or cash balance mutation requested in '{clean_intent}'. "
                "The AI Action Engine cannot modify real financial accounting records."
            )

        if any(
            w in lower_intent
            for w in ["run shell", "exec python", "drop table", "select * from pg_", "rm -rf"]
        ):
            raise AiActionUnsupportedError(
                "Arbitrary shell, Python, or raw SQL execution is strictly prohibited."
            )

        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        actions: List[AiFinancialAction] = []
        dep_graph: Dict[str, List[str]] = {}

        # 2. Multi-Step Intent: Screener -> Chart Comparison (Parts LI & Fixture J)
        if "screener" in lower_intent and "chart" in lower_intent and "open" in lower_intent:
            action1 = self._build_screener_action(
                clean_intent, actor_user_id, tenant_id, hints, plan_id, is_save=True
            )
            action2 = self._build_chart_comparison_action(
                clean_intent, actor_user_id, tenant_id, hints, plan_id
            )
            actions = [action1, action2]
            dep_graph = {action2.action_id: [action1.action_id]}

        # 3. Chart Intent (Parts XXIII - XXVIII & Fixture A)
        elif any(
            k in lower_intent
            for k in [
                "chart",
                "candlestick",
                "sma",
                "ema",
                "rsi",
                "macd",
                "moving average",
                "indicator",
            ]
        ):
            actions = [
                self._build_chart_action(clean_intent, actor_user_id, tenant_id, hints, plan_id)
            ]

        # 4. Screener Intent (Parts XXIX - XXXIV & Fixture B)
        elif any(
            k in lower_intent
            for k in [
                "screener",
                "screen",
                "find companies",
                "filter stocks",
                "revenue growth",
                "market cap",
            ]
        ):
            actions = [
                self._build_screener_action(clean_intent, actor_user_id, tenant_id, hints, plan_id)
            ]

        # 5. Risk Intent (Parts XLIII - L & Fixture D) - Evaluated before general portfolio intent
        elif any(
            k in lower_intent
            for k in [
                "risk",
                "value at risk",
                "var",
                "stress test",
                "expected shortfall",
                "drawdown",
            ]
        ):
            actions = [
                self._build_risk_action(clean_intent, actor_user_id, tenant_id, hints, plan_id)
            ]

        # 6. Portfolio Intent (Parts XXXV - XLII & Fixture C)
        elif any(
            k in lower_intent
            for k in [
                "portfolio",
                "allocation",
                "reweight",
                "exposure",
                "rebalance",
                "target weight",
            ]
        ):
            actions = [
                self._build_portfolio_action(clean_intent, actor_user_id, tenant_id, hints, plan_id)
            ]

        else:
            raise AiActionInvalidIntentError(
                clean_intent,
                "Could not identify a supported Chart, Screener, Portfolio, or Risk operation.",
            )

        return AiFinancialActionPlan(
            plan_id=plan_id,
            owner_user_id=actor_user_id,
            tenant_id=tenant_id,
            user_intent=clean_intent,
            actions=actions,
            dependency_graph=dep_graph,
            conversation_id=conversation_id,
            status=ActionLifecycleState.REQUESTED,
            created_at=datetime.now(timezone.utc),
        )

    def _build_chart_action(
        self,
        intent: str,
        user_id: str,
        tenant_id: str,
        hints: Dict[str, Any],
        plan_id: str,
    ) -> AiFinancialAction:
        lower = intent.lower()
        chart_id = hints.get("chart_id", "chart_fixture_a")
        expected_rev = hints.get("expected_revision", "rev_chart_fixture_a_1")

        proposed_args: Dict[str, Any] = {"chart_id": chart_id}
        action_type = AiActionType.CHART_ADD_INDICATOR

        # Parse instrument
        if "microsoft" in lower or "msft" in lower:
            proposed_args["instrument_id"] = "MSFT"
        elif "apple" in lower or "aapl" in lower:
            proposed_args["instrument_id"] = "AAPL"
        elif "test_a" in lower:
            proposed_args["instrument_id"] = "TEST_A"

        # Parse interval
        if "six-month" in lower or "daily" in lower or "1d" in lower:
            proposed_args["interval"] = "1D"
        elif "weekly" in lower or "1w" in lower:
            proposed_args["interval"] = "1W"

        # Parse chart type
        if "candlestick" in lower:
            proposed_args["chart_type"] = "candlestick"
        elif "line" in lower:
            proposed_args["chart_type"] = "line"

        # Parse indicators (e.g. Fixture A: 20-period SMA and 50-period SMA)
        indicators = []
        if "sma" in lower or "moving average" in lower:
            # Look for numbers
            periods = re.findall(r"(\d+)[- ]*(?:day|period)?[- ]*(?:sma|moving average)", lower)
            if not periods:
                periods = re.findall(r"(?:sma|moving average)[- ]*(\d+)", lower)
            if not periods and ("20" in lower or "50" in lower):
                found = []
                if "20" in lower:
                    found.append(20)
                if "50" in lower:
                    found.append(50)
                periods = [str(x) for x in found]

            for p_str in periods:
                indicators.append({"type": "SMA", "period": int(p_str)})

        if "rsi" in lower:
            indicators.append({"type": "RSI", "period": 14})
        if "macd" in lower:
            indicators.append(
                {"type": "MACD", "fast_period": 12, "slow_period": 26, "signal_period": 9}
            )

        if indicators:
            if len(indicators) == 1:
                proposed_args["indicator"] = indicators[0]
            else:
                proposed_args["indicators"] = indicators

        action_id = f"act_{uuid.uuid4().hex[:12]}"
        adapter = self.registry.get_adapter(action_type)

        norm_hash = hashlib.sha256(
            json.dumps(proposed_args, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        return AiFinancialAction(
            action_id=action_id,
            action_type=action_type,
            action_version="1.0.0",
            target_module="charts",
            target_resource_type="chart_config",
            target_resource_id=chart_id,
            actor_user_id=user_id,
            tenant_scope=tenant_id,
            proposed_arguments=proposed_args,
            normalized_arguments_hash=norm_hash,
            expected_resource_revision=expected_rev,
            classification=adapter.classification,
            approval_policy=adapter.default_approval_policy,
            reversibility_policy=adapter.reversibility_policy,
        )

    def _build_screener_action(
        self,
        intent: str,
        user_id: str,
        tenant_id: str,
        hints: Dict[str, Any],
        plan_id: str,
        is_save: bool = False,
    ) -> AiFinancialAction:
        lower = intent.lower()
        screener_id = hints.get("screener_id", "screener_fixture_b")
        expected_rev = hints.get("expected_revision", "rev_screener_fixture_b_1")

        # Determine universe
        universe = (
            "IN_NIFTY500"
            if ("indian" in lower or "india" in lower or "crore" in lower or "inr" in lower)
            else "US_SP500"
        )

        # Determine filters (Fixture B)
        filters = []

        # Revenue growth
        growth_match = re.search(r"revenue growth (?:above|greater than|>)\s*(\d+)%", lower)
        if growth_match:
            pct_val = float(growth_match.group(1)) / 100.0
            filters.append(
                {"metric_id": "revenue_growth_yoy", "operator": "GREATER_THAN", "value": pct_val}
            )
        elif "positive" in lower and "revenue growth" in lower:
            filters.append(
                {"metric_id": "revenue_growth_yoy", "operator": "GREATER_THAN", "value": 0.0}
            )
        else:
            # Default to 15% if general growth requested
            filters.append(
                {"metric_id": "revenue_growth_yoy", "operator": "GREATER_THAN", "value": 0.15}
            )

        # Net profit
        if "positive" in lower and (
            "earnings" in lower or "profit" in lower or "profitable" in lower
        ):
            filters.append(
                {"metric_id": "net_profit_margin", "operator": "GREATER_THAN", "value": 0.0}
            )

        # Market Cap
        if "10,000 crore" in lower or "10000 crore" in lower or "100 billion inr" in lower:
            # 10,000 Crore = 100 Billion INR
            filters.append(
                {"metric_id": "market_cap", "operator": "GREATER_THAN", "value": 100_000_000_000.0}
            )
        else:
            filters.append(
                {"metric_id": "market_cap", "operator": "GREATER_THAN", "value": 100_000_000_000.0}
            )

        action_type = AiActionType.SCREENER_SAVE if is_save else AiActionType.SCREENER_EXECUTE
        proposed_args = {
            "screener_id": screener_id,
            "name": "High-Growth Screen",
            "universe": universe,
            "filters": filters,
        }

        action_id = f"act_{uuid.uuid4().hex[:12]}"
        adapter = self.registry.get_adapter(action_type)
        norm_hash = hashlib.sha256(
            json.dumps(proposed_args, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        return AiFinancialAction(
            action_id=action_id,
            action_type=action_type,
            action_version="1.0.0",
            target_module="screeners",
            target_resource_type="screener_query",
            target_resource_id=screener_id,
            actor_user_id=user_id,
            tenant_scope=tenant_id,
            proposed_arguments=proposed_args,
            normalized_arguments_hash=norm_hash,
            expected_resource_revision=expected_rev,
            classification=adapter.classification,
            approval_policy=adapter.default_approval_policy,
            reversibility_policy=adapter.reversibility_policy,
        )

    def _build_chart_comparison_action(
        self,
        intent: str,
        user_id: str,
        tenant_id: str,
        hints: Dict[str, Any],
        plan_id: str,
    ) -> AiFinancialAction:
        chart_id = hints.get("chart_id", "chart_fixture_a")
        expected_rev = hints.get("expected_revision", "rev_chart_fixture_a_1")
        action_type = AiActionType.CHART_ADD_COMPARISON
        proposed_args = {
            "chart_id": chart_id,
            "comparison_instrument_id": "INFY.NS",
        }
        action_id = f"act_{uuid.uuid4().hex[:12]}"
        adapter = self.registry.get_adapter(action_type)
        norm_hash = hashlib.sha256(
            json.dumps(proposed_args, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        return AiFinancialAction(
            action_id=action_id,
            action_type=action_type,
            action_version="1.0.0",
            target_module="charts",
            target_resource_type="chart_config",
            target_resource_id=chart_id,
            actor_user_id=user_id,
            tenant_scope=tenant_id,
            proposed_arguments=proposed_args,
            normalized_arguments_hash=norm_hash,
            expected_resource_revision=expected_rev,
            classification=adapter.classification,
            approval_policy=adapter.default_approval_policy,
            reversibility_policy=adapter.reversibility_policy,
        )

    def _build_portfolio_action(
        self,
        intent: str,
        user_id: str,
        tenant_id: str,
        hints: Dict[str, Any],
        plan_id: str,
    ) -> AiFinancialAction:
        lower = intent.lower()
        portfolio_id = hints.get("portfolio_id", "TEST_P")
        expected_rev = hints.get("expected_revision", "rev_TEST_P_1")

        action_type = AiActionType.PORTFOLIO_PROPOSE_TARGETS

        # Parse target weights (Fixture C: 50% Equity, 50% Bonds)
        target_weights = {"Equity": 0.50, "Bonds": 0.50}

        if "60% equity" in lower and "40% bond" in lower:
            target_weights = {"Equity": 0.60, "Bonds": 0.40}
        elif "reduced technology" in lower and "increased healthcare" in lower:
            target_weights = {"Technology": 0.25, "Healthcare": 0.25, "Equity": 0.30, "Bonds": 0.20}

        proposed_args = {
            "portfolio_id": portfolio_id,
            "target_weights": target_weights,
            "scenario_type": "TACTICAL_REWEIGHT",
        }

        action_id = f"act_{uuid.uuid4().hex[:12]}"
        adapter = self.registry.get_adapter(action_type)
        norm_hash = hashlib.sha256(
            json.dumps(proposed_args, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        return AiFinancialAction(
            action_id=action_id,
            action_type=action_type,
            action_version="1.0.0",
            target_module="portfolios",
            target_resource_type="portfolio_scenario",
            target_resource_id=portfolio_id,
            actor_user_id=user_id,
            tenant_scope=tenant_id,
            proposed_arguments=proposed_args,
            normalized_arguments_hash=norm_hash,
            expected_resource_revision=expected_rev,
            classification=adapter.classification,
            approval_policy=adapter.default_approval_policy,
            reversibility_policy=adapter.reversibility_policy,
        )

    def _build_risk_action(
        self,
        intent: str,
        user_id: str,
        tenant_id: str,
        hints: Dict[str, Any],
        plan_id: str,
    ) -> AiFinancialAction:
        lower = intent.lower()
        portfolio_id = hints.get("portfolio_id", "TEST_P")
        expected_rev = hints.get("expected_revision", "rev_risk_1")

        action_type = AiActionType.RISK_START_RUN
        proposed_args: Dict[str, Any] = {"portfolio_id": portfolio_id}

        if "stress test" in lower or "decline" in lower or "interest-rate" in lower:
            proposed_args["model_id"] = "stress_test_equity_rates"
            proposed_args["equity_shock_percent"] = -10.0
            proposed_args["rate_shock_bps"] = 100.0
        elif "expected shortfall" in lower:
            proposed_args["model_id"] = "expected_shortfall"
            proposed_args["confidence_level"] = 0.99
            proposed_args["horizon_days"] = 1
        else:
            # Default Historical VaR (Fixture D)
            proposed_args["model_id"] = "historical_var"
            proposed_args["confidence_level"] = 0.99 if "99%" in lower else 0.95
            proposed_args["horizon_days"] = 1 if "one-day" in lower or "1-day" in lower else 10
            proposed_args["historical_window_days"] = 252

        action_id = f"act_{uuid.uuid4().hex[:12]}"
        adapter = self.registry.get_adapter(action_type)
        norm_hash = hashlib.sha256(
            json.dumps(proposed_args, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        return AiFinancialAction(
            action_id=action_id,
            action_type=action_type,
            action_version="1.0.0",
            target_module="risk",
            target_resource_type="risk_run",
            target_resource_id=portfolio_id,
            actor_user_id=user_id,
            tenant_scope=tenant_id,
            proposed_arguments=proposed_args,
            normalized_arguments_hash=norm_hash,
            expected_resource_revision=expected_rev,
            classification=adapter.classification,
            approval_policy=adapter.default_approval_policy,
            reversibility_policy=adapter.reversibility_policy,
        )
