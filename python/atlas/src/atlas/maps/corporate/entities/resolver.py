"""Entity resolution for corporate geography and securities mapping (Stage 132).

Ensures ticker symbols, share classes (e.g. GOOG vs GOOGL, BRK.A vs BRK.B), LEIs,
and CIKs correctly resolve to the singular canonical company entity ID.
"""

from __future__ import annotations

import re
from typing import Any

from atlas.maps.corporate.errors import CompanyNotFoundError


class CanonicalEntityResolver:
    """In-memory and repository-backed resolver for corporate entities."""

    def __init__(self, entities_catalog: list[dict[str, Any]] | None = None) -> None:
        self._catalog: dict[str, dict[str, Any]] = {}
        self._symbol_map: dict[str, str] = {}
        self._lei_map: dict[str, str] = {}
        self._cik_map: dict[str, str] = {}
        self._name_map: dict[str, str] = {}

        if entities_catalog:
            for item in entities_catalog:
                self.register_entity(item)

    def register_entity(self, item: dict[str, Any]) -> None:
        """Register an entity with its canonical identifiers and securities."""
        entity_id = str(item.get("entity_id") or item.get("company_id"))
        self._catalog[entity_id] = item

        canonical_name = item.get("canonical_name", "").strip().lower()
        if canonical_name:
            self._name_map[canonical_name] = entity_id

        legal_name = item.get("legal_name", "").strip().lower()
        if legal_name:
            self._name_map[legal_name] = entity_id

        lei = item.get("lei")
        if lei:
            self._lei_map[lei.strip().upper()] = entity_id

        cik = item.get("cik")
        if cik:
            self._cik_map[str(cik).strip().zfill(10)] = entity_id

        # Securities symbols mapping
        symbols = item.get("tickers") or item.get("symbols") or []
        if isinstance(symbols, str):
            symbols = [symbols]
        for sym in symbols:
            self._symbol_map[sym.strip().upper()] = entity_id

    def resolve(self, identifier: str) -> dict[str, Any]:
        """Resolve a query identifier (ID, ticker, LEI, CIK, name) to canonical company data."""
        if not identifier:
            raise CompanyNotFoundError("empty_identifier")

        clean = identifier.strip()
        upper = clean.upper()
        lower = clean.lower()

        # 1. Direct canonical ID match
        if clean in self._catalog:
            return self._catalog[clean]

        # 2. Ticker symbol match (e.g. GOOG, GOOGL -> Alphabet)
        if upper in self._symbol_map:
            ent_id = self._symbol_map[upper]
            return self._catalog[ent_id]

        # 3. LEI match
        if upper in self._lei_map:
            ent_id = self._lei_map[upper]
            return self._catalog[ent_id]

        # 4. CIK match
        cik_norm = clean.zfill(10)
        if cik_norm in self._cik_map:
            ent_id = self._cik_map[cik_norm]
            return self._catalog[ent_id]

        # 5. Canonical Name match
        if lower in self._name_map:
            ent_id = self._name_map[lower]
            return self._catalog[ent_id]

        # 6. Fuzzy / Normalized Name matching
        norm = re.sub(r"[^a-z0-9]", "", lower)
        for name_key, ent_id in self._name_map.items():
            key_norm = re.sub(r"[^a-z0-9]", "", name_key)
            if key_norm and (norm == key_norm or norm in key_norm or key_norm in norm):
                return self._catalog[ent_id]

        raise CompanyNotFoundError(identifier)

    def search_companies(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Search registered companies by name, symbol, or identifier."""
        if not query:
            return list(self._catalog.values())[:limit]

        q = query.strip().lower()
        results: list[dict[str, Any]] = []

        for entity in self._catalog.values():
            name = (entity.get("canonical_name") or "").lower()
            legal = (entity.get("legal_name") or "").lower()
            symbols = [s.lower() for s in (entity.get("tickers") or [])]
            lei = (entity.get("lei") or "").lower()
            cik = str(entity.get("cik") or "").lower()

            if (
                q in name
                or q in legal
                or any(q in s for s in symbols)
                or q in lei
                or q in cik
            ):
                results.append(entity)
                if len(results) >= limit:
                    break

        return results

