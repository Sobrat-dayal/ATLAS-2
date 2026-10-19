/**
 * Frontend Column Registry and Layout Mathematics for Watchlists V1 (Stage 77).
 */

import { WatchlistColumnConfigV1, WatchlistColumnDefinition } from "./types";

export const REQUIRED_COLUMN_ID = "instrument.symbol";
export const MAX_VISIBLE_COLUMNS = 20;
export const MAX_PINNED_COLUMNS = 5;

export const COLUMN_CATALOG: WatchlistColumnDefinition[] = [
  // Identity
  {
    id: "instrument.symbol",
    version: 1,
    label: "Symbol",
    description: "Canonical financial ticker symbol or root contract code.",
    category: "identity",
    value_type: "IDENTIFIER",
    source_capability: "canonical_instrument",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "symbol",
    sort_policy: "alpha",
    default_visible: true,
    default_width: 140,
    min_width: 90,
    max_width: 260,
    can_hide: false,
    can_resize: true,
    can_pin: true,
    can_sort: true,
  },
  {
    id: "instrument.name",
    version: 1,
    label: "Instrument Name",
    description: "Verified legal corporate name or official fund/instrument title.",
    category: "identity",
    value_type: "TEXT",
    source_capability: "canonical_instrument",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "text",
    sort_policy: "alpha",
    default_visible: true,
    default_width: 220,
    min_width: 140,
    max_width: 400,
    can_hide: true,
    can_resize: true,
    can_pin: true,
    can_sort: true,
  },
  {
    id: "instrument.asset_class",
    version: 1,
    label: "Asset Class",
    description: "Canonical asset class (Equity, ETF, Fund, Crypto, FX, Bond, Futures).",
    category: "identity",
    value_type: "ENUM",
    source_capability: "canonical_instrument",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "badge",
    sort_policy: "alpha",
    default_visible: true,
    default_width: 110,
    min_width: 80,
    max_width: 180,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "instrument.subtype",
    version: 1,
    label: "Subtype",
    description: "Instrument subtype (Common Stock, Preferred, ADR, Spot, Sovereign).",
    category: "identity",
    value_type: "TEXT",
    source_capability: "canonical_instrument",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "text",
    sort_policy: "alpha",
    default_visible: false,
    default_width: 130,
    min_width: 90,
    max_width: 200,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "instrument.identifier",
    version: 1,
    label: "Identifier",
    description: "Primary verified identifier (FIGI, ISIN, CUSIP, SEDOL, or exchange ticker).",
    category: "identity",
    value_type: "IDENTIFIER",
    source_capability: "entity_identifiers",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "identifier",
    sort_policy: "alpha",
    default_visible: false,
    default_width: 140,
    min_width: 100,
    max_width: 240,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },

  // Market
  {
    id: "market.venue",
    version: 1,
    label: "Venue / Market",
    description: "Authoritative exchange, operating venue, or OTC market series.",
    category: "market",
    value_type: "TEXT",
    source_capability: "market_series",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "text",
    sort_policy: "alpha",
    default_visible: true,
    default_width: 120,
    min_width: 80,
    max_width: 200,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "market.currency",
    version: 1,
    label: "Quote Currency",
    description: "ISO 4217 currency or settlement token for pricing and valuations.",
    category: "market",
    value_type: "ENUM",
    source_capability: "market_series",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "badge",
    sort_policy: "alpha",
    default_visible: false,
    default_width: 100,
    min_width: 70,
    max_width: 150,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "market.listing_country",
    version: 1,
    label: "Country",
    description: "Jurisdiction and primary country of listing or governance.",
    category: "market",
    value_type: "TEXT",
    source_capability: "canonical_instrument",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "text",
    sort_policy: "alpha",
    default_visible: false,
    default_width: 90,
    min_width: 60,
    max_width: 140,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },

  // Quote
  {
    id: "quote.latest_measure",
    version: 1,
    label: "Latest Measure",
    description: "Latest market observation (Last trade, indicative Mid, NAV, bond price).",
    category: "quote",
    value_type: "MONETARY",
    source_capability: "latest_quote",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "price",
    sort_policy: "numeric",
    default_visible: true,
    default_width: 130,
    min_width: 100,
    max_width: 200,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "quote.change",
    version: 1,
    label: "Change",
    description: "Net price change and percentage change relative to prior reference session.",
    category: "quote",
    value_type: "PERCENTAGE",
    source_capability: "latest_quote",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "change",
    sort_policy: "numeric",
    default_visible: true,
    default_width: 130,
    min_width: 100,
    max_width: 220,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "quote.kind",
    version: 1,
    label: "Quote Kind",
    description: "Measure classification (Last, Mid, Fixing, NAV, Clean Price, Yield).",
    category: "quote",
    value_type: "TEXT",
    source_capability: "latest_quote",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "badge",
    sort_policy: "alpha",
    default_visible: false,
    default_width: 110,
    min_width: 80,
    max_width: 160,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "quote.as_of",
    version: 1,
    label: "As Of",
    description: "Exact UTC observation timestamp or official valuation date of quote snapshot.",
    category: "quote",
    value_type: "TIMESTAMP",
    source_capability: "latest_quote",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "timestamp",
    sort_policy: "chronological",
    default_visible: false,
    default_width: 120,
    min_width: 90,
    max_width: 180,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },

  // Quality
  {
    id: "quality.freshness",
    version: 1,
    label: "Freshness",
    description: "Freshness and delivery delay status (Fresh, Delayed 15m, Stale, Unavailable).",
    category: "quality",
    value_type: "STATUS",
    source_capability: "freshness_monitor",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "status",
    sort_policy: "alpha",
    default_visible: true,
    default_width: 120,
    min_width: 90,
    max_width: 170,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
  {
    id: "quality.source",
    version: 1,
    label: "Source",
    description: "Authoritative market-data provider, feed, or venue publisher.",
    category: "quality",
    value_type: "TEXT",
    source_capability: "provenance",
    supported_asset_classes: ["equity", "etf", "fund", "crypto", "currency", "fx", "bond", "future", "commodity", "index", "security"],
    formatter_id: "text",
    sort_policy: "alpha",
    default_visible: false,
    default_width: 120,
    min_width: 90,
    max_width: 180,
    can_hide: true,
    can_resize: true,
    can_pin: false,
    can_sort: true,
  },
];

export const COLUMN_MAP = new Map<string, WatchlistColumnDefinition>(
  COLUMN_CATALOG.map((col) => [col.id, col])
);

export function getColumnDefinition(id: string): WatchlistColumnDefinition | undefined {
  return COLUMN_MAP.get(id);
}

export function getDefaultColumnConfig(): WatchlistColumnConfigV1 {
  const visibleCols = COLUMN_CATALOG.filter((c) => c.default_visible).map((c) => c.id);
  const optionalCols = COLUMN_CATALOG.filter((c) => !c.default_visible).map((c) => c.id);
  const orderedCols = [...visibleCols, ...optionalCols];
  const widths: Record<string, number> = {};
  for (const c of COLUMN_CATALOG) {
    widths[c.id] = c.default_width;
  }

  return {
    schema_version: 1,
    ordered_column_ids: orderedCols,
    visible_column_ids: visibleCols,
    widths,
    pinned_left_column_ids: [REQUIRED_COLUMN_ID],
    sort: { column_id: null, direction: null },
  };
}

/**
 * Calculates sticky left offset in pixels for each visible pinned column.
 * Accounts for any leading fixed non-configurable columns (e.g. drag handle: 32px, index #: 40px = 72px base).
 */
export function calculateStickyLeftOffsets(
  visibleColumns: WatchlistColumnDefinition[],
  pinnedColumnIds: string[],
  widths: Record<string, number>,
  baseOffsetPx: number = 72
): Map<string, number> {
  const offsets = new Map<string, number>();
  let currentLeft = baseOffsetPx;

  for (const col of visibleColumns) {
    if (pinnedColumnIds.includes(col.id)) {
      offsets.set(col.id, currentLeft);
      const width = widths[col.id] ?? col.default_width;
      currentLeft += width;
    }
  }

  return offsets;
}
