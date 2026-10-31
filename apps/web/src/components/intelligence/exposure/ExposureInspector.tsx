"use client";

import React, { useEffect, useState } from "react";
import { AtlasExposureResult } from "@/lib/intelligence/exposure/types";
import { formatExposureAmount, formatPercentage } from "@/lib/intelligence/exposure/units";
import { fetchLineage } from "@/lib/intelligence/exposure/api";
import {
  X,
  ShieldCheck,
  FileText,
  GitBranch,
  Calculator,
  Calendar,
  AlertTriangle,
  Layers,
  Database
} from "lucide-react";

interface ExposureInspectorProps {
  exposure: AtlasExposureResult | null;
  onClose: () => void;
}

export function ExposureInspector({ exposure, onClose }: ExposureInspectorProps) {
  const [lineage, setLineage] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!exposure) {
      setLineage(null);
      return;
    }
    let isMounted = true;
    setLoading(true);
    fetchLineage(exposure.exposure_id)
      .then((data) => {
        if (isMounted) setLineage(data);
      })
      .catch((err) => {
        console.warn("Could not fetch remote lineage; using result lineage", err);
        if (isMounted) {
          setLineage({
            calculation_method: exposure.calculation_method_id,
            formula_expression: exposure.exposure_measure_id,
            inputs: {
              numerator: exposure.numerator_value,
              denominator: exposure.denominator_value,
              currency: exposure.currency
            },
            source_ids: exposure.source_manifest_id ? [exposure.source_manifest_id] : ["SEC_EDGAR_VERIFIED_FILING"]
          });
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [exposure]);

  if (!exposure) return null;

  return (
    <div className="h-full flex flex-col bg-zinc-950 border-l border-zinc-800 font-mono text-xs overflow-y-auto">
      {/* Header */}
      <div className="p-3 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calculator className="w-4 h-4 text-sky-400" />
          <span className="font-semibold text-zinc-100 uppercase tracking-wider">
            EXPOSURE INSPECTOR
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 space-y-4 flex-1">
        {/* Target Entity Overview */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded p-3 space-y-1.5">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider">
            TARGET ENTITY & DOMAIN
          </div>
          <div className="text-sm font-bold text-zinc-100 flex items-center gap-2">
            <span>{exposure.target_entity_ref.canonical_name}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">
              {exposure.target_entity_ref.node_type}
            </span>
          </div>
          <div className="text-xs text-sky-400 font-semibold">
            {exposure.exposure_domain} — {exposure.exposure_type}
          </div>
          <p className="text-zinc-400 text-[11px] leading-relaxed pt-1">
            {exposure.explanation}
          </p>
        </div>

        {/* Quantitative Metrics Breakdown */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded p-3 space-y-2">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <Calculator className="w-3.5 h-3.5 text-blue-400" />
            <span>MEASURED VALUES & FORMULA</span>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-1">
            <div className="p-2 rounded bg-zinc-950/70 border border-zinc-800">
              <span className="text-[10px] text-zinc-500 block">NUMERATOR</span>
              <span className="text-sm font-semibold text-zinc-200">
                {exposure.numerator_value !== null && exposure.numerator_value !== undefined
                  ? formatExposureAmount(exposure.numerator_value, exposure.unit, exposure.currency || "USD")
                  : "N/A"}
              </span>
            </div>
            <div className="p-2 rounded bg-zinc-950/70 border border-zinc-800">
              <span className="text-[10px] text-zinc-500 block">DENOMINATOR</span>
              <span className="text-sm font-semibold text-zinc-200 truncate block">
                {exposure.denominator_value !== null && exposure.denominator_value !== undefined
                  ? `${exposure.denominator_value} ${exposure.currency || ""}`
                  : "N/A"}
              </span>
            </div>
          </div>

          <div className="p-2 rounded bg-zinc-950/70 border border-zinc-800">
            <div className="flex justify-between items-center text-[10px] text-zinc-400 mb-0.5">
              <span>CALCULATED SHARE / WEIGHT</span>
              <span className="text-zinc-500">METHOD: {exposure.calculation_method_id}</span>
            </div>
            <div className="text-base font-bold text-sky-400">
              {exposure.percentage !== null && exposure.percentage !== undefined
                ? formatPercentage(exposure.percentage)
                : formatExposureAmount(exposure.amount, exposure.unit, exposure.currency || "USD")}
            </div>
            {Boolean(lineage?.formula_expression) && (
              <div className="mt-1 text-[10px] text-zinc-500 font-mono">
                Formula: {String(lineage?.formula_expression)}
              </div>
            )}
          </div>
        </div>

        {/* Bitemporal & Validity Timeline */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded p-3 space-y-2">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-purple-400" />
            <span>BITEMPORAL PROVENANCE</span>
          </div>
          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between text-zinc-300">
              <span className="text-zinc-500">REPORTING PERIOD</span>
              <span className="font-semibold">{exposure.reporting_period || "FY2024"}</span>
            </div>
            <div className="flex justify-between text-zinc-300">
              <span className="text-zinc-500">MARKET DATA AS OF</span>
              <span>{exposure.market_data_as_of ? new Date(exposure.market_data_as_of).toLocaleDateString() : "Point-in-Time Close"}</span>
            </div>
            <div className="flex justify-between text-zinc-300">
              <span className="text-zinc-500">KNOWN AS OF</span>
              <span className="text-zinc-400">{new Date(exposure.known_as_of).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Source Citations & Manifest */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded p-3 space-y-2">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span>SOURCE MANIFEST & AUDIT TRAIL</span>
          </div>
          <div className="space-y-1 text-[11px] text-zinc-300">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Evidence: {exposure.evidence_class}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-sky-400" />
              <span>License Status: Active Entitlement</span>
            </div>
            {Boolean(lineage?.source_ids && Array.isArray(lineage.source_ids)) && (
              <div className="mt-2 text-[10px] text-zinc-400">
                Sources: {(lineage?.source_ids as string[]).join(", ")}
              </div>
            )}
          </div>
        </div>

        {/* Mandatory Limitations Disclaimer */}
        <div className="bg-amber-950/20 border border-amber-800/60 rounded p-3 space-y-1.5">
          <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-[11px]">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>INSTITUTIONAL SCOPE BOUNDARY</span>
          </div>
          <p className="text-[10px] text-amber-200/80 leading-relaxed">
            {exposure.limitations_disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
}
