"""Ingestion package for Stage 127 AI Research."""

from atlas.ai.research.ingestion.chunking import chunk_document_text
from atlas.ai.research.ingestion.extraction import extract_document_sections
from atlas.ai.research.ingestion.file_validation import validate_document_file
from atlas.ai.research.ingestion.indexing_jobs import IngestionJobManager, ResearchIngestionJob
from atlas.ai.research.ingestion.normalization import normalize_financial_text
from atlas.ai.research.ingestion.service import DocumentIngestionService

__all__ = [
    "validate_document_file",
    "normalize_financial_text",
    "extract_document_sections",
    "chunk_document_text",
    "IngestionJobManager",
    "ResearchIngestionJob",
    "DocumentIngestionService",
]
