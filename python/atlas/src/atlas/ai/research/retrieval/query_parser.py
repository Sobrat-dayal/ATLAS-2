"""Research Query Parser for Stage 127 (Part XXVI).

Extracts financial intent, company symbols, document types, date bounds,
and historical as-of dates from research prompts without hallucinating constraints.
"""

from __future__ import annotations

import re
from typing import List, Optional

from atlas.ai.research.domain import ResearchQueryPlan, RetrievalStrategy


def parse_research_query(
    query: str,
    explicit_symbols: Optional[List[str]] = None,
    explicit_document_types: Optional[List[str]] = None,
    explicit_historical_as_of: Optional[str] = None,
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.HYBRID_FUSION,
    max_evidence_units: int = 5,
    token_budget: int = 4000,
) -> ResearchQueryPlan:
    """Parses raw user query into a structured execution plan."""
    clean_query = query.strip()

    symbols = list(explicit_symbols or [])
    doc_types = list(explicit_document_types or [])

    # Extract common ticker patterns like TEST_COMPANY, AAPL, MSFT, NVDA
    ticker_pattern = re.compile(r"\b([A-Z]{2,10}(?:_[A-Z]{2,10})?)\b")
    for match in ticker_pattern.findall(clean_query):
        # Exclude common query words in uppercase
        if match not in {
            "WHAT",
            "WAS",
            "THE",
            "WHEN",
            "WHY",
            "HOW",
            "AND",
            "FOR",
            "CAPEX",
            "GAAP",
            "GROWTH",
        }:
            if match not in symbols:
                symbols.append(match)

    # Extract document types if mentioned
    if re.search(r"\b10-?k\b|annual\s+report", clean_query, re.IGNORECASE):
        if "10-K" not in doc_types:
            doc_types.append("10-K")
    if re.search(r"\b10-?q\b|quarterly", clean_query, re.IGNORECASE):
        if "10-Q" not in doc_types:
            doc_types.append("10-Q")
    if re.search(r"\bcapex\b|capital\s+plan", clean_query, re.IGNORECASE):
        if "CAPEX_PLAN" not in doc_types:
            doc_types.append("CAPEX_PLAN")
    if re.search(r"\btranscript\b|earnings\s+call", clean_query, re.IGNORECASE):
        if "TRANSCRIPT" not in doc_types:
            doc_types.append("TRANSCRIPT")

    # Extract historical as-of date if mentioned in query text (e.g. "on 2024-12-31" or "as of 2024-12-31")
    hist_as_of = explicit_historical_as_of
    if not hist_as_of:
        date_match = re.search(r"(?:as\s+of|on)\s+(\d{4}-\d{2}-\d{2})", clean_query, re.IGNORECASE)
        if date_match:
            hist_as_of = f"{date_match.group(1)}T23:59:59Z"

    return ResearchQueryPlan(
        plan_id=f"plan_{abs(hash(clean_query)) % 1000000}",
        query=clean_query,
        target_symbols=symbols,
        document_types=doc_types,
        historical_as_of=hist_as_of,
        retrieval_strategy=retrieval_strategy,
        max_evidence_units=max_evidence_units,
        token_budget=token_budget,
    )
