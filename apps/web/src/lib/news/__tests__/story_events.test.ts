import test from "node:test";
import assert from "node:assert/strict";

import {
  NewsStoryStatus,
  NewsStoryMembershipReason,
  NewsStoryMembershipStatus,
  FinancialEventType,
  NewsEventLifecycleStatus,
  NewsEventAssertionStatus,
  EventParticipantRole,
  EventAmountType,
  EventAmountApproximation,
  EventTimePrecision,
  NewsEvidenceType,
  NewsStoryThreadDTO,
  NewsFinancialEventDTO,
  NewsEventEvidenceDTO,
} from "../types";

test("Stage 101: NewsStoryStatus supports canonical operational states", () => {
  const statuses: NewsStoryStatus[] = [
    "ACTIVE",
    "DEVELOPING",
    "QUIET",
    "ARCHIVED",
    "MERGED",
    "WITHDRAWN_FROM_DISPLAY",
  ];
  assert.equal(statuses.length, 6);
  assert.ok(statuses.includes("ACTIVE"));
  assert.ok(statuses.includes("MERGED"));
  assert.ok(statuses.includes("ARCHIVED"));
});

test("Stage 101: FinancialEventType supports corporate announcements and macro policy", () => {
  const eventTypes: FinancialEventType[] = [
    "EARNINGS_RELEASE",
    "EARNINGS_GUIDANCE",
    "DIVIDEND_DECLARATION",
    "SHARE_REPURCHASE",
    "MERGER_ACQUISITION_AGREEMENT",
    "MERGER_ACQUISITION_PROPOSAL",
    "MERGER_ACQUISITION_COMPLETION",
    "MERGER_ACQUISITION_CANCELLATION",
    "EQUITY_FINANCING",
    "DEBT_FINANCING",
    "EXECUTIVE_APPOINTMENT",
    "EXECUTIVE_RESIGNATION",
    "REGULATORY_ACTION",
    "LITIGATION_FILING",
    "BANKRUPTCY_RESTRUCTURING",
    "PRODUCT_LAUNCH",
    "FACILITY_EXPANSION",
    "CENTRAL_BANK_POLICY_DECISION",
    "ECONOMIC_RELEASE",
    "GOVERNMENT_POLICY",
  ];
  assert.equal(eventTypes.length, 20);
  assert.ok(eventTypes.includes("MERGER_ACQUISITION_AGREEMENT"));
  assert.ok(eventTypes.includes("CENTRAL_BANK_POLICY_DECISION"));
  assert.ok(eventTypes.includes("SHARE_REPURCHASE"));
});

test("Stage 101: NewsEventAssertionStatus strictly separates rumors from official statements", () => {
  const assertionStatuses: NewsEventAssertionStatus[] = [
    "OFFICIALLY_REPORTED",
    "THIRD_PARTY_REPORTED",
    "ALLEGED",
    "RUMORED",
    "DENIED",
    "DISPUTED",
    "CORRECTED",
    "UNRESOLVED",
  ];
  assert.equal(assertionStatuses.length, 8);
  assert.ok(assertionStatuses.includes("RUMORED"));
  assert.ok(assertionStatuses.includes("OFFICIALLY_REPORTED"));
  assert.ok(assertionStatuses.includes("DISPUTED"));
});

test("Stage 101: NewsEventLifecycleStatus tracks deal and announcement stages", () => {
  const lifecycleStatuses: NewsEventLifecycleStatus[] = [
    "PROPOSED",
    "ANNOUNCED",
    "PENDING",
    "APPROVED",
    "COMPLETED",
    "CANCELLED",
    "WITHDRAWN",
    "UNKNOWN",
  ];
  assert.equal(lifecycleStatuses.length, 8);
  assert.ok(lifecycleStatuses.includes("PROPOSED"));
  assert.ok(lifecycleStatuses.includes("ANNOUNCED"));
  assert.ok(lifecycleStatuses.includes("COMPLETED"));
});

