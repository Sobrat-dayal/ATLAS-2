from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.preferences import UserPreferenceRepository, UserPreferenceService
from atlas_api.dependencies import get_db_session

def get_preference_service(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UserPreferenceService:
    repository = UserPreferenceRepository(session)
    return UserPreferenceService(repository)
