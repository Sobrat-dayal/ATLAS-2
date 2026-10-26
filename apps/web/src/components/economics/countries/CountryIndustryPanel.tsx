"use client";

import React from "react";
import {
  Factory,
  ShoppingBag,
  Home,
  Gauge,
  Smile,
  Briefcase,
  Info,
} from "lucide-react";
import { CountryIndustrySummaryDTO } from "@/lib/economics/countries";

interface CountryIndustryPanelProps {
  industry: CountryIndustrySummaryDTO | null;
}

export function CountryIndustryPanel({ industry }: CountryIndustryPanelProps) {
  if (!industry) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No industrial activity, retail sales, or sentiment indicators available for this country.
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  return (
    <div className="space-y-4">
      {/* Industry Header Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Industrial Activity, Retail Sales & Business Sentiment
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-blue-400 border border-atlas-border-subtle">
                {industry.reference_period}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Real economy indicators tracking factory output, consumer spending volumes, and construction permits.
            </p>
          </div>
        </div>

        {/* Industrial & Retail Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Industrial Production */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Factory className="w-3.5 h-3.5 text-blue-400" />
                Industrial Production
              </span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatPct(industry.industrial_production_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Index: {industry.industrial_production_index ? `${industry.industrial_production_index.toFixed(1)} pts` : "—"}
            </div>
          </div>

          {/* Card 2: Manufacturing Output */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-purple-400" />
                Manufacturing Output
              </span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatPct(industry.manufacturing_output_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Factory production volume
            </div>
          </div>

          {/* Card 3: Retail Sales Nominal */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <ShoppingBag className="w-3.5 h-3.5 text-emerald-400" />
                Retail Sales (Nominal)
              </span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {formatPct(industry.retail_sales_nominal_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Consumer demand value
            </div>
          </div>

          {/* Card 4: Capacity Utilization */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-amber-400" />
                Capacity Utilization
              </span>
              <span className="font-mono text-[10px]">%</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {industry.capacity_utilization_pct !== null && industry.capacity_utilization_pct !== undefined
                ? `${industry.capacity_utilization_pct.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Industrial operating capacity
            </div>
          </div>
        </div>
      </div>

      {/* Housing & Sentiment Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Housing & Construction */}
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Home className="w-4 h-4 text-cyan-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Housing & Construction Indicators
            </h4>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Housing Starts (Annualized):</span>
              <span className="font-bold text-atlas-text-primary">
                {industry.housing_starts_annualized_thousands !== null && industry.housing_starts_annualized_thousands !== undefined
                  ? `${industry.housing_starts_annualized_thousands.toLocaleString()}k units`
                  : "—"}
              </span>
            </div>
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Building Permits (Annualized):</span>
              <span className="font-bold text-atlas-text-primary">
                {industry.building_permits_annualized_thousands !== null && industry.building_permits_annualized_thousands !== undefined
                  ? `${industry.building_permits_annualized_thousands.toLocaleString()}k units`
                  : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Sentiment Surveys */}
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Smile className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Consumer & Business Confidence Surveys
            </h4>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Consumer Confidence Index:</span>
              <span className="font-bold text-atlas-text-primary">
                {industry.consumer_confidence_index !== null && industry.consumer_confidence_index !== undefined
                  ? `${industry.consumer_confidence_index.toFixed(1)} pts`
                  : "—"}
              </span>
            </div>
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Business Confidence Index:</span>
              <span className="font-bold text-atlas-text-primary">
                {industry.business_confidence_index !== null && industry.business_confidence_index !== undefined
                  ? `${industry.business_confidence_index.toFixed(1)} pts`
                  : "—"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {industry.notes && (
        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded-lg text-[11px] text-atlas-text-muted flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
          <span>{industry.notes}</span>
        </div>
      )}
    </div>
  );
}
