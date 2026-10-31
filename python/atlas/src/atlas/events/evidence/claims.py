"""Event Claim Registry and Source Conflict Engine (Stage 135).

Manages granular factual claims asserted by external sources.
Preserves explicit source contradictions without overwriting or fabricating averages.
"""

from typing import Dict, List, Optional
from ..domain import ClaimConflictStatus, EventClaim, EventEvidence, EvidenceRole


class EventClaimRegistry:
    """Registry maintaining source-backed claims and evaluating claim consensus/conflict."""

    def __init__(self) -> None:
        # Maps event_id -> list of EventClaim
        self._claims_by_event: Dict[str, List[EventClaim]] = {}
        # Maps event_id -> list of EventEvidence
        self._evidence_by_event: Dict[str, List[EventEvidence]] = {}

    def add_evidence(self, evidence: EventEvidence) -> None:
        """Link a supporting source evidence record to an event."""
        if evidence.event_id not in self._evidence_by_event:
            self._evidence_by_event[evidence.event_id] = []
        self._evidence_by_event[evidence.event_id].append(evidence)

    def get_evidence(self, event_id: str) -> List[EventEvidence]:
        """Retrieve all supporting evidence links for an event."""
        return list(self._evidence_by_event.get(event_id, []))

    def add_claim(self, claim: EventClaim) -> None:
        """Record an explicit factual assertion made by a source."""
        if claim.event_id not in self._claims_by_event:
            self._claims_by_event[claim.event_id] = []
        self._claims_by_event[claim.event_id].append(claim)

    def record_claim(self, claim: EventClaim) -> None:
        """Alias for add_claim."""
        self.add_claim(claim)

    def get_claims(self, event_id: str) -> List[EventClaim]:
        """Retrieve all claims associated with an event."""
        return list(self._claims_by_event.get(event_id, []))

    def get_claims_for_event(self, event_id: str) -> List[EventClaim]:
        """Alias for get_claims."""
        return self.get_claims(event_id)

    def migrate_claims_to_event(self, from_event_id: str, to_event_id: str) -> None:
        """Migrate claims from one event to another during merge."""
        claims = self._claims_by_event.pop(from_event_id, [])
        for c in claims:
            c.event_id = to_event_id
        if to_event_id not in self._claims_by_event:
            self._claims_by_event[to_event_id] = []
        self._claims_by_event[to_event_id].extend(claims)

    def evaluate_conflict_status(self, event_id: str) -> ClaimConflictStatus:
        """Evaluate cross-source agreement on predicates.

        Strict Invariant: Conflicting claims are preserved with attribution.
        Conflicting numbers are NEVER averaged without methodology.
        """
        claims = self.get_claims(event_id)
        if not claims or len(claims) <= 1:
            return ClaimConflictStatus.NO_CONFLICT

        # Group by predicate
        by_predicate: Dict[str, List[EventClaim]] = {}
        for c in claims:
            if c.predicate not in by_predicate:
                by_predicate[c.predicate] = []
            by_predicate[c.predicate].append(c)

        for predicate, plist in by_predicate.items():
            if len(plist) > 1:
                # Check for disparate values
                distinct_values = {str(c.claim_value) for c in plist}
                if len(distinct_values) > 1:
                    return ClaimConflictStatus.CONFLICTED

        return ClaimConflictStatus.NO_CONFLICT
