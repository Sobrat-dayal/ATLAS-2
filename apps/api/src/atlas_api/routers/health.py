from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings
from ..dependencies import get_app_settings
from ..schemas.health import HealthResponse, ReadinessResponse, VersionResponse
from ..database import db_manager

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_app_settings)):
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check():
    # Perform database connectivity check
    is_connected = await db_manager.check_connectivity()
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable"
        )
    return ReadinessResponse(status="ready")


@router.get("/system/version", response_model=VersionResponse)
async def system_version(settings: Settings = Depends(get_app_settings)):
    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.env.value
    )
