import uuid

from atlas.research.errors import ResearchDocumentNotFoundError
from atlas.research.schemas import ResearchDocumentResponse
from atlas.research.service import ResearchDocumentService
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from atlas_api.dependencies import get_current_user_with_access, get_db_session

router = APIRouter(
    prefix="/api/v1/research-documents",
    tags=["Research"],
)


@router.get(
    "/{entity_id}",
    response_model=ResearchDocumentResponse,
    status_code=status.HTTP_200_OK,
)
def get_research_document(
    entity_id: uuid.UUID = Path(..., description="The research document UUID"),
    session: Session = Depends(get_db_session),
    _user=Depends(get_current_user_with_access),
):
    service = ResearchDocumentService(session)
    try:
        return service.get_research_document(entity_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
