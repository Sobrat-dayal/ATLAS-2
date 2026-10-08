import uuid
from typing import List, Dict, Tuple, Optional

from atlas.search.models import GlobalSearchRequest, GlobalSearchResponse, GlobalSearchEntityResult
from atlas.search.settings import GlobalSearchSettings
from atlas.search.repository import GlobalSearchRepository
from atlas.search.enums import GlobalSearchMatchKind
from atlas.entities.name_normalization import normalize_entity_name
from atlas.entities.types import EntityTypeKey
from atlas.identifiers.types import IdentifierSchemeKey, IdentifierNormalizationStrategy
from atlas.identifiers.registry import IDENTIFIER_SCHEMES_REGISTRY
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


SEARCHABLE_IDENTIFIER_SCHEMES = [
    IdentifierSchemeKey.TICKER,
    IdentifierSchemeKey.FIGI,
    IdentifierSchemeKey.COMPOSITE_FIGI,
    IdentifierSchemeKey.SHARE_CLASS_FIGI,
    IdentifierSchemeKey.ISIN,
    IdentifierSchemeKey.CUSIP,
    IdentifierSchemeKey.SEDOL,
    IdentifierSchemeKey.OCC_OPTION_SYMBOL,
    IdentifierSchemeKey.ISO_4217_ALPHA,
    IdentifierSchemeKey.ISO_4217_NUMERIC,
    IdentifierSchemeKey.CIK,
    IdentifierSchemeKey.LEI,
    IdentifierSchemeKey.ISO_3166_ALPHA2,
    IdentifierSchemeKey.ISO_3166_ALPHA3,
    IdentifierSchemeKey.ISO_3166_NUMERIC,
    IdentifierSchemeKey.IATA_AIRPORT,
    IdentifierSchemeKey.ICAO_AIRPORT,
    IdentifierSchemeKey.UNLOCODE,
    IdentifierSchemeKey.MIC,
    IdentifierSchemeKey.FRED_SERIES,
    IdentifierSchemeKey.WORLD_BANK_INDICATOR,
    IdentifierSchemeKey.OECD_SERIES,
    IdentifierSchemeKey.IMF_SERIES,
    IdentifierSchemeKey.DOI,
    IdentifierSchemeKey.ARXIV,
    IdentifierSchemeKey.OPENALEX,
    IdentifierSchemeKey.SEMANTIC_SCHOLAR,
    IdentifierSchemeKey.PUBMED,
    IdentifierSchemeKey.ISBN_10,
    IdentifierSchemeKey.ISBN_13,
    IdentifierSchemeKey.CROSSREF,
]

PREFIX_IDENTIFIER_SCHEMES = [
    IdentifierSchemeKey.TICKER,
    IdentifierSchemeKey.MIC,
    IdentifierSchemeKey.IATA_AIRPORT,
    IdentifierSchemeKey.ICAO_AIRPORT,
    IdentifierSchemeKey.ISO_3166_ALPHA2,
    IdentifierSchemeKey.ISO_3166_ALPHA3,
]

RANK_TIERS = {
    GlobalSearchMatchKind.EXACT_IDENTIFIER: 1,
    GlobalSearchMatchKind.EXACT_CANONICAL_NAME: 2,
    GlobalSearchMatchKind.EXACT_DISPLAY_NAME: 2,
    GlobalSearchMatchKind.EXACT_ALIAS: 3,
    GlobalSearchMatchKind.PREFIX_IDENTIFIER: 4,
    GlobalSearchMatchKind.PREFIX_CANONICAL_NAME: 5,
    GlobalSearchMatchKind.PREFIX_DISPLAY_NAME: 5,
    GlobalSearchMatchKind.PREFIX_ALIAS: 6,
    GlobalSearchMatchKind.FUZZY_CANONICAL_NAME: 7,
    GlobalSearchMatchKind.FUZZY_DISPLAY_NAME: 7,
    GlobalSearchMatchKind.FUZZY_ALIAS: 8,
}

