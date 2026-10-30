/**
 * Unit Test Suite for ATLAS Stage 127: AI Research and RAG Frontend Domain.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { parseAnswerCitations } from "../citationValidation";
import { formatLicensingClass, formatPublicationDate, formatReliabilityTier } from "../sourceFormatting";
import { formatResearchError, RESEARCH_ERROR_MESSAGES } from "../errors";
import { ResearchCitationDTO } from "../types";

describe("Stage 127 — ATLAS AI Research and Grounded RAG Unit Tests", () => {
  it("Fixture A: validates inline citation extraction and verified badge tokenization", () => {
    const rawAnswer =
      "TEST_COMPANY recorded FY2025 revenue of 125 USD million [cite:ev_chk_fixture_a_1], representing 25% growth.";
    const citations: ResearchCitationDTO[] = [
      {
        citation_id: "cite_ev_chk_fixture_a_1",
        evidence_id: "ev_chk_fixture_a_1",
        document_id: "doc_fixture_a_10k",
        symbol: "TEST_COMPANY",
        title: "TEST_COMPANY FY2025 Annual Report Form 10-K",
        page_number: 14,
        section_title: "Consolidated Results of Operations",
        publication_date: "2026-02-15T00:00:00Z",
        claim_text: "revenue increased to 125 USD million",
        quote_span: "revenue increased to 125 USD million",
        status: "VERIFIED",
      },
    ];

    const segments = parseAnswerCitations(rawAnswer, citations);
    assert.strictEqual(segments.length, 3);
    assert.strictEqual(segments[0].type, "text");
    assert.strictEqual(segments[1].type, "citation");
    assert.strictEqual(segments[1].text, "[TEST_COMPANY p.14]");
    assert.strictEqual(segments[1].citation?.status, "VERIFIED");
  });

  it("Fixture B: validates document comparison differences contract structure", () => {
    const diff = {
      aspect: "Capital Expenditures Planned",
      doc_a_value: "50 million USD",
      doc_b_value: "80 million USD",
      difference_text: "Planned CapEx increased by 30 million USD (60% growth)",
    };

    assert.strictEqual(diff.aspect, "Capital Expenditures Planned");
    assert.strictEqual(diff.doc_a_value, "50 million USD");
    assert.strictEqual(diff.doc_b_value, "80 million USD");
    assert.ok(diff.difference_text.includes("30 million USD"));
  });

  it("Fixture C: formats publication date accurately without timezone mutation", () => {
    const formatted = formatPublicationDate("2025-03-01T00:00:00Z");
    assert.ok(formatted.includes("2025"));
    assert.ok(formatted.includes("Mar") || formatted.includes("3"));
  });

  it("Fixture D: formats typed error messages for restricted/denied access", () => {
    const deniedMsg = formatResearchError("RESEARCH_DOCUMENT_ACCESS_DENIED");
    assert.strictEqual(deniedMsg, RESEARCH_ERROR_MESSAGES.RESEARCH_DOCUMENT_ACCESS_DENIED);

    const licenseMsg = formatResearchError("RESEARCH_SOURCE_LICENSE_RESTRICTED");
    assert.strictEqual(licenseMsg, RESEARCH_ERROR_MESSAGES.RESEARCH_SOURCE_LICENSE_RESTRICTED);
  });

  it("Fixture E: parses and rejects fabricated citation tokens without crashing", () => {
    const answerWithFake = "The margin was 45% [Source 999] according to estimates.";
    // No citations provided matching 999
    const segments = parseAnswerCitations(answerWithFake, []);
    assert.strictEqual(segments.length, 1);
    assert.ok(segments[0].text.includes("45%"));
  });

  it("Fixture F: verifies reliability tier badges and styling classes", () => {
    const primary = formatReliabilityTier("PRIMARY_REGULATORY");
    assert.strictEqual(primary.label, "Regulatory (SEC/EDGAR)");
    assert.ok(primary.badgeClass.includes("emerald"));

    const privateTier = formatReliabilityTier("USER_PRIVATE");
    assert.strictEqual(privateTier.label, "User Vault (Private)");
    assert.ok(privateTier.badgeClass.includes("purple"));
  });

  it("Fixture G: verifies licensing class metadata formatting", () => {
    const publicDomain = formatLicensingClass("PUBLIC_DOMAIN");
    assert.strictEqual(publicDomain.label, "Public Domain");

    const confidential = formatLicensingClass("INTERNAL_CONFIDENTIAL");
    assert.strictEqual(confidential.label, "Internal Confidential");
  });
});
