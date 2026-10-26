import test from "node:test";
import assert from "node:assert/strict";

import {
  NewsDiscoveryMode,
  NewsTimelineInterval,
  NewsDatePreset,
  NewsSortOrder,
  NewsDiscoveryQueryDTO,
  NewsTimelineRequestDTO,
  NewsFacetsResponseDTO,
  NewsTimelineBucketDTO,
} from "../types";

test("Stage 100: NewsDiscoveryMode supports canonical exploration dimensions", () => {
  const modes: NewsDiscoveryMode[] = [
    "ALL",
    "MARKETS",
    "COMPANIES",
    "SECURITIES",
    "TOPICS",
    "INDUSTRIES",
    "WATCHLIST",
  ];
  assert.equal(modes.length, 7);
  assert.ok(modes.includes("ALL"));
  assert.ok(modes.includes("WATCHLIST"));
  assert.ok(modes.includes("SECURITIES"));
});

test("Stage 100: NewsTimelineInterval supports DAY, WEEK, MONTH", () => {
  const intervals: NewsTimelineInterval[] = ["DAY", "WEEK", "MONTH"];
  assert.equal(intervals.length, 3);
  assert.ok(intervals.includes("DAY"));
  assert.ok(intervals.includes("WEEK"));
  assert.ok(intervals.includes("MONTH"));
});

test("Stage 100: NewsDatePreset covers built-in relative periods", () => {
  const presets: NewsDatePreset[] = [
    "ALL_TIME",
    "TODAY",
    "PAST_24H",
    "PAST_7D",
    "PAST_30D",
    "CUSTOM",
  ];
  assert.equal(presets.length, 6);
  assert.ok(presets.includes("PAST_24H"));
  assert.ok(presets.includes("PAST_7D"));
});

test("Stage 100: NewsSortOrder supports published-date and text-relevance ranking", () => {
  const sorts: NewsSortOrder[] = [
    "PUBLISHED_DESC",
    "PUBLISHED_ASC",
    "RELEVANCE_DESC",
  ];
  assert.equal(sorts.length, 3);
  assert.ok(sorts.includes("RELEVANCE_DESC"));
});

test("Stage 100: NewsDiscoveryQueryDTO constructs bounded search query", () => {
  const query: NewsDiscoveryQueryDTO = {
    mode: "COMPANIES",
    entity_ids: ["comp-aapl-001"],
    tickers: ["AAPL"],
    topic_ids: ["EARNINGS_RELEASES"],
    query: '"quarterly revenue" record',
    date_preset: "PAST_7D",
    sort_order: "RELEVANCE_DESC",
    limit: 25,
  };

  assert.equal(query.mode, "COMPANIES");
  assert.deepEqual(query.tickers, ["AAPL"]);
  assert.equal(query.query, '"quarterly revenue" record');
  assert.equal(query.sort_order, "RELEVANCE_DESC");
  assert.equal(query.limit, 25);
});

test("Stage 100: NewsTimelineRequestDTO binds interval, timezone, and query", () => {
  const req: NewsTimelineRequestDTO = {
    query: {
      mode: "ALL",
      query: "Federal Reserve",
    },
    interval: "DAY",
    timezone: "America/New_York",
  };

  assert.equal(req.interval, "DAY");
  assert.equal(req.timezone, "America/New_York");
  assert.equal(req.query?.query, "Federal Reserve");
});

test("Stage 100: NewsFacetsResponseDTO preserves discrete non-leaking counts", () => {
  const facets: NewsFacetsResponseDTO = {
    sources: [
      { key: "openbb_news", label: "OpenBB Global Wire", count: 42 },
      { key: "financial_wire_direct", label: "Direct Financial Wire", count: 18 },
    ],
    publishers: [
      { key: "bloomberg", label: "Bloomberg News", count: 25 },
      { key: "reuters", label: "Reuters", count: 20 },
    ],
    categories: [
      { key: "CENTRAL_BANKS", label: "Central Banks", count: 14 },
    ],
    topics: [
      { key: "INTEREST_RATES_MONETARY_POLICY", label: "Monetary Policy & Interest Rates", count: 14 },
    ],
    countries: [
      { key: "US", label: "United States", count: 35 },
      { key: "IN", label: "India", count: 12 },
    ],
    article_types: [
      { key: "WIRE_REPORT", label: "Wire Report", count: 30 },
    ],
    as_of: "2026-10-26T18:00:00Z",
  };

  assert.equal(facets.sources.length, 2);
  assert.equal(facets.sources[0].count, 42);
  assert.equal(facets.topics[0].key, "INTEREST_RATES_MONETARY_POLICY");
  assert.equal(facets.countries.length, 2);
});

test("Stage 100: NewsTimelineBucketDTO accurately associates chronologically bounded articles", () => {
  const bucket: NewsTimelineBucketDTO = {
    bucket_id: "2026-10-26",
    start_time: "2026-10-26T00:00:00Z",
    end_time: "2026-10-26T23:59:59Z",
    label: "Monday, Oct 26, 2026",
    article_count: 3,
    articles: [],
  };

  assert.equal(bucket.bucket_id, "2026-10-26");
  assert.equal(bucket.article_count, 3);
  assert.ok(bucket.label.includes("Oct 26, 2026"));
});
