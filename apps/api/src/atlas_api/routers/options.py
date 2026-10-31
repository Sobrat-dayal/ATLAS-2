"""FastAPI Router for ATLAS Options Analytics (Stage 141).

Prefix: /options (accessible at /api/v1/options)

Provides institutional endpoints for:
- Options terminal capabilities & regulatory guardrails
- Underlying asset options discovery & expiration calendars
- Dual-sided options chains with bid-ask and open interest analytics
- Canonical contract inspector & corporate adjustment terms
- Implied volatility smile, skew & term structure
- Trading activity and volume/OI profiles
- Multi-leg strategy builder and piecewise expiration payoff modeling
- Read-only options portfolio integration with tenant isolation
- Authorized read-only AI tools
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.options import (
    AtlasOptionContract,
    AtlasOptionsService,
    OptionChainResponse,
    OptionQuote,
    OptionStrategyAnalysisResult,
    OptionStrategyLeg,
    OptionsAdjustedDeliverableUnsupportedError,
    OptionsContractNotFoundError,
    OptionsDataQualityError,
    OptionsDomainError,
    OptionsEntitlementRequiredError,
    OptionsInvalidStrategyLegError,
    OptionsMultiExpirationPayoffUnsupportedError,
    OptionsSourceUnavailableError,
    OptionsTenantAccessDeniedError,
    OptionsUnderlyingNotFoundError,
)
from atlas.options.portfolios.integration import OptionPositionItem
from atlas.options.strategies.templates import StrategyTemplateDefinition
from ..auth.dependencies import get_optional_user

router = APIRouter(prefix="/options", tags=["options-analytics"])

_options_service = AtlasOptionsService()


def get_options_service() -> AtlasOptionsService:
    return _options_service


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------
class AnalyzeStrategyRequest(BaseModel):
    strategy_name: str = "Custom Strategy"
    legs: List[OptionStrategyLeg]
    total_fees: float = 0.0


class AiToolRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.get("/capabilities", summary="Options Terminal Capabilities and Disclaimers")
def get_capabilities(
    service: AtlasOptionsService = Depends(get_options_service),
) -> Dict[str, Any]:
    return service.get_capabilities()


@router.get("/underlyings", summary="Search Underlyings With Options Coverage")
def search_underlyings(
    query: str = Query("", description="Search term for underlying symbol or company name"),
    service: AtlasOptionsService = Depends(get_options_service),
) -> List[Dict[str, Any]]:
    return service.search_underlyings(query)


@router.get("/underlyings/{symbol}/expirations", summary="List Expirations for Underlying")
def get_expirations(
    symbol: str,
    service: AtlasOptionsService = Depends(get_options_service),
) -> List[str]:
    try:
        return service.get_expirations(symbol)
    except OptionsUnderlyingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/underlyings/{symbol}/chains", summary="Get Dual-Sided Options Chain")
def get_option_chain(
    symbol: str,
    expiration_date: str = Query(..., description="Expiration date in YYYY-MM-DD format"),
    underlying_price: Optional[float] = Query(None, description="Optional spot price override for moneyness"),
    min_volume: Optional[int] = Query(None, description="Minimum trading volume filter"),
    min_open_interest: Optional[int] = Query(None, description="Minimum open interest filter"),
    strike_min: Optional[float] = Query(None, description="Lower strike boundary"),
    strike_max: Optional[float] = Query(None, description="Upper strike boundary"),
    service: AtlasOptionsService = Depends(get_options_service),
) -> OptionChainResponse:
    try:
        return service.get_option_chain(
            underlying_symbol=symbol,
            expiration_date=expiration_date,
            underlying_price=underlying_price,
            min_volume=min_volume,
            min_open_interest=min_open_interest,
            strike_min=strike_min,
            strike_max=strike_max,
        )
    except OptionsEntitlementRequiredError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except OptionsDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/underlyings/{symbol}/volatility", summary="Implied Volatility Smile and Term Structure")
def get_volatility(
    symbol: str,
    expiration_date: Optional[str] = Query(None, description="Expiration date for IV smile"),
    service: AtlasOptionsService = Depends(get_options_service),
) -> Dict[str, Any]:
    if expiration_date:
        return service.get_volatility_smile(symbol, expiration_date)
    else:
        return service.get_volatility_term_structure(symbol)


@router.get("/underlyings/{symbol}/activity", summary="Trading Activity and Volume/OI Breakdown")
def get_activity(
    symbol: str,
    expiration_date: str = Query(..., description="Expiration date for activity breakdown"),
    service: AtlasOptionsService = Depends(get_options_service),
) -> Dict[str, Any]:
    return service.get_activity(symbol, expiration_date)


@router.get("/contracts/{contract_id}", summary="Get Canonical Contract Terms")
def get_contract(
    contract_id: str,
    service: AtlasOptionsService = Depends(get_options_service),
) -> AtlasOptionContract:
    try:
        return service.get_contract(contract_id)
    except OptionsContractNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/contracts/{contract_id}/quote", summary="Get Normalized Option Quote")
def get_quote(
    contract_id: str,
    service: AtlasOptionsService = Depends(get_options_service),
) -> OptionQuote:
    try:
        return service.get_quote(contract_id)
    except OptionsEntitlementRequiredError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except OptionsContractNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/templates", summary="List Strategy Templates")
def list_strategy_templates(
    service: AtlasOptionsService = Depends(get_options_service),
) -> List[StrategyTemplateDefinition]:
    return service.list_strategy_templates()


@router.post("/strategies/analyze", summary="Analyze Multi-Leg Strategy Payoff and Breakevens")
def analyze_strategy(
    req: AnalyzeStrategyRequest,
    service: AtlasOptionsService = Depends(get_options_service),
) -> OptionStrategyAnalysisResult:
    try:
        return service.analyze_strategy(
            legs=req.legs,
            strategy_name=req.strategy_name,
            total_fees=req.total_fees,
        )
    except OptionsMultiExpirationPayoffUnsupportedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except OptionsAdjustedDeliverableUnsupportedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except OptionsInvalidStrategyLegError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except OptionsContractNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except OptionsDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/portfolios/{portfolio_id}/options", summary="Get Read-Only Options Holdings")
def get_portfolio_options(
    portfolio_id: str,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasOptionsService = Depends(get_options_service),
) -> List[OptionPositionItem]:
    try:
        return service.get_portfolio_options(portfolio_id, principal=principal)
    except OptionsTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.post("/ai-tool", summary="Execute Read-Only AI Options Tool")
def execute_ai_tool(
    req: AiToolRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasOptionsService = Depends(get_options_service),
) -> Dict[str, Any]:
    try:
        return service.execute_ai_options_tool(req.tool_name, req.params, principal=principal)
    except OptionsDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

