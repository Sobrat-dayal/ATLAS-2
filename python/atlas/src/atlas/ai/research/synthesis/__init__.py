"""Synthesis and Citation package for Stage 127 AI Research."""

from atlas.ai.research.synthesis.answer_generation import ResearchAnswerGenerator
from atlas.ai.research.synthesis.citation_validation import CitationValidator
from atlas.ai.research.synthesis.context_builder import build_research_context_envelope
from atlas.ai.research.synthesis.evidence import build_evidence_unit
from atlas.ai.research.synthesis.planner import ResearchPlanner
from atlas.ai.research.synthesis.source_manifest import build_source_manifest

__all__ = [
    "build_evidence_unit",
    "build_research_context_envelope",
    "CitationValidator",
    "build_source_manifest",
    "ResearchPlanner",
    "ResearchAnswerGenerator",
]
