"use client";

import React from "react";
import { X, FileText, ExternalLink, ShieldCheck, Calendar, Building, Quote } from "lucide-react";
import { CorporateFacility } from "@/lib/maps/corporate/types";

interface FacilityEvidenceViewerProps {
  facility: CorporateFacility;
  onClose: () => void;
}

export function FacilityEvidenceViewer({ facility, onClose }: FacilityEvidenceViewerProps) {
  const claims = facility.evidence_claims || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg max-w-xl w-full max-h-[80vh] flex flex-col shadow-2xl text-xs text-zinc-300 overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-sky-400" />
            <div>
              <h3 className="font-bold text-zinc-100 text-sm">Supporting Source Evidence</h3>
              <p className="text-[10px] text-zinc-500">{facility.canonical_name}</p>
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

        {/* Evidence Claims List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {claims.length === 0 ? (
            <div className="p-8 text-center text-zinc-500">
              <Quote className="w-8 h-8 mx-auto text-zinc-700 mb-2 opacity-50" />
              <p>No explicit evidence claims recorded for this facility.</p>
              <p className="text-[10px] mt-1 text-zinc-600">
                Source Manifest: {facility.source_manifest_id || "Unregistered"}
              </p>
            </div>
          ) : (
            claims.map((claim) => (
              <div
                key={claim.claim_id}
                className="p-3.5 bg-zinc-900/70 border border-zinc-800 rounded-md space-y-2.5"
              >
                {/* Source Document Title & Publisher */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-semibold text-zinc-100 text-xs">{claim.source_title}</div>
                    <div className="text-[10px] text-zinc-500 flex items-center gap-2 mt-0.5">
                      <span className="flex items-center gap-1">
                        <Building className="w-2.5 h-2.5" />
                        <span>{claim.publisher}</span>
                      </span>
                      {claim.publication_date && (
                        <span className="flex items-center gap-1 font-mono">
                          <Calendar className="w-2.5 h-2.5" />
                          <span>{claim.publication_date.split("T")[0]}</span>
                        </span>
                      )}
                    </div>
                  </div>

                  <span className="shrink-0 px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded text-[9px] font-medium flex items-center gap-1">
                    <ShieldCheck className="w-2.5 h-2.5" />
                    <span>{claim.verification_status}</span>
                  </span>
                </div>

                {/* Exact Cited Span */}
                <div className="p-2.5 bg-zinc-950 rounded border border-zinc-800/80 text-[11px] font-serif italic text-zinc-200 leading-relaxed relative pl-7">
                  <Quote className="w-3.5 h-3.5 text-zinc-600 absolute left-2 top-2.5" />
                  <span>&ldquo;{claim.exact_evidence_span}&rdquo;</span>
                </div>

                {/* Claim Metadata & External Link */}
                <div className="flex items-center justify-between text-[10px] pt-1 border-t border-zinc-800/50">
                  <div className="text-zinc-500">
                    <span>Predicate: </span>
                    <span className="font-mono text-zinc-400">{claim.predicate}</span>
                  </div>

                  {claim.document_url && (
                    <a
                      href={claim.document_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-sky-400 hover:text-sky-300 transition-colors"
                    >
                      <span>Original Filing</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-zinc-800 bg-zinc-900/60 flex items-center justify-between text-[10px] text-zinc-500">
          <span>Stage 127 Grounded Source Citations</span>
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

