"""Entity target resolver delegating deterministically to Stage 22 EntityResolutionService."""

from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.resolution.schemas import EntityResolutionRequest, ResolutionCandidate
from atlas.resolution.service import EntityResolutionService

from .enums import AtlasCommandErrorCode, AtlasCommandParseStatus
from .models import AmbiguityCandidate, ResolvedTargetSummary


@dataclass
class TargetResolutionOutcome:
    """Outcome of resolving an entity target for a bound command."""

    status: AtlasCommandParseStatus
    resolved_target: Optional[ResolvedTargetSummary] = None
    ambiguity_candidates: Optional[List[AmbiguityCandidate]] = None
    error_code: Optional[AtlasCommandErrorCode] = None
    error_message: Optional[str] = None


class AtlasCommandTargetResolver:
    """Resolves entity targets for ATLAS commands using Stage 22 EntityResolutionService.

    Guarantees deterministic, exact matching without fuzzy auto-correction,
    enforcing type constraints and strict ambiguity handling.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.resolution_service = EntityResolutionService(session)

    async def resolve(
        self,
        raw_target: str,
        allowed_entity_types: Optional[List[str]] = None,
        max_candidates: int = 10,
    ) -> TargetResolutionOutcome:
        """Resolves target string to a unique Entity or reports ambiguity / mismatch.

        Args:
            raw_target: Raw text target (e.g. 'NVDA', '"NVIDIA Corporation"', 'TSMC').
            allowed_entity_types: Entity types permitted by the command spec.
            max_candidates: Maximum ambiguity candidates to return.
        """
        clean_target = raw_target.strip()
        if not clean_target:
            return TargetResolutionOutcome(
                status=AtlasCommandParseStatus.INCOMPLETE,
                error_code=AtlasCommandErrorCode.MISSING_TARGET,
                error_message="Target entity identifier cannot be empty.",
            )

        # Delegate to Stage 22 EntityResolutionService
        req = EntityResolutionRequest(
            query=clean_target,
            include_historical=False,  # Section 17: Exclude historical
            max_candidates=max_candidates,
        )

        res = await self.resolution_service.resolve_entity(req)

        # Case 1: Target not found
        if res.status == "not_found" or not res.candidates:
            return TargetResolutionOutcome(
                status=AtlasCommandParseStatus.INVALID,
                error_code=AtlasCommandErrorCode.TARGET_NOT_FOUND,
                error_message=f"Target entity '{clean_target}' not found.",
            )

        # Case 2: Ambiguous target
        if res.status == "ambiguous":
            candidates_summary = [
                AmbiguityCandidate(
                    entity_id=c.entity_id,
                    entity_type=c.entity_type,
                    canonical_name=c.canonical_name,
                    display_name=c.display_name,
                    matched_value=c.matched_value,
                    match_kind=c.match_kind,
                    scope_entity_id=c.scope_entity_id,
                )
                for c in res.candidates[:max_candidates]
            ]
            ambig_msg = (
                f"Target '{clean_target}' is ambiguous ({len(candidates_summary)} candidates)."
            )
            return TargetResolutionOutcome(
                status=AtlasCommandParseStatus.AMBIGUOUS,
                ambiguity_candidates=candidates_summary,
                error_code=AtlasCommandErrorCode.TARGET_AMBIGUOUS,
                error_message=ambig_msg,
            )

        # Case 3: Resolved uniquely
        top_cand: ResolutionCandidate = res.candidates[0]

        # Validate target entity type constraints (Sections 20, 21, 176, 180)
        if allowed_entity_types:
            cand_type = top_cand.entity_type.lower()
            allowed_normalized = [t.lower() for t in allowed_entity_types]
            if cand_type not in allowed_normalized:
                allowed_str = ", ".join(allowed_entity_types)
                type_msg = (
                    f"Target entity type '{top_cand.entity_type}' is not allowed for this command "
                    f"(allowed: {allowed_str}). No implicit conversion is performed."
                )
                return TargetResolutionOutcome(
                    status=AtlasCommandParseStatus.INVALID,
                    error_code=AtlasCommandErrorCode.TARGET_TYPE_MISMATCH,
                    error_message=type_msg,
                )

        resolved_summary = ResolvedTargetSummary(
            entity_id=top_cand.entity_id,
            entity_type=top_cand.entity_type,
            canonical_name=top_cand.canonical_name,
            display_name=top_cand.display_name,
            matched_value=top_cand.matched_value,
            match_kind=top_cand.match_kind,
            scope_entity_id=top_cand.scope_entity_id,
        )

        return TargetResolutionOutcome(
            status=AtlasCommandParseStatus.READY,
            resolved_target=resolved_summary,
        )
