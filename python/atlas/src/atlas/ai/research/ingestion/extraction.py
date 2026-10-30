"""Structural Document Extraction for Stage 127 (Part XII & XIII).

Extracts structural sections, paragraphs, page boundaries, and tabular blocks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ExtractedSection:
    section_title: str
    page_number: int
    content: str
    char_start: int
    char_end: int


def extract_document_sections(text: str) -> List[ExtractedSection]:
    """Splits raw text into logical structural sections based on headers and page breaks."""
    sections: List[ExtractedSection] = []
    lines = text.split("\n")

    current_title = "General"
    current_page = 1
    current_buffer: List[str] = []
    char_offset = 0
    section_start = 0

    header_pattern = re.compile(
        r"^(Section\s+\d+|Item\s+\d+[A-Z]?|Part\s+[I|V|X]+|Consolidated\s+Results|Capital\s+Allocation|Management\s+Discussion|Risk\s+Factors)",
        re.IGNORECASE,
    )
    page_pattern = re.compile(r"^(Page\s+(\d+)|\[Page\s+(\d+)\])", re.IGNORECASE)

    for line in lines:
        page_match = page_pattern.match(line.strip())
        if page_match:
            try:
                current_page = int(page_match.group(2) or page_match.group(3))
            except Exception:
                pass

        header_match = header_pattern.match(line.strip())
        if header_match and current_buffer:
            # Flush current section
            body = "\n".join(current_buffer).strip()
            if body:
                sections.append(
                    ExtractedSection(
                        section_title=current_title,
                        page_number=current_page,
                        content=body,
                        char_start=section_start,
                        char_end=char_offset,
                    )
                )
            current_buffer = []
            current_title = line.strip()
            section_start = char_offset

        current_buffer.append(line)
        char_offset += len(line) + 1

    if current_buffer:
        body = "\n".join(current_buffer).strip()
        if body:
            sections.append(
                ExtractedSection(
                    section_title=current_title,
                    page_number=current_page,
                    content=body,
                    char_start=section_start,
                    char_end=char_offset,
                )
            )

    return sections if sections else [ExtractedSection("General", 1, text, 0, len(text))]
