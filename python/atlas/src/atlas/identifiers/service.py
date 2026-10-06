import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.repository import EntityRepository
from atlas.identifiers.errors import (
    IdentifierAlreadyRetiredError,
    IdentifierConflictError,
    IdentifierHistoryConflictError,
    IdentifierNamespaceForbiddenError,
    IdentifierNamespaceRequiredError,
    IdentifierScopeForbiddenError,
    IdentifierScopeRequiredError,
    IdentifierScopeTypeInvalidError,
    IdentifierSubjectTypeInvalidError,
    InvalidIdentifierNamespaceError,
    InvalidIdentifierValidityError,
    InvalidIdentifierValueError,
    UnknownIdentifierSchemeError,
)
from atlas.identifiers.models import EntityIdentifier
from atlas.identifiers.normalizers import (
    normalize_arxiv,
    normalize_compact_uppercase,
    normalize_digits,
    normalize_doi,
    normalize_isbn10,
    normalize_isbn13,
    normalize_lowercase_trim,
    normalize_openalex,
    normalize_preserve_trim,
    normalize_uppercase_trim,
)
from atlas.identifiers.registry import IDENTIFIER_SCHEMES_REGISTRY, IdentifierSchemeDefinition
from atlas.identifiers.repository import IdentifierRepository
from atlas.identifiers.schemas import EntityIdentifierResponse, IdentifierSchemeResponse
from atlas.identifiers.types import IdentifierNormalizationStrategy, IdentifierScopePolicy
from atlas.identifiers.validators import (
    validate_cusip,
    validate_doi,
    validate_figi,
    validate_iata,
    validate_icao,
    validate_isbn10,
    validate_isbn13,
    validate_isin,
    validate_iso3166_alpha2,
    validate_iso3166_alpha3,
    validate_iso4217_alpha,
    validate_lei,
    validate_mic,
    validate_sedol,
)