test("Stage 101: EventParticipantRole covers key corporate transaction actors", () => {
  const roles: EventParticipantRole[] = [
    "PRIMARY_SUBJECT",
    "ACQUIRER",
    "TARGET",
    "SELLER",
    "BUYER",
    "ISSUER",
    "LENDER",
    "INVESTOR",
    "UNDERWRITER",
    "REGULATOR",
    "SUBJECT",
    "RESPONDENT",
    "OFFICER",
  ];
  assert.equal(roles.length, 13);
  assert.ok(roles.includes("ACQUIRER"));
  assert.ok(roles.includes("TARGET"));
  assert.ok(roles.includes("REGULATOR"));
});

test("Stage 101: NewsStoryThreadDTO and NewsFinancialEventDTO contract validation", () => {
  const mockStory: NewsStoryThreadDTO = {
    story_id: "story-test-1234",
    display_title: "Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50%",
    canonical_topic_label: "INTEREST_RATES_MONETARY_POLICY",
    topic_ids: ["INTEREST_RATES_MONETARY_POLICY"],
    primary_entity_id: "fed_reserve",
    primary_entity_name: "Federal Reserve Board",
    related_entities: [],
    first_source_published_at: "2026-10-26T18:00:00Z",
    latest_source_published_at: "2026-10-26T18:30:00Z",
    first_seen_at: "2026-10-26T18:00:00Z",
    latest_activity_at: "2026-10-26T18:30:00Z",
    story_status: "ACTIVE",
    article_count: 2,
    independent_publisher_count: 2,
    publishers: ["Federal Reserve Board", "Reuters"],
    article_ids: ["art-1", "art-2"],
    representative_article_id: "art-1",
    clustering_method: "CONSERVATIVE_ENTITY_TOPIC_TEMPORAL_V1",
    clustering_version: "1.0.0",
    linked_event_ids: ["fev-test-5678"],
  };

  assert.equal(mockStory.story_id, "story-test-1234");
  assert.equal(mockStory.article_count, 2);
  assert.equal(mockStory.independent_publisher_count, 2);

  const mockEvidence: NewsEventEvidenceDTO = {
    evidence_id: "evd-test-999",
    event_id: "fev-test-5678",
    article_id: "art-1",
    publisher_id: "fed_reserve",
    publisher_name: "Federal Reserve Board",
    source_provider_id: "regulator_announcements",
    evidence_type: "CENTRAL_BANK_RELEASE",
    headline: "Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50%",
    permitted_excerpt: "The FOMC decided today to maintain target rate at 5.25-5.50%.",
    source_published_at: "2026-10-26T18:00:00Z",
    first_observed_at: "2026-10-26T18:00:00Z",
    is_verified_by_filing: false,
    filing_id: null,
  };

  const mockEvent: NewsFinancialEventDTO = {
    event_id: "fev-test-5678",
    event_type: "CENTRAL_BANK_POLICY_DECISION",
    event_title: "Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50%",
    primary_entity_id: "fed_reserve",
    primary_entity_name: "Federal Reserve Board",
    lifecycle_status: "ANNOUNCED",
    assertion_status: "OFFICIALLY_REPORTED",
    event_date: "2026-10-26T18:00:00Z",
    event_time_precision: "CALENDAR_DAY",
    announcement_time: "2026-10-26T18:00:00Z",
    first_seen_at: "2026-10-26T18:00:00Z",
    last_evidence_updated_at: "2026-10-26T18:00:00Z",
    participants: [
      {
        entity_id: "fed_reserve",
        canonical_name: "Federal Reserve Board",
        role: "REGULATOR",
        resolution_status: "CONFIRMED",
      },
    ],
    amounts: [
      {
        amount_type: "INTEREST_RATE_TARGET",
        amount_value: 5.5,
        currency: "PERCENT",
        approximation_status: "RANGE_MAX",
        source_text: "5.25%-5.50%",
      },
    ],
    supporting_article_ids: ["art-1"],
    evidence_records: [mockEvidence],
    linked_story_ids: ["story-test-1234"],
    revisions: [],
    is_disputed: false,
    is_corrected: false,
  };

  assert.equal(mockEvent.event_id, "fev-test-5678");
  assert.equal(mockEvent.assertion_status, "OFFICIALLY_REPORTED");
  assert.equal(mockEvent.amounts[0].amount_value, 5.5);
  assert.equal(mockEvent.evidence_records.length, 1);
});
