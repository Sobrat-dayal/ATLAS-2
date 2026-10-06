import re
import uuid
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.aliases.models import EntityAlias
from atlas.entities.models import Entity
from atlas.entities.name_normalization import normalize_entity_name
from atlas.identifiers.models import EntityIdentifier
from atlas.identifiers.validators import validate_doi, validate_figi, validate_isin, validate_lei

from .schemas import EntityResolutionRequest, EntityResolutionResponse, ResolutionCandidate

# Map alias types to a priority rank (lower number = higher priority)
ALIAS_PRIORITY_MAP = {
    "common_name": 1,
    "short_name": 2,
    "brand_name": 3,
    "acronym": 4,
    "abbreviation": 5,
    "localized_name": 6,
    "informal_name": 7,
    "former_name": 8,
}

MATCH_KIND_PRIORITY = {
    "explicit_identifier": 1,
    "detected_identifier": 2,
    "explicit_scoped_ticker": 3,
    "unscoped_ticker": 4,
    "canonical_name": 5,
    "display_name": 6,
    "alias": 7,
    "historical_identifier": 8,
    "historical_alias": 9,
}


class EntityResolutionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve_entity(self, request: EntityResolutionRequest) -> EntityResolutionResponse:
        query = request.query.strip()
        if not query:
            return EntityResolutionResponse(status="not_found", query=query, candidates=[])

        try:
            normalized_query = normalize_entity_name(query)
        except ValueError:
            normalized_query = None

        candidates: Dict[uuid.UUID, ResolutionCandidate] = {}

        def add_candidate(
            cand: ResolutionCandidate,
            priority: int,
            alias_prio: int = 99,
            is_lang_match: bool = False,
        ):
            # Type hint filtering
            if request.entity_type_hints and cand.entity_type not in request.entity_type_hints:
                return

            if cand.entity_id in candidates:
                existing = candidates[cand.entity_id]
                existing_prio = getattr(existing, "_priority", 99)
                existing_alias_prio = getattr(existing, "_alias_prio", 99)

                # Replace if current candidate is better
                if priority < existing_prio:
                    cand._priority = priority
                    cand._alias_prio = alias_prio
                    cand._is_lang_match = is_lang_match
                    candidates[cand.entity_id] = cand
                elif (
                    priority == existing_prio
                    and cand.match_kind == "alias"
                    and existing.match_kind == "alias"
                ):
                    if alias_prio < existing_alias_prio:
                        cand._priority = priority
                        cand._alias_prio = alias_prio
                        cand._is_lang_match = is_lang_match
                        candidates[cand.entity_id] = cand
                    elif (
                        alias_prio == existing_alias_prio
                        and is_lang_match
                        and not getattr(existing, "_is_lang_match", False)
                    ):
                        cand._priority = priority
                        cand._alias_prio = alias_prio
                        cand._is_lang_match = is_lang_match
                        candidates[cand.entity_id] = cand
            else:
                cand._priority = priority
                cand._alias_prio = alias_prio
                cand._is_lang_match = is_lang_match
                candidates[cand.entity_id] = cand

        # 1. Explicit scheme hint
        if request.identifier_scheme_hint:
            stmt = select(Entity, EntityIdentifier).join(
                EntityIdentifier, Entity.entity_id == EntityIdentifier.entity_id
            )
            stmt = stmt.where(EntityIdentifier.scheme_key == request.identifier_scheme_hint)
            stmt = stmt.where(EntityIdentifier.normalized_value == query.strip().upper())

            if request.scope_entity_id:
                stmt = stmt.where(EntityIdentifier.scope_entity_id == request.scope_entity_id)
            elif request.identifier_scheme_hint == "ticker":
                # For explicit scheme=ticker without scope, we don't filter by scope
                pass
            else:
                stmt = stmt.where(EntityIdentifier.scope_entity_id.is_(None))

            if request.namespace:
                stmt = stmt.where(EntityIdentifier.namespace == request.namespace)
            else:
                stmt = stmt.where(EntityIdentifier.namespace.is_(None))

            if not request.include_historical:
                stmt = stmt.where(EntityIdentifier.is_current == True)

            result = await self.session.execute(stmt)
            for entity, ident in result.all():
                match_kind = "explicit_identifier" if ident.is_current else "historical_identifier"
                prio = MATCH_KIND_PRIORITY[match_kind]

                cand = ResolutionCandidate(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    canonical_name=entity.canonical_name,
                    display_name=entity.display_name,
                    match_kind=match_kind,
                    matched_value=ident.value,
                    identifier_scheme=ident.scheme_key,
                    scope_entity_id=ident.scope_entity_id,
                    is_historical=not ident.is_current,
                )
                add_candidate(cand, prio)

            # If explicit scheme hint, stop here
            return self._finalize_resolution(request, candidates)

        # 2. Strong Auto-detected Identifiers
        detected_schemes = []
        upper_query = query.upper()
        if validate_doi(query):
            detected_schemes.append("doi")
        if validate_isin(upper_query):
            detected_schemes.append("isin")
        if validate_figi(upper_query):
            detected_schemes.append("figi")
        if validate_lei(upper_query):
            detected_schemes.append("lei")

        if detected_schemes:
            stmt = select(Entity, EntityIdentifier).join(
                EntityIdentifier, Entity.entity_id == EntityIdentifier.entity_id
            )
            stmt = stmt.where(EntityIdentifier.scheme_key.in_(detected_schemes))
            stmt = stmt.where(EntityIdentifier.normalized_value == upper_query)
            if not request.include_historical:
                stmt = stmt.where(EntityIdentifier.is_current == True)

            result = await self.session.execute(stmt)
            for entity, ident in result.all():
                match_kind = "detected_identifier" if ident.is_current else "historical_identifier"
                prio = MATCH_KIND_PRIORITY[match_kind]
                cand = ResolutionCandidate(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    canonical_name=entity.canonical_name,
                    display_name=entity.display_name,
                    match_kind=match_kind,
                    matched_value=ident.value,
                    identifier_scheme=ident.scheme_key,
                    scope_entity_id=ident.scope_entity_id,
                    is_historical=not ident.is_current,
                )
                add_candidate(cand, prio)

        # 3. Ticker (unscoped)
        if len(query) <= 15 and re.match(r"^[A-Z0-9.\-/]+$", upper_query):
            stmt = select(Entity, EntityIdentifier).join(
                EntityIdentifier, Entity.entity_id == EntityIdentifier.entity_id
            )
            stmt = stmt.where(EntityIdentifier.scheme_key == "ticker")
            stmt = stmt.where(EntityIdentifier.normalized_value == upper_query)
            if not request.include_historical:
                stmt = stmt.where(EntityIdentifier.is_current == True)

            result = await self.session.execute(stmt)
            for entity, ident in result.all():
                match_kind = "unscoped_ticker" if ident.is_current else "historical_identifier"
                prio = MATCH_KIND_PRIORITY[match_kind]
                cand = ResolutionCandidate(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    canonical_name=entity.canonical_name,
                    display_name=entity.display_name,
                    match_kind=match_kind,
                    matched_value=ident.value,
                    identifier_scheme=ident.scheme_key,
                    scope_entity_id=ident.scope_entity_id,
                    is_historical=not ident.is_current,
                )
                add_candidate(cand, prio)

        # 4 & 5. Canonical and Display Names
        if normalized_query:
            stmt = select(Entity).where(
                (Entity.canonical_name_normalized == normalized_query)
                | (Entity.display_name_normalized == normalized_query)
            )
            result = await self.session.execute(stmt)
            for entity in result.scalars().all():
                if entity.canonical_name_normalized == normalized_query:
                    cand = ResolutionCandidate(
                        entity_id=entity.entity_id,
                        entity_type=entity.entity_type,
                        canonical_name=entity.canonical_name,
                        display_name=entity.display_name,
                        match_kind="canonical_name",
                        matched_value=entity.canonical_name,
                    )
                    add_candidate(cand, MATCH_KIND_PRIORITY["canonical_name"])

                if entity.display_name_normalized == normalized_query:
                    cand = ResolutionCandidate(
                        entity_id=entity.entity_id,
                        entity_type=entity.entity_type,
                        canonical_name=entity.canonical_name,
                        display_name=entity.display_name,
                        match_kind="display_name",
                        matched_value=entity.display_name,
                    )
                    add_candidate(cand, MATCH_KIND_PRIORITY["display_name"])

            # 6. Aliases
            stmt = select(Entity, EntityAlias).join(
                EntityAlias, Entity.entity_id == EntityAlias.entity_id
            )
            stmt = stmt.where(EntityAlias.normalized_value == normalized_query)
            if not request.include_historical:
                stmt = stmt.where(EntityAlias.is_current == True)

            result = await self.session.execute(stmt)
            for entity, alias in result.all():
                match_kind = "alias" if alias.is_current else "historical_alias"
                prio = MATCH_KIND_PRIORITY[match_kind]
                alias_prio = ALIAS_PRIORITY_MAP.get(alias.alias_type_key, 99)
                is_lang_match = (
                    request.language_code and alias.language_code == request.language_code
                )

                cand = ResolutionCandidate(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    canonical_name=entity.canonical_name,
                    display_name=entity.display_name,
                    match_kind=match_kind,
                    matched_value=alias.value,
                    alias_type=alias.alias_type_key,
                    is_historical=not alias.is_current,
                )
                add_candidate(cand, prio, alias_prio, is_lang_match)

        return self._finalize_resolution(request, candidates)

    def _finalize_resolution(self, request, candidates_dict) -> EntityResolutionResponse:
        cands = list(candidates_dict.values())

        # Sort candidates deterministically
        cands.sort(
            key=lambda c: (
                getattr(c, "_priority", 99),
                getattr(c, "_alias_prio", 99),
                0 if getattr(c, "_is_lang_match", False) else 1,
                c.is_historical,
                c.entity_type,
                c.canonical_name,
                str(c.entity_id),
            )
        )

        cands = cands[: request.max_candidates]

        if not cands:
            return EntityResolutionResponse(status="not_found", query=request.query, candidates=[])

        top_cand = cands[0]

        def get_sort_key(c):
            return (
                getattr(c, "_priority", 99),
                getattr(c, "_alias_prio", 99),
                0 if getattr(c, "_is_lang_match", False) else 1,
                c.is_historical,
            )

        top_key = get_sort_key(top_cand)

        is_ambiguous = False
        if len(cands) > 1:
            if get_sort_key(cands[1]) == top_key:
                is_ambiguous = True

        status = "ambiguous" if is_ambiguous else "resolved"
        resolved_id = None if is_ambiguous else top_cand.entity_id

        # clean internal fields
        for c in cands:
            if hasattr(c, "_priority"):
                delattr(c, "_priority")
            if hasattr(c, "_alias_prio"):
                delattr(c, "_alias_prio")
            if hasattr(c, "_is_lang_match"):
                delattr(c, "_is_lang_match")

        return EntityResolutionResponse(
            status=status, query=request.query, resolved_entity_id=resolved_id, candidates=cands
        )
