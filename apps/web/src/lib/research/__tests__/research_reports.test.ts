import test from "node:test";
import assert from "node:assert/strict";

import {
  formatResearchDate,
  getReportStatusDisplay,
  getReportTypeDisplay,
  getThesisStatusDisplay,
  getThesisArgumentTypeDisplay,
  getExportFormatDisplay,
  getVerificationSeverityDisplay,
} from "../formatting";

test("Stage 107: formatResearchDate handles valid dates, nulls, and empty values", () => {
  assert.equal(formatResearchDate("2026-10-27T18:00:00Z"), "2026-10-27");
  assert.equal(formatResearchDate("2025-01-15"), "2025-01-15");
  assert.equal(formatResearchDate(null), "—");
  assert.equal(formatResearchDate(undefined), "—");
  assert.equal(formatResearchDate("invalid-date-string"), "—");
});

test("Stage 107: getReportStatusDisplay maps lifecycle status to badge styles", () => {
  const finalized = getReportStatusDisplay("FINALIZED");
  assert.equal(finalized.label, "Finalized");
  assert.equal(finalized.variant, "positive");

  const published = getReportStatusDisplay("PUBLISHED");
  assert.equal(published.label, "Published");
  assert.equal(published.variant, "positive");

  const underReview = getReportStatusDisplay("UNDER_REVIEW");
  assert.equal(underReview.label, "Under Review");
  assert.equal(underReview.variant, "warning");

  const superseded = getReportStatusDisplay("SUPERSEDED");
  assert.equal(superseded.label, "Superseded");
  assert.equal(superseded.variant, "negative");

  const draft = getReportStatusDisplay("DRAFT");
  assert.equal(draft.label, "Draft");
  assert.equal(draft.variant, "outline");
});

test("Stage 107: getReportTypeDisplay maps report types to human labels", () => {
  assert.equal(getReportTypeDisplay("COMPANY_RESEARCH"), "Company Research Report");
  assert.equal(getReportTypeDisplay("EQUITY_INITIATION"), "Equity Initiation Coverage");
  assert.equal(getReportTypeDisplay("EARNINGS_REVIEW"), "Earnings Review Note");
  assert.equal(getReportTypeDisplay("MACROECONOMIC_REPORT"), "Macroeconomic Outlook");
  assert.equal(getReportTypeDisplay("INDUSTRY_PRIMER"), "Industry Primer");
  assert.equal(getReportTypeDisplay("INVESTMENT_THESIS"), "Investment Thesis Memo");
  assert.equal(getReportTypeDisplay("EVENT_MEMO"), "Event Reaction Memo");
  assert.equal(getReportTypeDisplay("RISK_BRIEF"), "Risk Assessment Brief");
});

test("Stage 107: getThesisStatusDisplay maps investment thesis lifecycle states", () => {
  const active = getThesisStatusDisplay("ACTIVE");
  assert.equal(active.label, "Active Thesis");
  assert.equal(active.variant, "positive");

  const validated = getThesisStatusDisplay("VALIDATED");
  assert.equal(validated.label, "Validated");
  assert.equal(validated.variant, "primary");

  const disproven = getThesisStatusDisplay("DISPROVEN");
  assert.equal(disproven.label, "Disproven");
  assert.equal(disproven.variant, "negative");

  const underReview = getThesisStatusDisplay("UNDER_REVIEW");
  assert.equal(underReview.label, "Under Review");
  assert.equal(underReview.variant, "warning");
});

test("Stage 107: getThesisArgumentTypeDisplay maps thesis argument roles", () => {
  const bull = getThesisArgumentTypeDisplay("BULL_CASE");
  assert.equal(bull.label, "Bull Case");
  assert.equal(bull.variant, "positive");

  const bear = getThesisArgumentTypeDisplay("BEAR_CASE");
  assert.equal(bear.label, "Bear Case");
  assert.equal(bear.variant, "negative");

  const catalyst = getThesisArgumentTypeDisplay("CATALYST");
  assert.equal(catalyst.label, "Catalyst");
  assert.equal(catalyst.variant, "warning");

  const risk = getThesisArgumentTypeDisplay("KEY_RISK");
  assert.equal(risk.label, "Key Risk");
  assert.equal(risk.variant, "negative");

  const assumption = getThesisArgumentTypeDisplay("CORE_ASSUMPTION");
  assert.equal(assumption.label, "Core Assumption");
  assert.equal(assumption.variant, "default");
});

test("Stage 107: getExportFormatDisplay maps export formats", () => {
  assert.equal(getExportFormatDisplay("PDF"), "Institutional PDF");
  assert.equal(getExportFormatDisplay("DOCX"), "Office Word (DOCX)");
  assert.equal(getExportFormatDisplay("HTML"), "Self-Contained HTML");
  assert.equal(getExportFormatDisplay("MARKDOWN"), "Research Markdown");
  assert.equal(getExportFormatDisplay("JSON_ARCHIVE"), "Point-in-Time JSON Archive");
});

test("Stage 107: getVerificationSeverityDisplay maps issue severity", () => {
  const blocking = getVerificationSeverityDisplay("BLOCKING");
  assert.equal(blocking.label, "Blocking Violation");
  assert.equal(blocking.variant, "negative");

  const warning = getVerificationSeverityDisplay("WARNING");
  assert.equal(warning.label, "Warning");
  assert.equal(warning.variant, "warning");

  const info = getVerificationSeverityDisplay("INFORMATIONAL");
  assert.equal(info.label, "Info");
  assert.equal(info.variant, "outline");
});
