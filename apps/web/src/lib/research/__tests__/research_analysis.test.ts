import test from "node:test";
import assert from "node:assert/strict";

import {
  formatCAGR,
  formatPercentageDelta,
  formatStatisticsValue,
  getAnalysisStatusDisplay,
  getAnalysisTypeLabel,
  getFindingReviewStatusDisplay,
  getFindingTypeDisplay,
  getHypothesisOutcomeDisplay,
} from "../formatting";

test("Stage 106: formatCAGR handles valid and invalid endpoint bounds", () => {
  assert.equal(formatCAGR(16.75), "+16.75% CAGR");
  assert.equal(formatCAGR(0.0), "0.00% CAGR");
  assert.equal(formatCAGR(-5.25), "-5.25% CAGR");
  assert.equal(formatCAGR(null), "N/A (Invalid Endpoints)");
  assert.equal(formatCAGR(undefined), "N/A (Invalid Endpoints)");
  assert.equal(formatCAGR(NaN), "N/A (Invalid Endpoints)");
});

test("Stage 106: formatPercentageDelta handles valid deltas and zero baseline guards", () => {
  assert.equal(formatPercentageDelta(12.5), "+12.50%");
  assert.equal(formatPercentageDelta(-4.12), "-4.12%");
  assert.equal(formatPercentageDelta(0.0), "0.00%");
  assert.equal(formatPercentageDelta(null), "N/A (Zero Base)");
  assert.equal(formatPercentageDelta(undefined), "N/A (Zero Base)");
  assert.equal(formatPercentageDelta(NaN), "N/A (Zero Base)");
});

test("Stage 106: formatStatisticsValue handles numbers and units", () => {
  assert.equal(formatStatisticsValue(123456.78, "$M"), "123,456.78 $M");
  assert.equal(formatStatisticsValue(35.5, "%"), "35.5 %");
  assert.equal(formatStatisticsValue(null), "—");
  assert.equal(formatStatisticsValue(undefined), "—");
});

test("Stage 106: getHypothesisOutcomeDisplay maps evaluation states to visual badges", () => {
  const met = getHypothesisOutcomeDisplay("CRITERIA_MET");
  assert.equal(met.label, "Criteria Met (Consistent)");
  assert.equal(met.variant, "positive");

  const notMet = getHypothesisOutcomeDisplay("CRITERIA_NOT_MET");
  assert.equal(notMet.label, "Criteria Not Met");
  assert.equal(notMet.variant, "negative");

  const mixed = getHypothesisOutcomeDisplay("MIXED_RESULTS");
  assert.equal(mixed.label, "Mixed Results");
  assert.equal(mixed.variant, "warning");

  const inconclusive = getHypothesisOutcomeDisplay("INCONCLUSIVE");
  assert.equal(inconclusive.label, "Inconclusive");
  assert.equal(inconclusive.variant, "outline");

  const insufficient = getHypothesisOutcomeDisplay("INSUFFICIENT_DATA");
  assert.equal(insufficient.label, "Insufficient Observations");
  assert.equal(insufficient.variant, "outline");
});

test("Stage 106: getAnalysisStatusDisplay maps analysis execution lifecycle", () => {
  const completed = getAnalysisStatusDisplay("COMPLETED");
  assert.equal(completed.label, "Completed");
  assert.equal(completed.variant, "positive");

  const running = getAnalysisStatusDisplay("RUNNING");
  assert.equal(running.label, "Computing...");
  assert.equal(running.variant, "primary");

  const configured = getAnalysisStatusDisplay("CONFIGURED");
  assert.equal(configured.label, "Ready to Run");
  assert.equal(configured.variant, "default");

  const failed = getAnalysisStatusDisplay("FAILED");
  assert.equal(failed.label, "Execution Failed");
  assert.equal(failed.variant, "negative");
});

test("Stage 106: getFindingTypeDisplay and getFindingReviewStatusDisplay classify epistemic categories", () => {
  const calc = getFindingTypeDisplay("CALCULATED_RESULT");
  assert.equal(calc.label, "Calculated Derivation");
  assert.equal(calc.variant, "primary");

  const fact = getFindingTypeDisplay("OBSERVED_FACT");
  assert.equal(fact.label, "Reported Fact");
  assert.equal(fact.variant, "positive");

  const interp = getFindingTypeDisplay("ANALYST_INTERPRETATION");
  assert.equal(interp.label, "Analyst Interpretation");
  assert.equal(interp.variant, "warning");

  const reviewed = getFindingReviewStatusDisplay("REVIEWED");
  assert.equal(reviewed.label, "Reviewed & Verified");
  assert.equal(reviewed.variant, "positive");

  const needsEv = getFindingReviewStatusDisplay("NEEDS_EVIDENCE");
  assert.equal(needsEv.label, "Needs Citations");
  assert.equal(needsEv.variant, "warning");
});

test("Stage 106: getAnalysisTypeLabel resolves human-readable names for all institutional types", () => {
  assert.equal(getAnalysisTypeLabel("COMPANY_FINANCIAL_TREND"), "Company Financial Trend");
  assert.equal(getAnalysisTypeLabel("COMPANY_RATIO_ANALYSIS"), "Company Financial Ratios");
  assert.equal(getAnalysisTypeLabel("PEER_BENCHMARKING"), "Cross-Sectional Peer Benchmarking");
  assert.equal(getAnalysisTypeLabel("MACROECONOMIC_TIME_SERIES"), "Macroeconomic Time Series");
  assert.equal(getAnalysisTypeLabel("HYPOTHESIS_EVALUATION"), "Deterministic Hypothesis Test");
  assert.equal(getAnalysisTypeLabel("ASSUMPTION_SENSITIVITY_ANALYSIS"), "Scenario Sensitivity Matrix");
});
