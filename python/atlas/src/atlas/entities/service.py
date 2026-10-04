import uuid
from typing import Optional, Sequence

from .errors import (
    EntityNotFoundError,
    InvalidEntityDescriptionError,
    InvalidEntityNameError,
    UnknownEntityTypeError,
)
from .models import Entity, EntityType
from .registry import get_entity_type_definition
from .repository import EntityRepository
from .name_normalization import normalize_entity_name


class EntityService:
    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def _validate_name(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise InvalidEntityNameError("Name cannot be empty")
        if len(name) > 512:
            raise InvalidEntityNameError("Name exceeds 512 characters")
        return name

    def _validate_description(self, description: Optional[str]) -> Optional[str]:
        if description is None:
            return None
        description = description.strip()
        if len(description) > 8192:
            raise InvalidEntityDescriptionError("Description exceeds 8192 characters")
        return description

    async def get_entity(self, entity_id: uuid.UUID) -> Entity:
        entity = await self.repository.get_by_id(entity_id)
        if not entity:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def list_entity_types(self) -> Sequence[EntityType]:
        return await self.repository.list_entity_types()

    async def get_entity_type(self, key: str) -> EntityType:
        et = await self.repository.get_entity_type(key)
        if not et:
            raise UnknownEntityTypeError(key)
        return et

    async def create_entity(
        self,
        entity_type: str,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        force_entity_id: Optional[uuid.UUID] = None,
    ) -> Entity:
        # Validate type against code registry, then against DB
        # This prevents polluting the DB with invalid types if the DB is misaligned
        if not get_entity_type_definition(entity_type):
            raise UnknownEntityTypeError(entity_type)

        # Verify it exists in DB
        et = await self.repository.get_entity_type(entity_type)
        if not et:
            raise UnknownEntityTypeError(entity_type)

        canonical_name = self._validate_name(canonical_name)
        if display_name:
            display_name = self._validate_name(display_name)
        else:
            display_name = canonical_name

        description = self._validate_description(description)

        eid = force_entity_id or uuid.uuid4()

        # Creates in session without committing
        return self.repository.create(
            entity_id=eid,
            entity_type=entity_type,
            canonical_name=canonical_name,
            canonical_name_normalized=normalize_entity_name(canonical_name),
            display_name=display_name,
            display_name_normalized=normalize_entity_name(display_name),
            description=description,
        )

    async def update_base_entity(
        self,
        entity_id: uuid.UUID,
        canonical_name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Entity:
        entity = await self.get_entity(entity_id)

        if canonical_name is not None:
            entity.canonical_name = self._validate_name(canonical_name)
            entity.canonical_name_normalized = normalize_entity_name(entity.canonical_name)

        if display_name is not None:
            entity.display_name = self._validate_name(display_name)
            entity.display_name_normalized = normalize_entity_name(entity.display_name)

        if description is not None:
            entity.description = self._validate_description(description)

        # Let the session commit whenever the caller commits
        return entity
