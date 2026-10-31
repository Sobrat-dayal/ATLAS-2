"""FastAPI REST Router for QuantLib Options Strategy Engine (Stage 142)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from atlas.auth import AuthPrincipal


def get_current_principal() -> AuthPrincipal:
    return AuthPrincipal(sub="DEFAULT_USER", raw_claims={"tenant_id": "default_tenant"})
from atlas.options.domain import ExerciseStyle, LegSide, OptionType
from atlas.options.quant.domain import PricingModelFamily, QuantStrategyLeg
from atlas.options.quant.errors import (
    QuantContractNotFoundError,
    QuantDomainError,
    QuantEntitlementRequiredError,
    QuantModelIncompatibleError,
    QuantMultiTenantAccessDeniedError,
)
from atlas.options.quant.service import AtlasQuantOptionsService
from atlas.options.quant.strategies.models import QuantStrategyDefinition

router = APIRouter(prefix="/options/quant", tags=["options-quant"])

_quant_service = AtlasQuantOptionsService()


def get_quant_service() -> AtlasQuantOptionsService:
    return _quant_service


# Request Schemas
class SinglePriceRequest(BaseModel):
    contract_id: str
    evaluation_date: str = "2024-05-20"
    spot_price: float = 500.0
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    volatility: Optional[float] = None
    model_id: Optional[str] = None
    dividend_items: Optional[List[Dict[str, Any]]] = None
    numerical_steps: int = 100
    provider_source_id: str = "SRC_CBOE_AUTHORIZED"


class BatchPriceRequest(BaseModel):
    contract_ids: List[str]
    evaluation_date: str = "2024-05-20"
    spot_price: float = 500.0
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    model_id: Optional[str] = None
    provider_source_id: str = "SRC_CBOE_AUTHORIZED"


class QuantLegInput(BaseModel):
    contract_id: str
    side: LegSide
    quantity: int = 1
    entry_premium: float
    multiplier: float = 100.0
    strike_price: float
    expiration_date: str
    option_type: OptionType
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN
    custom_fee: float = 0.0


class StrategyAnalyzeRequest(BaseModel):
    strategy_name: str = "Custom Multi-Leg Strategy"
    underlying_symbol: str = "SPY"
    evaluation_date: str = "2024-05-20"
    spot_price: float = 500.0
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    volatility: float = 0.20
    total_fees: float = 0.0
    model_id: str = "BLACK_SCHOLES_MERTON"
    legs: List[QuantLegInput]


class StrategyScenarioRequest(BaseModel):
    legs: List[QuantLegInput]
    base_spot: float = 500.0
    base_eval_date: str = "2024-05-20"
    base_vol: float = 0.20
    base_rate: float = 0.05
    dividend_yield: float = 0.0
    net_opening_cash_flow: float = 0.0
    total_fees: float = 0.0
    model_id: str = "BLACK_SCHOLES_MERTON"


class SaveStrategyRequest(BaseModel):
    strategy_id: str
    title: str
    underlying_symbol: str
    legs: List[QuantLegInput]
    pricing_model_id: str = "BLACK_SCHOLES_MERTON"
    evaluation_date: str = "2024-05-20"
    total_fees: float = 0.0
    is_private: bool = True


class SurfaceBuildRequest(BaseModel):
    underlying_symbol: str
    evaluation_date: str
    observations: List[Dict[str, Any]]
    strict_validation: bool = False


class AiQuantToolRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)


# Endpoints
@router.get("/capabilities")
def get_capabilities(service: AtlasQuantOptionsService = Depends(get_quant_service)):
    return service.get_capabilities()


@router.get("/models")
def list_models(service: AtlasQuantOptionsService = Depends(get_quant_service)):
    return {"models": service.list_pricing_models()}


@router.get("/models/{model_id}")
def get_model(model_id: str, service: AtlasQuantOptionsService = Depends(get_quant_service)):
    m = service.get_pricing_model(model_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model '{model_id}' not found.")
    return m


@router.get("/templates")
def list_templates(service: AtlasQuantOptionsService = Depends(get_quant_service)):
    return {"templates": service.list_strategy_templates()}


@router.post("/price")
def price_contract(
    req: SinglePriceRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        return service.price_contract(
            contract_id=req.contract_id,
            evaluation_date=req.evaluation_date,
            spot_price=req.spot_price,
            risk_free_rate=req.risk_free_rate,
            dividend_yield=req.dividend_yield,
            volatility=req.volatility,
            model_id=req.model_id,
            dividend_items=req.dividend_items,
            numerical_steps=req.numerical_steps,
            provider_source_id=req.provider_source_id,
            principal=principal,
        )
    except QuantEntitlementRequiredError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except QuantContractNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except QuantDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/price/batch")
def price_batch(
    req: BatchPriceRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        results = service.price_batch(
            contract_ids=req.contract_ids,
            evaluation_date=req.evaluation_date,
            spot_price=req.spot_price,
            risk_free_rate=req.risk_free_rate,
            dividend_yield=req.dividend_yield,
            model_id=req.model_id,
            provider_source_id=req.provider_source_id,
        )
        return {"results": results, "count": len(results)}
    except QuantDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/strategies/analyze")
def analyze_strategy(
    req: StrategyAnalyzeRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        quant_legs = [
            QuantStrategyLeg(
                contract_id=l.contract_id,
                side=l.side,
                quantity=l.quantity,
                entry_premium=l.entry_premium,
                multiplier=l.multiplier,
                strike_price=l.strike_price,
                expiration_date=l.expiration_date,
                option_type=l.option_type,
                exercise_style=l.exercise_style,
                custom_fee=l.custom_fee,
            )
            for l in req.legs
        ]

        return service.analyze_strategy(
            legs=quant_legs,
            strategy_name=req.strategy_name,
            underlying_symbol=req.underlying_symbol,
            evaluation_date=req.evaluation_date,
            spot_price=req.spot_price,
            risk_free_rate=req.risk_free_rate,
            dividend_yield=req.dividend_yield,
            volatility=req.volatility,
            total_fees=req.total_fees,
            model_id=req.model_id,
        )
    except QuantDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/strategies/scenarios")
def generate_scenarios(
    req: StrategyScenarioRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        quant_legs = [
            QuantStrategyLeg(
                contract_id=l.contract_id,
                side=l.side,
                quantity=l.quantity,
                entry_premium=l.entry_premium,
                multiplier=l.multiplier,
                strike_price=l.strike_price,
                expiration_date=l.expiration_date,
                option_type=l.option_type,
                exercise_style=l.exercise_style,
                custom_fee=l.custom_fee,
            )
            for l in req.legs
        ]

        return service.run_scenario_matrix(
            legs=quant_legs,
            base_spot=req.base_spot,
            base_eval_date=req.base_eval_date,
            base_vol=req.base_vol,
            base_rate=req.base_rate,
            dividend_yield=req.dividend_yield,
            net_opening_cash_flow=req.net_opening_cash_flow,
            total_fees=req.total_fees,
            model_id=req.model_id,
        )
    except QuantDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/strategies/save")
def save_strategy(
    req: SaveStrategyRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    quant_legs = [
        QuantStrategyLeg(
            contract_id=l.contract_id,
            side=l.side,
            quantity=l.quantity,
            entry_premium=l.entry_premium,
            multiplier=l.multiplier,
            strike_price=l.strike_price,
            expiration_date=l.expiration_date,
            option_type=l.option_type,
            exercise_style=l.exercise_style,
            custom_fee=l.custom_fee,
        )
        for l in req.legs
    ]

    strat_def = QuantStrategyDefinition(
        strategy_id=req.strategy_id,
        owner_id=principal.sub,
        title=req.title,
        underlying_symbol=req.underlying_symbol,
        legs=quant_legs,
        pricing_model_id=req.pricing_model_id,
        evaluation_date=req.evaluation_date,
        total_fees=req.total_fees,
        tenant_id=principal.raw_claims.get("tenant_id") or "default_tenant",
        is_private=req.is_private,
    )

    saved = service.save_user_strategy(strat_def, principal=principal)
    return {"saved": True, "strategy_id": saved.strategy_id, "title": saved.title}


@router.get("/strategies/{strategy_id}")
def get_strategy(
    strategy_id: str,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        strat = service.get_user_strategy(strategy_id, principal=principal)
        if not strat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Strategy '{strategy_id}' not found.")
        return strat
    except QuantMultiTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get("/strategies")
def list_user_strategies(
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    strats = service.list_user_strategies(principal)
    return {"strategies": strats, "count": len(strats)}


@router.post("/volatility/surface")
def build_surface(
    req: SurfaceBuildRequest,
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        surface = service.build_volatility_surface(
            underlying_symbol=req.underlying_symbol,
            evaluation_date=req.evaluation_date,
            observations=req.observations,
            strict_validation=req.strict_validation,
        )
        return {
            "underlying_symbol": surface.underlying_symbol,
            "evaluation_date": surface.evaluation_date,
            "is_calibrated": surface.is_calibrated,
            "points_count": len(surface.points),
            "diagnostics": surface.diagnostics,
        }
    except QuantDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/ai-tool")
def execute_ai_quant_tool(
    req: AiQuantToolRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    service: AtlasQuantOptionsService = Depends(get_quant_service),
):
    try:
        return service.execute_ai_quant_tool(req.tool_name, req.params, principal=principal)
    except QuantDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
