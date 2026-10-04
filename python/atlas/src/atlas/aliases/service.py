import uuid
from typing import Sequence, Optional
import datetime

from .errors import InvalidAliasError, UnknownAliasTypeError
from .registry import get_alias_type_definition, get_all_alias_type_definitions
from .repository import AliasRepository
from atlas.entities.name_normalization import normalize_entity_name


class AliasService:
    def __init__(self, repository: AliasRepository):
        self.repository = repository

    async def initialize_alias_types(self) -> None:
        """Upserts all alias types defined in the registry into the database."""
        for definition in get_all_alias_type_definitions():
            await self.repository.upsert_alias_type(
                key=definition.key,
                name=definition.name,
                category=definition.category,
                normalization_strategy=definition.normalization_strategy,
                description=definition.description,
                is_system=definition.is_system,
            )

    async def list_alias_types(self) -> Sequence:
        return await self.repository.list_alias_types()

    async def add_alias(
        self,
        entity_id: uuid.UUID,
        alias_type: str,
        value: str,
        language_code: Optional[str] = None,
        valid_from: Optional[datetime.date] = None,
        is_current: bool = True
    ):
        if not get_alias_type_definition(alias_type):
            raise UnknownAliasTypeError(alias_type)

        # verify in DB
        db_type = await self.repository.get_alias_type(alias_type)
        if not db_type:
            raise UnknownAliasTypeError(alias_type)

        try:
            normalized = normalize_entity_name(value)
        except ValueError as e:
            raise InvalidAliasError(str(e))
            
        if len(normalized) == 0:
            raise InvalidAliasError("Alias cannot be empty")
            
        if len(value) > 512:
             raise InvalidAliasError("Alias value exceeds length limit of 512")
             
        if language_code and len(language_code) > 35:
             raise InvalidAliasError("Language code exceeds length limit of 35")

        return await self.repository.add_alias(
            entity_id=entity_id,
            alias_type_key=alias_type,
            value=value,
            normalized_value=normalized,
            language_code=language_code,
            valid_from=valid_from,
            is_current=is_current
        )

    async def get_entity_aliases(self, entity_id: uuid.UUID, include_history: bool = False):
        return await self.repository.get_entity_aliases(entity_id, include_history)

    async def retire_alias(
        self, alias_id: uuid.UUID, valid_to: Optional[datetime.date] = None
    ):
        return await self.repository.retire_alias(alias_id, valid_to)
