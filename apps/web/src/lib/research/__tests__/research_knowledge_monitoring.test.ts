import test from "node:test";
import assert from "node:assert/strict";

import {
  getKnowledgeEntryTypeDisplay,
  getKnowledgeStatusDisplay,
  getKnowledgeSourceAvailabilityDisplay,
  getSourceChangeTypeDisplay,
  getImpactCategoryDisplay,
  getRevalidationOutcomeDisplay,
  getUpdateItemStatusDisplay,
  getUpdateItemPriorityDisplay,
  formatResearchDate,
} from "../formatting";

test("Stage 109: getKnowledgeEntryTypeDisplay maps canonical knowledge types accurately", () => {
  const inv = getKnowledgeEntryTypeDisplay("RESEARCH_INVESTIGATION");
  assert.equal(inv.label, "Investigation");
  assert.equal(inv.variant, "primary");

  const rep = getKnowledgeEntryTypeDisplay("RESEARCH_REPORT");
  assert.equal(rep.label, "Report");
  assert.equal(rep.variant, "positive");

  const th = getKnowledgeEntryTypeDisplay("RESEARCH_THESIS");
  assert.equal(th.label, "Thesis");
  assert.equal(th.variant, "warning");

  const an = getKnowledgeEntryTypeDisplay("RESEARCH_ANALYSIS");
  assert.equal(an.label, "Analysis");
  assert.equal(an.variant, "default");

  const fn = getKnowledgeEntryTypeDisplay("RESEARCH_FINDING");
  assert.equal(fn.label, "Finding");
  assert.equal(fn.variant, "outline");

  const ev = getKnowledgeEntryTypeDisplay("RESEARCH_EVIDENCE");
  assert.equal(ev.label, "Evidence");
  assert.equal(ev.variant, "positive");

  const cl = getKnowledgeEntryTypeDisplay("RESEARCH_CLAIM");
  assert.equal(cl.label, "Claim");
  assert.equal(cl.variant, "outline");
});

test("Stage 109: getKnowledgeStatusDisplay maps knowledge lifecycle statuses", () => {
  const act = getKnowledgeStatusDisplay("ACTIVE");
  assert.equal(act.label, "Active");
  assert.equal(act.variant, "positive");

  const arch = getKnowledgeStatusDisplay("ARCHIVED");
  assert.equal(arch.label, "Archived");
  assert.equal(arch.variant, "outline");

  const dep = getKnowledgeStatusDisplay("DEPRECATED");
  assert.equal(dep.label, "Deprecated");
  assert.equal(dep.variant, "negative");

  const dft = getKnowledgeStatusDisplay("DRAFT");
  assert.equal(dft.label, "Draft");
  assert.equal(dft.variant, "warning");
});

test("Stage 109: getKnowledgeSourceAvailabilityDisplay maps data rights & presence", () => {
  const avail = getKnowledgeSourceAvailabilityDisplay("AVAILABLE");
  assert.equal(avail.label, "Available");
  assert.equal(avail.variant, "positive");

  const pending = getKnowledgeSourceAvailabilityDisplay("PENDING_VERIFICATION");
  assert.equal(pending.label, "Pending Verification");
  assert.equal(pending.variant, "warning");

  const restr = getKnowledgeSourceAvailabilityDisplay("RESTRICTED");
  assert.equal(restr.label, "Restricted");
  assert.equal(restr.variant, "negative");

  const unavail = getKnowledgeSourceAvailabilityDisplay("UNAVAILABLE");
  assert.equal(unavail.label, "Unavailable");
  assert.equal(unavail.variant, "outline");
});

