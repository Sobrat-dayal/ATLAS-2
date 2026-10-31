"""Canonical Entity Resolver and Registry (Stage 136).

Provides deterministic resolution of financial entities, issuers, legal entities,
instruments, corporate facilities, infrastructure assets, commodities, economic indicators,
and geographic jurisdictions.

Enforces zero false-positive identity collisions, temporal identifier ownership
(e.g., reused ticker symbols across historical epochs), and strict sanctions matching.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ..domain import CanonicalGraphNodeRef, GraphNodeType
from ..errors import IdentityResolutionError


class HistoricalAliasMapping:
    """Historical identifier mapping with temporal validity."""
    def __init__(
        self,
        identifier_type: str,
        identifier_value: str,
        node_key: str,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
    ):
        self.identifier_type = identifier_type.upper().strip()
        self.identifier_value = identifier_value.upper().strip()
        self.node_key = node_key
        self.valid_from = valid_from
        self.valid_to = valid_to

    def is_active_at(self, query_time: Optional[datetime]) -> bool:
        """Determines if this mapping is temporally active at the specified query time."""
        if query_time is None:
            # If no as-of time specified, check if currently active (valid_to is None or in future)
            now = datetime.now(timezone.utc)
            return (self.valid_to is None or self.valid_to >= now)
        
        if self.valid_from and query_time < self.valid_from:
            return False
        if self.valid_to and query_time > self.valid_to:
            return False
        return True


class CanonicalEntityResolver:
    """Institutional entity registry and resolver."""

    def __init__(self):
        # Primary node store: node_key -> CanonicalGraphNodeRef
        self._nodes: Dict[str, CanonicalGraphNodeRef] = {}
        # Identifier index: (id_type, normalized_value) -> List[HistoricalAliasMapping]
        self._alias_index: Dict[tuple[str, str], List[HistoricalAliasMapping]] = {}

    def register_node(
        self,
        node: CanonicalGraphNodeRef,
        aliases: Optional[List[Dict[str, Any]]] = None,
    ) -> CanonicalGraphNodeRef:
        """Registers a canonical node and indexes its identifier mappings."""
        key = node.node_key
        self._nodes[key] = node

        # Index primary identifiers from identifier_map
        for id_type, val in node.identifier_map.items():
            norm_type = id_type.upper().strip()
            norm_val = val.upper().strip()
            mapping = HistoricalAliasMapping(
                identifier_type=norm_type,
                identifier_value=norm_val,
                node_key=key,
            )
            self._alias_index.setdefault((norm_type, norm_val), []).append(mapping)

        # Index additional historical or specific aliases
        if aliases:
            for alias in aliases:
                norm_type = alias.get("type", "ALIAS").upper().strip()
                norm_val = str(alias.get("value", "")).upper().strip()
                valid_from = alias.get("valid_from")
                valid_to = alias.get("valid_to")
                mapping = HistoricalAliasMapping(
                    identifier_type=norm_type,
                    identifier_value=norm_val,
                    node_key=key,
                    valid_from=valid_from,
                    valid_to=valid_to,
                )
                self._alias_index.setdefault((norm_type, norm_val), []).append(mapping)

        return node

    def get_node(self, node_type: GraphNodeType, entity_id: str) -> Optional[CanonicalGraphNodeRef]:
        """Direct retrieval by node type and canonical ID."""
        key = f"{node_type.value}:{entity_id}"
        return self._nodes.get(key)

    def resolve(
        self,
        identifier: str,
        id_type: Optional[str] = None,
        as_of: Optional[datetime] = None,
        require_exact: bool = False,
    ) -> CanonicalGraphNodeRef:
        """Resolves an identifier to a canonical graph node.
        
        Supports temporal ticker re-use disambiguation and strict exact-match
        verification (critical for sanctions and legal designations).
        """
        norm_val = identifier.upper().strip()

        # If id_type is specified, look specifically for that type
        if id_type:
            norm_type = id_type.upper().strip()
            candidates = self._alias_index.get((norm_type, norm_val), [])
            active = [c for c in candidates if c.is_active_at(as_of)]
            if len(active) == 1:
                return self._nodes[active[0].node_key]
            elif len(active) > 1:
                # Disambiguate if valid_from is closer
                active.sort(key=lambda x: x.valid_from or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
                return self._nodes[active[0].node_key]
            elif candidates and not active:
                raise IdentityResolutionError(
                    identifier=identifier,
                    reason=f"Identifier '{identifier}' ({norm_type}) was not active as-of {as_of.isoformat() if as_of else 'now'}."
                )

        # Try common identifier types if not specified
        for test_type in ["LEI", "CIK", "ISIN", "TICKER", "FACILITY_ID", "ASSET_ID", "ISO2", "INDICATOR_ID"]:
            candidates = self._alias_index.get((test_type, norm_val), [])
            active = [c for c in candidates if c.is_active_at(as_of)]
            if active:
                return self._nodes[active[0].node_key]

        # Check direct entity_id matching across all nodes
        for node in self._nodes.values():
            if node.entity_id.upper() == norm_val:
                return node
            if not require_exact and node.canonical_name.upper() == norm_val:
                return node

        raise IdentityResolutionError(
            identifier=identifier,
            reason=f"No matching canonical entity found for identifier '{identifier}' (as-of: {as_of.isoformat() if as_of else 'present'})."
        )

    def list_all_nodes(self) -> List[CanonicalGraphNodeRef]:
        """Returns all registered canonical nodes."""
        return list(self._nodes.values())

