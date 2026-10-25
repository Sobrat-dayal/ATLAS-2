"use client";

import { useState } from "react";
import Link from "next/link";
import { Badge } from "@/design-system";
import { RelatedSecurityItem } from "@/lib/companies/types";
import { AddToWatchlistModal } from "./AddToWatchlistModal";
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart2,
  BookmarkPlus,
  Layers,
  LineChart,
  Star,
} from "lucide-react";

export interface CompanySecuritiesTabProps {
  securities: RelatedSecurityItem[];
}

export function CompanySecuritiesTab({ securities }: CompanySecuritiesTabProps) {
  const [watchlistTarget, setWatchlistTarget] = useState<RelatedSecurityItem | null>(null);

  if (!securities || securities.length === 0) {
    return (
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-8 text-center">
        <Layers className="w-8 h-8 text-atlas-text-muted mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">
          No Verified Related Securities Available
        </h3>
        <p className="text-xs text-atlas-text-muted mt-1 max-w-md mx-auto">
          This corporate entity currently has no canonical listed equity securities, depositary receipts, or corporate bonds linked in the ATLAS Relationship Graph.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
              Issued Financial Instruments & Listings
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              {securities.length} {securities.length === 1 ? "Instrument" : "Instruments"}
            </Badge>
          </div>
          <span className="text-[11px] text-atlas-text-muted">Stage 23 Relationship Graph</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-default bg-atlas-surface-0/60 text-atlas-text-muted font-medium uppercase tracking-wider text-[11px]">
                <th className="px-4 py-2.5">Security / Identifier</th>
                <th className="px-3 py-2.5">Asset Class & Type</th>
                <th className="px-3 py-2.5">Share Class</th>
                <th className="px-3 py-2.5">Venue & Currency</th>
                <th className="px-3 py-2.5 text-right">Latest Measure</th>
                <th className="px-3 py-2.5 text-right">Price</th>
                <th className="px-3 py-2.5 text-right">Change</th>
                <th className="px-3 py-2.5">Status</th>
                <th className="px-4 py-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-sans">
              {securities.map((sec) => {
                const isBond = sec.asset_class === "bond";
                const marketsHref = isBond
                  ? `/markets/bonds?instrument=${encodeURIComponent(sec.instrument_entity_id)}`
                  : `/markets/equities?instrument=${encodeURIComponent(sec.instrument_entity_id)}`;

                const chartsHref = `/charts?instrument=${encodeURIComponent(sec.instrument_entity_id)}${
                  sec.symbol ? `&symbol=${encodeURIComponent(sec.symbol)}` : ""
                }`;

                const isUp = sec.change_direction === "up";
                const isDown = sec.change_direction === "down";

                return (
                  <tr
                    key={sec.instrument_entity_id}
                    className="hover:bg-atlas-surface-2/60 transition-colors group"
                  >
                    {/* Security Name & Symbol */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        {sec.is_primary_listing && (
                          <span title="Primary Reference Listing">
                            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500 shrink-0" />
                          </span>
                        )}
                        <span className="font-semibold text-atlas-text-primary text-sm font-mono">
                          {sec.symbol || "—"}
                        </span>
                      </div>
                      <div className="text-[11px] text-atlas-text-muted truncate max-w-xs mt-0.5" title={sec.display_name}>
                        {sec.display_name}
                      </div>
                      <div className="font-mono text-[9px] text-atlas-text-muted truncate max-w-xs">
                        ID: {sec.instrument_entity_id}
                      </div>
                    </td>

                    {/* Asset Class & Security Type */}
                    <td className="px-3 py-3">
                      <div className="font-medium text-atlas-text-secondary capitalize">
                        {sec.security_type.replace(/_/g, " ")}
                      </div>
                      <div className="font-mono text-[10px] text-atlas-text-muted uppercase">
                        {sec.asset_class}
                      </div>
                    </td>

                    {/* Share Class */}
                    <td className="px-3 py-3 font-mono text-atlas-text-secondary">
                      {sec.share_class_name || "—"}
                    </td>

                    {/* Venue & Currency */}
                    <td className="px-3 py-3">
                      <div className="font-medium text-atlas-text-primary font-mono">
                        {sec.exchange_or_venue || "OTC"}
                      </div>
                      <div className="font-mono text-[10px] text-atlas-text-muted">
                        {sec.currency}
                      </div>
                    </td>

                    {/* Latest Measure */}
                    <td className="px-3 py-3 text-right font-mono text-[11px] text-atlas-text-muted">
                      {sec.quote_measure || (isBond ? "Clean Price" : "Last")}
                    </td>

                    {/* Price */}
                    <td className="px-3 py-3 text-right font-mono font-medium text-atlas-text-primary text-sm">
                      {sec.is_quote_available && sec.latest_price ? (
                        sec.latest_price
                      ) : (
                        <span className="text-atlas-text-muted italic text-xs">Unavailable</span>
                      )}
                    </td>

                    {/* Change */}
                    <td className="px-3 py-3 text-right font-mono text-xs">
                      {sec.is_quote_available && sec.percentage_change ? (
                        <span
                          className={`inline-flex items-center gap-0.5 ${
                            isUp
                              ? "text-atlas-positive"
                              : isDown
                              ? "text-atlas-negative"
                              : "text-atlas-text-muted"
                          }`}
                        >
                          {isUp && <ArrowUpRight className="w-3.5 h-3.5" />}
                          {isDown && <ArrowDownRight className="w-3.5 h-3.5" />}
                          <span>{sec.percentage_change}</span>
                        </span>
                      ) : (
                        <span className="text-atlas-text-muted">—</span>
                      )}
                    </td>

                    {/* Status / Delay */}
                    <td className="px-3 py-3">
                      <span className="inline-flex items-center gap-1 font-mono text-[10px] text-atlas-text-muted capitalize">
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            sec.is_quote_available ? "bg-atlas-positive" : "bg-atlas-text-muted"
                          }`}
                        />
                        {sec.delay_status}
                      </span>
                    </td>

                    {/* Cross-Module Navigation Actions */}
                    <td className="px-4 py-3 text-right">
                      <div className="inline-flex items-center gap-1">
                        <Link
                          href={marketsHref}
                          className="px-2 py-1 text-[11px] font-medium border border-atlas-border-default rounded-xs text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-3 transition-colors inline-flex items-center gap-1"
                          title="Open Security in Markets"
                        >
                          <BarChart2 className="w-3 h-3" />
                          <span className="hidden sm:inline">Markets</span>
                        </Link>

                        <Link
                          href={chartsHref}
                          className="px-2 py-1 text-[11px] font-medium border border-atlas-border-default rounded-xs text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-3 transition-colors inline-flex items-center gap-1"
                          title="Open Security in Charts"
                        >
                          <LineChart className="w-3 h-3" />
                          <span className="hidden sm:inline">Charts</span>
                        </Link>

                        <button
                          type="button"
                          onClick={() => setWatchlistTarget(sec)}
                          className="px-2 py-1 text-[11px] font-medium border border-atlas-border-default rounded-xs text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-3 transition-colors inline-flex items-center gap-1 focus:outline-none"
                          title="Add Security to Watchlist"
                        >
                          <BookmarkPlus className="w-3 h-3" />
                          <span className="hidden md:inline">+ Watchlist</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {watchlistTarget && (
        <AddToWatchlistModal
          isOpen={Boolean(watchlistTarget)}
          onClose={() => setWatchlistTarget(null)}
          instrumentEntityId={watchlistTarget.instrument_entity_id}
          instrumentSymbol={watchlistTarget.symbol}
          instrumentName={watchlistTarget.display_name}
        />
      )}
    </div>
  );
}
