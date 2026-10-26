"use client";

import React from "react";
import {
  Building2,
  Cpu,
  Layers,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Truck,
  ArrowRight,
} from "lucide-react";
import { SupplyChainOverviewResponseDTO } from "@/lib/companies/supply-chain";

interface SupplyChainOverviewCardsProps {
  overview: SupplyChainOverviewResponseDTO | null;
  onSelectTab?: (tab: string) => void;
}

export function SupplyChainOverviewCards({ overview, onSelectTab }: SupplyChainOverviewCardsProps) {
  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      {/* 1. Direct Suppliers */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            Verified Upstream
          </span>
          <span className="font-mono text-[10px] bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded">
            Tier-1 & Tier-2
          </span>
        </div>
        <div className="mt-1">
          <div className="text-xl font-semibold text-atlas-text-primary">
            {overview.verified_tier_1_suppliers_count} Direct Suppliers
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            +{overview.tier_2_upstream_count} Verified Multi-Tier Precursors
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Foundry & Assemblies</span>
          {onSelectTab && (
            <button
              onClick={() => onSelectTab("suppliers")}
              className="text-blue-400 hover:text-blue-300 font-medium flex items-center gap-0.5"
            >
              View All <ArrowRight className="w-2.5 h-2.5" />
            </button>
          )}
        </div>
      </div>

      {/* 2. Direct Customers & Channels */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <Truck className="w-3.5 h-3.5 text-emerald-400" />
            Downstream Channels
          </span>
          <span className="font-mono text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded">
            Distribution
          </span>
        </div>
        <div className="mt-1">
          <div className="text-xl font-semibold text-atlas-text-primary">
            {overview.verified_tier_1_customers_count} Verified Channels
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            Carriers, Retail & Enterprise Resellers
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Directionality</span>
          <span className="font-mono text-emerald-400 text-[10px]">SUPPLIER → CUSTOMER</span>
        </div>
      </div>

      {/* 3. Disclosed Concentration Risks */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Disclosed Concentration
          </span>
          <span className="font-mono text-[10px] bg-amber-500/10 text-amber-400 px-1.5 py-0.5 rounded">
            SEC Form 10-K
          </span>
        </div>
        <div className="mt-1">
          <div className="text-sm font-semibold text-atlas-text-primary flex items-center gap-1.5">
            {overview.has_material_customer_concentration ? (
              <span className="text-amber-400">Material Customer Disclosed</span>
            ) : (
              <span className="text-atlas-text-secondary">No &gt;10% Customer Disclosed</span>
            )}
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            {overview.has_critical_single_source_suppliers
              ? "Critical single-source fabrication (Foundry)"
              : "Multiple qualified component suppliers"}
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Sole-Source Packaging</span>
          <span className="text-amber-400 font-medium">Disclosed in Item 1A</span>
        </div>
      </div>

      {/* 4. Traceable Source Coverage */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-atlas-accent" />
            Evidence & Lineage
          </span>
          <span className="font-mono text-[10px] bg-atlas-surface-subtle px-1.5 py-0.5 rounded text-atlas-text-secondary">
            100% Traceable
          </span>
        </div>
        <div className="mt-1">
          <div className="text-sm font-semibold text-atlas-text-primary">
            {overview.coverage.authorized_providers.join(", ")}
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            Latest Filing: {overview.latest_disclosure_date || "2024-11-01"}
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Jurisdictions</span>
          <span className="font-medium text-atlas-text-secondary">
            {overview.coverage.jurisdiction_coverage.slice(0, 3).join(", ")}
          </span>
        </div>
      </div>
    </div>
  );
}
