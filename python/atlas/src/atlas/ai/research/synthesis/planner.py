"""Research Planner and Synthesis package for Stage 127 AI Research."""

from __future__ import annotations

from typing import List

from atlas.ai.research.domain import ResearchQueryPlan


class ResearchPlanner:
    """Formulates and optimizes retrieval queries based on research goals."""

    @staticmethod
    def plan_research_query(query_plan: ResearchQueryPlan) -> List[str]:
        """Expands query plan into bounded sub-queries for hybrid search."""
        queries = [query_plan.query]
        for sym in query_plan.target_symbols:
            if sym.lower() not in query_plan.query.lower():
                queries.append(f"{sym} {query_plan.query}")
        return queries[:3]
