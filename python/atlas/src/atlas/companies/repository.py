import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Company

class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_company(self, entity_id: uuid.UUID) -> Optional[Company]:
        stmt = select(Company).where(Company.entity_id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, company: Company) -> None:
        self._session.add(company)
