"use client";

import React from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Globe,
  Database,
  Calendar,
  Layers,
  Info,
} from "lucide-react";
import { EconomicCoverageResponseDTO } from "@/lib/economics";

interface EconomicCoveragePanelProps {
  coverage: EconomicCoverageResponseDTO | null;
}

export function EconomicCoveragePanel({ coverage }: EconomicCoveragePanelProps) {
  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-4 mb-6">
      <div className="flex items-center gap-2 pb-3 border-b border-atlas-border-subtle mb-3">
        <Globe className="w-4 h-4 text-atlas-accent" />
        <h4 className="text-xs font-semibold text-atlas-text-primary">
          Verified Institutional Coverage & Macroeconomic Governance
        </h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs mb-4">
        {/* Coverage Scope */}
        <div className="p-3 bg-atlas-background/60 rounded border border-atlas-border-subtle/50">
          <div className="flex items-center gap-1.5 text-atlas-text-primary font-medium mb-1">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span>Sovereign Coverage Bounds</span>
          </div>
          <p className="text-[11px] text-atlas-text-muted leading-relaxed">
            Directly integrates verified sovereign statistical agencies and central banks across G6 major economies
            (US, Euro Area, China, India, Japan, United Kingdom). No synthetic proxy interpolation.
          </p>
        </div>

        {/* Vintage & Revision Integrity */}
        <div className="p-3 bg-atlas-background/60 rounded border border-atlas-border-subtle/50">
          <div className="flex items-center gap-1.5 text-atlas-text-primary font-medium mb-1">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>Revision Vintages & Point-in-Time</span>
          </div>
          <p className="text-[11px] text-atlas-text-muted leading-relaxed">
            Maintains multi-vintage revision tracking for major series (e.g. BEA Advance, Second, Third GDP estimates).
            Point-in-time query bounds prevent historical look-ahead information leakage.
          </p>
        </div>

        {/* Statistical Qualification */}
        <div className="p-3 bg-atlas-background/60 rounded border border-atlas-border-subtle/50">
          <div className="flex items-center gap-1.5 text-atlas-text-primary font-medium mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Exact Units & Transformation Registry</span>
          </div>
          <p className="text-[11px] text-atlas-text-muted leading-relaxed">
            Enforces strict differentiation between price levels (index points) and rates (%), real and nominal values,
            YoY and MoM, and annualized vs. non-annualized quarterly growth calculations.
          </p>
        </div>
      </div>

      {/* Disclaimers & Roadmap Boundary Note */}
      <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded text-[11px] text-atlas-text-muted">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-atlas-text-primary block mb-0.5">
              Roadmap Boundary & Institutional Notice (Stage 89 Economics V1):
            </span>
            Stage 89 owns the foundational global macroeconomic terminal, canonical indicator catalog, observation qualification,
            and historical series visualization. Future stages expand into dedicated Country Economics (Stage 90), Central Banks
            (Stage 91), Economic Calendar (Stage 92), and Macro Comparisons (Stage 93). Stage 89 strictly performs 0 LLM calls,
            0 trading actions, and avoids fabricated global aggregates.
          </div>
        </div>
      </div>
    </div>
  );
}
