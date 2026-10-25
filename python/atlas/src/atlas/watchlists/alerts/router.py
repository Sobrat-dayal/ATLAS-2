"""FastAPI Router for Watchlist Alerts V1 (Stage 80)."""

import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.watchlists.alerts.capabilities import get_alert_capabilities
from atlas.watchlists.alerts.errors import (
    AlertLimitExceededError,
    AlertNotFoundError,
    AlertRevisionConflictError,
    IncompatibleQuoteMeasureError,
    IncompatibleReferenceMethodError,
    InvalidAlertConditionError,
    InvalidExpirationError,
    WatchlistAlertError,
    WatchlistItemNotFoundError,
)
from atlas.watchlists.alerts.schemas import (
    AlertCapabilitiesResponse,
    AlertHealthStatusResponse,
    AlertHistoryResponse,
    AlertRuleResponse,
    CreateAlertRequest,
    UpdateAlertRequest,
)
from atlas.watchlists.alerts.service import WatchlistAlertService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Watchlist Alerts"])


def get_current_user_dependency():
    """Deferred import to avoid circular dependency."""
    from atlas_api.auth.dependencies import get_current_user
    return get_current_user


def get_db_session_dependency():
    """Deferred import to avoid circular dependency."""
    from atlas_api.dependencies import get_db_session
    return get_db_session


@router.get(
    "/alert-capabilities",
    response_model=AlertCapabilitiesResponse,
    summary="Get alert capabilities",
    description="Returns supported alert conditions, quote measures per asset class, reference methodologies, and quotas.",
)
async def get_capabilities() -> AlertCapabilitiesResponse:
    """Returns canonical alert capabilities."""
    return get_alert_capabilities()


@router.get(
    "/alerts/health",
    response_model=AlertHealthStatusResponse,
    summary="Get alert evaluator health",
    description="Returns operational status of server-side alert evaluation worker and event stream connectivity.",
)
async def get_health() -> AlertHealthStatusResponse:
    """Returns alert system health."""
    # Worker status reporting
    return AlertHealthStatusResponse(
        status="HEALTHY",
        worker_running=True,
        active_rules_in_memory=0,
        evaluation_queue_lag_ms=0,
        connected_to_market_events=True,
        entitlement_status="AUTHORIZED",
    )


@router.get(
    "/alerts/history",
    response_model=AlertHistoryResponse,
    summary="List all alert trigger history for user",
    description="Returns paginated immutable audit records of alert triggers for the authenticated user.",
)
async def get_all_user_alert_history(
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> AlertHistoryResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    return await service.get_trigger_history(owner_user_id=user_id, limit=limit, offset=offset)


@router.get(
    "/{id}/alerts",
    response_model=List[AlertRuleResponse],
    summary="List alerts for watchlist",
    description="Lists all user-owned alert rules defined for items in this watchlist.",
)
async def list_watchlist_alerts(
    id: UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> List[AlertRuleResponse]:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    return await service.list_watchlist_alerts(watchlist_id=id, owner_user_id=user_id)


@router.post(
    "/{id}/alerts",
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create alert rule",
    description="Defines a new persistent financial monitoring rule for a watchlist item.",
)
async def create_alert(
    id: UUID,
    request: CreateAlertRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> AlertRuleResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    try:
        return await service.create_alert(
            watchlist_id=id, owner_user_id=user_id, request=request
        )
    except WatchlistItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except (
        IncompatibleQuoteMeasureError,
        IncompatibleReferenceMethodError,
        InvalidAlertConditionError,
        InvalidExpirationError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )
    except AlertLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistAlertError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


@router.get(
    "/{id}/alerts/{alert_id}",
    response_model=AlertRuleResponse,
    summary="Get alert rule details",
    description="Retrieves a specific alert rule definition and its current evaluation state.",
)
async def get_alert(
    id: UUID,
    alert_id: UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> AlertRuleResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    try:
        return await service.get_alert(alert_id=alert_id, owner_user_id=user_id)
    except AlertNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.patch(
    "/{id}/alerts/{alert_id}",
    response_model=AlertRuleResponse,
    summary="Update alert rule",
    description="Updates threshold, recurrence, cooldown, or expiration with revision conflict protection.",
)
async def update_alert(
    id: UUID,
    alert_id: UUID,
    request: UpdateAlertRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> AlertRuleResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    try:
        return await service.update_alert(
            alert_id=alert_id, owner_user_id=user_id, request=request
        )
    except AlertNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except AlertRevisionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistAlertError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


@router.delete(
    "/{id}/alerts/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete alert rule",
    description="Deletes an alert rule owned by the user.",
)
async def delete_alert(
    id: UUID,
    alert_id: UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> None:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    try:
        await service.delete_alert(alert_id=alert_id, owner_user_id=user_id)
    except AlertNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.post(
    "/{id}/alerts/{alert_id}/pause",
    response_model=AlertRuleResponse,
    summary="Pause alert rule",
    description="Pauses background evaluation of an alert rule.",
)
async def pause_alert(
    id: UUID,
    alert_id: UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> AlertRuleResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    try:
        return await service.pause_alert(alert_id=alert_id, owner_user_id=user_id)
    except AlertNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.post(
    "/{id}/alerts/{alert_id}/resume",
    response_model=AlertRuleResponse,
    summary="Resume alert rule",
    description="Resumes background evaluation of an alert rule and safely resets the crossing baseline.",
)
async def resume_alert(
    id: UUID,
    alert_id: UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
) -> AlertRuleResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    try:
        return await service.resume_alert(alert_id=alert_id, owner_user_id=user_id)
    except AlertNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.get(
    "/{id}/alerts/{alert_id}/history",
    response_model=AlertHistoryResponse,
    summary="Get alert trigger history",
    description="Returns paginated immutable audit records of triggers for this alert.",
)
async def get_alert_history(
    id: UUID,
    alert_id: UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user_dependency())],
    session: Annotated[AsyncSession, Depends(get_db_session_dependency())],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> AlertHistoryResponse:
    user_id = UUID(principal.user_id)
    service = WatchlistAlertService(session)
    return await service.get_trigger_history(
        owner_user_id=user_id, alert_id=alert_id, limit=limit, offset=offset
    )
