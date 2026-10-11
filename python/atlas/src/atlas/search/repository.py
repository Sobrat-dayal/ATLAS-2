from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import bindparam, text
from sqlalchemy.engine.row import Row

from atlas.entities.types import EntityTypeKey
from atlas.identifiers.types import IdentifierSchemeKey
from atlas.search.settings import GlobalSearchSettings


class GlobalSearchRepository:
    def __init__(self, session: Any, settings: GlobalSearchSettings):
        self.session = session
        self.settings = settings

    async def _execute(self, stmt: Any, params: Dict[str, Any]) -> Sequence[Row[Any]]:
        res = self.session.execute(stmt, params)
        if hasattr(res, "__await__"):
            res = await res
        return res.fetchall()

    async def get_exact_name_candidates(
        self, normalized_query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Row[Any]]:
        sql = """
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                e.canonical_name_normalized = :q AS exact_canonical,
                e.display_name_normalized = :q AS exact_display
            FROM entities e
            WHERE (e.canonical_name_normalized = :q OR e.display_name_normalized = :q)
        """
        params: Dict[str, Any] = {"q": normalized_query}
        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " LIMIT :limit"
        params["limit"] = self.settings.exact_prefix_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_exact_alias_candidates(
        self, normalized_query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Row[Any]]:
        sql = """
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                a.alias_type_key,
                a.value AS matched_text
            FROM entity_aliases a
            JOIN entities e ON e.entity_id = a.entity_id
            WHERE a.normalized_value = :q
              AND a.is_current = TRUE
        """
        params: Dict[str, Any] = {"q": normalized_query}
        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " LIMIT :limit"
        params["limit"] = self.settings.exact_prefix_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_exact_identifier_candidates(
        self,
        candidates_normalized: dict[IdentifierSchemeKey, str],
        entity_types: Optional[List[EntityTypeKey]],
    ) -> Sequence[Row[Any]]:
        if not candidates_normalized:
            return []

        or_clauses = []
        params: Dict[str, Any] = {}
        for i, (scheme, norm_val) in enumerate(candidates_normalized.items()):
            scheme_param = f"scheme_{i}"
            val_param = f"val_{i}"
            or_clauses.append(
                f"(i.scheme_key = :{scheme_param} AND i.normalized_value = :{val_param})"
            )
            params[scheme_param] = scheme.value if hasattr(scheme, "value") else str(scheme)
            params[val_param] = norm_val

        or_sql = " OR ".join(or_clauses)

        sql = f"""
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                i.scheme_key,
                i.value AS matched_text,
                i.scope_entity_id,
                se.display_name AS scope_display_name
            FROM entity_identifiers i
            JOIN entities e ON e.entity_id = i.entity_id
            LEFT JOIN entities se ON se.entity_id = i.scope_entity_id
            WHERE ({or_sql})
              AND i.is_current = TRUE
        """

        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " LIMIT :limit"
        params["limit"] = self.settings.exact_prefix_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_prefix_name_candidates(
        self, prefix: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Row[Any]]:
        escaped_prefix = prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like_pattern = f"{escaped_prefix}%"

        sql = """
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                e.canonical_name_normalized LIKE :like_pattern AS prefix_canonical,
                e.display_name_normalized LIKE :like_pattern AS prefix_display
            FROM entities e
            WHERE (
                e.canonical_name_normalized LIKE :like_pattern
                OR e.display_name_normalized LIKE :like_pattern
            )
        """
        params: Dict[str, Any] = {"like_pattern": like_pattern}
        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " LIMIT :limit"
        params["limit"] = self.settings.exact_prefix_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_prefix_alias_candidates(
        self, prefix: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Row[Any]]:
        escaped_prefix = prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like_pattern = f"{escaped_prefix}%"

        sql = """
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                a.alias_type_key,
                a.value AS matched_text
            FROM entity_aliases a
            JOIN entities e ON e.entity_id = a.entity_id
            WHERE a.normalized_value LIKE :like_pattern
              AND a.is_current = TRUE
        """
        params: Dict[str, Any] = {"like_pattern": like_pattern}
        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " LIMIT :limit"
        params["limit"] = self.settings.exact_prefix_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_prefix_identifier_candidates(
        self,
        prefix_candidates: dict[IdentifierSchemeKey, str],
        entity_types: Optional[List[EntityTypeKey]],
    ) -> Sequence[Row[Any]]:
        if not prefix_candidates:
            return []

        or_clauses = []
        params: Dict[str, Any] = {}
        for i, (scheme, prefix) in enumerate(prefix_candidates.items()):
            scheme_param = f"scheme_{i}"
            val_param = f"val_{i}"
            escaped_prefix = prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            like_pattern = f"{escaped_prefix}%"

            or_clauses.append(
                f"(i.scheme_key = :{scheme_param} AND i.normalized_value LIKE :{val_param})"
            )
            params[scheme_param] = scheme.value if hasattr(scheme, "value") else str(scheme)
            params[val_param] = like_pattern

        or_sql = " OR ".join(or_clauses)

        sql = f"""
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                i.scheme_key,
                i.value AS matched_text,
                i.scope_entity_id,
                se.display_name AS scope_display_name
            FROM entity_identifiers i
            JOIN entities e ON e.entity_id = i.entity_id
            LEFT JOIN entities se ON se.entity_id = i.scope_entity_id
            WHERE ({or_sql})
              AND i.is_current = TRUE
        """

        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " LIMIT :limit"
        params["limit"] = self.settings.exact_prefix_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_fuzzy_name_candidates(
        self, query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Row[Any]]:
        sql = """
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                similarity(e.canonical_name_normalized, :q) AS sim_canonical,
                similarity(e.display_name_normalized, :q) AS sim_display
            FROM entities e
            WHERE (e.canonical_name_normalized % :q OR e.display_name_normalized % :q)
              AND (
                  similarity(e.canonical_name_normalized, :q) >= :sim_threshold
                  OR similarity(e.display_name_normalized, :q) >= :sim_threshold
              )
        """
        params: Dict[str, Any] = {
            "q": query,
            "sim_threshold": self.settings.minimum_trigram_similarity,
        }
        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += (
            " ORDER BY GREATEST("
            "similarity(e.canonical_name_normalized, :q), "
            "similarity(e.display_name_normalized, :q)"
            ") DESC LIMIT :limit"
        )
        params["limit"] = self.settings.fuzzy_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)

    async def get_fuzzy_alias_candidates(
        self, query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Row[Any]]:
        sql = """
            SELECT 
                e.entity_id, 
                e.entity_type, 
                e.canonical_name, 
                e.display_name,
                a.alias_type_key,
                a.value AS matched_text,
                similarity(a.normalized_value, :q) AS sim_alias
            FROM entity_aliases a
            JOIN entities e ON e.entity_id = a.entity_id
            WHERE a.normalized_value % :q
              AND similarity(a.normalized_value, :q) >= :sim_threshold
              AND a.is_current = TRUE
        """
        params: Dict[str, Any] = {
            "q": query,
            "sim_threshold": self.settings.minimum_trigram_similarity,
        }
        if entity_types:
            sql += " AND e.entity_type IN :entity_types"
            params["entity_types"] = tuple(
                t.value if hasattr(t, "value") else str(t) for t in entity_types
            )

        sql += " ORDER BY similarity(a.normalized_value, :q) DESC LIMIT :limit"
        params["limit"] = self.settings.fuzzy_candidate_limit

        stmt = text(sql)
        if entity_types:
            stmt = stmt.bindparams(bindparam("entity_types", expanding=True))

        return await self._execute(stmt, params)
