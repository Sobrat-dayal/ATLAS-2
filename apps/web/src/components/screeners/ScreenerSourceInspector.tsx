"use client";

import React from "react";
import Link from "next/link";
import {
  Building,
  CheckCircle2,
  ExternalLink,
  Globe,
  Landmark,
  LineChart,
  ShieldCheck,
  X,
} from "lucide-react";
import { ScreenerResultRow } from "@/lib/screeners/types";

interface ScreenerSourceInspectorProps {
  row: ScreenerResultRow | null;
  onClose: () => void;
}

export function ScreenerSourceInspector({
  row,
  onClose,
}: ScreenerSourceInspectorProps) {
  if (!row) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-border bg-card shadow-2xl backdrop-blur">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-5 py-4 bg-muted/20">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-foreground">
              {row.ticker}
            </h2>
            <span className="rounded bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-[10px] font-mono font-medium text-primary uppercase">
              {row.security_type}
            </span>
          </div>
          <p className="text-xs text-muted-foreground truncate max-w-[280px]">
            {row.canonical_security_name}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs">
        {/* Navigation Shortcuts */}
        <div className="flex items-center gap-2">
          <Link
            href={`/charts?symbol=${encodeURIComponent(row.ticker)}`}
            className="flex-1 flex items-center justify-center gap-1.5 rounded-md border border-border bg-background py-2 text-xs font-medium text-foreground hover:bg-muted transition-colors"
          >
            <LineChart className="h-3.5 w-3.5 text-primary" />
            <span>Interactive Chart</span>
          </Link>
          <Link
            href={`/companies?id=${row.issuer_company_entity_id}`}
            className="flex-1 flex items-center justify-center gap-1.5 rounded-md border border-border bg-background py-2 text-xs font-medium text-foreground hover:bg-muted transition-colors"
          >
            <Building className="h-3.5 w-3.5 text-primary" />
            <span>Company Profile</span>
          </Link>
        </div>

        {/* Canonical Identity Card */}
        <div className="rounded-lg border border-border/80 bg-background/50 p-3.5 space-y-2.5">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5 text-primary" />
            <span>Canonical Identity</span>
          </div>
          <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
            <div>
              <span className="text-muted-foreground block">Instrument UUID:</span>
              <span className="text-foreground truncate block" title={row.instrument_entity_id}>
                {row.instrument_entity_id.slice(0, 16)}...
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block">Listing ID:</span>
              <span className="text-foreground truncate block" title={row.listing_id}>
                {row.listing_id.slice(0, 16)}...
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block">Issuer Entity UUID:</span>
              <span className="text-foreground truncate block" title={row.issuer_company_entity_id}>
                {row.issuer_company_entity_id.slice(0, 16)}...
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block">Listing Status:</span>
              <span className="font-semibold text-emerald-500 uppercase">
                {row.listing_status}
              </span>
            </div>
          </div>
        </div>

        {/* Venue & Classification */}
        <div className="rounded-lg border border-border/80 bg-background/50 p-3.5 space-y-2.5">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            <Landmark className="h-3.5 w-3.5 text-primary" />
            <span>Exchange & Classification</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground block text-[11px]">Exchange:</span>
              <span className="font-medium text-foreground">
                {row.exchange_name} ({row.exchange_mic})
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block text-[11px]">Trading Currency:</span>
              <span className="font-mono font-medium text-foreground">
                {row.currency}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block text-[11px]">Sector:</span>
              <span className="font-medium text-foreground">
                {row.sector ?? "—"}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block text-[11px]">Industry:</span>
              <span className="font-medium text-foreground">
                {row.industry ?? "—"}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block text-[11px]">Market Country:</span>
              <span className="font-medium text-foreground">
                {row.listing_country_code}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground block text-[11px]">Issuer Domicile:</span>
              <span className="font-medium text-foreground">
                {row.issuer_country_code}
              </span>
            </div>
          </div>
        </div>

        {/* Metric Cells Provenance Table */}
        <div className="space-y-2">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Source Provenance & Observation Periods
          </div>
          <div className="divide-y divide-border/40 rounded-lg border border-border/80 bg-background/50 overflow-hidden">
            {Object.entries(row.metrics).map(([metricKey, cell]) => (
              <div key={metricKey} className="flex items-center justify-between p-2.5 hover:bg-muted/30">
                <div>
                  <div className="font-medium text-foreground capitalize">
                    {metricKey.replace(/_/g, " ")}
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    {cell.observation_period && (
                      <span className="font-mono">{cell.observation_period}</span>
                    )}
                    {cell.provider && (
                      <span>Source: {cell.provider}</span>
                    )}
                    {cell.freshness && (
                      <span className="text-emerald-500 uppercase">{cell.freshness}</span>
                    )}
                  </div>
                </div>
                <div className="font-mono font-semibold text-right text-xs">
                  {cell.display_value}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
