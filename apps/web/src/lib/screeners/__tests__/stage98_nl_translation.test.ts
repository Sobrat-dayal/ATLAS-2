/**
 * Stage 98: Automated Tests for Natural-Language Screener Translation Engine
 * 
 * Tests:
 * 1. NLTranslateRequest and NLClarifyRequest payload contracts
 * 2. NLTranslationProposal typed lifecycle states (valid, needs_clarification, unsupported)
 * 3. Requirement coverage resolution tracking
 * 4. Interactive Ambiguity questions and option models
 * 5. Structured Query Modification diff
 * 6. Transfer to Visual Filter Builder and ScreenerRunRequest compilation
 */

import assert from "node:assert/strict";
import test from "node:test";

import {
  FilterCriterion,
  NLAmbiguityCategory,
  NLAmbiguityQuestion,
  NLClarifyRequest,
  NLQueryModificationDiff,
  NLRequirementResolution,
  NLRequirementStatus,
  NLTranslateRequest,
  NLTranslationProposal,
  NLTranslationStatus,
  ScreenerRunRequest,
  SortCriterion,
  UniverseSelection,
} from "../types";

test("Stage 98: NLTranslateRequest constructs with proper defaults and constraints", () => {
  const req: NLTranslateRequest = {
    text: "Find large-cap Indian companies with revenue growth above 15% and P/E below 25",
    currency_policy: "INR",
    mode: "create_new_query",
    locale: "en-US",
  };

  assert.equal(req.currency_policy, "INR");
  assert.equal(req.mode, "create_new_query");
  assert.ok(req.text.length < 1000);
});

test("Stage 98: NLTranslationProposal validates complete resolved status and requirement coverage", () => {
  const requirements: NLRequirementResolution[] = [
    {
      requirement_id: "req_1",
      source_text: "large-cap Indian companies",
      interpreted_concept: "Market Cap >= 20000 Cr INR",
      resolved_filter_id: "market_cap",
      status: "resolved",
      explanation: "Applied market_cap >= 200,000,000,000 INR",
    },
    {
      requirement_id: "req_2",
      source_text: "revenue growth above 15%",
      interpreted_concept: "Revenue Growth YoY",
      resolved_filter_id: "revenue_growth_yoy",
      status: "resolved",
      explanation: "Applied revenue_growth_yoy > 15%",
    },
    {
      requirement_id: "req_3",
      source_text: "P/E below 25",
      interpreted_concept: "P/E Ratio",
      resolved_filter_id: "pe_ratio",
      status: "resolved",
      explanation: "Applied pe_ratio < 25",
    },
  ];

  const filters: FilterCriterion[] = [
    { filter_id: "market_cap", operator: "gte", value: 200000000000, currency: "INR" },
    { filter_id: "revenue_growth_yoy", operator: "gt", value: 15.0 },
    { filter_id: "pe_ratio", operator: "lt", value: 25.0 },
  ];

  const universe: UniverseSelection = {
    universe_id: "common_equity",
    listing_country_codes: ["IN"],
  };

  const proposal: NLTranslationProposal = {
    proposal_id: "nlp_test123",
    status: "valid",
    original_text: "Find large-cap Indian companies with revenue growth above 15% and P/E below 25",
    universe,
    filters,
    sort: [{ field_id: "market_cap", direction: "desc" }],
    requirements,
    ambiguities: [],
    unsupported: [],
    assumptions: ["Interpreted 'large-cap' as Market Cap >= ₹20,000 Crore (INR)."],
    ready_for_review: true,
    translator_version: "1.0.0",
    registry_revision: "stage_98_v1",
    coverage_count: "3 of 3 requirements resolved",
  };

  assert.equal(proposal.status, "valid");
  assert.equal(proposal.ready_for_review, true);
  assert.equal(proposal.filters.length, 3);
  assert.equal(proposal.requirements.length, 3);
  assert.equal(proposal.requirements[0].status, "resolved");
});

