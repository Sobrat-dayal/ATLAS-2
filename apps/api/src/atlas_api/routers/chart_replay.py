"""FastAPI Router for Historical Chart Replay V1 (Stage 75).

Exposes authenticated REST endpoints under `/charts/replay`:
- GET /charts/replay/capabilities: Check replay support and historical coverage
- POST /charts/replay/sessions: Create an authenticated replay session
- GET /charts/replay/sessions/{id}: Retrieve replay session status
- POST /charts/replay/sessions/{id}/step: Advance (+1) or step back (-1) replay cursor
- POST /charts/replay/sessions/{id}/seek: Relocate cursor to target index or timestamp
- DELETE /charts/replay/sessions/{id}: Close and release replay session resources
- POST /charts/replay/sessions/{id}/indicators: Compute indicators strictly on replay-visible bars
"""

import uuid
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.charts.indicators import IndicatorCalculationRequest, IndicatorCalculationResponse
from atlas.charts.replay import (
    HistoricalChartReplayService,
    ReplayCapabilityResponse,
    ReplaySeekRequest,
    ReplaySeekResponse,
    ReplaySessionDTO,
    ReplayStartRequest,
    ReplayStartResponse,
    ReplayStepRequest,
    ReplayStepResponse,
    default_replay_service,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/charts/replay", tags=["Chart Replay"])


def get_replay_service() -> HistoricalChartReplayService:
    """Dependency provider for the replay domain service."""
    return default_replay_service


@router.get(
    "/capabilities",
    response_model=ReplayCapabilityResponse,
    summary="Discover historical replay capabilities and coverage",
    description=(
        "Returns available intervals, earliest/latest qualified bar timestamps, "
        "and methodological disclosures regarding revised historical datasets."
    ),
)
async def get_replay_capabilities(
    instrument_id: Optional[str] = Query(None, description="Canonical instrument UUID"),
    symbol: Optional[str] = Query(None, description="Alternative ticker symbol"),
    interval: str = Query("1d", description="Canonical chart interval"),
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)] = None,
) -> ReplayCapabilityResponse:
    target_ident = instrument_id or symbol or "SPY"
    try:
        return replay_service.get_capabilities(
            instrument_identifier=target_ident, interval=interval
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))



@router.post(
    "/sessions",
    response_model=ReplayStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initialize a historical chart replay session",
    description=(
        "Creates a new user-owned replay session. Returns revealed bars strictly up to "
        "the selected starting position, with NO future bars exposed."
    ),
)
async def start_replay_session(
    request: ReplayStartRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)],
) -> ReplayStartResponse:
    try:
        return replay_service.start_session(user_id=current_user.user_id, request=request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/sessions/{session_id}",
    response_model=ReplaySessionDTO,
    summary="Get active replay session status",
    description="Returns session cursor, playback status, and progress metrics.",
)
async def get_replay_session(
    session_id: uuid.UUID,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)],
) -> ReplaySessionDTO:
    try:
        return replay_service.get_session_status(
            session_id=session_id, user_id=current_user.user_id
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/sessions/{session_id}/step",
    response_model=ReplayStepResponse,
    summary="Advance or reverse replay cursor by single or multiple bars",
    description=(
        "Steps forward or backward in historical time. Guarantees strict future isolation: "
        "step response returns only the single newly revealed bar on forward movement."
    ),
)
async def step_replay_session(
    session_id: uuid.UUID,
    request: ReplayStepRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)],
) -> ReplayStepResponse:
    try:
        return replay_service.step_session(
            session_id=session_id, user_id=current_user.user_id, request=request
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/sessions/{session_id}/seek",
    response_model=ReplaySeekResponse,
    summary="Seek replay cursor to target index or timestamp",
    description=(
        "Relocates replay cursor. Returns revealed bars strictly up to the target position."
    ),
)
async def seek_replay_session(
    session_id: uuid.UUID,
    request: ReplaySeekRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)],
) -> ReplaySeekResponse:
    try:
        return replay_service.seek_session(
            session_id=session_id, user_id=current_user.user_id, request=request
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Close and terminate a replay session",
    description="Releases ephemeral session resources and marks session closed.",
)
async def close_replay_session(
    session_id: uuid.UUID,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)],
) -> None:
    deleted = replay_service.close_session(session_id=session_id, user_id=current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Replay session '{session_id}' not found or access denied.",
        )


@router.post(
    "/sessions/{session_id}/indicators",
    response_model=IndicatorCalculationResponse,
    summary="Calculate technical indicators strictly over replay-visible bars",
    description=(
        "Executes TA-Lib calculations strictly bounded by the replay cursor. "
        "No historical bars after cursor_index are provided to indicator algorithms."
    ),
)
async def calculate_replay_indicators(
    session_id: uuid.UUID,
    request: IndicatorCalculationRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    replay_service: Annotated[HistoricalChartReplayService, Depends(get_replay_service)],
) -> IndicatorCalculationResponse:
    try:
        return replay_service.calculate_replay_indicators(
            session_id=session_id, user_id=current_user.user_id, request=request
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
