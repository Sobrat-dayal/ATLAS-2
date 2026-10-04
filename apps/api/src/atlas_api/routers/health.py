from fastapi import APIRouter, Depends

from ..config import Settings
from ..dependencies import get_app_settings
from ..schemas.health import HealthResponse, ReadinessResponse, VersionResponse

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
    # Future stages will check DB/Redis connectivity
    return ReadinessResponse(status="ready")


@router.get("/system/version", response_model=VersionResponse)
async def system_version(settings: Settings = Depends(get_app_settings)):
    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.env.value
    )
