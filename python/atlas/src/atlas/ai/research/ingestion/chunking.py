"""Document Chunking for Stage 127 AI Research (Part XV & XVI).

Generates structurally bounded chunks with stable IDs, character spans,
page numbers, and token estimates.
"""

from __future__ import annotations

import hashlib
from typing import List

from atlas.ai.research.domain import ResearchChunk
from atlas.ai.research.ingestion.extraction import extract_document_sections
from atlas.ai.research.ingestion.normalization import normalize_financial_text

MAX_CHUNK_TOKENS = 512
OVERLAP_TOKENS = 50


def chunk_document_text(
    document_id: str,
    revision_id: str,
    raw_text: str,
) -> List[ResearchChunk]:
    """Transforms raw document text into structural ResearchChunks."""
    clean_full_text = normalize_financial_text(raw_text)
    sections = extract_document_sections(clean_full_text)
    chunks: List[ResearchChunk] = []

    chunk_idx = 0
    for sec in sections:
        sec_text = sec.content
        # If section is small, treat as single chunk
        if len(sec_text) < 1800:
            token_est = max(1, len(sec_text) // 4)
            chk_id = f"chk_{document_id}_{chunk_idx}"
            chk_hash = hashlib.sha256(sec_text.encode()).hexdigest()
            chunks.append(
                ResearchChunk(
                    chunk_id=chk_id,
                    document_id=document_id,
                    revision_id=revision_id,
                    chunk_index=chunk_idx,
                    section_title=sec.section_title,
                    page_number=sec.page_number,
                    raw_text=sec_text,
                    clean_text=sec_text,
                    char_start=sec.char_start,
                    char_end=sec.char_end,
                    token_estimate=token_est,
                    content_hash=chk_hash,
                )
            )
            chunk_idx += 1
        else:
            # Paragraph-bounded chunking
            paragraphs = sec_text.split("\n\n")
            curr_para_buf: List[str] = []
            curr_len = 0
            p_start = sec.char_start

            for p in paragraphs:
                p_len = len(p)
                if curr_len + p_len > 1600 and curr_para_buf:
                    joined = "\n\n".join(curr_para_buf)
                    chk_id = f"chk_{document_id}_{chunk_idx}"
                    chk_hash = hashlib.sha256(joined.encode()).hexdigest()
                    chunks.append(
                        ResearchChunk(
                            chunk_id=chk_id,
                            document_id=document_id,
                            revision_id=revision_id,
                            chunk_index=chunk_idx,
                            section_title=sec.section_title,
                            page_number=sec.page_number,
                            raw_text=joined,
                            clean_text=joined,
                            char_start=p_start,
                            char_end=p_start + len(joined),
                            token_estimate=max(1, len(joined) // 4),
                            content_hash=chk_hash,
                        )
                    )
                    chunk_idx += 1
                    curr_para_buf = [p]
                    curr_len = p_len
                    p_start += len(joined) + 2
                else:
                    curr_para_buf.append(p)
                    curr_len += p_len + 2

            if curr_para_buf:
                joined = "\n\n".join(curr_para_buf)
                chk_id = f"chk_{document_id}_{chunk_idx}"
                chk_hash = hashlib.sha256(joined.encode()).hexdigest()
                chunks.append(
                    ResearchChunk(
                        chunk_id=chk_id,
                        document_id=document_id,
                        revision_id=revision_id,
                        chunk_index=chunk_idx,
                        section_title=sec.section_title,
                        page_number=sec.page_number,
                        raw_text=joined,
                        clean_text=joined,
                        char_start=p_start,
                        char_end=p_start + len(joined),
                        token_estimate=max(1, len(joined) // 4),
                        content_hash=chk_hash,
                    )
                )
                chunk_idx += 1

    return chunks

