import test from "node:test";
import assert from "node:assert/strict";

import {
  getReviewStatusDisplay,
  getReviewDecisionDisplay,
  getResearchRoleDisplay,
  getCommentThreadStatusDisplay,
  getCirculationStatusDisplay,
} from "../formatting";

test("Stage 108: getReviewStatusDisplay maps formal review states to badge variants", () => {
  const submitted = getReviewStatusDisplay("SUBMITTED");
  assert.equal(submitted.label, "Submitted");
  assert.equal(submitted.variant, "primary");

  const inReview = getReviewStatusDisplay("IN_REVIEW");
  assert.equal(inReview.label, "In Review");
  assert.equal(inReview.variant, "warning");

  const changes = getReviewStatusDisplay("CHANGES_REQUESTED");
  assert.equal(changes.label, "Changes Requested");
  assert.equal(changes.variant, "warning");

  const approved = getReviewStatusDisplay("APPROVED");
  assert.equal(approved.label, "Approved");
  assert.equal(approved.variant, "positive");

  const rejected = getReviewStatusDisplay("REJECTED");
  assert.equal(rejected.label, "Rejected");
  assert.equal(rejected.variant, "negative");

  const canceled = getReviewStatusDisplay("CANCELED");
  assert.equal(canceled.label, "Canceled");
  assert.equal(canceled.variant, "default");

  const draft = getReviewStatusDisplay("DRAFT");
  assert.equal(draft.label, "Draft");
  assert.equal(draft.variant, "outline");
});

test("Stage 108: getReviewDecisionDisplay maps review actions accurately", () => {
  const approve = getReviewDecisionDisplay("APPROVE");
  assert.equal(approve.label, "Approve Revision");
  assert.equal(approve.variant, "positive");

  const reqChanges = getReviewDecisionDisplay("REQUEST_CHANGES");
  assert.equal(reqChanges.label, "Request Changes");
  assert.equal(reqChanges.variant, "warning");

  const reject = getReviewDecisionDisplay("REJECT");
  assert.equal(reject.label, "Reject Revision");
  assert.equal(reject.variant, "negative");
});

test("Stage 108: getResearchRoleDisplay provides role labels and descriptions", () => {
  const owner = getResearchRoleDisplay("OWNER");
  assert.equal(owner.label, "Owner");
  assert.equal(owner.variant, "primary");
  assert.match(owner.description, /Full administrative ownership/);

  const editor = getResearchRoleDisplay("EDITOR");
  assert.equal(editor.label, "Editor");
  assert.equal(editor.variant, "positive");

  const reviewer = getResearchRoleDisplay("REVIEWER");
  assert.equal(reviewer.label, "Reviewer");
  assert.equal(reviewer.variant, "warning");

  const commenter = getResearchRoleDisplay("COMMENTER");
  assert.equal(commenter.label, "Commenter");
  assert.equal(commenter.variant, "outline");

  const viewer = getResearchRoleDisplay("VIEWER");
  assert.equal(viewer.label, "Viewer");
  assert.equal(viewer.variant, "default");
});

test("Stage 108: getCommentThreadStatusDisplay maps resolution statuses", () => {
  const open = getCommentThreadStatusDisplay("OPEN");
  assert.equal(open.label, "Open");
  assert.equal(open.variant, "warning");

  const resolved = getCommentThreadStatusDisplay("RESOLVED");
  assert.equal(resolved.label, "Resolved");
  assert.equal(resolved.variant, "positive");

  const reopened = getCommentThreadStatusDisplay("REOPENED");
  assert.equal(reopened.label, "Reopened");
  assert.equal(reopened.variant, "negative");
});

test("Stage 108: getCirculationStatusDisplay maps internal circulation states", () => {
  const active = getCirculationStatusDisplay("ACTIVE");
  assert.equal(active.label, "Active Circulation");
  assert.equal(active.variant, "positive");

  const revoked = getCirculationStatusDisplay("REVOKED");
  assert.equal(revoked.label, "Revoked");
  assert.equal(revoked.variant, "negative");

  const expired = getCirculationStatusDisplay("EXPIRED");
  assert.equal(expired.label, "Expired");
  assert.equal(expired.variant, "default");
});

