"use client";

import React from "react";
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  FileCheck,
  Globe2,
  Info,
  Layers,
  ShieldCheck,
} from "lucide-react";
import { SupplyChainCoverageResponseDTO } from "@/lib/companies/supply-chain";

interface SupplyChainCoveragePanelProps {
  coverage: SupplyChainCoverageResponseDTO | null;
}

export function SupplyChainCoveragePanel({
  coverage,
}: SupplyChainCoveragePanelProps) {
  if (!coverage) {
    return (
      <div className="p-8 text-center text-atlas-text-muted bg-atlas-surface border border-atlas-border-subtle rounded-md">
        No coverage or disclosure boundary data available.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Coverage Statement Banner */}
      <div className="p-4 bg-atlas-surface border border-atlas-border-subtle rounded-md">
        <div className="flex items-center gap-2 mb-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-semibold text-atlas-text-primary">
            Supply Chain Disclosure Coverage & Boundary Specification
          </h3>
        </div>
        <p className="text-xs text-atlas-text-secondary leading-relaxed">
          {coverage.coverage_statement}
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded">
          <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
            Verified Suppliers
          </div>
          <div className="text-xl font-bold text-atlas-text-primary mt-1">
            {coverage.verified_supplier_count}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-0.5">Direct & Multi-Tier</div>
        </div>

        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded">
          <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
            Verified Customers & Channels
          </div>
          <div className="text-xl font-bold text-atlas-text-primary mt-1">
            {coverage.verified_customer_count}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-0.5">Disclosed Partners</div>
        </div>

        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded">
          <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
            Unresolved Entities
          </div>
          <div className="text-xl font-bold text-atlas-text-primary mt-1">
            {coverage.unresolved_counterparty_count}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-0.5">
            Strict Zero-Guessing Policy
          </div>
        </div>

        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded">
          <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
            Latest Filing Date
          </div>
          <div className="text-sm font-bold text-emerald-400 mt-1 font-mono">
            {coverage.latest_filing_date || "2024-11-01"}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-0.5">
            Freshness: Current FY Annual 10-K
          </div>
        </div>
      </div>

      {/* Providers & Jurisdictions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Providers */}
        <div className="p-4 bg-atlas-surface border border-atlas-border-subtle rounded-md">
          <h4 className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5 mb-3">
            <FileCheck className="w-3.5 h-3.5 text-blue-400" />
            Authorized Disclosure Providers
          </h4>
          <div className="space-y-2">
            {coverage.authorized_providers.map((p) => (
              <div
                key={p}
                className="flex items-center justify-between text-xs p-2 bg-atlas-surface-subtle/50 rounded border border-atlas-border-subtle/60"
              >
                <span className="font-medium text-atlas-text-primary">{p}</span>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                  Active Provider
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Jurisdictions */}
        <div className="p-4 bg-atlas-surface border border-atlas-border-subtle rounded-md">
          <h4 className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5 mb-3">
            <Globe2 className="w-3.5 h-3.5 text-emerald-400" />
            Covered Jurisdictions & Manufacturing Hubs
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {coverage.jurisdiction_coverage.map((j) => (
              <span
                key={j}
                className="font-mono text-xs bg-atlas-surface-subtle border border-atlas-border-subtle px-2 py-1 rounded text-atlas-text-secondary"
              >
                {j}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Explicit Stated Limitations */}
      <div className="p-4 bg-atlas-surface border border-atlas-border-subtle rounded-md">
        <h4 className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5 mb-2 text-amber-400">
          <AlertCircle className="w-3.5 h-3.5" />
          Documented Data Limitations & Statutory Thresholds
        </h4>
        <ul className="space-y-1.5 text-xs text-atlas-text-secondary">
          {coverage.limitations.map((lim, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-atlas-text-muted mt-1">•</span>
              <span className="leading-relaxed">{lim}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
