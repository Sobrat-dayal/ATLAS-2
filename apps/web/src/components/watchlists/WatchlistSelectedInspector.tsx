import React from "react";
import { useRouter } from "next/navigation";
import {
  BarChart2,
  TrendingUp,
  Building2,
  X,
  ShieldCheck,
} from "lucide-react";
import { WatchlistItem } from "@/lib/watchlists/types";
import {
  formatChange,
  formatObservationTime,
  formatPrice,
  getAssetClassBadge,
  getMarketRouteForAssetClass,
} from "@/lib/watchlists/formatting";
import { WatchlistStatusBadge } from "./WatchlistStatusBadge";

interface WatchlistSelectedInspectorProps {
  item: WatchlistItem | null;
  onClose: () => void;
}

export function WatchlistSelectedInspector({
  item,
  onClose,
}: WatchlistSelectedInspectorProps) {
  const router = useRouter();

  if (!item) return null;

  const badge = getAssetClassBadge(item.asset_class);
  const formattedPrice = formatPrice(item.last_price, item.asset_class, item.quote_currency);
  const changeData = formatChange(item.absolute_change, item.percentage_change);
  const marketRoute = getMarketRouteForAssetClass(item.asset_class);

  return (
    <div className="mt-4 p-4 rounded border border-zinc-800 bg-zinc-950/90 shadow-lg text-xs space-y-4">
      <div className="flex items-start justify-between border-b border-zinc-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-zinc-900 border border-zinc-700/80 flex items-center justify-center font-mono font-bold text-zinc-200 text-xs">
            {item.symbol.slice(0, 3)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-sm text-zinc-100 tracking-wide">
                {item.symbol}
              </span>
              <span className="px-1.5 py-0.2 rounded text-[10px] font-mono font-medium border border-zinc-700 bg-zinc-800 text-zinc-300">
                {badge.label}
              </span>
              <WatchlistStatusBadge
                freshnessStatus={item.freshness_status}
                deliveryDelayStatus={item.delivery_delay_status}
                delaySeconds={item.delay_seconds}
              />
            </div>
            <div className="text-zinc-400 text-xs mt-0.5">{item.display_name}</div>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="text-zinc-400 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800 transition-colors"
          aria-label="Close inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="p-2.5 rounded bg-zinc-900/40 border border-zinc-800/60">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">
            Latest Observation
          </div>
          <div className="font-mono text-sm font-semibold text-zinc-100">
            {formattedPrice}{" "}
            <span className="text-[10px] font-normal text-zinc-400 uppercase">
              {item.quote_currency || ""}
            </span>
          </div>
          <div
            className={`text-[11px] font-mono mt-0.5 ${
              changeData.direction === "up"
                ? "text-emerald-400"
                : changeData.direction === "down"
                ? "text-rose-400"
                : "text-zinc-400"
            }`}
          >
            {changeData.text}
          </div>
        </div>

        <div className="p-2.5 rounded bg-zinc-900/40 border border-zinc-800/60 font-mono">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">
            Market Series / Venue
          </div>
          <div className="text-zinc-200 font-semibold">{item.venue || "Global Consolidated"}</div>
          <div className="text-[10px] text-zinc-400 mt-0.5">
            Measure: {item.quote_measure || "Last Trade"}
          </div>
        </div>

        <div className="p-2.5 rounded bg-zinc-900/40 border border-zinc-800/60 font-mono">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">
            Bid / Ask Quotes
          </div>
          <div className="text-zinc-200">
            Bid: {item.bid_price ? formatPrice(item.bid_price, item.asset_class) : "—"}
          </div>
          <div className="text-zinc-200">
            Ask: {item.ask_price ? formatPrice(item.ask_price, item.asset_class) : "—"}
          </div>
        </div>

        <div className="p-2.5 rounded bg-zinc-900/40 border border-zinc-800/60 font-mono">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">
            Observation Timestamp
          </div>
          <div className="text-zinc-200 text-[11px]">
            {formatObservationTime(item.source_timestamp)}
          </div>
          <div className="text-[10px] text-zinc-500 truncate mt-0.5" title={item.instrument_entity_id}>
            UUID: {item.instrument_entity_id.slice(0, 8)}...
          </div>
        </div>
      </div>

      {/* Cross-navigation Actions Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-zinc-800/80">
        <div className="flex items-center gap-2 text-[11px] text-zinc-500 font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-zinc-400" />
          <span>Canonical Financial Instrument Authority</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => router.push(`/charts?instrument=${encodeURIComponent(item.instrument_entity_id)}`)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 text-xs font-medium transition-colors"
          >
            <BarChart2 className="w-3.5 h-3.5 text-sky-400" />
            Open in Charts
          </button>

          <button
            type="button"
            onClick={() => router.push(`${marketRoute}?instrument=${encodeURIComponent(item.instrument_entity_id)}`)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 text-xs font-medium transition-colors"
          >
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            Open in Markets
          </button>

          {item.has_company_page && item.issuer_entity_id ? (
            <button
              type="button"
              onClick={() => router.push(`/companies?entity=${encodeURIComponent(item.issuer_entity_id!)}`)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 text-xs font-medium transition-colors"
            >
              <Building2 className="w-3.5 h-3.5 text-amber-400" />
              Open Company
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
