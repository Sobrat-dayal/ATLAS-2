from enum import StrEnum


class ResearchDocumentKind(StrEnum):
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    PREPRINT = "preprint"
    WORKING_PAPER = "working_paper"
    RESEARCH_REPORT = "research_report"
    TECHNICAL_REPORT = "technical_report"
    WHITE_PAPER = "white_paper"
    THESIS = "thesis"
    DISSERTATION = "dissertation"
    BOOK_CHAPTER = "book_chapter"
    DATASET_DOCUMENTATION = "dataset_documentation"
    OTHER = "other"
