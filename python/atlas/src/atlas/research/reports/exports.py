"""Institutional Research Report PDF and DOCX Rendering Engines (Stage 107).

Provides zero-external-dependency, standard-compliant PDF-1.4 and OpenXML DOCX
generation for professional financial research publication and archiving.
"""

import io
import xml.sax.saxutils as saxutils
import zipfile
from typing import List, Tuple

from atlas.research.domain import ResearchReport, ResearchReportSection


def _sanitize_pdf_text(text: str) -> str:
    """Escape text for PDF literal strings."""
    if not text:
        return ""
    # Replace backslash and parentheses
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    # Strip non-ascii control chars except common whitespace
    return "".join(c if ord(c) < 128 and (ord(c) >= 32 or c in "\t\n\r") else "?" for c in text)


def _wrap_text(text: str, max_chars: int = 80) -> List[str]:
    """Simple greedy word wrapper."""
    if not text:
        return []
    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []
    current_len = 0

    for word in words:
        if current_len + len(word) + (1 if current_line else 0) <= max_chars:
            current_line.append(word)
            current_len += len(word) + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def render_report_pdf(
    report: ResearchReport,
    sections: List[ResearchReportSection],
    author_name: str = "ATLAS Senior Analyst",
) -> Tuple[bytes, int]:
    """Render an institutional research report into standard-compliant binary PDF-1.4."""
    # Build text flow lines across pages (60 lines per page, 10pt/14pt leading)
    pages_content: List[List[str]] = []
    current_page: List[str] = []

    def add_line(line: str, blank_after: bool = False):
        nonlocal current_page
        current_page.append(line)
        if blank_after:
            current_page.append("")
        if len(current_page) >= 48:
            pages_content.append(current_page)
            current_page = []

    # Title Page / Header
    add_line("================================================================================")
    add_line("                           ATLAS INSTITUTIONAL RESEARCH                         ")
    add_line(f"                           {report.report_type.value.replace('_', ' ')}         ")
    add_line("================================================================================", blank_after=True)
    
    add_line(f"TITLE:    {report.title.upper()}")
    if report.subtitle:
        add_line(f"SUBTITLE: {report.subtitle}")
    add_line(f"SUBJECT:  {report.primary_subject_id or 'GENERAL RESEARCH'}")
    add_line(f"AS-OF:    {report.report_as_of.isoformat()}   |   CUTOFF: {report.research_cutoff.date().isoformat()}")
    add_line(f"STATUS:   {report.status.value}   |   REVISION: v{report.current_revision}")
    add_line(f"AUTHOR:   {author_name}   |   REPORT ID: {report.report_id}", blank_after=True)
    add_line("--------------------------------------------------------------------------------", blank_after=True)

    if report.abstract:
        add_line("EXECUTIVE ABSTRACT:")
        for line in _wrap_text(report.abstract, max_chars=76):
            add_line(f"  {line}")
        add_line("", blank_after=True)

    # Sections & Blocks
    for sec in sections:
        add_line("--------------------------------------------------------------------------------")
        add_line(f"SECTION: {sec.heading.upper()}")
        add_line("--------------------------------------------------------------------------------", blank_after=True)

        for block in sec.content_blocks:
            b_type = block.get("block_type", "PARAGRAPH")
            text = block.get("content_text", "")
            caption = block.get("caption")

            if b_type == "HEADING":
                add_line(f"### {text.upper()}", blank_after=True)
            elif b_type in ("PARAGRAPH", "BLOCK_QUOTE"):
                prefix = "> " if b_type == "BLOCK_QUOTE" else ""
                for line in _wrap_text(text, max_chars=74):
                    add_line(f"{prefix}{line}")
                add_line("")
            elif b_type in ("BULLET_LIST", "NUMBERED_LIST"):
                for line in _wrap_text(text, max_chars=72):
                    add_line(f"  * {line}")
                add_line("")
            elif b_type in ("FINANCIAL_TABLE", "ANALYSIS_TABLE"):
                add_line(f"[TABLE] {caption or 'Financial Observation Table'}")
                if text:
                    for line in text.split("\n"):
                        add_line(f"  {line}")
                add_line("")
            elif b_type == "CHART":
                add_line(f"[FIGURE] {caption or 'Financial Research Time-Series Chart'}")
                if text:
                    add_line(f"  Observation Series: {text}")
                add_line("")
            elif b_type == "REFERENCES":
                add_line(f"[REFERENCES] {text}")
                add_line("")

    # Mandatory Institutional Disclaimer
    add_line("================================================================================")
    add_line("DISCLOSURE & LIMITATIONS:")
    for line in _wrap_text(
        "This institutional research document represents qualitative and quantitative analytical synthesis "
        "authored strictly for professional evaluation purposes. It does not constitute an automated investment "
        "recommendation, endorsement, or price target forecast. Empirical figures reflect verified source filings "
        "as of the stated historical research cutoff.", max_chars=76
    ):
        add_line(f"  {line}")
    add_line("================================================================================")

    if current_page:
        pages_content.append(current_page)
    if not pages_content:
        pages_content.append(["[ATLAS Empty Research Report]"])

    # Now assemble standard PDF-1.4 binary document
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")

    offsets: List[int] = []

    # Object 1: Catalog
    offsets.append(out.tell())
    out.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # We will reserve Object 2 for Pages
    # Objects for each Page: Page objects start from 3
    num_pages = len(pages_content)
    page_obj_ids = [3 + i * 2 for i in range(num_pages)]
    content_obj_ids = [4 + i * 2 for i in range(num_pages)]
    font_obj_id = 3 + num_pages * 2

    # Object 2: Pages
    offsets.append(out.tell())
    kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    out.write(f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>\nendobj\n".encode("latin1"))

    # Generate Page and Content Stream objects
    for i in range(num_pages):
        pid = page_obj_ids[i]
        cid = content_obj_ids[i]
        page_lines = pages_content[i]

        # Build stream text
        stream_buf = io.BytesIO()
        stream_buf.write(b"BT\n/F1 9 Tf\n14 TL\n54 738 Td\n")
        
        # Header on each page
        stream_buf.write(f"({_sanitize_pdf_text(f'ATLAS RESEARCH | {report.title[:45]} | Page {i+1} of {num_pages}')}) '\n".encode("latin1"))
        stream_buf.write(b"() '\n")

        for pl in page_lines:
            safe_text = _sanitize_pdf_text(pl)
            stream_buf.write(f"({safe_text}) '\n".encode("latin1"))
        stream_buf.write(b"ET\n")

        stream_bytes = stream_buf.getvalue()

        # Page Object
        offsets.append(out.tell())
        out.write(
            f"{pid} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {cid} 0 R /Resources << /Font << /F1 {font_obj_id} 0 R >> >> >>\nendobj\n".encode("latin1")
        )

        # Content Stream Object
        offsets.append(out.tell())
        out.write(
            f"{cid} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin1")
        )
        out.write(stream_bytes)
        out.write(b"\nendstream\nendobj\n")

    # Font Object (Standard Helvetica)
    offsets.append(out.tell())
    out.write(
        f"{font_obj_id} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n".encode("latin1")
    )

    # Cross-Reference Table
    xref_pos = out.tell()
    total_objects = font_obj_id + 1
    out.write(f"xref\n0 {total_objects}\n".encode("latin1"))
    out.write(b"0000000000 65535 f \n")
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode("latin1"))

    # Trailer
    out.write(
        f"trailer\n<< /Size {total_objects} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin1")
    )

    return out.getvalue(), num_pages


