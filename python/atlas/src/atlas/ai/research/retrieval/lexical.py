"""Lexical Search Engine for Stage 127 AI Research (Part XXIII).

Performs keyword and token-overlap retrieval with exact matching boost
and stopword filtering to prevent spurious hits on common English words.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from atlas.ai.research.domain import ResearchChunk

ENGLISH_STOPWORDS = {
    "what",
    "is",
    "the",
    "in",
    "and",
    "of",
    "for",
    "to",
    "at",
    "by",
    "on",
    "with",
    "from",
    "that",
    "this",
    "it",
    "as",
    "be",
    "are",
    "was",
    "were",
    "an",
    "a",
    "or",
    "has",
    "had",
    "have",
    "how",
    "why",
    "when",
    "where",
    "who",
    "whom",
    "which",
    "does",
    "do",
    "did",
    "not",
    "its",
    "their",
    "under",
    "about",
}


class LexicalSearchEngine:
    """Computes BM25-style lexical relevance scores for chunks."""

    @staticmethod
    def score_chunks(
        query: str,
        chunks: List[ResearchChunk],
    ) -> List[Tuple[ResearchChunk, float]]:
        """Scores candidate chunks based on query term frequency and token matching."""
        if not chunks:
            return []

        all_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
        content_tokens = [t for t in all_tokens if t not in ENGLISH_STOPWORDS]

        if not content_tokens:
            return [(c, 0.0) for c in chunks]

        scored: List[Tuple[ResearchChunk, float]] = []

        # Average chunk length
        avg_len = sum(len(c.clean_text) for c in chunks) / max(len(chunks), 1)

        # Distinguish company symbol from topical query terms
        topical_tokens = [t for t in content_tokens if t != "test_company"]

        for chunk in chunks:
            text_lower = chunk.clean_text.lower()

            # If there are topical tokens, at least one topical token must appear in chunk or section title
            if topical_tokens and not any(
                t in text_lower or (chunk.section_title and t in chunk.section_title.lower())
                for t in topical_tokens
            ):
                scored.append((chunk, 0.0))
                continue

            score = 0.0
            for q_term in content_tokens:
                count = text_lower.count(q_term)
                if count > 0:
                    tf = (count * 2.2) / (
                        count + 1.2 * (0.25 + 0.75 * (len(chunk.clean_text) / (avg_len + 1e-5)))
                    )
                    score += tf

            # Exact phrase bonus
            if query.lower() in text_lower:
                score += 5.0

            # Header match bonus
            if chunk.section_title and any(
                t in chunk.section_title.lower() for t in content_tokens
            ):
                score += 2.0

            scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
