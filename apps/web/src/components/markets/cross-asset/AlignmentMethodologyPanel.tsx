"use client";

import React from "react";
import { AlertCircle, BookOpen, Clock, ShieldCheck, X } from "lucide-react";

interface AlignmentMethodologyPanelProps {
  onClose: () => void;
}

export function AlignmentMethodologyPanel({
  onClose,
}: AlignmentMethodologyPanelProps) {
  return (
    <div className="p-4 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] space-y-3.5 text-xs text-[var(--atlas-text-secondary)]">
      <div className="flex items-center justify-between pb-2 border-b border-[var(--atlas-border-subtle)]">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-bold text-[var(--atlas-text-primary)]">
            Institutional Cross-Asset Methodology & Financial Integrity Disclosures
          </h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)]"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Core Invariant */}
        <div className="p-3 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)] space-y-1.5">
          <div className="font-semibold text-xs text-[var(--atlas-text-primary)] flex items-center gap-1.5 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>NATIVE VS ALIGNED MODES</span>
          </div>
          <p className="text-[11px] leading-relaxed">
            Displaying different asset classes side by side does not make their numerical
            measurements directly comparable. <strong>Native Overview</strong> preserves authentic
            market conventions (equity returns, FX spot rates, bond yields in bps, futures settlement).{" "}
            <strong>Aligned Performance</strong> evaluates strict common UTC windows.
          </p>
        </div>

        {/* Bond Yield Invariant */}
        <div className="p-3 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)] space-y-1.5">
          <div className="font-semibold text-xs text-[var(--atlas-text-primary)] flex items-center gap-1.5 font-mono">
            <AlertCircle className="w-3.5 h-3.5 text-purple-400" />
            <span>FIXED INCOME CONVENTIONS</span>
          </div>
          <p className="text-[11px] leading-relaxed">
            A government bond yield movement (e.g. from 4.00% to 4.25% = +25 basis points) is not a
            percentage price return. In Aligned Mode, series with yield-only observations are
            truthfully excluded with <code>UNSUPPORTED_METRIC</code> rather than fabricating a fake
            price return.
          </p>
        </div>

        {/* Temporal Alignment & No Look-Ahead */}
        <div className="p-3 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)] space-y-1.5">
          <div className="font-semibold text-xs text-[var(--atlas-text-primary)] flex items-center gap-1.5 font-mono">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>ZERO LOOK-AHEAD SAFEGUARDS</span>
          </div>
          <p className="text-[11px] leading-relaxed">
            Start reference observations must have occurred strictly at or before the requested
            window start (effective start ≤ requested start). If observation latency exceeds the
            maximum tolerance (7,200 seconds), the instrument is safely excluded with{" "}
            <code>WINDOW_MISALIGNED</code>.
          </p>
        </div>
      </div>

      <div className="p-2.5 rounded bg-zinc-900/40 border border-zinc-800 text-[11px] font-mono text-[var(--atlas-text-tertiary)] flex flex-wrap items-center justify-between gap-2">
        <span>Formula: Return % = ((End Price - Start Price) / Start Price) × 100</span>
        <span>Currencies: Local Quote Currency • Proxies Disclosed</span>
      </div>
    </div>
  );
}
