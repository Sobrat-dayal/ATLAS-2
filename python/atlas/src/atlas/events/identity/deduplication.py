"""Multi-Source Deduplication and Candidate Matching Engine (Stage 135).

Enforces institutional deduplication: multiple reports or articles describing the
same real-world event attach to a single canonical event.
Strict Invariant: Never deduplicate solely on headline or title similarity!
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..domain import AtlasUniversalEvent
from .canonical import generate_canonical_event_key


class MatchConfidence(str, Enum):
    """Classification of candidate match strength."""
    EXACT_CANONICAL_KEY = "EXACT_CANONICAL_KEY"
    EXACT_IDENTITY = "EXACT_IDENTITY"
    HIGH_EVIDENCE_MATCH = "HIGH_EVIDENCE_MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    AMBIGUOUS = "AMBIGUOUS"
    DISTINCT = "DISTINCT"
    UNRELATED = "UNRELATED"
    CONFLICTED = "CONFLICTED"


class DeduplicationEngine:
    """Manages cross-source candidate matching and deduplication checks."""

    def __init__(self) -> None:
        # Maps canonical_event_key -> event_id
        self._key_to_event_id: Dict[str, str] = {}
        # Maps source_alias -> event_id
        self._alias_to_event_id: Dict[str, str] = {}

    def register_event(self, event: AtlasUniversalEvent) -> None:
        """Register canonical key and aliases for fast lookup."""
        self._key_to_event_id[event.canonical_event_key] = event.event_id
        for alias in event.aliases:
            self._alias_to_event_id[alias] = event.event_id

    def unregister_event(self, event: AtlasUniversalEvent) -> None:
        """Remove event mappings."""
        self._key_to_event_id.pop(event.canonical_event_key, None)
        for alias in event.aliases:
            self._alias_to_event_id.pop(alias, None)

    def find_match_by_key(self, canonical_key: str) -> Optional[str]:
        """Look up existing event ID by exact canonical key or alias."""
        if canonical_key in self._key_to_event_id:
            return self._key_to_event_id[canonical_key]
        return self._alias_to_event_id.get(canonical_key)

    def find_matching_event(
        self,
        candidate_event: AtlasUniversalEvent,
        existing_events: List[AtlasUniversalEvent],
    ) -> Tuple[Optional[str], MatchConfidence, str]:
        """Find matching event among existing events.
        
        Strict Invariant: Never deduplicate solely on headline or title similarity!
        """
        # 1. Exact canonical key match or alias match
        for existing in existing_events:
            if existing.event_id == candidate_event.event_id:
                continue
            if existing.canonical_event_key == candidate_event.canonical_event_key:
                return existing.event_id, MatchConfidence.EXACT_CANONICAL_KEY, "Exact canonical event key match"
            if candidate_event.canonical_event_key in existing.aliases or existing.canonical_event_key in candidate_event.aliases:
                return existing.event_id, MatchConfidence.EXACT_CANONICAL_KEY, "Alias key match"

        # 2. Structural candidate evaluation
        for existing in existing_events:
            if existing.event_id == candidate_event.event_id:
                continue
            confidence, reason = self.evaluate_candidate(
                candidate_key=candidate_event.canonical_event_key,
                candidate_type=candidate_event.event_type,
                candidate_payload=candidate_event.event_payload,
                existing_event=existing,
            )
            if confidence in [MatchConfidence.EXACT_IDENTITY, MatchConfidence.EXACT_CANONICAL_KEY]:
                return existing.event_id, MatchConfidence.EXACT_CANONICAL_KEY, reason
            if confidence == MatchConfidence.HIGH_EVIDENCE_MATCH:
                return existing.event_id, MatchConfidence.EXACT_CANONICAL_KEY, reason
            if confidence in [MatchConfidence.POSSIBLE_MATCH, MatchConfidence.AMBIGUOUS]:
                return existing.event_id, MatchConfidence.AMBIGUOUS, reason

        return None, MatchConfidence.DISTINCT, "No matching canonical event found"

    def evaluate_candidate(
        self,
        candidate_key: str,
        candidate_type: str,
        candidate_payload: Dict[str, Any],
        existing_event: AtlasUniversalEvent,
    ) -> Tuple[MatchConfidence, str]:
        """Evaluate match confidence between an incoming candidate and an existing event.

        Strict Invariant: Title/headline similarity ALONE is never sufficient to establish match.
        """
        # 1. Exact canonical key match
        if candidate_key == existing_event.canonical_event_key or candidate_key in existing_event.aliases:
            return MatchConfidence.EXACT_IDENTITY, "Exact canonical key match"

        # 2. Check type compatibility
        if candidate_type != existing_event.event_type:
            # Different subtypes: check if one is lifecycle continuation (e.g. Announced vs Completed)
            if "MERGER_ANNOUNCED" in candidate_type and "MERGER_COMPLETED" in existing_event.event_type:
                return MatchConfidence.CONFLICTED, "Distinct merger lifecycle stages must remain separate events"
            if "SCHEDULED" in candidate_type and "RELEASED" in existing_event.event_type:
                return MatchConfidence.UNRELATED, "Scheduled announcement vs actual published release"
            return MatchConfidence.UNRELATED, "Incompatible event types"

        # 3. Type-specific deep matching
        # Earthquakes: distinct USGS IDs are distinct earthquakes even if close geographically
        if "EARTHQUAKE" in candidate_type:
            c_src = candidate_payload.get("source_event_id")
            e_src = existing_event.event_payload.get("source_event_id")
            if c_src and e_src and c_src != e_src:
                return MatchConfidence.UNRELATED, "Distinct seismic hypocenter event identifiers"

        # Earnings: same issuer, same fiscal year and quarter
        if "EARNINGS" in candidate_type:
            c_iss = candidate_payload.get("issuer_reference")
            e_iss = existing_event.event_payload.get("issuer_reference")
            c_fy = candidate_payload.get("fiscal_year")
            e_fy = existing_event.event_payload.get("fiscal_year")
            c_fq = candidate_payload.get("fiscal_quarter")
            e_fq = existing_event.event_payload.get("fiscal_quarter")

            if c_iss and e_iss and c_iss == e_iss and c_fy == e_fy and c_fq == e_fq:
                return MatchConfidence.HIGH_EVIDENCE_MATCH, "Identical issuer, fiscal year, and fiscal quarter"

        # Sanctions: matching designated subject and legal action
        if "SANCTIONS" in candidate_type:
            c_subj = candidate_payload.get("designated_subject_reference")
            e_subj = existing_event.event_payload.get("designated_subject_reference")
            c_act = candidate_payload.get("action_type")
            e_act = existing_event.event_payload.get("action_type")
            if c_subj and e_subj and c_subj == e_subj and c_act == e_act:
                return MatchConfidence.HIGH_EVIDENCE_MATCH, "Matching designated subject and sanction action"

        return MatchConfidence.UNRELATED, "Insufficient structural evidence to link records"
