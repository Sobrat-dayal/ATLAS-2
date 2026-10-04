import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.aliases.repository import AliasRepository
from atlas.aliases.schemas import AliasTypeResponse, EntityAliasResponse
from atlas.aliases.service import AliasService
from atlas_api.dependencies import get_db_session

router = APIRouter(prefix="/aliases", tags=["Aliases"])


def get_alias_service(
    session: AsyncSession = Depends(get_db_session),
) -> AliasService:
    return AliasService(AliasRepository(session))


@router.get("/types", response_model=List[AliasTypeResponse])
async def list_alias_types(
    service: AliasService = Depends(get_alias_service),
):
    """
    Lists all supported alias types.
    """
    return await service.list_alias_types()


@router.get("/entities/{entity_id}", response_model=List[EntityAliasResponse])
async def get_entity_aliases(
    entity_id: uuid.UUID,
    service: AliasService = Depends(get_alias_service),
):
    """
    Lists all aliases for a given entity.
    """
    return await service.get_entity_aliases(entity_id)
