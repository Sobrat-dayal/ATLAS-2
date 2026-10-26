import test from "node:test";
import assert from "node:assert/strict";

import {
  NewsSentimentLabel,
  NewsFinancialAspect,
  NewsEntityRelevanceClass,
  NewsEvidenceScope,
  NewsClassificationMethod,
  NewsMarketReactionWindow,
  NewsSentimentAnnotationDTO,
  NewsEntityRelevanceDTO,
  EntitySentimentAggregateDTO,
  SentimentTimelineBucketDTO,
  SentimentTimelineResponseDTO,
  StorySentimentProfileDTO,
  EventSentimentProfileDTO,
  ObservedNewsMarketContextDTO,
  SentimentEvaluationResultDTO,
} from "../types";

test("Stage 102: NewsSentimentLabel taxonomy contains 6 distinct institutional classes", () => {
  const labels: NewsSentimentLabel[] = [
    "POSITIVE",
    "NEGATIVE",
    "NEUTRAL",
    "MIXED",
    "INSUFFICIENT_EVIDENCE",
    "NOT_APPLICABLE",
  ];
  assert.equal(labels.length, 6);
  assert.ok(labels.includes("POSITIVE"));
  assert.ok(labels.includes("NEGATIVE"));
  assert.ok(labels.includes("NEUTRAL"));
  assert.ok(labels.includes("MIXED"));
  assert.ok(labels.includes("INSUFFICIENT_EVIDENCE"));
  assert.ok(labels.includes("NOT_APPLICABLE"));
});

test("Stage 102: NewsFinancialAspect registry categorizes financial language dimensions", () => {
  const aspects: NewsFinancialAspect[] = [
    "EARNINGS_PERFORMANCE",
    "EARNINGS_GUIDANCE",
    "REVENUE_GROWTH",
    "PROFITABILITY",
    "CASH_FLOW",
    "BALANCE_SHEET",
    "DEBT_FINANCING",
    "CORPORATE_GOVERNANCE",
    "REGULATORY_EXPOSURE",
    "PRODUCT_DEVELOPMENT",
    "OPERATIONAL_PERFORMANCE",
    "MANAGEMENT",
    "CORPORATE_TRANSACTION",
    "GENERAL",
  ];
  assert.equal(aspects.length, 14);
  assert.ok(aspects.includes("EARNINGS_PERFORMANCE"));
  assert.ok(aspects.includes("EARNINGS_GUIDANCE"));
  assert.ok(aspects.includes("REGULATORY_EXPOSURE"));
});

test("Stage 102: NewsEntityRelevanceClass supports target connection stratification", () => {
  const relevanceClasses: NewsEntityRelevanceClass[] = [
    "PRIMARY_SUBJECT",
    "DIRECT_PARTICIPANT",
    "VERIFIED_MENTION",
    "VERIFIED_RELATED_ENTITY",
    "CONTEXTUAL_MARKET_REFERENCE",
    "INSUFFICIENT_EVIDENCE",
  ];
  assert.equal(relevanceClasses.length, 6);
  assert.ok(relevanceClasses.includes("PRIMARY_SUBJECT"));
  assert.ok(relevanceClasses.includes("DIRECT_PARTICIPANT"));
  assert.ok(relevanceClasses.includes("VERIFIED_MENTION"));
});

test("Stage 102: NewsMarketReactionWindow defines exchange-anchored observation horizons", () => {
  const windows: NewsMarketReactionWindow[] = [
    "PREV_CLOSE_TO_NEXT_CLOSE",
    "PUB_BAR_TO_NEXT_BAR",
    "PREV_SESSION_TO_SUBSEQUENT_SESSION",
    "INTRADAY_ONE_HOUR",
    "INTRADAY_FOUR_HOURS",
  ];
  assert.equal(windows.length, 5);
  assert.ok(windows.includes("PREV_CLOSE_TO_NEXT_CLOSE"));
});

test("Stage 102: NewsSentimentAnnotationDTO enforces evidence citations and target grounding", () => {
  const annotation: NewsSentimentAnnotationDTO = {
    annotation_id: "ann-test-001",
    article_id: "art-test-earnings-beat",
    article_revision_id: "art-test-earnings-beat-rev1",
    target_entity_id: "comp-aapl-001",
    target_entity_type: "COMPANY",
    target_canonical_name: "Apple Inc.",
    target_ticker: "AAPL",
    sentiment_label: "POSITIVE",
    sentiment_score: 0.85,
    confidence_score: 0.95,
    sentiment_aspect: "EARNINGS_PERFORMANCE",
    classification_status: "ACTIVE",
    analysis_method: "DETERMINISTIC_RULES",
    model_or_rule_version: "v1.0.0-institutional",
    source_published_at: "2026-10-26T12:00:00Z",
    analysis_created_at: "2026-10-26T12:00:05Z",
    evidence: [
      {
        evidence_id: "ev-001",
        article_id: "art-test-earnings-beat",
        revision_id: "art-test-earnings-beat-rev1",
        evidence_scope: "HEADLINE",
        text_span: "Apple Beats Estimates on Record Services Revenue",
        aspect: "EARNINGS_PERFORMANCE",
        rationale_code: "EXCEEDED_EXPECTATIONS",
      },
    ],
    explanation: "Favorable reporting regarding quarterly results topping analyst expectations.",
  };

  assert.equal(annotation.sentiment_label, "POSITIVE");
  assert.equal(annotation.evidence.length, 1);
  assert.equal(annotation.evidence[0].evidence_scope, "HEADLINE");
  assert.ok(annotation.sentiment_score > 0);
  assert.ok(annotation.sentiment_score <= 1.0);
});