class IdentifierService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = IdentifierRepository(session)
        self.entity_repository = EntityRepository(session)

    async def list_identifier_schemes(self) -> List[IdentifierSchemeResponse]:
        schemes = await self.repository.list_schemes()
        return [IdentifierSchemeResponse.model_validate(s) for s in schemes]

    async def get_entity_identifiers(
        self, entity_id: uuid.UUID, include_history: bool = False
    ) -> List[EntityIdentifierResponse]:
        # The API layer should have already checked that the entity exists.
        identifiers = await self.repository.list_entity_identifiers(entity_id, include_history)
        return [EntityIdentifierResponse.model_validate(i) for i in identifiers]

    def _normalize(self, scheme_def: IdentifierSchemeDefinition, value: str) -> str:
        strategy = scheme_def.normalization_strategy
        if strategy == IdentifierNormalizationStrategy.UPPERCASE_TRIM:
            return normalize_uppercase_trim(value)
        elif strategy == IdentifierNormalizationStrategy.LOWERCASE_TRIM:
            return normalize_lowercase_trim(value)
        elif strategy == IdentifierNormalizationStrategy.COMPACT_UPPERCASE:
            return normalize_compact_uppercase(value)
        elif strategy == IdentifierNormalizationStrategy.DIGITS_ONLY:
            return normalize_digits(value)
        elif strategy == IdentifierNormalizationStrategy.DOI:
            return normalize_doi(value)
        elif strategy == IdentifierNormalizationStrategy.ARXIV:
            return normalize_arxiv(value)
        elif strategy == IdentifierNormalizationStrategy.OPENALEX:
            return normalize_openalex(value)
        elif strategy == IdentifierNormalizationStrategy.ISBN10:
            return normalize_isbn10(value)
        elif strategy == IdentifierNormalizationStrategy.ISBN13:
            return normalize_isbn13(value)
        elif strategy == IdentifierNormalizationStrategy.PRESERVE_TRIM:
            return normalize_preserve_trim(value)
        return value.strip()

    def _validate_format(self, scheme_key: str, normalized_value: str) -> bool:
        if scheme_key == "isin":
            return validate_isin(normalized_value)
        if scheme_key == "cusip":
            return validate_cusip(normalized_value)
        if scheme_key == "sedol":
            return validate_sedol(normalized_value)
        if scheme_key in ("figi", "composite_figi", "share_class_figi"):
            return validate_figi(normalized_value)
        if scheme_key == "lei":
            return validate_lei(normalized_value)
        if scheme_key == "iso_3166_alpha2":
            return validate_iso3166_alpha2(normalized_value)
        if scheme_key == "iso_3166_alpha3":
            return validate_iso3166_alpha3(normalized_value)
        if scheme_key == "iso_4217_alpha":
            return validate_iso4217_alpha(normalized_value)
        if scheme_key == "mic":
            return validate_mic(normalized_value)
        if scheme_key == "iata_airport":
            return validate_iata(normalized_value)
        if scheme_key == "icao_airport":
            return validate_icao(normalized_value)
        if scheme_key == "doi":
            return validate_doi(normalized_value)
        if scheme_key == "isbn_10":
            return validate_isbn10(normalized_value)
        if scheme_key == "isbn_13":
            return validate_isbn13(normalized_value)
        return True

    async def assign_identifier(
        self,
        entity_id: uuid.UUID,
        scheme_key: str,
        value: str,
        scope_entity_id: Optional[uuid.UUID] = None,
        namespace: Optional[str] = None,
        valid_from: Optional[date] = None,
    ) -> EntityIdentifierResponse:
        scheme_def = IDENTIFIER_SCHEMES_REGISTRY.get(scheme_key)
        if not scheme_def:
            raise UnknownIdentifierSchemeError(f"Unknown scheme: {scheme_key}")

        entity = await self.entity_repository.get_entity(entity_id)
        if not entity:
            raise ValueError("Entity not found")  # Ideally handled before

        # Subject policy
        if entity.entity_type not in scheme_def.subject_policy:
            raise IdentifierSubjectTypeInvalidError(
                f"Entity type {entity.entity_type} not valid for {scheme_key}"
            )

        # Scope/Namespace policy
        if scheme_def.scope_policy == IdentifierScopePolicy.GLOBAL:
            if scope_entity_id:
                raise IdentifierScopeForbiddenError(
                    f"{scheme_key} is global and forbids scope_entity_id"
                )
            if namespace:
                raise IdentifierNamespaceForbiddenError(
                    f"{scheme_key} is global and forbids namespace"
                )

        elif scheme_def.scope_policy == IdentifierScopePolicy.ENTITY:
            if not scope_entity_id:
                raise IdentifierScopeRequiredError(f"{scheme_key} requires scope_entity_id")
            if namespace:
                raise IdentifierNamespaceForbiddenError(f"{scheme_key} forbids namespace")

            scope_entity = await self.entity_repository.get_entity(scope_entity_id)
            if not scope_entity:
                raise ValueError("Scope Entity not found")

            if (
                scheme_def.scope_entity_types
                and scope_entity.entity_type not in scheme_def.scope_entity_types
            ):
                raise IdentifierScopeTypeInvalidError(
                    f"Scope Entity type {scope_entity.entity_type} not allowed for {scheme_key}"
                )

        elif scheme_def.scope_policy == IdentifierScopePolicy.NAMESPACE:
            if not namespace or not namespace.strip():
                raise IdentifierNamespaceRequiredError(f"{scheme_key} requires namespace")
            if scope_entity_id:
                raise IdentifierScopeForbiddenError(f"{scheme_key} forbids scope_entity_id")
            if len(namespace) > 128:
                raise InvalidIdentifierNamespaceError("Namespace exceeds max length")

        normalized_value = self._normalize(scheme_def, value)
        if not normalized_value or len(normalized_value) > scheme_def.max_length:
            raise InvalidIdentifierValueError(f"Invalid value length for {scheme_key}")

        if not self._validate_format(scheme_key, normalized_value):
            raise InvalidIdentifierValueError(f"Value fails format validation for {scheme_key}")

        # Idempotency check: Exact same current assignment for this entity?
        current_existing = await self.repository.find_current(
            scheme_key, normalized_value, scope_entity_id, namespace
        )
        if current_existing:
            if current_existing.entity_id == entity_id:
                return EntityIdentifierResponse.model_validate(current_existing)
            else:
                raise IdentifierConflictError(
                    f"Identifier currently assigned to entity {current_existing.entity_id}"
                )

        # History overlap check
        history = await self.repository.find_overlapping_history(
            scheme_key, normalized_value, scope_entity_id, namespace, valid_from, None
        )
        for h in history:
            if h.entity_id != entity_id:
                # Does h overlap with valid_from..infinity?
                h_start = h.valid_from or date.min
                h_end = h.valid_to or date.max
                req_start = valid_from or date.min
                req_end = date.max

                # Overlap condition
                if max(h_start, req_start) <= min(h_end, req_end):
                    raise IdentifierHistoryConflictError(
                        "Overlaps with historical assignment to another entity"
                    )

        # Create
        assignment = EntityIdentifier(
            entity_id=entity_id,
            scheme_key=scheme_key,
            value=value.strip() if not scheme_def.case_sensitive else value.strip(),
            normalized_value=normalized_value,
            scope_entity_id=scope_entity_id,
            namespace=namespace,
            is_current=True,
            valid_from=valid_from,
        )
        try:
            assignment = await self.repository.create_assignment(assignment)
        except IntegrityError:
            await self.session.rollback()
            raise IdentifierConflictError("Database uniqueness conflict")

        return EntityIdentifierResponse.model_validate(assignment)

    async def retire_identifier(
        self, identifier_id: uuid.UUID, valid_to: date
    ) -> EntityIdentifierResponse:
        stmt = select(EntityIdentifier).where(EntityIdentifier.identifier_id == identifier_id)
        result = await self.session.execute(stmt)
        assignment = result.scalars().first()
        if not assignment:
            raise ValueError("Identifier assignment not found")

        if not assignment.is_current:
            if assignment.valid_to == valid_to:
                return EntityIdentifierResponse.model_validate(assignment)
            raise IdentifierAlreadyRetiredError(
                "Identifier is already retired with different valid_to"
            )

        if assignment.valid_from and valid_to < assignment.valid_from:
            raise InvalidIdentifierValidityError("valid_to cannot be earlier than valid_from")

        assignment.is_current = False
        assignment.valid_to = valid_to
        await self.session.flush()
        return EntityIdentifierResponse.model_validate(assignment)

    async def lookup_exact_identifier(
        self,
        scheme_key: str,
        value: str,
        scope_entity_id: Optional[uuid.UUID] = None,
        namespace: Optional[str] = None,
    ) -> Optional[uuid.UUID]:
        scheme_def = IDENTIFIER_SCHEMES_REGISTRY.get(scheme_key)
        if not scheme_def:
            return None

        normalized_value = self._normalize(scheme_def, value)
        current = await self.repository.find_current(
            scheme_key, normalized_value, scope_entity_id, namespace
        )
        if current:
            return current.entity_id
        return None
