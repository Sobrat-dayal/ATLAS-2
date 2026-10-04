import uuid

from atlas.economics.errors import EconomicSeriesNotFoundError
from atlas.economics.schemas import EconomicSeriesResponse
from atlas.economics.service import EconomicSeriesService
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from atlas_api.dependencies import get_current_user_with_access, get_db_session

router = APIRouter(
    prefix="/api/v1/economic-series",
    tags=["Economics"],
)


@router.get(
    "/{entity_id}",
    response_model=EconomicSeriesResponse,
    status_code=status.HTTP_200_OK,
)
def get_economic_series(
    entity_id: uuid.UUID = Path(..., description="The economic series UUID"),
    session: Session = Depends(get_db_session),
    _user=Depends(get_current_user_with_access),
):
    service = EconomicSeriesService(session)
    try:
        return service.get_economic_series(entity_id)
    except EconomicSeriesNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
