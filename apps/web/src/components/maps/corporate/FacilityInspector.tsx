"use client";

import React, { useState } from "react";
import {
  Building2,
  MapPin,
  FileText,
  Clock,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  X,
  Compass,
  Building,
  UserCheck,
} from "lucide-react";
import { CorporateFacility } from "@/lib/maps/corporate/types";
import {
  FACILITY_STATUS_STYLES,
  FACILITY_TYPE_STYLES,
  PRECISION_CLASS_INFO,
} from "@/lib/maps/corporate/facilityStyles";
import { FacilityEvidenceViewer } from "./FacilityEvidenceViewer";
import { FacilityHistory } from "./FacilityHistory";
import { useRouter } from "next/navigation";

interface FacilityInspectorProps {
  facility: CorporateFacility | null;
  onClose: () => void;
  className?: string;
}

export function FacilityInspector({ facility, onClose, className = "" }: FacilityInspectorProps) {
  const router = useRouter();
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  if (!facility) return null;

  const typeStyle = FACILITY_TYPE_STYLES[facility.facility_type];
  const statusStyle = FACILITY_STATUS_STYLES[facility.facility_status];
  const precisionInfo = PRECISION_CLASS_INFO[facility.precision_class];

  // Distinguish owners and operators
  const ownerLinks = facility.links.filter((l) => l.relationship_type === "OWNED_BY");
  const operatorLinks = facility.links.filter((l) => l.relationship_type === "OPERATED_BY");
  const hqLinks = facility.links.filter(
    (l) => l.relationship_type === "HEADQUARTERS_OF" || l.relationship_type === "REGISTERED_ADDRESS_OF"
  );
  const tenantLinks = facility.links.filter(
    (l) => l.relationship_type === "LEASED_BY" || l.relationship_type === "OCCUPIED_BY"
  );

  return (
    <div
      className={`flex flex-col h-full bg-zinc-950 border-l border-zinc-800 text-xs text-zinc-300 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="p-3 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/50 shrink-0">
        <div className="flex items-center gap-1.5 font-bold text-zinc-100 uppercase tracking-wider text-[11px]">
          <Building2 className="w-3.5 h-3.5 text-sky-400" />
          <span>Facility Inspector</span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-200 transition-colors"
          title="Close Inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Main Details Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Facility Name & Badges */}
        <div>
          <h2 className="text-sm font-bold text-zinc-100 leading-snug">{facility.canonical_name}</h2>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {/* Facility Type Badge */}
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium border ${
                typeStyle?.borderColor || "border-zinc-700"
              } ${typeStyle?.textColor || "text-zinc-300"} bg-zinc-900`}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: typeStyle?.color || "#71717a" }}
              />
              <span>{typeStyle?.label || facility.facility_type}</span>
            </span>

            {/* Operational Status Badge */}
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium border ${
                statusStyle?.border || "border-zinc-700"
              } ${statusStyle?.bg || "bg-zinc-900"} ${statusStyle?.text || "text-zinc-300"}`}
            >
              <span>{statusStyle?.label || facility.facility_status}</span>
            </span>

            {/* Precision Badge */}
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium border ${
                precisionInfo?.badge || "text-zinc-400 border-zinc-700 bg-zinc-900"
              }`}
              title={precisionInfo?.description}
            >
              <Compass className="w-2.5 h-2.5" />
              <span>{precisionInfo?.label || facility.precision_class}</span>
            </span>
          </div>
        </div>

        {/* Corporate Roles: Owner vs Operator Distinction */}
        <div className="p-3 bg-zinc-900/50 rounded border border-zinc-800/80 space-y-2">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold border-b border-zinc-800 pb-1 flex items-center gap-1.5">
            <UserCheck className="w-3 h-3 text-sky-400" />
            <span>Corporate Roles & Operation</span>
          </div>

          {ownerLinks.length > 0 && (
            <div>
              <div className="text-[10px] text-zinc-400 font-semibold">Property Owner:</div>
              {ownerLinks.map((ol) => (
                <div key={ol.link_id} className="text-zinc-200 text-xs font-medium">
                  {ol.role_description || ol.legal_entity_id}
                </div>
              ))}
            </div>
          )}

          {operatorLinks.length > 0 && (
            <div>
              <div className="text-[10px] text-zinc-400 font-semibold">Operating Entity:</div>
              {operatorLinks.map((op) => (
                <div key={op.link_id} className="text-zinc-200 text-xs font-medium">
                  {op.role_description || op.legal_entity_id}
                </div>
              ))}
            </div>
          )}

          {hqLinks.length > 0 && (
            <div>
              <div className="text-[10px] text-zinc-400 font-semibold">Headquarters Role:</div>
              {hqLinks.map((hq) => (
                <div key={hq.link_id} className="text-zinc-200 text-xs font-medium">
                  {hq.role_description || "Corporate Headquarters Seat"}
                </div>
              ))}
            </div>
          )}

          {tenantLinks.length > 0 && (
            <div>
              <div className="text-[10px] text-zinc-400 font-semibold">Tenant / Lessee:</div>
              {tenantLinks.map((tl) => (
                <div key={tl.link_id} className="text-zinc-200 text-xs font-medium">
                  {tl.role_description || tl.legal_entity_id}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Geographic Coordinates & Location */}
        <div className="p-3 bg-zinc-900/50 rounded border border-zinc-800/80 space-y-2">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold border-b border-zinc-800 pb-1 flex items-center gap-1.5">
            <MapPin className="w-3 h-3 text-sky-400" />
            <span>Physical Location</span>
          </div>

          {facility.address_text && (
            <div>
              <div className="text-[10px] text-zinc-400">Street Address:</div>
              <div className="text-zinc-200 font-mono text-[11px] mt-0.5">{facility.address_text}</div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div>
              <div className="text-[10px] text-zinc-400">Locality:</div>
              <div className="text-zinc-200">{facility.locality || "—"}</div>
            </div>
            <div>
              <div className="text-[10px] text-zinc-400">Country:</div>
              <div className="text-zinc-200">{facility.country_code}</div>
            </div>
          </div>

          <div className="pt-1 border-t border-zinc-800/60 flex items-center justify-between text-[10px] font-mono text-zinc-400">
            <span>Coordinates (WGS84):</span>
            <span className="text-zinc-200">
              {facility.longitude !== null && facility.latitude !== null
                ? `${facility.longitude.toFixed(4)}, ${facility.latitude.toFixed(4)}`
                : "Unresolved"}
            </span>
          </div>
        </div>

        {/* Verification Status & Citations */}
        <div className="p-3 bg-zinc-900/50 rounded border border-zinc-800/80 space-y-2">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold border-b border-zinc-800 pb-1 flex items-center gap-1.5">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span>Source Grounding & Evidence</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-400">Verification State:</span>
            <span className="text-emerald-400 font-medium inline-flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>{facility.verification_status}</span>
            </span>
          </div>
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-zinc-400">Source Manifest:</span>
            <span className="font-mono text-zinc-300 text-[10px]">{facility.source_manifest_id}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2 pt-2">
          <button
            type="button"
            onClick={() => setIsEvidenceOpen(true)}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-2 bg-sky-950/40 hover:bg-sky-900/40 border border-sky-800/40 rounded text-xs text-sky-300 font-medium transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>View Supporting Evidence Claims</span>
          </button>

          <button
            type="button"
            onClick={() => setIsHistoryOpen(true)}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/60 rounded text-xs text-zinc-300 font-medium transition-colors"
          >
            <Clock className="w-3.5 h-3.5 text-zinc-400" />
            <span>Operational & Ownership History</span>
          </button>

          {facility.primary_entity_id && (
            <button
              type="button"
              onClick={() => router.push(`/companies?id=${encodeURIComponent(facility.primary_entity_id)}`)}
              className="w-full flex items-center justify-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/60 rounded text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Open Financial Company Profile</span>
            </button>
          )}
        </div>
      </div>

      {/* Supporting Evidence Modal */}
      {isEvidenceOpen && (
        <FacilityEvidenceViewer
          facility={facility}
          onClose={() => setIsEvidenceOpen(false)}
        />
      )}

      {/* Historical Timeline Modal */}
      {isHistoryOpen && (
        <FacilityHistory
          facility={facility}
          onClose={() => setIsHistoryOpen(false)}
        />
      )}
    </div>
  );
}

