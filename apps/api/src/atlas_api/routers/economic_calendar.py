"""FastAPI Router for Global Economic Calendar (Stage 92).

Endpoints:
- GET    /api/v1/economics/calendar/events
- GET    /api/v1/economics/calendar/events/{event_id}
- GET    /api/v1/economics/calendar/events/{event_id}/observations
- GET    /api/v1/economics/calendar/events/{event_id}/forecasts
- GET    /api/v1/economics/calendar/events/{event_id}/history
- GET    /api/v1/economics/calendar/categories
- GET    /api/v1/economics/calendar/geographies
- GET    /api/v1/economics/calendar/sources
- GET    /api/v1/economics/calendar/coverage
- GET    /api/v1/economics/calendar/alerts
- POST   /api/v1/economics/calendar/alerts
- GET    /api/v1/economics/calendar/alerts/{alert_id}
- PATCH  /api/v1/economics/calendar/alerts/{alert_id}
- DELETE /api/v1/economics/calendar/alerts/{alert_id}
- GET    /api/v1/economics/calendar/alerts/history
- POST   /api/v1/economics/calendar/alerts/evaluate
"""

import logging
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization.permissions import PermissionCode
from atlas.economics.calendar import (
    AlertDeliveryIntentDTO,
    ConsensusSnapshotDTO,
    CreateEventAlertRequestDTO,
    EconomicCalendarCoverageDTO,
    EconomicCalendarEventDetailDTO,
    EconomicCalendarResponseDTO,
    EconomicCalendarService,
    EconomicEventAlertNotFoundError,
    EconomicEventAlertQuotaExceededError,
    EconomicEventDateRangeInvalidError,
    EconomicEventNotFoundError,
    EconomicEventObservationDTO,
    EconomicEventTimezoneInvalidError,
    ScheduleRevisionDTO,
    UpdateEventAlertRequestDTO,
    UserEventAlertDTO,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/economics/calendar",
    tags=["Economic Calendar"],
)

_service: Optional[EconomicCalendarService] = None


def get_economic_calendar_service() -> EconomicCalendarService:
    global _service
    if _service is None:
        _service = EconomicCalendarService()
    return _service


