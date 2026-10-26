import test from "node:test";
import assert from "node:assert/strict";

import {
  formatCitationBadge,
  formatResearchDate,
  getClaimCategoryDisplay,
  getInvestigationStatusDisplay,
  isSafeExternalResearchUrl,
} from "../formatting";

test("Stage 104: isSafeExternalResearchUrl validates authorized URLs and prevents SSRF", () => {
  // Valid external research sources
  assert.equal(isSafeExternalResearchUrl("https://www.sec.gov/edgar"), true);
  assert.equal(isSafeExternalResearchUrl("https://investor.apple.com"), true);
  assert.equal(isSafeExternalResearchUrl("https://www.bloomberg.com/news"), true);
  assert.equal(isSafeExternalResearchUrl("http://www.bls.gov/cpi"), true);

  // Dangerous protocols
  assert.equal(isSafeExternalResearchUrl("javascript:alert(1)"), false);
  assert.equal(isSafeExternalResearchUrl("data:text/html;base64,PHNjcmlwdD4="), false);
  assert.equal(isSafeExternalResearchUrl("ftp://files.sec.gov"), false);
  assert.equal(isSafeExternalResearchUrl("file:///C:/Windows/System32"), false);

  // SSRF Private IP & Metadata endpoints
  assert.equal(isSafeExternalResearchUrl("http://localhost:8000/admin"), false);
  assert.equal(isSafeExternalResearchUrl("http://127.0.0.1:3000"), false);
  assert.equal(isSafeExternalResearchUrl("http://169.254.169.254/latest/meta-data"), false);
  assert.equal(isSafeExternalResearchUrl("http://metadata.google.internal"), false);
  assert.equal(isSafeExternalResearchUrl(""), false);
  assert.equal(isSafeExternalResearchUrl(null), false);
  assert.equal(isSafeExternalResearchUrl(undefined), false);
});

test("Stage 104: formatResearchDate formats valid ISO dates and handles edge cases", () => {
  assert.equal(formatResearchDate("2024-11-01T16:12:00Z"), "2024-11-01");
  assert.equal(formatResearchDate("2024-09-18T18:00:00Z"), "2024-09-18");
  assert.equal(formatResearchDate("invalid-date"), "—");
  assert.equal(formatResearchDate(""), "—");
  assert.equal(formatResearchDate(null), "—");
});

test("Stage 104: getInvestigationStatusDisplay maps lifecycle states to visual badges", () => {
  const active = getInvestigationStatusDisplay("ACTIVE");
  assert.equal(active.label, "Active");
  assert.equal(active.variant, "positive");

  const completed = getInvestigationStatusDisplay("COMPLETED");
  assert.equal(completed.label, "Completed");
  assert.equal(completed.variant, "default");

  const onHold = getInvestigationStatusDisplay("ON_HOLD");
  assert.equal(onHold.label, "On Hold");
  assert.equal(onHold.variant, "warning");

  const archived = getInvestigationStatusDisplay("ARCHIVED");
  assert.equal(archived.label, "Archived");
  assert.equal(archived.variant, "outline");

  const draft = getInvestigationStatusDisplay("DRAFT");
  assert.equal(draft.label, "Draft");
  assert.equal(draft.variant, "outline");
});

test("Stage 104: getClaimCategoryDisplay distinguishes facts from interpretations and estimates", () => {
  // Fact
  const fact = getClaimCategoryDisplay("SOURCE_REPORTED_FACT");
  assert.equal(fact.label, "Source Fact");
  assert.equal(fact.variant, "positive");

  // Analyst Interpretation
  const interp = getClaimCategoryDisplay("ANALYST_INTERPRETATION");
  assert.equal(interp.label, "Analyst Interpretation");
  assert.equal(interp.variant, "primary");

  // Estimate
  const est = getClaimCategoryDisplay("ESTIMATE");
  assert.equal(est.label, "Estimate");
  assert.equal(est.variant, "warning");

  // Assumption
  const assumption = getClaimCategoryDisplay("ASSUMPTION");
  assert.equal(assumption.label, "Assumption");
  assert.equal(assumption.variant, "outline");
});

test("Stage 104: formatCitationBadge decorates valid and broken citations", () => {
  const valid = formatCitationBadge("[SEC Form 10-K FY2024, Item 1A, p. 6]", false);
  assert.equal(valid, "[SEC Form 10-K FY2024, Item 1A, p. 6]");

  const broken = formatCitationBadge("[SEC Form 10-K FY2024, Item 1A, p. 6]", true);
  assert.equal(broken, "[Broken Citation: [SEC Form 10-K FY2024, Item 1A, p. 6]]");
});
