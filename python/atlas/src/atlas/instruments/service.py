import uuid
from typing import Any, Optional

from atlas.entities.models import Entity
from atlas.entities.service import EntityService

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
from .repository import InstrumentRepository


class InstrumentService:
    def __init__(
        self,
        repository: InstrumentRepository,
        entity_service: EntityService,
    ):
        self.repository = repository
        self.entity_service = entity_service

    async def get_instrument_model(self, entity_id: uuid.UUID) -> Optional[Any]:
        # Helper to get the fully specialized model
        # We start by ensuring it's an instrument
        base_inst = await self.repository.get_instrument(entity_id)
        if not base_inst:
            return None
        
        # In a real system, we'd know the type from the base Entity.
        # Let's get the base entity.
        entity = await self.entity_service.get_entity(entity_id)
        entity_type = entity.entity_type

        # Dispatch based on entity_type
        if entity_type == "equity":
            return await self.repository.get_equity(entity_id)
        elif entity_type == "etf":
            return await self.repository.get_etf(entity_id)
        elif entity_type == "bond":
            return await self.repository.get_bond(entity_id)
        elif entity_type == "option":
            return await self.repository.get_option(entity_id)
        elif entity_type == "future":
            return await self.repository.get_future(entity_id)
        elif entity_type == "fund":
            return await self.repository.get_fund(entity_id)
        elif entity_type == "crypto":
            return await self.repository.get_crypto_asset(entity_id)
        elif entity_type == "currency":
            return await self.repository.get_currency(entity_id)
        elif entity_type == "commodity":
            return await self.repository.get_commodity(entity_id)
        elif entity_type == "index":
            return await self.repository.get_market_index(entity_id)
        elif entity_type == "security":
            return await self.repository.get_security(entity_id)
        else:
            return base_inst

    async def create_instrument(
        self,
        entity_type: str,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any
    ) -> Entity:
        """
        Creates a base entity, a FinancialInstrument record, and a Security/Specialization record.
        This does not commit to the database. The caller is responsible for the transaction.
        """
        entity = await self.entity_service.create_entity(
            entity_type=entity_type,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description
        )

        # Base financial instrument
        fi = FinancialInstrument(entity_id=entity.entity_id)
        self.repository.add(fi)

        # Is it a security? (equity, etf, bond, option, future, fund)
        is_security = entity_type in ("security", "equity", "etf", "bond", "option", "future", "fund")
        if is_security:
            sec = Security(entity_id=entity.entity_id)
            self.repository.add(sec)

        # Specialized tables
        if entity_type == "equity":
            specialized = Equity(
                entity_id=entity.entity_id,
                equity_kind=kwargs.get("equity_kind"),
                share_class_name=kwargs.get("share_class_name")
            )
            self.repository.add(specialized)
        elif entity_type == "etf":
            specialized = ETF(
                entity_id=entity.entity_id,
                base_currency_entity_id=kwargs.get("base_currency_entity_id"),
                replication_method=kwargs.get("replication_method"),
                distribution_policy=kwargs.get("distribution_policy")
            )
            self.repository.add(specialized)
        elif entity_type == "bond":
            specialized = Bond(
                entity_id=entity.entity_id,
                denomination_currency_entity_id=kwargs.get("denomination_currency_entity_id"),
                face_value=kwargs.get("face_value"),
                coupon_rate=kwargs.get("coupon_rate"),
                coupon_type=kwargs.get("coupon_type"),
                coupon_frequency=kwargs.get("coupon_frequency"),
                issue_date=kwargs.get("issue_date"),
                maturity_date=kwargs.get("maturity_date")
            )
            self.repository.add(specialized)
        elif entity_type == "option":
            specialized = Option(
                entity_id=entity.entity_id,
                underlying_entity_id=kwargs["underlying_entity_id"],
                option_right=kwargs["option_right"],
                strike_price=kwargs["strike_price"],
                expiration_at=kwargs["expiration_at"],
                exercise_style=kwargs.get("exercise_style"),
                contract_multiplier=kwargs.get("contract_multiplier"),
                settlement_type=kwargs.get("settlement_type")
            )
            self.repository.add(specialized)
        elif entity_type == "future":
            specialized = Future(
                entity_id=entity.entity_id,
                underlying_entity_id=kwargs["underlying_entity_id"],
                expiration_at=kwargs.get("expiration_at"),
                contract_size=kwargs.get("contract_size"),
                settlement_type=kwargs.get("settlement_type"),
                settlement_currency_entity_id=kwargs.get("settlement_currency_entity_id")
            )
            self.repository.add(specialized)
        elif entity_type == "fund":
            specialized = Fund(
                entity_id=entity.entity_id,
                fund_kind=kwargs.get("fund_kind"),
                base_currency_entity_id=kwargs.get("base_currency_entity_id"),
                distribution_policy=kwargs.get("distribution_policy")
            )
            self.repository.add(specialized)
        elif entity_type == "crypto":
            specialized = CryptoAsset(
                entity_id=entity.entity_id,
                asset_kind=kwargs.get("asset_kind")
            )
            self.repository.add(specialized)
        elif entity_type == "currency":
            specialized = Currency(
                entity_id=entity.entity_id,
                currency_kind=kwargs.get("currency_kind")
            )
            self.repository.add(specialized)
        elif entity_type == "commodity":
            specialized = Commodity(
                entity_id=entity.entity_id,
                commodity_category=kwargs.get("commodity_category"),
                unit_of_measure=kwargs.get("unit_of_measure")
            )
            self.repository.add(specialized)
        elif entity_type == "index":
            specialized = MarketIndex(
                entity_id=entity.entity_id,
                index_kind=kwargs.get("index_kind"),
                base_currency_entity_id=kwargs.get("base_currency_entity_id"),
                weighting_method=kwargs.get("weighting_method")
            )
            self.repository.add(specialized)

        return entity
