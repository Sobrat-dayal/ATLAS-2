import React from "react";
import { ExternalLink, Info, ShieldCheck, X } from "lucide-react";
import { WatchlistRowCellValue } from "@/lib/watchlists/columns/types";

interface EnrichmentDetailsPopoverProps {
  label: string;
  columnId: string;
  cell: WatchlistRowCellValue;
  isOpen: boolean;
  onClose: () => void;
  position?: { x: number; y: number };
}

export function EnrichmentDetailsPopover({
  label,
  columnId,
  cell,
  isOpen,
  onClose,
  position,
}: EnrichmentDetailsPopoverProps) {
  if (!isOpen) return null;

  const style: React.CSSProperties = position
    ? {
        position: "fixed",
        left: `${Math.min(position.x, window.innerWidth - 320)}px`,
        top: `${Math.min(position.y + 10, window.innerHeight - 240)}px`,
        zIndex: 60,
      }
    : { position: "relative" };

  const isFundamental = columnId.startsWith("fundamentals.");
  const isValuation = columnId.startsWith("valuation.");
  const isTechnical = columnId.startsWith("technical.");
  const isEvent = columnId.startsWith("events.");
  const isEarnings = columnId.startsWith("earnings.");
  const isNews = columnId.startsWith("news.");

  return (
    <div
      style={style}
      className="w-72 rounded-lg border border-zinc-800 bg-zinc-950 p-3 shadow-2xl text-xs text-zinc-200 animate-in fade-in zoom-in-95 duration-100 select-none"
      onClick={(e) => e.stopPropagation()}
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800/80 mb-2.5">
        <div className="flex items-center gap-1.5 font-medium text-zinc-100">
          <Info className="w-3.5 h-3.5 text-sky-400 shrink-0" />
          <span className="truncate">{label}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
            {cell.status}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="p-0.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Close popover"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Metadata Key-Value pairs */}
      <div className="space-y-1.5 font-mono text-[11px]">
        {/* Value and unit */}
        <div className="flex justify-between items-center text-zinc-400">
          <span>Value:</span>
          <span className="text-zinc-100 font-semibold tabular-nums">
            {cell.value !== null && cell.value !== undefined ? String(cell.value) : "—"}
            {cell.unit ? ` ${cell.unit}` : ""}
          </span>
        </div>

        {/* Fundamentals context */}
        {isFundamental && (
          <>
            {cell.fiscal_period && (
              <div className="flex justify-between text-zinc-400">
                <span>Fiscal Period:</span>
                <span className="text-zinc-200">{cell.fiscal_period}</span>
              </div>
            )}
            {cell.period_end_date && (
              <div className="flex justify-between text-zinc-400">
                <span>Period Ended:</span>
                <span className="text-zinc-200">{cell.period_end_date}</span>
              </div>
            )}
            {cell.currency && (
              <div className="flex justify-between text-zinc-400">
                <span>Currency:</span>
                <span className="text-zinc-200">{cell.currency}</span>
              </div>
            )}
          </>
        )}

        {/* Valuation context */}
        {isValuation && (
          <>
            {cell.methodology_id && (
              <div className="flex justify-between text-zinc-400">
                <span>Methodology:</span>
                <span className="text-zinc-200 text-[10px] truncate max-w-[150px]">
                  {cell.methodology_id}
                </span>
              </div>
            )}
            {cell.fiscal_period && (
              <div className="flex justify-between text-zinc-400">
                <span>EPS Period:</span>
                <span className="text-zinc-200">{cell.fiscal_period}</span>
              </div>
            )}
          </>
        )}

        {/* Technical context */}
        {isTechnical && (
          <>
            <div className="flex justify-between text-zinc-400">
              <span>Interval:</span>
              <span className="text-zinc-200">1D (Finalized)</span>
            </div>
            <div className="flex justify-between text-zinc-400">
              <span>Engine:</span>
              <span className="text-zinc-200">TA-Lib v0.8.2</span>
            </div>
            {cell.observation_time && (
              <div className="flex justify-between text-zinc-400">
                <span>As of Bar:</span>
                <span className="text-zinc-200 text-[10px]">
                  {String(cell.observation_time).slice(0, 10)}
                </span>
              </div>
            )}
          </>
        )}

        {/* Events context */}
        {isEvent && (
          <>
            {cell.event_status && (
              <div className="flex justify-between text-zinc-400">
                <span>Status:</span>
                <span
                  className={
                    cell.event_status === "CONFIRMED"
                      ? "text-emerald-400 font-medium"
                      : "text-amber-400"
                  }
                >
                  {cell.event_status}
                </span>
              </div>
            )}
          </>
        )}

        {/* Earnings context */}
        {isEarnings && (
          <>
            {cell.fiscal_period && (
              <div className="flex justify-between text-zinc-400">
                <span>Period:</span>
                <span className="text-zinc-200">{cell.fiscal_period}</span>
              </div>
            )}
          </>
        )}

        {/* News context */}
        {isNews && (
          <>
            {cell.publisher && (
              <div className="flex justify-between text-zinc-400">
                <span>Publisher:</span>
                <span className="text-zinc-200 truncate max-w-[150px]">{cell.publisher}</span>
              </div>
            )}
            {cell.publication_time && (
              <div className="flex justify-between text-zinc-400">
                <span>Published:</span>
                <span className="text-zinc-200 text-[10px]">
                  {new Date(cell.publication_time).toLocaleString([], {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            )}
          </>
        )}

        {/* Provenance source */}
        {cell.source_id && (
          <div className="flex justify-between text-zinc-400 pt-1 border-t border-zinc-900">
            <span>Verified Source:</span>
            <span className="text-zinc-300 font-medium">{cell.source_id}</span>
          </div>
        )}

        {/* Reason / error details if unavailable */}
        {cell.reason && cell.status !== "AVAILABLE" && (
          <div className="pt-1.5 text-zinc-400 text-[10px] font-sans leading-relaxed border-t border-zinc-900">
            <span className="text-zinc-500 block mb-0.5 font-mono">Qualification note:</span>
            {cell.reason}
          </div>
        )}
      </div>

      {/* Verified Document URL link */}
      {cell.url && (
        <div className="mt-2.5 pt-2 border-t border-zinc-800/80 flex items-center justify-between">
          <a
            href={cell.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] text-sky-400 hover:text-sky-300 hover:underline"
          >
            <span>Open Verified Article</span>
            <ExternalLink className="w-3 h-3" />
          </a>
          <span title="Canonical Entitlement Verified">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          </span>
        </div>
      )}
    </div>
  );
}
