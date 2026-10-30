"""Context Relevance Scoring, Ranking, and Ambiguity Detection for Stage 125."""

from typing import Any, Dict, List, Optional, Tuple

from atlas.ai.context.domain import AtlasAiContextItem, ContextExclusionReason


class ContextRelevanceEngine:
    """Scores candidate context items and detects multi-panel ambiguities."""

    EXPLICIT_SELECTION_WEIGHT = 4.0
    FOCUSED_PANEL_WEIGHT = 3.0
    MODULE_MATCH_WEIGHT = 2.0
    ENTITY_MATCH_WEIGHT = 2.5
    RECENCY_WEIGHT = 1.0
    STALENESS_PENALTY = 2.0
    REDUNDANCY_PENALTY = 1.5

    @classmethod
    def score_context_item(
        cls,
        item: AtlasAiContextItem,
        user_query: str,
        current_route: str,
        focused_panel_id: Optional[str] = None,
        referenced_entity_ids: Optional[List[str]] = None,
        is_pinned: bool = False,
    ) -> float:
        """Calculates deterministic relevance score for a context candidate."""
        score = 1.0
        q = user_query.lower()

        # 1. Explicit selection / Pinning
        if is_pinned or item.is_pinned:
            score += cls.EXPLICIT_SELECTION_WEIGHT

        # 2. Focused panel match
        if focused_panel_id and (
            item.canonical_target_id == focused_panel_id
            or item.structured_payload.get("panel_id") == focused_panel_id
            or item.structured_payload.get("active_panel_id") == focused_panel_id
        ):
            score += cls.FOCUSED_PANEL_WEIGHT

        # 3. Current route/module match
        if current_route and item.source_reference and current_route in item.source_reference:
            score += cls.MODULE_MATCH_WEIGHT

        # 4. Entity match in user query
        symbol = str(item.structured_payload.get("symbol", "")).lower()
        canonical_name = str(item.structured_payload.get("canonical_name", "")).lower()
        target_id = item.canonical_target_id.lower()

        if referenced_entity_ids and (item.canonical_target_id in referenced_entity_ids):
            score += cls.ENTITY_MATCH_WEIGHT
        elif (
            (symbol and symbol in q) or (canonical_name and canonical_name in q) or (target_id in q)
        ):
            score += cls.ENTITY_MATCH_WEIGHT

        # 5. Stale penalty
        if item.data_quality_status.value == "STALE":
            score -= cls.STALENESS_PENALTY

        return round(score, 2)

    @classmethod
    def detect_ambiguity(
        cls,
        user_query: str,
        candidate_items: List[AtlasAiContextItem],
        focused_panel_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], List[Dict[str, str]]]:
        """Detects whether a query like 'explain this chart' is ambiguous across multiple panels without focus."""
        q = user_query.lower().strip()
        deictic_queries = [
            "this chart",
            "explain the chart",
            "explain this",
            "this company",
            "this portfolio",
        ]

        is_deictic = any(dq in q for dq in deictic_queries)
        if not is_deictic:
            return False, None, []

        # If user explicitly specified focused panel, there is no ambiguity
        if focused_panel_id:
            return False, None, []

        # Count charts or items of the same type
        same_type_items = [item for item in candidate_items if "CHART" in item.context_type.value]

        if len(same_type_items) >= 2:
            candidates = [
                {
                    "target_id": it.canonical_target_id,
                    "summary": it.content_summary,
                }
                for it in same_type_items
            ]
            msg = (
                f"Your workspace contains {len(same_type_items)} charts, but no panel is currently focused. "
                "Please select which chart you would like to analyze."
            )
            return True, msg, candidates

        return False, None, []

    @classmethod
    def rank_and_deduplicate(
        cls,
        candidate_items: List[AtlasAiContextItem],
        token_budget: int = 8000,
    ) -> Tuple[List[AtlasAiContextItem], List[Dict[str, Any]], int]:
        """Ranks items by relevance score, removes duplicates, and trims to fit token budget."""
        # Sort descending by relevance score
        sorted_items = sorted(candidate_items, key=lambda it: it.relevance_score, reverse=True)

        included: List[AtlasAiContextItem] = []
        excluded: List[Dict[str, Any]] = []
        seen_targets: set[str] = set()
        accumulated_tokens = 0

        for it in sorted_items:
            key = f"{it.context_type.value}:{it.canonical_target_id}"
            if key in seen_targets:
                excluded.append(
                    {
                        "context_item_id": it.context_item_id,
                        "target_id": it.canonical_target_id,
                        "reason": ContextExclusionReason.NOT_RELEVANT.value,
                        "detail": "Duplicate context item for same canonical target",
                    }
                )
                continue

            est_tokens = it.estimated_tokens or 100
            if accumulated_tokens + est_tokens > token_budget:
                excluded.append(
                    {
                        "context_item_id": it.context_item_id,
                        "target_id": it.canonical_target_id,
                        "reason": ContextExclusionReason.TOO_LARGE.value,
                        "detail": f"Item exceeds remaining token budget ({token_budget - accumulated_tokens} tokens remaining)",
                    }
                )
                continue

            seen_targets.add(key)
            included.append(it)
            accumulated_tokens += est_tokens

        return included, excluded, accumulated_tokens
