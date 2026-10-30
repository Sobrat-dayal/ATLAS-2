"""Retrieval package for Stage 127 AI Research."""

from atlas.ai.research.retrieval.deduplication import deduplicate_chunks, rerank_evidence
from atlas.ai.research.retrieval.filters import ResearchRetrievalFilter
from atlas.ai.research.retrieval.hybrid import HybridRetrievalEngine
from atlas.ai.research.retrieval.lexical import LexicalSearchEngine
from atlas.ai.research.retrieval.query_parser import parse_research_query
from atlas.ai.research.retrieval.semantic import SemanticSearchEngine

__all__ = [
    "parse_research_query",
    "ResearchRetrievalFilter",
    "LexicalSearchEngine",
    "SemanticSearchEngine",
    "HybridRetrievalEngine",
    "deduplicate_chunks",
    "rerank_evidence",
]
