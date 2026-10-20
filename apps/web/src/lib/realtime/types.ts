/**
 * Shared Realtime WebSocket Types (Stage 43 / Stage 78).
 */

export interface QuoteSubscriptionKeyDTO {
  instrument_entity_id: string;
  variant?: string | null;
  symbol?: string | null;
}

export type RealtimeConnectionState =
  | "DISCONNECTED"
  | "CONNECTING"
  | "CONNECTED"
  | "RECONNECTING"
  | "ERROR";

export type RealtimeSubscriptionState =
  | "REQUESTED"
  | "PENDING"
  | "ACTIVE"
  | "DENIED";

export interface ServerConnectionReadyMessage {
  type: "connection.ready";
  protocol_version: number;
  connection_id: string;
  server_time: string;
  heartbeat_interval_seconds: number;
  max_series_per_message: number;
  max_series_per_connection: number;
}

export interface SubscriptionAckMessage {
  type: "subscription.ack";
  protocol_version: number;
  request_id: string;
  accepted: QuoteSubscriptionKeyDTO[];
  rejected: Record<string, string>;
}

export interface QuoteSnapshotMessage {
  type: "market.quote.snapshot";
  protocol_version: number;
  series: QuoteSubscriptionKeyDTO;
  snapshot: Record<string, unknown> | null;
  freshness?: Record<string, unknown> | null;
  barrier_cursor: string;
}

export interface LiveEventMessageOut {
  type: "live.event";
  protocol_version: number;
  stream_id: string;
  event: {
    schema_version: number;
    event_id: string;
    event_type: string;
    emitted_at: string;
    instrument_entity_id: string;
    provider_key: string;
    payload: {
      quote?: Record<string, unknown>;
      received_at?: string;
      cached_at?: string;
      source_timestamp?: string;
      [key: string]: unknown;
    };
    [key: string]: unknown;
  };
}

export interface ServerPingMessage {
  type: "system.ping";
  protocol_version: number;
  ping_id: string;
  sent_at: string;
}

export interface SystemResyncRequiredMessage {
  type: "system.resync_required";
  protocol_version: number;
  reason: string;
  barrier_cursor?: string | null;
}

export interface ProtocolErrorMessage {
  type: "error";
  protocol_version: number;
  error_code: string;
  message: string;
  request_id?: string | null;
}

export type ServerMessage =
  | ServerConnectionReadyMessage
  | SubscriptionAckMessage
  | QuoteSnapshotMessage
  | LiveEventMessageOut
  | ServerPingMessage
  | SystemResyncRequiredMessage
  | ProtocolErrorMessage;

export interface ClientSubscribeMessage {
  type: "subscribe";
  protocol_version: number;
  request_id: string;
  series: QuoteSubscriptionKeyDTO[];
}

export interface ClientUnsubscribeMessage {
  type: "unsubscribe";
  protocol_version: number;
  request_id: string;
  series: QuoteSubscriptionKeyDTO[];
}

export interface ClientPongMessage {
  type: "pong";
  protocol_version: number;
  ping_id: string;
}

export type ClientMessage =
  | ClientSubscribeMessage
  | ClientUnsubscribeMessage
  | ClientPongMessage;

export interface SeriesSubscriptionCallbacks {
  onSnapshot?: (snapshot: QuoteSnapshotMessage) => void;
  onLiveEvent?: (event: LiveEventMessageOut) => void;
  onStatusChange?: (state: RealtimeSubscriptionState, reason?: string) => void;
}
