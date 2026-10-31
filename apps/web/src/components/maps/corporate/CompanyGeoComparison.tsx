"use client";

import React, { useEffect, useState } from "react";
import { X, ArrowRightLeft, Building2, Globe, Layers, AlertCircle, Loader2 } from "lucide-react";
import { compareCompanyFootprintsApi, searchMappedCompanies } from "@/lib/maps/corporate/api";
import { CompanyComparisonResult, MappedCompanySearchResult } from "@/lib/maps/corporate/types";
import { FACILITY_TYPE_STYLES } from "@/lib/maps/corporate/facilityStyles";

interface CompanyGeoComparisonProps {
  initialCompanyAId: string;
  onClose: () => void;
}

export function CompanyGeoComparison({ initialCompanyAId, onClose }: CompanyGeoComparisonProps) {
  const [companies, setCompanies] = useState<MappedCompanySearchResult[]>([]);
  const [companyAId, setCompanyAId] = useState<string>(initialCompanyAId);
  const [companyBId, setCompanyBId] = useState<string>("");
  const [comparison, setComparison] = useState<CompanyComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    searchMappedCompanies().then((res) => {
      setCompanies(res);
      // Auto-select a different company if available
      const alt = res.find((c) => c.entity_id !== initialCompanyAId);
      if (alt) setCompanyBId(alt.entity_id);
    });
  }, [initialCompanyAId]);

  useEffect(() => {
    if (!companyAId || !companyBId || companyAId === companyBId) {
      setComparison(null);
      return;
    }

    setLoading(true);
    setError(null);
    compareCompanyFootprintsApi(companyAId, companyBId, true)
      .then((data) => setComparison(data))
      .catch((err: any) => setError(err?.message || "Comparison failed"))
      .finally(() => setLoading(false));
  }, [companyAId, companyBId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs">
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl text-xs text-zinc-300 overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <ArrowRightLeft className="w-4 h-4 text-sky-400" />
            <div>
              <h3 className="font-bold text-zinc-100 text-sm">Company Footprint Comparison</h3>
              <p className="text-[10px] text-zinc-500">Cross-company verified corporate geography analysis</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Company Selectors */}
        <div className="p-4 bg-zinc-900/40 border-b border-zinc-800 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1">
              Company A
            </label>
            <select
              value={companyAId}
              onChange={(e) => setCompanyAId(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-sky-500/50"
            >
              {companies.map((c) => (
                <option key={c.entity_id} value={c.entity_id}>
                  {c.canonical_name} ({c.tickers?.[0] || c.entity_id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1">
              Company B
            </label>
            <select
              value={companyBId}
              onChange={(e) => setCompanyBId(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-sky-500/50"
            >
              {companies.map((c) => (
                <option key={c.entity_id} value={c.entity_id}>
                  {c.canonical_name} ({c.tickers?.[0] || c.entity_id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Comparison Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {loading ? (
            <div className="p-8 flex items-center justify-center gap-2 text-zinc-500">
              <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
              <span>Comparing corporate footprints...</span>
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-950/20 border border-rose-900/30 rounded text-rose-400 text-center">
              {error}
            </div>
          ) : comparison ? (
            <>
              {/* Top Summary Metrics Comparison */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-zinc-900/70 border border-zinc-800 rounded space-y-2">
                  <div className="font-bold text-zinc-100 border-b border-zinc-800 pb-1">
                    {comparison.company_a.canonical_name}
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-500">Distinct Facilities:</span>
                    <span className="font-mono font-bold text-zinc-100">
                      {comparison.company_a.distinct_facilities}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-500">Countries Represented:</span>
                    <span className="font-mono font-bold text-sky-400">
                      {comparison.company_a.countries_count}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-500">Direct / Subsidiary:</span>
                    <span className="font-mono text-zinc-300">
                      {comparison.company_a.direct_facilities_count} / {comparison.company_a.subsidiary_facilities_count}
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-zinc-900/70 border border-zinc-800 rounded space-y-2">
                  <div className="font-bold text-zinc-100 border-b border-zinc-800 pb-1">
                    {comparison.company_b.canonical_name}
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-500">Distinct Facilities:</span>
                    <span className="font-mono font-bold text-zinc-100">
                      {comparison.company_b.distinct_facilities}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-500">Countries Represented:</span>
                    <span className="font-mono font-bold text-sky-400">
                      {comparison.company_b.countries_count}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-500">Direct / Subsidiary:</span>
                    <span className="font-mono text-zinc-300">
                      {comparison.company_b.direct_facilities_count} / {comparison.company_b.subsidiary_facilities_count}
                    </span>
                  </div>
                </div>
              </div>

              {/* Geographic Footprint Distribution Table */}
              <div className="space-y-2">
                <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold flex items-center gap-1.5">
                  <Layers className="w-3 h-3 text-sky-400" />
                  <span>Facility Types Side-by-Side</span>
                </div>
                <div className="border border-zinc-800 rounded overflow-hidden">
                  <table className="w-full text-left border-collapse text-[11px]">
                    <thead>
                      <tr className="bg-zinc-900 border-b border-zinc-800 text-zinc-400">
                        <th className="p-2">Facility Type</th>
                        <th className="p-2 text-right">{comparison.company_a.canonical_name}</th>
                        <th className="p-2 text-right">{comparison.company_b.canonical_name}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/60">
                      {Object.entries(comparison.type_comparison).map(([fType, counts]) => {
                        const style = FACILITY_TYPE_STYLES[fType as keyof typeof FACILITY_TYPE_STYLES];
                        const countA = counts[comparison.company_a.company_id] || 0;
                        const countB = counts[comparison.company_b.company_id] || 0;
                        return (
                          <tr key={fType} className="hover:bg-zinc-900/40">
                            <td className="p-2 flex items-center gap-1.5">
                              <span
                                className="w-2 h-2 rounded-full shrink-0"
                                style={{ backgroundColor: style?.color || "#71717a" }}
                              />
                              <span>{style?.label || fType}</span>
                            </td>
                            <td className="p-2 text-right font-mono font-semibold text-zinc-200">
                              {countA}
                            </td>
                            <td className="p-2 text-right font-mono font-semibold text-zinc-200">
                              {countB}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="p-2.5 bg-zinc-900/50 border border-zinc-800 rounded flex items-start gap-2 text-[10px] text-zinc-400">
                <AlertCircle className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                <span>
                  Comparison reflects currently recorded, verified corporate records. Incomplete source disclosures do not prove lesser worldwide operational presence.
                </span>
              </div>
            </>
          ) : (
            <div className="p-8 text-center text-zinc-500">
              Select two companies to compare their geographic presence.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-zinc-800 bg-zinc-900/60 flex items-center justify-between text-[10px] text-zinc-500">
          <span>Stage 132 Company Comparison Engine</span>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