test("Stage 109: getSourceChangeTypeDisplay identifies canonical change categories", () => {
  const docAmend = getSourceChangeTypeDisplay("DOCUMENT_AMENDED");
  assert.equal(docAmend.label, "Filing Amended");
  assert.equal(docAmend.variant, "warning");

  const factRest = getSourceChangeTypeDisplay("FACT_RESTATED");
  assert.equal(factRest.label, "Fact Restated");
  assert.equal(factRest.variant, "negative");

  const vintage = getSourceChangeTypeDisplay("VINTAGE_UPDATED");
  assert.equal(vintage.label, "Vintage Updated");
  assert.equal(vintage.variant, "primary");

  const news = getSourceChangeTypeDisplay("NEWS_CORRECTED");
  assert.equal(news.label, "News Corrected");
  assert.equal(news.variant, "warning");

  const entRevoked = getSourceChangeTypeDisplay("ENTITLEMENT_REVOKED");
  assert.equal(entRevoked.label, "Entitlement Revoked");
  assert.equal(entRevoked.variant, "negative");
});

test("Stage 109: getImpactCategoryDisplay maps mechanical and downstream impact tiers", () => {
  const direct = getImpactCategoryDisplay("DIRECT_SOURCE_REFERENCE_CHANGED");
  assert.equal(direct.label, "Direct Source Reference Changed");
  assert.equal(direct.variant, "negative");

  const calc = getImpactCategoryDisplay("INTERMEDIATE_CALCULATION_IMPACTED");
  assert.equal(calc.label, "Calculation Impacted");
  assert.equal(calc.variant, "warning");

  const finding = getImpactCategoryDisplay("DOWNSTREAM_FINDING_REQUIRING_REVALIDATION");
  assert.equal(finding.label, "Finding Needs Revalidation");
  assert.equal(finding.variant, "warning");

  const report = getImpactCategoryDisplay("REPORT_ASSERTION_AFFECTED");
  assert.equal(report.label, "Report Assertion Affected");
  assert.equal(report.variant, "negative");
});

test("Stage 109: getRevalidationOutcomeDisplay classifies citation and approval checks", () => {
  const valid = getRevalidationOutcomeDisplay("VALID_REFERENCES");
  assert.equal(valid.label, "Valid References");
  assert.equal(valid.variant, "positive");

  const warn = getRevalidationOutcomeDisplay("VALID_WITH_WARNINGS");
  assert.equal(warn.label, "Valid with Warnings");
  assert.equal(warn.variant, "warning");

  const review = getRevalidationOutcomeDisplay("REQUIRES_HUMAN_REVIEW");
  assert.equal(review.label, "Requires Review");
  assert.equal(review.variant, "warning");

  const invalid = getRevalidationOutcomeDisplay("INVALID_CITATIONS");
  assert.equal(invalid.label, "Invalid Citations");
  assert.equal(invalid.variant, "negative");

  const revAdvised = getRevalidationOutcomeDisplay("APPROVAL_REVOCATION_RECOMMENDED");
  assert.equal(revAdvised.label, "Approval Revocation Advised");
  assert.equal(revAdvised.variant, "negative");
});

test("Stage 109: getUpdateItemStatusDisplay and PriorityDisplay format lifecycle state machine", () => {
  assert.equal(getUpdateItemStatusDisplay("OPEN").label, "Open");
  assert.equal(getUpdateItemStatusDisplay("ACKNOWLEDGED").label, "Acknowledged");
  assert.equal(getUpdateItemStatusDisplay("IN_PROGRESS").label, "In Progress");
  assert.equal(getUpdateItemStatusDisplay("RESOLVED").label, "Resolved");
  assert.equal(getUpdateItemStatusDisplay("DISMISSED").label, "Dismissed");
  assert.equal(getUpdateItemStatusDisplay("REOPENED").label, "Reopened");

  assert.equal(getUpdateItemPriorityDisplay("CRITICAL").variant, "negative");
  assert.equal(getUpdateItemPriorityDisplay("HIGH").variant, "warning");
  assert.equal(getUpdateItemPriorityDisplay("MEDIUM").variant, "primary");
  assert.equal(getUpdateItemPriorityDisplay("LOW").variant, "outline");
});

test("Stage 109: formatResearchDate formats valid ISO dates and handles nil values safely", () => {
  assert.equal(formatResearchDate("2024-10-31T14:30:00Z"), "2024-10-31");
  assert.equal(formatResearchDate(null), "—");
  assert.equal(formatResearchDate(undefined), "—");
  assert.equal(formatResearchDate("invalid-date-string"), "—");
});

