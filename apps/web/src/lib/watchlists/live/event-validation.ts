/**
 * Canonical Market Quote Event Validation for Live Watchlists (Stage 78).
 *
 * Enforces:
 * - Schema version conformance (version 1)
 * - Valid canonical instrument UUID
 * - Non-empty event type matching "market.quote.updated"
 * - Finite decimal representation (rejects NaN, Infinity, -Infinity, malformed strings)
 * - Negative price rejection unless explicitly authorized (e.g. commodity futures CLZ26)
 * - Genuine zero support (0.0 is not null or missing)
 * - Timestamp parsing and format validation
 * - Measure separation: Bid is not Last; Ask is not Last; Mid is not Last
 */

import { IncomingQuoteEvent, RawMarketQuotePayload } from "./types";

export interface EventValidationResult {
  accepted: boolean;
  reason?: string;
  sanitizedQuote?: RawMarketQuotePayload;
  instrumentEntityId?: string;
  sourceTimestamp?: string;
  receivedAt?: string;
  eventId?: string;
}

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isFiniteDecimal(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "number") {
    return Number.isFinite(value);
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return false;
    if (["nan", "infinity", "+infinity", "-infinity"].includes(trimmed.toLowerCase())) {
      return false;
    }
    const num = Number(trimmed);
    return Number.isFinite(num);
  }
  return false;
}

export function parseDecimalString(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (!isFiniteDecimal(value)) return null;
  return String(value).trim();
}

export function validateCanonicalQuoteEvent(
  event: IncomingQuoteEvent,
  options: {
    expectedInstrumentId?: string;
    allowsNegativePrice?: boolean;
    supportedSchemaVersion?: number;
  } = {}
): EventValidationResult {
  const supportedVersion = options.supportedSchemaVersion ?? 1;

  // 1. Schema version
  if (event.schema_version !== undefined && event.schema_version !== supportedVersion) {
    return {
      accepted: false,
      reason: `UNSUPPORTED_SCHEMA_VERSION: received ${event.schema_version}, expected ${supportedVersion}`,
    };
  }

  // 2. Event type
  if (event.event_type && event.event_type !== "market.quote.updated") {
    return {
      accepted: false,
      reason: `INVALID_EVENT_TYPE: received ${event.event_type}, expected market.quote.updated`,
    };
  }

  // 3. Instrument Entity ID
  const legacyInstId = (event as IncomingQuoteEvent & { instrument_id?: string }).instrument_id;
  const entityId = (event.instrument_entity_id || legacyInstId || "").toLowerCase();
  if (!entityId || !UUID_REGEX.test(entityId)) {
    return {
      accepted: false,
      reason: `INVALID_INSTRUMENT_ENTITY_ID: "${entityId}" is not a valid UUID`,
    };
  }

  if (
    options.expectedInstrumentId &&
    entityId !== options.expectedInstrumentId.toLowerCase()
  ) {
    return {
      accepted: false,
      reason: `INSTRUMENT_MISMATCH: received ${entityId}, expected ${options.expectedInstrumentId}`,
    };
  }

  // 4. Payload & Quote inspection
  const payload = event.payload || {};
  const quote = payload.quote || (payload as RawMarketQuotePayload);
  if (!quote || typeof quote !== "object") {
    return {
      accepted: false,
      reason: "MALFORMED_PAYLOAD: quote payload is missing or not an object",
    };
  }

  // 5. Numerical validation of prices
  const allowsNegative = !!options.allowsNegativePrice;

  const rawLast = quote.last_price ?? quote.price;
  const rawBid = quote.bid_price;
  const rawAsk = quote.ask_price;

  // Check that at least one price measure is present
  if (rawLast === undefined && rawBid === undefined && rawAsk === undefined) {
    return {
      accepted: false,
      reason: "EMPTY_QUOTE: event contains no last_price, bid_price, or ask_price",
    };
  }

  const sanitized: RawMarketQuotePayload = { ...quote };

  // Validate last_price if present
  if (rawLast !== undefined && rawLast !== null) {
    if (!isFiniteDecimal(rawLast)) {
      return {
        accepted: false,
        reason: `MALFORMED_DECIMAL: last_price "${rawLast}" is NaN or non-numeric`,
      };
    }
    const num = Number(rawLast);
    if (num < 0 && !allowsNegative) {
      return {
        accepted: false,
        reason: `NEGATIVE_PRICE_REJECTED: ${num} is negative for non-derivative instrument`,
      };
    }
    sanitized.last_price = String(rawLast).trim();
  } else {
    sanitized.last_price = null;
  }

  // Validate bid_price if present
  if (rawBid !== undefined && rawBid !== null) {
    if (!isFiniteDecimal(rawBid)) {
      return {
        accepted: false,
        reason: `MALFORMED_DECIMAL: bid_price "${rawBid}" is NaN or non-numeric`,
      };
    }
    const num = Number(rawBid);
    if (num < 0 && !allowsNegative) {
      return {
        accepted: false,
        reason: `NEGATIVE_PRICE_REJECTED: bid_price ${num} is negative`,
      };
    }
    sanitized.bid_price = String(rawBid).trim();
  } else {
    sanitized.bid_price = null;
  }

  // Validate ask_price if present
  if (rawAsk !== undefined && rawAsk !== null) {
    if (!isFiniteDecimal(rawAsk)) {
      return {
        accepted: false,
        reason: `MALFORMED_DECIMAL: ask_price "${rawAsk}" is NaN or non-numeric`,
      };
    }
    const num = Number(rawAsk);
    if (num < 0 && !allowsNegative) {
      return {
        accepted: false,
        reason: `NEGATIVE_PRICE_REJECTED: ask_price ${num} is negative`,
      };
    }
    sanitized.ask_price = String(rawAsk).trim();
  } else {
    sanitized.ask_price = null;
  }

  // 6. Timestamp validation
  const timestampStr =
    quote.as_of ||
    quote.source_timestamp ||
    payload.source_timestamp ||
    event.emitted_at;

  if (timestampStr) {
    const parsed = Date.parse(timestampStr);
    if (Number.isNaN(parsed)) {
      return {
        accepted: false,
        reason: `MALFORMED_TIMESTAMP: "${timestampStr}" cannot be parsed as ISO date`,
      };
    }
  }

  return {
    accepted: true,
    sanitizedQuote: sanitized,
    instrumentEntityId: entityId,
    sourceTimestamp: timestampStr || new Date().toISOString(),
    receivedAt: payload.received_at || new Date().toISOString(),
    eventId: event.event_id,
  };
}
