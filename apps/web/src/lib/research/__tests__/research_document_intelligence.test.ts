import test from "node:test";
import assert from "node:assert/strict";

import {
  formatFinancialDelta,
  formatPercentageDelta,
  getDocumentProcessingStatusDisplay,
} from "../formatting";

test("Stage 105: formatFinancialDelta correctly formats positive, negative, and currency values", () => {
  // Positive delta USD
  assert.equal(formatFinancialDelta(7870, "USD"), "+$7,870");

  // Negative delta USD
  assert.equal(formatFinancialDelta(-15200, "USD"), "-$15,200");

  // Zero delta USD
  assert.equal(formatFinancialDelta(0, "USD"), "$0");

  // Alternate currencies
  assert.equal(formatFinancialDelta(1250.5, "EUR"), "+EUR 1,250.5");
  assert.equal(formatFinancialDelta(-500, "GBP"), "-GBP 500");
});

test("Stage 105: formatPercentageDelta handles valid deltas and guards against zero-base division", () => {
  // Normal positive percentage
  assert.equal(formatPercentageDelta(2.02), "+2.02%");

  // Normal negative percentage
  assert.equal(formatPercentageDelta(-5.45), "-5.45%");

  // Zero percentage
  assert.equal(formatPercentageDelta(0), "0.00%");

  // Zero-base guards (null, undefined, NaN)
  assert.equal(formatPercentageDelta(null), "N/A (Zero Base)");
  assert.equal(formatPercentageDelta(undefined as any), "N/A (Zero Base)");
  assert.equal(formatPercentageDelta(NaN), "N/A (Zero Base)");
});

test("Stage 105: getDocumentProcessingStatusDisplay maps ingestion and parsing states to UI badges", () => {
  const completed = getDocumentProcessingStatusDisplay("COMPLETED");
  assert.equal(completed.label, "Indexed & Processed");
  assert.equal(completed.variant, "positive");

  const processing = getDocumentProcessingStatusDisplay("PROCESSING");
  assert.equal(processing.label, "Processing...");
  assert.equal(processing.variant, "primary");

  const queued = getDocumentProcessingStatusDisplay("QUEUED");
  assert.equal(queued.label, "Queued");
  assert.equal(queued.variant, "warning");

  const partial = getDocumentProcessingStatusDisplay("PARTIAL");
  assert.equal(partial.label, "Partially Processed");
  assert.equal(partial.variant, "warning");

  const failed = getDocumentProcessingStatusDisplay("FAILED");
  assert.equal(failed.label, "Processing Failed");
  assert.equal(failed.variant, "negative");

  const restricted = getDocumentProcessingStatusDisplay("RESTRICTED");
  assert.equal(restricted.label, "Restricted Rights");
  assert.equal(restricted.variant, "outline");

  const notStarted = getDocumentProcessingStatusDisplay("NOT_STARTED");
  assert.equal(notStarted.label, "Not Started");
  assert.equal(notStarted.variant, "outline");
});
