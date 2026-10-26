"use client";

import React from "react";
import {
  FileText,
  ShieldCheck,
  ExternalLink,
  Building2,
  Calendar,
  Layers,
  ArrowRight,
  X,
  Quote,
} from "lucide-react";
import {
  RelationshipEvidenceDTO,
  SupplyChainRelationshipDTO,
} from "@/lib/companies/supply-chain";

interface SupplyChainEdgeInspectorProps {
  relationship: SupplyChainRelationshipDTO | null;
  evidenceList: RelationshipEvidenceDTO[];
  isLoading: boolean;
  onClose: () => void;
}

export function SupplyChainEdgeInspector({
  relationship,
  evidenceList,
  isLoading,
  onClose,
}: SupplyChainEdgeInspectorProps) {
  if (!relationship) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-xl h-full bg-atlas-surface border-l border-atlas-border-subtle p-5 overflow-y-auto flex flex-col justify-between shadow-2xl">
        <div>
          {/* Top Bar */}
          <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle mb-4">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                RELATIONSHIP EVIDENCE AUDIT
              </span>
              <span className="text-xs text-atlas-text-muted">ID: {relationship.relationship_id}</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-atlas-surface-subtle text-atlas-text-muted hover:text-atlas-text-primary"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Orientation Banner: Supplier -> Customer */}
          <div className="p-3 bg-atlas-surface-subtle/80 border border-atlas-border-subtle rounded-md mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-blue-400 shrink-0" />
              <div>
                <div className="text-[10px] uppercase font-mono text-atlas-text-muted">Supplier</div>
                <div className="text-xs font-semibold text-atlas-text-primary">
                  {relationship.supplier_name}
                </div>
              </div>
            </div>

            <div className="flex flex-col items-center px-3">
              <span className="font-mono text-[10px] text-atlas-text-muted mb-0.5">provides to</span>
              <div className="w-16 h-px bg-atlas-border-subtle relative flex items-center justify-center">
                <ArrowRight className="w-3.5 h-3.5 text-atlas-accent" />
              </div>
            </div>

            <div className="flex items-center gap-2 text-right">
              <div>
                <div className="text-[10px] uppercase font-mono text-atlas-text-muted">Customer</div>
                <div className="text-xs font-semibold text-atlas-text-primary">
                  {relationship.customer_name}
                </div>
              </div>
              <Building2 className="w-4 h-4 text-emerald-400 shrink-0" />
            </div>
          </div>

          {/* Key Relationship Specs */}
          <div className="grid grid-cols-2 gap-2 text-xs mb-4">
            <div className="p-2.5 bg-atlas-surface-subtle/40 rounded border border-atlas-border-subtle">
              <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                Relationship Taxonomy
              </div>
              <div className="font-medium text-atlas-text-primary mt-0.5">
                {relationship.relationship_type.replace(/_/g, " ")}
              </div>
            </div>
            <div className="p-2.5 bg-atlas-surface-subtle/40 rounded border border-atlas-border-subtle">
              <div className="text-[10px] text-atlas-text-muted uppercase font-mono">Tier & Scope</div>
              <div className="font-medium text-atlas-text-primary mt-0.5">
                Tier {relationship.tier_level} ({relationship.is_direct ? "Direct" : "Indirect"})
              </div>
            </div>
            <div className="p-2.5 bg-atlas-surface-subtle/40 rounded border border-atlas-border-subtle">
              <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                Supplied Product / Service
              </div>
              <div className="font-medium text-atlas-text-primary mt-0.5">
                {relationship.supplied_item_type}
              </div>
            </div>
            <div className="p-2.5 bg-atlas-surface-subtle/40 rounded border border-atlas-border-subtle">
              <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                Lifecycle & Verification
              </div>
              <div className="font-medium text-emerald-400 mt-0.5 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                {relationship.verification_status} ({relationship.lifecycle_status})
              </div>
            </div>
          </div>

          {/* Item Detailed Scope */}
          <div className="p-3 bg-atlas-surface-subtle/40 rounded border border-atlas-border-subtle mb-4 text-xs">
            <div className="text-[10px] text-atlas-text-muted uppercase font-mono mb-1">
              Disclosed Commercial Description
            </div>
            <div className="text-atlas-text-secondary leading-relaxed">
              {relationship.supplied_item_description}
            </div>
          </div>

          {/* Traceable Supporting Evidence Excerpts */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-atlas-accent" />
                Supporting Regulatory Evidence & Filings ({evidenceList.length})
              </h4>
              <span className="text-[10px] text-atlas-text-muted font-mono">
                Source Lineage Verified
              </span>
            </div>

            {isLoading ? (
              <div className="py-6 text-center text-xs text-atlas-text-muted">
                Loading verified evidence records...
              </div>
            ) : evidenceList.length === 0 ? (
              <div className="p-4 text-center text-xs text-atlas-text-muted bg-atlas-surface-subtle/30 rounded border border-atlas-border-subtle">
                No individual filing excerpt linked to this relationship record.
              </div>
            ) : (
              <div className="space-y-3">
                {evidenceList.map((ev) => (
                  <div
                    key={ev.evidence_id}
                    className="p-3 bg-atlas-surface-subtle/60 rounded border border-atlas-border-subtle text-xs"
                  >
                    <div className="flex items-center justify-between text-[11px] mb-1.5 pb-1 border-b border-atlas-border-subtle/50">
                      <div className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                        <FileText className="w-3 h-3 text-blue-400" />
                        <span>{ev.source_title}</span>
                      </div>
                      <span className="font-mono text-[10px] text-atlas-text-muted flex items-center gap-1">
                        <Calendar className="w-2.5 h-2.5" />
                        Filing Date: {ev.filing_date}
                      </span>
                    </div>

                    <div className="text-[10px] font-mono text-atlas-text-muted mb-2">
                      Section Anchor: <span className="text-atlas-text-secondary">{ev.section_anchor}</span>
                    </div>

                    {/* Excerpt Quote */}
                    <div className="relative pl-3 border-l-2 border-atlas-accent/40 italic text-atlas-text-secondary leading-relaxed bg-black/20 p-2 rounded-r text-[11px]">
                      <Quote className="w-3 h-3 text-atlas-accent/40 absolute -left-1.5 -top-1.5" />
                      &ldquo;{ev.excerpt}&rdquo;
                    </div>

                    <div className="mt-2 flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                      <span>Provider: {ev.source_provider_id}</span>
                      <span className="text-emerald-400 flex items-center gap-1">
                        <ShieldCheck className="w-2.5 h-2.5" />
                        {ev.review_status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-atlas-border-subtle mt-4 flex items-center justify-between">
          <div className="text-[10px] text-atlas-text-muted font-mono">
            Audit Standard: Zero-Inference SEC Evidence
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-atlas-surface-subtle hover:bg-atlas-accent hover:text-white text-atlas-text-primary rounded text-xs transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
