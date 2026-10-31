"use client";

import React from "react";
import { useRouter } from "next/navigation";
import {
  MapPin,
  Building2,
  ExternalLink,
  ShieldCheck,
  Globe,
  Layers,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { useCompanyFootprint } from "@/hooks/maps/corporate/useCompanyFootprint";
import { FACILITY_STATUS_STYLES, FACILITY_TYPE_STYLES } from "@/lib/maps/corporate/facilityStyles";

export interface CompanyFootprintTabProps {
  companyId: string;
}

export function CompanyFootprintTab({ companyId }: CompanyFootprintTabProps) {
  const router = useRouter();
  const { footprint, facilities, summary, loading, error } = useCompanyFootprint({
    initialCompanyId: companyId,
    initialIncludeSubsidiaries: true,
  });

  const handleOpenInMaps = () => {
    router.push(`/maps?company=${encodeURIComponent(companyId)}`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-zinc-500 gap-2 text-xs">
        <Loader2 className="w-5 h-5 animate-spin text-sky-400" />
        <span>Loading verified corporate geography footprint...</span>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="p-8 text-center bg-zinc-950 border border-zinc-800 rounded text-xs text-zinc-500 space-y-3">
        <MapPin className="w-8 h-8 text-zinc-700 mx-auto" />
        <div className="font-medium text-zinc-400">No verified facility records found for this company.</div>
        <p className="text-[11px] text-zinc-600 max-w-md mx-auto">
          Corporate geography requires explicit evidence from authorized filings, official corporate disclosures, or LEI records.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner with Direct Map Navigation */}
      <div className="p-4 bg-zinc-950 border border-zinc-800 rounded-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-sky-400" />
            <h2 className="text-sm font-bold text-zinc-100">
              Verified Corporate Geography & Operating Footprint
            </h2>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Traceable physical facilities, global headquarters, research centers, and subsidiary locations.
          </p>
        </div>

        <button
          type="button"
          onClick={handleOpenInMaps}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-semibold shadow transition-colors shrink-0"
        >
          <MapPin className="w-3.5 h-3.5" />
          <span>Explore on Interactive Map</span>
          <ExternalLink className="w-3 h-3 ml-0.5 opacity-80" />
        </button>
      </div>

      {/* 4 Metrics Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-sm">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Recorded Facilities
          </div>
          <div className="text-xl font-bold font-mono text-zinc-100 mt-0.5">
            {summary.distinct_facilities}
          </div>
          <div className="text-[10px] text-zinc-500 mt-1">
            {summary.total_facilities} documented sites
          </div>
        </div>

        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-sm">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Countries Represented
          </div>
          <div className="text-xl font-bold font-mono text-sky-400 mt-0.5">
            {summary.countries_count}
          </div>
          <div className="text-[10px] text-zinc-500 mt-1">Operating jurisdictions</div>
        </div>

        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-sm">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Direct / Subsidiary
          </div>
          <div className="text-base font-bold font-mono text-zinc-200 mt-1 flex items-center gap-1.5">
            <span className="text-emerald-400">{summary.direct_facilities_count}</span>
            <span className="text-zinc-600">/</span>
            <span className="text-indigo-400">{summary.subsidiary_facilities_count}</span>
          </div>
          <div className="text-[10px] text-zinc-500 mt-1">Direct vs Group Sub sites</div>
        </div>

        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-sm">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Data Quality & Evidence
          </div>
          <div className="text-base font-bold font-mono text-emerald-400 mt-1 flex items-center gap-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Verified Sources</span>
          </div>
          <div className="text-[10px] text-zinc-500 mt-1">
            {summary.source_coverage?.sources_count || 1} filing & disclosure manifests
          </div>
        </div>
      </div>

      {/* Facilities Table */}
      <div className="bg-zinc-950 border border-zinc-800 rounded-sm overflow-hidden">
        <div className="p-3 border-b border-zinc-800 bg-zinc-900/40 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-bold text-zinc-200 uppercase tracking-wider">
            <Layers className="w-3.5 h-3.5 text-sky-400" />
            <span>Recorded Facilities Directory ({facilities.length})</span>
          </div>
          <span className="text-[10px] text-zinc-500">Stage 132 Global Corporate Registry</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-zinc-900 border-b border-zinc-800 text-zinc-400 text-[11px]">
                <th className="p-3">Facility Name</th>
                <th className="p-3">Type</th>
                <th className="p-3">Status</th>
                <th className="p-3">Location</th>
                <th className="p-3 text-right">Coordinates</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {facilities.map((fac) => {
                const typeStyle = FACILITY_TYPE_STYLES[fac.facility_type];
                const statusStyle = FACILITY_STATUS_STYLES[fac.facility_status];
                return (
                  <tr key={fac.facility_id} className="hover:bg-zinc-900/30 transition-colors">
                    <td className="p-3 font-semibold text-zinc-200">
                      <div>{fac.canonical_name}</div>
                      {fac.address_text && (
                        <div className="text-[10px] text-zinc-500 font-mono mt-0.5">
                          {fac.address_text}
                        </div>
                      )}
                    </td>
                    <td className="p-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium border ${
                          typeStyle?.borderColor || "border-zinc-700"
                        } ${typeStyle?.textColor || "text-zinc-300"} bg-zinc-900`}
                      >
                        <span
                          className="w-1.5 h-1.5 rounded-full"
                          style={{ backgroundColor: typeStyle?.color || "#71717a" }}
                        />
                        <span>{typeStyle?.label || fac.facility_type}</span>
                      </span>
                    </td>
                    <td className="p-3">
                      <span
                        className={`inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-medium border ${
                          statusStyle?.border || "border-zinc-700"
                        } ${statusStyle?.bg || "bg-zinc-900"} ${statusStyle?.text || "text-zinc-300"}`}
                      >
                        {statusStyle?.label || fac.facility_status}
                      </span>
                    </td>
                    <td className="p-3 text-zinc-300">
                      <span>{fac.locality ? `${fac.locality}, ` : ""}</span>
                      <span className="font-semibold">{fac.country_code}</span>
                    </td>
                    <td className="p-3 text-right font-mono text-zinc-400 text-[11px]">
                      {fac.longitude != null && fac.latitude != null
                        ? `${fac.longitude.toFixed(4)}, ${fac.latitude.toFixed(4)}`
                        : "Unresolved"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

