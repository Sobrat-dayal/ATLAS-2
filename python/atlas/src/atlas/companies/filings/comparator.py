"""Comparison engine for Regulatory Filings & Amendments (Stage 86).

Provides:
- Bounded unified text diffing across comparable filing sections.
- Context-qualified XBRL financial fact variance calculations.
- Restatement and revision detection for amended filings.
"""

import difflib
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Dict, List, Optional

from .models import (
    FilingComparisonResult,
    RegulatoryFiling,
    SectionDiff,
    XBRLFact,
    XBRLFactDiff,
)
from .sanitizer import MAX_DIFF_LINES


def compute_text_section_diff(
    left_title: str,
    left_text: str,
    right_title: str,
    right_text: str,
) -> SectionDiff:
    """Computes line-by-line differences between two sections using unified diff."""
    left_lines = left_text.splitlines(keepends=True)
    right_lines = right_text.splitlines(keepends=True)

    # Bound diff lines to prevent denial of service
    if len(left_lines) > MAX_DIFF_LINES:
        left_lines = left_lines[:MAX_DIFF_LINES]
    if len(right_lines) > MAX_DIFF_LINES:
        right_lines = right_lines[:MAX_DIFF_LINES]

    diff_generator = difflib.unified_diff(
        left_lines,
        right_lines,
        fromfile=left_title,
        tofile=right_title,
        n=2,
    )

    diff_lines = list(diff_generator)
    added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    return SectionDiff(
        section_name=left_title or right_title,
        added_lines_count=added,
        removed_lines_count=removed,
        diff_text="".join(diff_lines),
    )


def compute_xbrl_facts_diff(
    left_facts: List[XBRLFact],
    right_facts: List[XBRLFact],
    is_amendment: bool = False,
) -> List[XBRLFactDiff]:
    """Calculates variance between compatible XBRL concepts across two filings."""
    # Index left facts by concept_name
    left_map: Dict[str, XBRLFact] = {f.concept_name: f for f in left_facts}
    diffs: List[XBRLFactDiff] = []

    for r_fact in right_facts:
        concept = r_fact.concept_name
        if concept not in left_map:
            continue

        l_fact = left_map[concept]

        # Check unit compatibility
        if l_fact.unit != r_fact.unit:
            continue

        val_prior = l_fact.exact_value
        val_current = r_fact.exact_value
        abs_diff = val_current - val_prior

        pct_diff: Optional[Decimal] = None
        if val_prior != Decimal("0"):
            try:
                raw_pct = (abs_diff / abs(val_prior)) * Decimal("100")
                pct_diff = raw_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except (ZeroDivisionError, InvalidOperation):
                pct_diff = None

        # If it's an amendment for the same reporting period and values differ, it's a restatement
        is_restatement = is_amendment and (val_prior != val_current) and (l_fact.period_end == r_fact.period_end)

        diffs.append(
            XBRLFactDiff(
                concept_name=concept,
                label=r_fact.label or l_fact.label or concept,
                period_label=f"{r_fact.period_end}",
                unit=r_fact.unit.value,
                prior_value=val_prior,
                current_value=val_current,
                absolute_difference=abs_diff,
                percentage_difference=pct_diff,
                is_restatement=is_restatement,
            )
        )

    return diffs


def compare_regulatory_filings(
    left_filing: RegulatoryFiling,
    right_filing: RegulatoryFiling,
) -> FilingComparisonResult:
    """Orchestrates comprehensive textual and structured fact comparison between two filings."""
    is_amendment = (
        right_filing.is_amendment
        and (right_filing.amends_accession_number == left_filing.accession_number)
    )
    comparison_type = "AMENDMENT" if is_amendment else "PERIOD_OVER_PERIOD"

    # 1. Section text comparison
    section_diffs: List[SectionDiff] = []
    total_text_changes = 0

    left_sec_map = {s.item_id: s for s in left_filing.sections}
    right_sec_map = {s.item_id: s for s in right_filing.sections}

    all_item_ids = list(dict.fromkeys(list(left_sec_map.keys()) + list(right_sec_map.keys())))

    for item_id in all_item_ids:
        l_sec = left_sec_map.get(item_id)
        r_sec = right_sec_map.get(item_id)

        title = (r_sec.title if r_sec else l_sec.title) if (r_sec or l_sec) else item_id
        l_text = l_sec.summary_excerpt if l_sec and l_sec.summary_excerpt else ""
        r_text = r_sec.summary_excerpt if r_sec and r_sec.summary_excerpt else ""

        if l_text or r_text:
            diff = compute_text_section_diff(
                f"{left_filing.accession_number} [{title}]",
                l_text,
                f"{right_filing.accession_number} [{title}]",
                r_text,
            )
            section_diffs.append(diff)
            total_text_changes += diff.added_lines_count + diff.removed_lines_count

    # If no structured sections, fall back to overall content text
    if not section_diffs and (left_filing.content_text or right_filing.content_text):
        diff = compute_text_section_diff(
            f"{left_filing.accession_number} [Full Document]",
            left_filing.content_text or "",
            f"{right_filing.accession_number} [Full Document]",
            right_filing.content_text or "",
        )
        section_diffs.append(diff)
        total_text_changes += diff.added_lines_count + diff.removed_lines_count

    # 2. Structured XBRL facts comparison
    fact_diffs = compute_xbrl_facts_diff(
        left_filing.xbrl_facts,
        right_filing.xbrl_facts,
        is_amendment=is_amendment,
    )
    total_fact_adjustments = sum(1 for d in fact_diffs if d.absolute_difference != Decimal("0"))

    return FilingComparisonResult(
        left_filing_id=left_filing.filing_id,
        right_filing_id=right_filing.filing_id,
        left_accession=left_filing.accession_number,
        right_accession=right_filing.accession_number,
        comparison_type=comparison_type,
        left_filing_date=left_filing.filing_date,
        right_filing_date=right_filing.filing_date,
        text_diff_sections=section_diffs,
        xbrl_fact_diffs=fact_diffs,
        total_text_changes=total_text_changes,
        total_fact_adjustments=total_fact_adjustments,
    )
