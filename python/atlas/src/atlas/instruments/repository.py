import uuid
from typing import Any, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    ETF,
    Bond,
    Commodity,
    CryptoAsset,
    Currency,
    Equity,
    FinancialInstrument,
    Fund,
    Future,
    MarketIndex,
    Option,
    Security,
)

T = TypeVar("T")

class InstrumentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_instrument(self, entity_id: uuid.UUID) -> Optional[FinancialInstrument]:
        stmt = select(FinancialInstrument).where(FinancialInstrument.entity_id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_security(self, entity_id: uuid.UUID) -> Optional[Security]:
        stmt = select(Security).where(Security.entity_id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_subtype(self, model: Type[T], entity_id: uuid.UUID) -> Optional[T]:
        stmt = select(model).where(model.entity_id == entity_id) # type: ignore
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_equity(self, entity_id: uuid.UUID) -> Optional[Equity]:
        return await self._get_subtype(Equity, entity_id)

    async def get_etf(self, entity_id: uuid.UUID) -> Optional[ETF]:
        return await self._get_subtype(ETF, entity_id)

    async def get_bond(self, entity_id: uuid.UUID) -> Optional[Bond]:
        return await self._get_subtype(Bond, entity_id)

    async def get_option(self, entity_id: uuid.UUID) -> Optional[Option]:
        return await self._get_subtype(Option, entity_id)

    async def get_future(self, entity_id: uuid.UUID) -> Optional[Future]:
        return await self._get_subtype(Future, entity_id)

    async def get_fund(self, entity_id: uuid.UUID) -> Optional[Fund]:
        return await self._get_subtype(Fund, entity_id)

    async def get_crypto_asset(self, entity_id: uuid.UUID) -> Optional[CryptoAsset]:
        return await self._get_subtype(CryptoAsset, entity_id)

    async def get_currency(self, entity_id: uuid.UUID) -> Optional[Currency]:
        return await self._get_subtype(Currency, entity_id)

    async def get_commodity(self, entity_id: uuid.UUID) -> Optional[Commodity]:
        return await self._get_subtype(Commodity, entity_id)

    async def get_market_index(self, entity_id: uuid.UUID) -> Optional[MarketIndex]:
        return await self._get_subtype(MarketIndex, entity_id)

    def add(self, model_instance: Any) -> None:
        """
        Adds a specialized model instance to the session without committing.
        """
        self._session.add(model_instance)
