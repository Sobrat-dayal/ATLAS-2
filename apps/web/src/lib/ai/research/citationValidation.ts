/**
 * Client-Side Citation Parsing and Validation for Stage 127 AI Research.
 */

import { ResearchCitationDTO } from "./types";

export interface ParsedAnswerSegment {
  type: "text" | "citation";
  text: string;
  citation?: ResearchCitationDTO;
}

export function parseAnswerCitations(
  answerText: string,
  citations: ResearchCitationDTO[],
): ParsedAnswerSegment[] {
  if (!answerText) return [];

  const citationMap = new Map<string, ResearchCitationDTO>();
  for (const c of citations) {
    citationMap.set(c.citation_id, c);
    citationMap.set(c.evidence_id, c);
  }

  // Matches [cite:...] or [cite_...]
  const regex = /\[(?:cite:)?(cite_[a-zA-Z0-9_\-]+|ev_[a-zA-Z0-9_\-]+|chk_[a-zA-Z0-9_\-]+)\]/g;
  const segments: ParsedAnswerSegment[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(answerText)) !== null) {
    const preText = answerText.slice(lastIndex, match.index);
    if (preText) {
      segments.push({ type: "text", text: preText });
    }

    const token = match[1];
    const matchedCite = citationMap.get(token) || citationMap.get(`cite_${token}`);

    if (matchedCite) {
      segments.push({
        type: "citation",
        text: `[${matchedCite.symbol || "Source"} p.${matchedCite.page_number}]`,
        citation: matchedCite,
      });
    } else {
      // Unresolved or stripped token
      segments.push({
        type: "text",
        text: match[0],
      });
    }

    lastIndex = regex.lastIndex;
  }

  const remaining = answerText.slice(lastIndex);
  if (remaining) {
    segments.push({ type: "text", text: remaining });
  }

  return segments;
}
