import React from "react";
import { useRouter } from "next/navigation";
import {
  BarChart2,
  TrendingUp,
  Building2,
  Trash2,
  ArrowUp,
  ArrowDown,
  Bell,
} from "lucide-react";
import { WatchlistItem } from "@/lib/watchlists/types";
import { getMarketRouteForAssetClass } from "@/lib/watchlists/formatting";

interface WatchlistRowActionsProps {
  item: WatchlistItem;
  index: number;
  totalCount: number;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onRemove: () => void;
  onCreateAlert?: (item: WatchlistItem) => void;
}

export function WatchlistRowActions({
  item,
  index,
  totalCount,
  onMoveUp,
  onMoveDown,
  onRemove,
  onCreateAlert,
}: WatchlistRowActionsProps) {
  const router = useRouter();

  const handleOpenCharts = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push(`/charts?instrument=${encodeURIComponent(item.instrument_entity_id)}`);
  };

  const handleOpenMarkets = (e: React.MouseEvent) => {
    e.stopPropagation();
    const route = getMarketRouteForAssetClass(item.asset_class);
    router.push(`${route}?instrument=${encodeURIComponent(item.instrument_entity_id)}`);
  };

  const handleOpenCompany = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (item.issuer_entity_id) {
      router.push(`/companies?entity=${encodeURIComponent(item.issuer_entity_id)}`);
    }
  };

  return (
    <div className="flex items-center gap-1 justify-end" onClick={(e) => e.stopPropagation()}>
      {/* Keyboard Reorder buttons */}
      <button
        type="button"
        disabled={index === 0}
        onClick={(e) => {
          e.stopPropagation();
          onMoveUp();
        }}
        className="p-1 rounded text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
        title="Move Up in Watchlist"
        aria-label={`Move ${item.symbol} up`}
      >
        <ArrowUp className="w-3.5 h-3.5" />
      </button>

      <button
        type="button"
        disabled={index === totalCount - 1}
        onClick={(e) => {
          e.stopPropagation();
          onMoveDown();
        }}
        className="p-1 rounded text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
        title="Move Down in Watchlist"
        aria-label={`Move ${item.symbol} down`}
      >
        <ArrowDown className="w-3.5 h-3.5" />
      </button>

      {/* Cross-navigation: Open in Charts */}
      <button
        type="button"
        onClick={handleOpenCharts}
        className="p-1 rounded text-zinc-400 hover:text-sky-300 hover:bg-sky-950/40 transition-colors"
        title="Open in Professional Charts"
        aria-label={`Open ${item.symbol} in Charts`}
      >
        <BarChart2 className="w-3.5 h-3.5" />
      </button>

      {/* Cross-navigation: Open in Markets */}
      <button
        type="button"
        onClick={handleOpenMarkets}
        className="p-1 rounded text-zinc-400 hover:text-emerald-300 hover:bg-emerald-950/40 transition-colors"
        title="Open in Markets Module"
        aria-label={`Open ${item.symbol} in Markets`}
      >
        <TrendingUp className="w-3.5 h-3.5" />
      </button>

      {/* Cross-navigation: Open verified Company (only when relationship exists) */}
      {item.has_company_page && item.issuer_entity_id ? (
        <button
          type="button"
          onClick={handleOpenCompany}
          className="p-1 rounded text-zinc-400 hover:text-amber-300 hover:bg-amber-950/40 transition-colors"
          title="Open Issuer Profile in Companies"
          aria-label={`Open Issuer Profile for ${item.symbol}`}
        >
          <Building2 className="w-3.5 h-3.5" />
        </button>
      ) : null}

      {/* Create Alert */}
      {onCreateAlert && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onCreateAlert(item);
          }}
          className="p-1 rounded text-zinc-400 hover:text-sky-300 hover:bg-sky-950/40 transition-colors"
          title="Create Alert for Instrument"
          aria-label={`Create alert for ${item.symbol}`}
        >
          <Bell className="w-3.5 h-3.5" />
        </button>
      )}

      {/* Remove from Watchlist */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onRemove();
        }}
        className="p-1 rounded text-zinc-500 hover:text-red-400 hover:bg-red-950/30 transition-colors ml-1"
        title="Remove from Watchlist"
        aria-label={`Remove ${item.symbol} from watchlist`}
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