class GlobalSearchService:
    def __init__(self, repository: GlobalSearchRepository, settings: GlobalSearchSettings):
        self.repository = repository
        self.settings = settings

    def _normalize_identifier(self, scheme_key: IdentifierSchemeKey, value: str) -> Optional[str]:
        scheme_def = IDENTIFIER_SCHEMES_REGISTRY.get(scheme_key)
        if not scheme_def:
            return None
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

    def search_entities(self, request: GlobalSearchRequest) -> GlobalSearchResponse:
        query = request.query.strip()
        if not query:
            return GlobalSearchResponse(results=[])

        if len(query) > self.settings.max_query_characters:
            raise ValueError("SEARCH_QUERY_TOO_LONG")
            
        try:
            normalized_query = normalize_entity_name(query)
        except ValueError:
            return GlobalSearchResponse(results=[])
            
        if not normalized_query:
            return GlobalSearchResponse(results=[])

        limit = request.limit or self.settings.default_limit
        entity_types = request.entity_types

        candidates: Dict[uuid.UUID, GlobalSearchEntityResult] = {}
        
        # Helper to merge candidates deterministically
        def add_candidate(result: GlobalSearchEntityResult, score: float = 1.0):
            existing = candidates.get(result.entity_id)
            if existing:
                existing_tier = RANK_TIERS[existing.match_kind]
                new_tier = RANK_TIERS[result.match_kind]
                
                if new_tier < existing_tier:
                    candidates[result.entity_id] = result
                elif new_tier == existing_tier:
                    # Tie break: shorter matched text, then display name, then entity UUID
                    if len(result.matched_text) < len(existing.matched_text):
                        candidates[result.entity_id] = result
                    elif len(result.matched_text) == len(existing.matched_text):
                        if result.display_name < existing.display_name:
                            candidates[result.entity_id] = result
                        elif result.display_name == existing.display_name:
                            if str(result.entity_id) < str(existing.entity_id):
                                candidates[result.entity_id] = result
            else:
                candidates[result.entity_id] = result

        # 1. Exact Name/Alias Candidates
        name_rows = self.repository.get_exact_name_candidates(normalized_query, entity_types)
        for row in name_rows:
            if row.exact_canonical:
                kind = GlobalSearchMatchKind.EXACT_CANONICAL_NAME
                text = row.canonical_name
            else:
                kind = GlobalSearchMatchKind.EXACT_DISPLAY_NAME
                text = row.display_name
            
            add_candidate(GlobalSearchEntityResult(
                entity_id=row.entity_id,
                entity_type=EntityTypeKey(row.entity_type),
                canonical_name=row.canonical_name,
                display_name=row.display_name,
                match_kind=kind,
                matched_text=text
            ))

        alias_rows = self.repository.get_exact_alias_candidates(normalized_query, entity_types)
        for row in alias_rows:
            add_candidate(GlobalSearchEntityResult(
                entity_id=row.entity_id,
                entity_type=EntityTypeKey(row.entity_type),
                canonical_name=row.canonical_name,
                display_name=row.display_name,
                match_kind=GlobalSearchMatchKind.EXACT_ALIAS,
                matched_text=row.matched_text,
                alias_type_key=row.alias_type_key
            ))

        # 2. Exact Identifier Candidates
        exact_id_targets = {}
        for scheme in SEARCHABLE_IDENTIFIER_SCHEMES:
            try:
                norm_val = self._normalize_identifier(scheme, query)
                if norm_val:
                    exact_id_targets[scheme] = norm_val
            except Exception:
                pass
                
        id_rows = self.repository.get_exact_identifier_candidates(exact_id_targets, entity_types)
        for row in id_rows:
            add_candidate(GlobalSearchEntityResult(
                entity_id=row.entity_id,
                entity_type=EntityTypeKey(row.entity_type),
                canonical_name=row.canonical_name,
                display_name=row.display_name,
                match_kind=GlobalSearchMatchKind.EXACT_IDENTIFIER,
                matched_text=row.matched_text,
                identifier_scheme_key=row.scheme_key,
                scope_entity_id=row.scope_entity_id,
                scope_display_name=row.scope_display_name
            ))

        # 3. Prefix Name/Alias Candidates
        prefix_name_rows = self.repository.get_prefix_name_candidates(normalized_query, entity_types)
        for row in prefix_name_rows:
            if row.prefix_canonical:
                kind = GlobalSearchMatchKind.PREFIX_CANONICAL_NAME
                text = row.canonical_name
            else:
                kind = GlobalSearchMatchKind.PREFIX_DISPLAY_NAME
                text = row.display_name
                
            add_candidate(GlobalSearchEntityResult(
                entity_id=row.entity_id,
                entity_type=EntityTypeKey(row.entity_type),
                canonical_name=row.canonical_name,
                display_name=row.display_name,
                match_kind=kind,
                matched_text=text
            ))
            
        prefix_alias_rows = self.repository.get_prefix_alias_candidates(normalized_query, entity_types)
        for row in prefix_alias_rows:
            add_candidate(GlobalSearchEntityResult(
                entity_id=row.entity_id,
                entity_type=EntityTypeKey(row.entity_type),
                canonical_name=row.canonical_name,
                display_name=row.display_name,
                match_kind=GlobalSearchMatchKind.PREFIX_ALIAS,
                matched_text=row.matched_text,
                alias_type_key=row.alias_type_key
            ))

        # 4. Prefix Identifier Candidates
        prefix_id_targets = {}
        for scheme in PREFIX_IDENTIFIER_SCHEMES:
            # For prefix, we normalize as much as possible but don't strictly enforce length if normalizer doesn't barf
            # Actually, we can reuse exact targets if the normalizer is prefix-safe. Usually uppercase trim is.
            if scheme in exact_id_targets:
                prefix_id_targets[scheme] = exact_id_targets[scheme]
                
        prefix_id_rows = self.repository.get_prefix_identifier_candidates(prefix_id_targets, entity_types)
        for row in prefix_id_rows:
            add_candidate(GlobalSearchEntityResult(
                entity_id=row.entity_id,
                entity_type=EntityTypeKey(row.entity_type),
                canonical_name=row.canonical_name,
                display_name=row.display_name,
                match_kind=GlobalSearchMatchKind.PREFIX_IDENTIFIER,
                matched_text=row.matched_text,
                identifier_scheme_key=row.scheme_key,
                scope_entity_id=row.scope_entity_id,
                scope_display_name=row.scope_display_name
            ))

        # 5. Fuzzy Candidates
        if len(normalized_query) >= self.settings.fuzzy_min_characters and len(candidates) < limit:
            fuzzy_name_rows = self.repository.get_fuzzy_name_candidates(normalized_query, entity_types)
            for row in fuzzy_name_rows:
                if row.sim_canonical >= row.sim_display:
                    kind = GlobalSearchMatchKind.FUZZY_CANONICAL_NAME
                    text = row.canonical_name
                else:
                    kind = GlobalSearchMatchKind.FUZZY_DISPLAY_NAME
                    text = row.display_name
                    
                add_candidate(GlobalSearchEntityResult(
                    entity_id=row.entity_id,
                    entity_type=EntityTypeKey(row.entity_type),
                    canonical_name=row.canonical_name,
                    display_name=row.display_name,
                    match_kind=kind,
                    matched_text=text
                ))
                
            fuzzy_alias_rows = self.repository.get_fuzzy_alias_candidates(normalized_query, entity_types)
            for row in fuzzy_alias_rows:
                add_candidate(GlobalSearchEntityResult(
                    entity_id=row.entity_id,
                    entity_type=EntityTypeKey(row.entity_type),
                    canonical_name=row.canonical_name,
                    display_name=row.display_name,
                    match_kind=GlobalSearchMatchKind.FUZZY_ALIAS,
                    matched_text=row.matched_text,
                    alias_type_key=row.alias_type_key
                ))

        # Final Rank and Limit
        results = list(candidates.values())
        results.sort(key=lambda r: (
            RANK_TIERS[r.match_kind],
            len(r.matched_text),
            r.display_name,
            str(r.entity_id)
        ))
        
        return GlobalSearchResponse(results=results[:limit])
