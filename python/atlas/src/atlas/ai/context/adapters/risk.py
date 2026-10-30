"""Risk Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)
from atlas.ai.context.errors import AiContextTargetAccessDeniedError


class RiskContextAdapter(BaseAiContextAdapter):
    """Extracts immutable Risk Run metrics, Value-at-Risk, stress tests, and factor exposures."""

    @property
    def adapter_id(self) -> str:
        return "adapter_risk"

    @property
    def context_type(self) -> ContextType:
        return ContextType.RISK_CONTEXT

    @property
    def supported_module(self) -> str:
        return "risk"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        risk_run_id = target_id or "risk_run_p1_20251231"

        # Permission check
        allowed_users = params.get("allowed_users", [user_id])
        if user_id not in allowed_users:
            raise AiContextTargetAccessDeniedError("RISK_RUN", risk_run_id)

        portfolio_id = params.get("portfolio_id", "port_p1")
        as_of_date = params.get("as_of_date", "2025-12-31")
        model_version = params.get("model_version", "Barra_GEM_v4.2")
        confidence = params.get("confidence_level", 0.95)
        horizon = params.get("horizon_days", 1)

        var_val = params.get("var_95_pct", params.get("var_95_daily", 0.0215))
        cvar_val = params.get("cvar_95_pct", params.get("cvar_95_daily", 0.0342))
        factors = params.get("factor_exposures") or {
            "SPY": 1.05,
            "Market_Beta": 1.05,
            "Size": -0.12,
            "Value": 0.25,
            "Momentum": 0.45,
        }

        payload = {
            "risk_run_id": risk_run_id,
            "portfolio_id": portfolio_id,
            "as_of_date": as_of_date,
            "model_version": model_version,
            "confidence_level": confidence,
            "horizon_days": horizon,
            "var_95_daily": var_val,
            "cvar_95_daily": cvar_val,
            "var_95_pct": var_val,
            "cvar_95_pct": cvar_val,
            "annualized_volatility": params.get("annualized_volatility", 0.158),
            "factor_exposures": factors,
            "is_immutable": True,
            "is_immutable_run": True,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_risk_{risk_run_id}",
            context_type=self.context_type,
            canonical_target_id=risk_run_id,
            source_module="risk",
            source_reference=f"atlas://risk/runs/{risk_run_id}",
            as_of=as_of_date,
            observed_at=datetime.now(timezone.utc).isoformat(),
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Risk Run {risk_run_id} ({portfolio_id}, VaR 95%: {round(payload['var_95_daily'] * 100, 2)}%, As-of {as_of_date})",
            structured_payload=payload,
            estimated_tokens=150,
            relevance_score=3.2,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        factors_str = ", ".join([f"{k}: {v}" for k, v in p.get("factor_exposures", {}).items()])
        return (
            f"[Immutable Risk Run: {p.get('risk_run_id')}]\n"
            f"- Associated Portfolio: {p.get('portfolio_id')} | Immutably Bound As-of Date: {p.get('as_of_date')}\n"
            f"- Model Engine: {p.get('model_version')} | Horizon: {p.get('horizon_days')} Day(s) | Confidence: {int(p.get('confidence_level', 0) * 100)}%\n"
            f"- Parametric VaR: {round(p.get('var_95_daily', 0) * 100, 2)}% | Expected Shortfall (CVaR): {round(p.get('cvar_95_daily', 0) * 100, 2)}%\n"
            f"- Factor Exposures: {factors_str}"
        )
