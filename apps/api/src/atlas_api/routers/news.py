import uuid

from atlas.news.errors import NewsEventNotFoundError
from atlas.news.schemas import NewsEventResponse
from atlas.news.service import NewsEventService
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from atlas_api.dependencies import get_db_session
from atlas_api.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/news-events",
    tags=["News Events"],
)


@router.get(
    "/{entity_id}",
    response_model=NewsEventResponse,
    status_code=status.HTTP_200_OK,
)
def get_news_event(
    entity_id: uuid.UUID = Path(..., description="The news event UUID"),
    session: Session = Depends(get_db_session),
    _user=Depends(get_current_user),
):
    service = NewsEventService(session)
    try:
        return service.get_news_event(entity_id)
    except NewsEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
