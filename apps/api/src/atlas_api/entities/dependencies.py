from typing import Annotated

from atlas.entities import EntityRepository, EntityService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.dependencies import get_db_session


def get_entity_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> EntityService:
    repository = EntityRepository(session)
    return EntityService(repository)