# -----------------------------------------------------------------------------
# Calendar Event Query Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/events",
    response_model=EconomicCalendarResponseDTO,
    summary="Query Global Economic Calendar Events",
    description="Returns chronological macroeconomic releases with presets (today, tomorrow, this_week, upcoming, released, central_bank), country/category/importance filters, and timezone conversion.",
)
async def query_calendar_events(
    view_preset: str = Query("all", description="View preset: all, today, tomorrow, this_week, next_week, upcoming, released, central_bank, my_alerts, historical"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    geography: Optional[List[str]] = Query(None, description="ISO country or area code filters"),
    category: Optional[List[str]] = Query(None, description="Event category filter"),
    importance: Optional[List[str]] = Query(None, description="Importance level filter (HIGH, MEDIUM, LOW)"),
    status_filter: Optional[List[str]] = Query(None, alias="status", description="Lifecycle status filter"),
    search: Optional[str] = Query(None, description="Text search filter on title or indicator"),
    display_timezone: str = Query("UTC", description="IANA timezone name for civil date conversion"),
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicCalendarResponseDTO:
    try:
        return service.query_calendar(
            view_preset=view_preset,
            start_date=start_date,
            end_date=end_date,
            geography_ids=geography,
            categories=category,
            importance_levels=importance,
            event_statuses=status_filter,
            search=search,
            display_timezone=display_timezone,
            current_user_id=user.sub,
        )
    except (EconomicEventTimezoneInvalidError, EconomicEventDateRangeInvalidError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/events/{event_id}",
    response_model=EconomicCalendarEventDetailDTO,
    summary="Get Detailed Economic Calendar Event",
    description="Returns full release event detail with observations, consensus forecasts, schedule revisions, and surprise calculations.",
)
async def get_calendar_event_detail(
    event_id: str,
    display_timezone: str = Query("UTC", description="IANA timezone for display formatting"),
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicCalendarEventDetailDTO:
    try:
        return service.get_event_detail(event_id, display_timezone)
    except EconomicEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except EconomicEventTimezoneInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/events/{event_id}/observations",
    response_model=List[EconomicEventObservationDTO],
    summary="Get Released Statistical Observations",
    description="Returns all actual, previous, and revised previous observation values published in this release occurrence.",
)
async def get_event_observations(
    event_id: str,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[EconomicEventObservationDTO]:
    try:
        detail = service.get_event_detail(event_id)
        return detail.observations
    except EconomicEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/events/{event_id}/forecasts",
    response_model=List[ConsensusSnapshotDTO],
    summary="Get Authorized Consensus Forecast Snapshots",
    description="Returns authorized pre-release consensus snapshots, contributor count, and aggregation methodology.",
)
async def get_event_forecasts(
    event_id: str,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[ConsensusSnapshotDTO]:
    try:
        detail = service.get_event_detail(event_id)
        return detail.consensus_snapshots
    except EconomicEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/events/{event_id}/history",
    response_model=List[ScheduleRevisionDTO],
    summary="Get Release Schedule Revision History",
    description="Returns official schedule changes, postponements, and revision rationales.",
)
async def get_event_history(
    event_id: str,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[ScheduleRevisionDTO]:
    try:
        detail = service.get_event_detail(event_id)
        return detail.schedule_revisions
    except EconomicEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# -----------------------------------------------------------------------------
# Metadata & Coverage Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/categories",
    response_model=List[str],
    summary="List Supported Economic Event Categories",
    description="Returns taxonomy of supported macroeconomic categories (gdp, inflation, labor, retail, manufacturing, trade, central_bank).",
)
async def list_event_categories(
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[str]:
    return [c.value for c in service.repo.list_families()[0].category.__class__]


@router.get(
    "/geographies",
    response_model=List[str],
    summary="List Supported Geographic Jurisdictions",
    description="Returns ISO codes for supported economic regions (US, EU, GB, JP, IN, CN).",
)
async def list_event_geographies(
    _service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[str]:
    return ["US", "EU", "GB", "JP", "IN", "CN"]


@router.get(
    "/coverage",
    response_model=EconomicCalendarCoverageDTO,
    summary="Get Economic Calendar Source Coverage Matrix",
    description="Returns verification coverage of official schedule sources, forecast coverage, and schedule precision breakdown.",
)
async def get_calendar_coverage(
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicCalendarCoverageDTO:
    return service.get_coverage()


@router.get(
    "/sources",
    summary="List Authoritative Economic Release Sources",
    description="Returns official publishing authorities and statistical agencies.",
)
async def list_event_sources(
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[dict]:
    events = service.repo.list_events()
    seen = {}
    for ev in events:
        if ev.official_source_id not in seen:
            seen[ev.official_source_id] = {
                "source_id": ev.official_source_id,
                "source_name": ev.official_source_name,
                "source_url": ev.official_source_url,
                "geographies": ev.geographic_entity_ids,
                "is_official_authority": True,
            }
    return list(seen.values())


# -----------------------------------------------------------------------------
# User Event Alerts & Notification Center Integration
# -----------------------------------------------------------------------------


@router.get(
    "/alerts",
    response_model=List[UserEventAlertDTO],
    summary="List User Economic Release Alerts",
    description="Returns all active and past event alerts configured by the authenticated user.",
)
async def list_user_alerts(
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[UserEventAlertDTO]:
    return service.list_alerts(user.sub)


@router.post(
    "/alerts",
    response_model=UserEventAlertDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Economic Release Alert",
    description="Creates a user-owned notification rule (reminder before release, release verified notification, schedule change alert).",
)
async def create_user_alert(
    request: CreateEventAlertRequestDTO,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserEventAlertDTO:
    try:
        return service.create_alert(user.sub, request)
    except EconomicEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except EconomicEventAlertQuotaExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)


@router.get(
    "/alerts/history",
    response_model=List[AlertDeliveryIntentDTO],
    summary="Get Alert Notification Delivery History",
    description="Returns delivery intent history dispatched to Stage 49 Notification Center for the user.",
)
async def list_alert_delivery_history(
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[AlertDeliveryIntentDTO]:
    return service.list_delivery_history(user.sub)


@router.get(
    "/alerts/{alert_id}",
    response_model=UserEventAlertDTO,
    summary="Get Specific User Event Alert",
    description="Returns single event alert owned by user.",
)
async def get_user_alert(
    alert_id: str,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserEventAlertDTO:
    try:
        return service.get_alert(alert_id, user.sub)
    except EconomicEventAlertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch(
    "/alerts/{alert_id}",
    response_model=UserEventAlertDTO,
    summary="Update User Event Alert",
    description="Updates reminder offset, enabled status, or paused state of user alert.",
)
async def update_user_alert(
    alert_id: str,
    request: UpdateEventAlertRequestDTO,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserEventAlertDTO:
    try:
        return service.update_alert(alert_id, user.sub, request)
    except EconomicEventAlertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete(
    "/alerts/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete / Cancel User Event Alert",
    description="Cancels and removes user event alert rule.",
)
async def delete_user_alert(
    alert_id: str,
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    try:
        service.delete_alert(alert_id, user.sub)
        return None
    except EconomicEventAlertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "/alerts/evaluate",
    response_model=List[AlertDeliveryIntentDTO],
    summary="Evaluate Active Alerts (Worker Simulation)",
    description="Evaluates pending release reminders and verified publication alerts against release schedule.",
)
async def evaluate_pending_alerts(
    service: EconomicCalendarService = Depends(get_economic_calendar_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[AlertDeliveryIntentDTO]:
    return service.evaluate_alerts()