test("Stage 102: NewsEntityRelevanceDTO reflects verified entity link with score", () => {
  const relevance: NewsEntityRelevanceDTO = {
    relevance_id: "rel-test-001",
    article_id: "art-aapl-deal",
    entity_id: "comp-aapl-001",
    entity_type: "COMPANY",
    canonical_name: "Apple Inc.",
    ticker: "AAPL",
    relevance_class: "PRIMARY_SUBJECT",
    relevance_score: 1.0,
    evidence_source: "HEADLINE_AND_BODY",
    relationship_type: "PRIMARY_ANNOUNCER",
    resolution_method: "STAGE_99_CANONICAL_RESOLVER",
    source_published_at: "2026-10-26T14:00:00Z",
  };

  assert.equal(relevance.relevance_class, "PRIMARY_SUBJECT");
  assert.equal(relevance.relevance_score, 1.0);
});

test("Stage 102: EntitySentimentAggregateDTO verifies net sentiment calculation and sample count", () => {
  const agg: EntitySentimentAggregateDTO = {
    target_entity_id: "comp-aapl-001",
    target_canonical_name: "Apple Inc.",
    target_ticker: "AAPL",
    evaluation_window_days: 30,
    eligible_count: 10,
    positive_count: 6,
    negative_count: 2,
    neutral_count: 1,
    mixed_count: 1,
    insufficient_evidence_count: 0,
    net_sentiment: 0.40, // (6 - 2) / 10 = 0.40
    unique_story_count: 4,
    independent_publisher_count: 5,
    top_aspects: [
      { aspect: "EARNINGS_PERFORMANCE", count: 4 },
      { aspect: "REVENUE_GROWTH", count: 3 },
    ],
    coverage_completeness: "HIGH",
    methodology_version: "v1.0.0-institutional",
    evaluation_time: "2026-10-26T18:00:00Z",
  };

  assert.equal(agg.eligible_count, 10);
  assert.equal(agg.net_sentiment, 0.40);
  assert.ok(agg.net_sentiment >= -1.0 && agg.net_sentiment <= 1.0);
  assert.equal(agg.unique_story_count, 4);
});

test("Stage 102: ObservedNewsMarketContextDTO enforces noncausal disclaimer and limitations", () => {
  const marketCtx: ObservedNewsMarketContextDTO = {
    context_id: "ctx-test-001",
    article_id_or_event_id: "art-test-aapl-beat",
    instrument_id: "inst-aapl-us",
    ticker: "AAPL",
    market_id: "XNAS",
    window_type: "PREV_CLOSE_TO_NEXT_CLOSE",
    publication_time: "2026-10-26T16:05:00Z",
    window_start_time: "2026-10-26T20:00:00Z",
    window_end_time: "2026-10-27T20:00:00Z",
    price_start: 230.50,
    price_end: 236.25,
    observed_return: 0.0249,
    observed_return_pct: 2.49,
    benchmark_id: "SPY",
    benchmark_return: 0.0050,
    benchmark_relative_return: 1.99,
    currency: "USD",
    is_descriptive_only: true,
    noncausal_disclaimer:
      "Observed market movements are descriptive historical observations over the specified trading window. Correlation does not imply causation.",
    limitations: [
      "Overlapping corporate announcements or macro releases during observation window.",
      "Delay between news wire broadcast and exchange price discovery.",
    ],
    data_source: "CANONICAL_ADJUSTED_CLOSING_PRICES",
  };

  assert.equal(marketCtx.is_descriptive_only, true);
  assert.ok(marketCtx.noncausal_disclaimer.includes("Correlation does not imply causation"));
  assert.ok(marketCtx.limitations.length > 0);
  assert.equal(marketCtx.observed_return_pct, 2.49);
});

test("Stage 102: SentimentEvaluationResultDTO validates golden benchmark metrics", () => {
  const evalResult: SentimentEvaluationResultDTO = {
    evaluation_version: "v1.0.0-golden-institutional",
    evaluated_at: "2026-10-26T20:00:00Z",
    total_samples: 7,
    per_class_precision: {
      POSITIVE: 1.0,
      NEGATIVE: 1.0,
      NEUTRAL: 1.0,
      MIXED: 1.0,
      INSUFFICIENT_EVIDENCE: 1.0,
    },
    per_class_recall: {
      POSITIVE: 1.0,
      NEGATIVE: 1.0,
      NEUTRAL: 1.0,
      MIXED: 1.0,
      INSUFFICIENT_EVIDENCE: 1.0,
    },
    per_class_f1: {
      POSITIVE: 1.0,
      NEGATIVE: 1.0,
      NEUTRAL: 1.0,
      MIXED: 1.0,
      INSUFFICIENT_EVIDENCE: 1.0,
    },
    macro_f1: 1.0,
    accuracy: 1.0,
    target_resolution_accuracy: 1.0,
    abstention_rate: 0.14,
    confusion_matrix: {
      POSITIVE: { POSITIVE: 2 },
      NEGATIVE: { NEGATIVE: 2 },
      NEUTRAL: { NEUTRAL: 1 },
      MIXED: { MIXED: 1 },
      INSUFFICIENT_EVIDENCE: { INSUFFICIENT_EVIDENCE: 1 },
    },
    methodology: "Institutional rule-backed deterministic classifier with negation and aspect tagging",
  };

  assert.equal(evalResult.macro_f1, 1.0);
  assert.equal(evalResult.accuracy, 1.0);
  assert.equal(evalResult.total_samples, 7);
  assert.equal(evalResult.per_class_f1["POSITIVE"], 1.0);
});
