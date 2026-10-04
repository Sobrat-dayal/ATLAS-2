import uuid
from typing import Union

from atlas.geography.errors import GeographicEntityNotFoundError
from atlas.geography.schemas import (
    AirportResponse,
    CountryResponse,
    ExchangeResponse,
    FacilityResponse,
    PortResponse,
)
from atlas.geography.service import GeographicEntityService
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from atlas_api.dependencies import get_db_session
from atlas_api.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/geographic-entities",
    tags=["Geographic Entities"],
)


@router.get(
    "/{entity_id}",
    response_model=Union[
        CountryResponse, PortResponse, AirportResponse, FacilityResponse, ExchangeResponse
    ],
    status_code=status.HTTP_200_OK,
)
def get_geographic_entity(
    entity_id: uuid.UUID = Path(..., description="The geographic entity UUID"),
    session: Session = Depends(get_db_session),
    _user=Depends(get_current_user),
):
    service = GeographicEntityService(session)
    try:
        return service.get_geographic_entity(entity_id)
    except GeographicEntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