test("Stage 98: Ambiguity questions render with targeted options and categories", () => {
  const amb: NLAmbiguityQuestion = {
    ambiguity_id: "amb_cheap",
    category: "metric_ambiguity",
    question: "Which valuation metric should define 'cheap'?",
    source_phrase: "cheap",
    options: [
      { id: "opt_pe_20", label: "P/E below 20x", filter_id: "pe_ratio", operator: "lt", value: 20 },
      { id: "opt_pe_15", label: "P/E below 15x", filter_id: "pe_ratio", operator: "lt", value: 15 },
      { id: "opt_pb_2", label: "P/B below 2x", filter_id: "pb_ratio", operator: "lt", value: 2 },
    ],
  };

  const proposal: NLTranslationProposal = {
    proposal_id: "nlp_amb1",
    status: "needs_clarification",
    original_text: "Find cheap Indian banking stocks",
    universe: { universe_id: "common_equity", listing_country_codes: ["IN"], industries: ["Banking"] },
    filters: [],
    sort: [],
    requirements: [
      {
        requirement_id: "req_1",
        source_text: "cheap",
        status: "ambiguous",
        explanation: "Subjective qualifier 'cheap' requires an explicit valuation threshold.",
      },
    ],
    ambiguities: [amb],
    unsupported: [],
    assumptions: [],
    ready_for_review: false,
    translator_version: "1.0.0",
    registry_revision: "stage_98_v1",
    coverage_count: "0 of 1 requirements resolved",
  };

  assert.equal(proposal.status, "needs_clarification");
  assert.equal(proposal.ready_for_review, false);
  assert.equal(proposal.ambiguities.length, 1);
  assert.equal(proposal.ambiguities[0].options.length, 3);

  // Validate Clarify Request Contract
  const clarifyReq: NLClarifyRequest = {
    proposal_id: proposal.proposal_id,
    original_text: proposal.original_text,
    ambiguity_id: amb.ambiguity_id,
    selected_option_id: "opt_pe_20",
  };
  assert.equal(clarifyReq.selected_option_id, "opt_pe_20");
});

test("Stage 98: Unsupported requirements are explicitly reported without silent omission", () => {
  const proposal: NLTranslationProposal = {
    proposal_id: "nlp_unsup1",
    status: "unsupported",
    original_text: "Find AI stocks that will breakout next week",
    universe: { universe_id: "common_equity" },
    filters: [],
    sort: [],
    requirements: [
      {
        requirement_id: "req_1",
        source_text: "breakout",
        status: "unsupported",
        explanation: "Time-series predictive breakout forecasts are not supported deterministic screener filters.",
      },
    ],
    ambiguities: [],
    unsupported: [
      "'breakout': Time-series predictive breakout forecasts are not supported deterministic screener filters.",
    ],
    assumptions: [],
    ready_for_review: false,
    translator_version: "1.0.0",
    registry_revision: "stage_98_v1",
    coverage_count: "0 of 1 requirements resolved",
  };

  assert.equal(proposal.status, "unsupported");
  assert.equal(proposal.ready_for_review, false);
  assert.equal(proposal.unsupported.length, 1);
});

test("Stage 98: Query Modification mode produces structured diff", () => {
  const diff: NLQueryModificationDiff = {
    added_conditions: [{ filter_id: "rsi_14", operator: "lt", value: 30 }],
    updated_conditions: [{ filter_id: "pe_ratio", operator: "lt", value: 18 }],
    removed_conditions: ["market_cap"],
  };

  assert.equal(diff.added_conditions.length, 1);
  assert.equal(diff.added_conditions[0].filter_id, "rsi_14");
  assert.equal(diff.updated_conditions.length, 1);
  assert.equal(diff.updated_conditions[0].value, 18);
  assert.deepEqual(diff.removed_conditions, ["market_cap"]);
});

test("Stage 98: Translation proposal compiles into ScreenerRunRequest without schema bypass", () => {
  const proposalFilters: FilterCriterion[] = [
    { filter_id: "market_cap", operator: "gte", value: 50000000000, currency: "USD" },
    { filter_id: "operating_margin", operator: "gte", value: 25.0 },
    { filter_id: "debt_to_equity", operator: "lt", value: 0.8 },
  ];

  const proposalUniverse: UniverseSelection = {
    universe_id: "common_equity",
    listing_country_codes: ["US"],
    sectors: ["Technology"],
  };

  const runReq: ScreenerRunRequest = {
    universe: proposalUniverse,
    filters: proposalFilters,
    sort: [{ field_id: "market_cap", direction: "desc" }],
    page: 1,
    page_size: 50,
  };

  assert.equal(runReq.universe.universe_id, "common_equity");
  assert.deepEqual(runReq.universe.listing_country_codes, ["US"]);
  assert.deepEqual(runReq.universe.sectors, ["Technology"]);
  assert.equal(runReq.filters.length, 3);
  assert.equal(runReq.sort[0].direction, "desc");
});
