"use client";

/**
 * Live Market Data Status & Provenance Bar for ATLAS Charts (Stage 67).
 *
 * Displays transport connection state, market-data freshness classification,
 * delay status, provider provenance, and canonical observation timestamps.
 */

import React from "react";
import {
  Activity,
  AlertCircle,
  Clock,
  Radio,
  RefreshCw,
  Wifi,
  WifiOff,
} from "lucide-react";
import {
  ChartConnectionState,
  ChartInstrumentMetadata,
  ChartLiveCapability,
  ChartMarketDataFreshness,
  LiveQuoteDTO,
} from "@/lib/charts";
import { formatBarDateTime } from "@/lib/charts/formatting";

export interface LiveMarketDataStatusProps {
  connectionState: ChartConnectionState;
  freshnessStatus: ChartMarketDataFreshness;
  delayStatus: string;
  liveCapability: ChartLiveCapability;
  quote: LiveQuoteDTO | null;
  instrument: ChartInstrumentMetadata | null;
  provider: string;
  venue: string;
}

export function LiveMarketDataStatus({
  connectionState,
  freshnessStatus,
  delayStatus,
  liveCapability,
  quote,
  instrument,
  provider,
  venue,
}: LiveMarketDataStatusProps) {
  // Connection badge color & icon
  const getConnectionPill = () => {
    switch (connectionState) {
      case "CONNECTED":
        return {
          icon: <Wifi className="w-3 h-3 text-emerald-400" />,
          label: "CONNECTED",
          className: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
        };
      case "CONNECTING":
        return {
          icon: <RefreshCw className="w-3 h-3 text-cyan-400 animate-spin" />,
          label: "CONNECTING",
          className: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
        };
      case "RECONNECTING":
        return {
          icon: <RefreshCw className="w-3 h-3 text-amber-400 animate-spin" />,
          label: "RECONNECTING",
          className: "text-amber-400 bg-amber-500/10 border-amber-500/30",
        };
      case "ERROR":
        return {
          icon: <AlertCircle className="w-3 h-3 text-rose-400" />,
          label: "TRANSPORT ERROR",
          className: "text-rose-400 bg-rose-500/10 border-rose-500/30",
        };
      default:
        return {
          icon: <WifiOff className="w-3 h-3 text-zinc-400" />,
          label: "DISCONNECTED",
          className: "text-zinc-400 bg-zinc-800 border-zinc-700",
        };
    }
  };

  // Freshness & delay badge
  const getFreshnessPill = () => {
    if (delayStatus === "DELAYED_15M" || freshnessStatus === "DELAYED") {
      return {
        label: "DELAYED 15M",
        className: "text-amber-400 bg-amber-500/10 border-amber-500/30",
      };
    }
    switch (freshnessStatus) {
      case "LIVE":
        return {
          label: "REALTIME",
          className: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
        };
      case "STALE":
        return {
          label: "STALE QUOTE",
          className: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
        };
      case "UNAVAILABLE":
        return {
          label: "FEED UNAVAILABLE",
          className: "text-zinc-500 bg-zinc-800 border-zinc-700",
        };
      default:
        return {
          label: "UNKNOWN FRESHNESS",
          className: "text-zinc-400 bg-zinc-800 border-zinc-700",
        };
    }
  };

  // Capability badge
  const getCapabilityPill = () => {
    if (liveCapability === "LIVE_PRICE_AVAILABLE") {
      return {
        label: "LIVE LAST OVERLAY ACTIVE",
        className: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
      };
    }
    if (liveCapability === "HISTORICAL_ONLY") {
      return {
        label: "HISTORICAL ONLY (OTC BID/ASK)",
        className: "text-zinc-400 bg-zinc-900 border-zinc-800",
      };
    }
    return {
      label: "CAPABILITY UNKNOWN",
      className: "text-zinc-500 bg-zinc-900 border-zinc-800",
    };
  };

  const conn = getConnectionPill();
  const fresh = getFreshnessPill();
  const cap = getCapabilityPill();

  const asOfText = quote?.as_of ? formatBarDateTime(quote.as_of) : "—";
  const displayVenue = venue || instrument?.market_or_venue || "Primary Exchange";
  const displayProvider = provider || instrument?.provider_key || "canonical_feed";

  return (
    <div
      role="region"
      aria-label="Live Market Data Status"
      className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono"
    >
      {/* Left: Status Badges */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Connection status */}
        <span
          className={`px-2 py-0.5 rounded border text-[11px] font-semibold flex items-center gap-1.5 ${conn.className}`}
          title={`Transport connection: ${conn.label}`}
        >
          {conn.icon}
          <span>{conn.label}</span>
        </span>

        {/* Freshness status */}
        <span
          className={`px-2 py-0.5 rounded border text-[11px] font-semibold flex items-center gap-1 ${fresh.className}`}
          title={`Market data freshness: ${fresh.label}`}
        >
          <Activity className="w-3 h-3" />
          <span>{fresh.label}</span>
        </span>

        {/* Live capability */}
        <span
          className={`px-2 py-0.5 rounded border text-[10px] font-medium flex items-center gap-1 ${cap.className}`}
          title={`Stream capability: ${cap.label}`}
        >
          <Radio className="w-3 h-3" />
          <span>{cap.label}</span>
        </span>
      </div>

      {/* Right: Provenance & Observation Timestamp */}
      <div className="flex flex-wrap items-center gap-3 text-zinc-400">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3 text-zinc-500" />
          <span className="text-zinc-500">AS OF:</span>
          <span className="text-zinc-200 tabular-nums">{asOfText}</span>
        </div>

        <div className="hidden sm:flex items-center gap-1">
          <span className="text-zinc-500">VENUE:</span>
          <span className="text-zinc-300 font-semibold">{displayVenue}</span>
        </div>

        <div className="hidden md:flex items-center gap-1">
          <span className="text-zinc-500">SOURCE:</span>
          <span className="text-zinc-300">{displayProvider}</span>
        </div>
      </div>
    </div>
  );
}