def render_report_docx(
    report: ResearchReport,
    sections: List[ResearchReportSection],
    author_name: str = "ATLAS Senior Analyst",
) -> Tuple[bytes, int]:
    """Render an institutional research report into standard-compliant OpenXML DOCX archive."""
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. [Content_Types].xml
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
            '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
            '  <Default Extension="xml" ContentType="application/xml"/>\n'
            '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
            '  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>\n'
            '</Types>'
        )
        zf.writestr("[Content_Types].xml", content_types)

        # 2. _rels/.rels
        package_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
            '</Relationships>'
        )
        zf.writestr("_rels/.rels", package_rels)

        # 3. word/_rels/document.xml.rels
        doc_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
            '</Relationships>'
        )
        zf.writestr("word/_rels/document.xml.rels", doc_rels)

        # 4. word/styles.xml
        styles_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            '  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">\n'
            '    <w:name w:val="Normal"/>\n'
            '    <w:rPr>\n'
            '      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>\n'
            '      <w:sz w:val="22"/>\n'
            '      <w:color w:val="1E293B"/>\n'
            '    </w:rPr>\n'
            '  </w:style>\n'
            '</w:styles>'
        )
        zf.writestr("word/styles.xml", styles_xml)

        # 5. word/document.xml
        doc_body: List[str] = []

        def p(text: str, bold: bool = False, size: int = 22, color: str = "1E293B", space_after: int = 120):
            escaped = saxutils.escape(text or "")
            b_tag = "<w:b/>" if bold else ""
            doc_body.append(
                f'<w:p><w:pPr><w:spacing w:after="{space_after}"/></w:pPr>'
                f'<w:r><w:rPr>{b_tag}<w:sz w:val="{size}"/><w:color w:val="{color}"/></w:rPr>'
                f'<w:t>{escaped}</w:t></w:r></w:p>'
            )

        # Document Header
        p("ATLAS INSTITUTIONAL RESEARCH", bold=True, size=28, color="0F172A", space_after=80)
        p(report.title, bold=True, size=36, color="0369A1", space_after=60)
        if report.subtitle:
            p(report.subtitle, size=24, color="475569", space_after=120)

        meta_line = (
            f"Subject: {report.primary_subject_id or 'General'}  |  Type: {report.report_type.value}  |  "
            f"As-Of: {report.report_as_of.isoformat()}  |  Cutoff: {report.research_cutoff.date().isoformat()}"
        )
        p(meta_line, size=18, color="64748B", space_after=60)
        p(f"Author: {author_name}  |  Status: {report.status.value}  |  Revision: v{report.current_revision}", size=18, color="64748B", space_after=200)

        if report.abstract:
            p("Executive Abstract", bold=True, size=24, color="0F172A", space_after=80)
            p(report.abstract, space_after=200)

        # Sections
        for sec in sections:
            p(sec.heading, bold=True, size=26, color="0F172A", space_after=120)

            for block in sec.content_blocks:
                b_type = block.get("block_type", "PARAGRAPH")
                text = block.get("content_text", "")
                caption = block.get("caption")

                if b_type == "HEADING":
                    p(text, bold=True, size=22, color="334155", space_after=80)
                elif b_type in ("PARAGRAPH", "BLOCK_QUOTE"):
                    p(text, space_after=120)
                elif b_type in ("BULLET_LIST", "NUMBERED_LIST"):
                    p(f"•  {text}", space_after=80)
                elif b_type in ("FINANCIAL_TABLE", "ANALYSIS_TABLE"):
                    p(f"[Table: {caption or 'Financial Data Table'}]", bold=True, size=20, color="0369A1", space_after=60)
                    if text:
                        p(text, size=18, color="334155", space_after=120)
                elif b_type == "CHART":
                    p(f"[Chart: {caption or 'Financial Research Figure'}]", bold=True, size=20, color="0369A1", space_after=60)
                    if text:
                        p(f"Series Data: {text}", size=18, color="334155", space_after=120)
                elif b_type == "REFERENCES":
                    p(f"[References: {text}]", size=18, color="64748B", space_after=120)

        # Disclaimer
        p("Institutional Disclosure", bold=True, size=22, color="0F172A", space_after=60)
        disclaimer = (
            "This document is an institutional research synthesis for evaluation purposes only. "
            "It does not constitute an investment recommendation, rating, or price target."
        )
        p(disclaimer, size=18, color="64748B", space_after=120)

        body_content = "".join(doc_body)
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            f'  <w:body>{body_content}<w:sectPr/></w:body>\n'
            '</w:document>'
        )
        zf.writestr("word/document.xml", document_xml)

    page_est = max(1, len(sections) // 3 + 1)
    return buf.getvalue(), page_est
