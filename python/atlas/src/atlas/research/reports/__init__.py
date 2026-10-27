"""Institutional Financial Research Reports, Theses, Verification, and Export Engine (Stage 107)."""

from atlas.research.reports.exports import render_report_docx, render_report_pdf
from atlas.research.reports.templates import (
    BUILTIN_TEMPLATES,
    get_report_template,
    list_report_templates,
)
from atlas.research.reports.verification import verify_research_report

__all__ = [
    "BUILTIN_TEMPLATES",
    "get_report_template",
    "list_report_templates",
    "verify_research_report",
    "render_report_pdf",
    "render_report_docx",
]
