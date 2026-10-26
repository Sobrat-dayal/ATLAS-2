"use client";

import React, { useState, useMemo } from "react";
import {
  Search,
  Filter,
  Check,
  Plus,
  ShieldCheck,
  Building,
  HelpCircle,
  AlertCircle,
  ExternalLink,
} from "lucide-react";
import { CompanyPeerCandidateDTO, PeerRelationshipType } from "@/lib/companies/peers";

interface PeerCandidateExplorerProps {
  candidates: CompanyPeerCandidateDTO[];
  selectedPeerIds: string[];
  onAddPeer: (id: string) => void;
  onRemovePeer: (id: string) => void;
  competitorsOnly: boolean;
  onToggleCompetitorsOnly: (val: boolean) => void;
}

export function PeerCandidateExplorer({
  candidates,
  selectedPeerIds,
  onAddPeer,
  onRemovePeer,
  competitorsOnly,
  onToggleCompetitorsOnly,
}: PeerCandidateExplorerProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCandidates = useMemo(() => {
    return candidates.filter((c) => {
      if (competitorsOnly && !c.is_competitor) return false;
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        c.ticker.toLowerCase().includes(q) ||
        c.display_name.toLowerCase().includes(q) ||
        c.classification.industry?.toLowerCase().includes(q) ||
        c.headquarters_country.toLowerCase().includes(q)
      );
    });
  }, [candidates, competitorsOnly, searchQuery]);

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col h-full">
      {/* Explorer Controls Bar */}
      <div className="p-3 border-b border-atlas-border-subtle flex flex-wrap items-center justify-between gap-3 bg-atlas-surface-subtle">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-atlas-text-muted" />
            <input
              type="text"
              placeholder="Search candidate peers (ticker, name, industry)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1 bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-atlas-accent w-64 md:w-80"
            />
          </div>

          <button
            onClick={() => onToggleCompetitorsOnly(!competitorsOnly)}
            className={`px-2.5 py-1 text-xs rounded border transition-colors flex items-center gap-1.5 ${
              competitorsOnly
                ? "bg-red-500/10 border-red-500/30 text-red-400 font-medium"
                : "bg-atlas-surface border-atlas-border-subtle text-atlas-text-muted hover:text-atlas-text-secondary"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Verified Competitors Only</span>
          </button>
        </div>

        <div className="text-xs text-atlas-text-muted flex items-center gap-2">
          <span>Showing</span>
          <span className="font-mono font-medium text-atlas-text-secondary">
            {filteredCandidates.length} of {candidates.length}
          </span>
          <span>candidates</span>
        </div>
      </div>

      {/* Candidates Table */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-surface text-[11px] font-semibold text-atlas-text-muted">
              <th className="py-2.5 px-3">Company / Security</th>
              <th className="py-2.5 px-3">Relationship Semantics</th>
              <th className="py-2.5 px-3">Industry Classification</th>
              <th className="py-2.5 px-3">Country</th>
              <th className="py-2.5 px-3 text-right">Market Cap</th>
              <th className="py-2.5 px-3 text-right">Revenue (FY24)</th>
              <th className="py-2.5 px-3 text-right">Relevance</th>
              <th className="py-2.5 px-3">Selection Provenance & Rationale</th>
              <th className="py-2.5 px-3 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle font-mono text-[11px]">
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-atlas-text-muted font-sans">
                  No comparable candidate companies match your active filters.
                </td>
              </tr>
            ) : (
              filteredCandidates.map((candidate) => {
                const isSelected = selectedPeerIds.includes(candidate.candidate_company_id);
                return (
                  <tr
                    key={candidate.candidate_company_id}
                    className="hover:bg-atlas-surface-subtle transition-colors group"
                  >
                    {/* Ticker & Display Name */}
                    <td className="py-2.5 px-3">
                      <div className="font-sans font-semibold text-atlas-text-primary text-xs">
                        {candidate.display_name}
                      </div>
                      <div className="text-[10px] text-atlas-accent font-mono mt-0.5">
                        {candidate.ticker}
                      </div>
                    </td>

                    {/* Relationship Type */}
                    <td className="py-2.5 px-3 font-sans">
                      {candidate.relationship_type === "VERIFIED_COMPETITOR" ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                          <ShieldCheck className="w-3 h-3" />
                          Direct Competitor
                        </span>
                      ) : candidate.relationship_type === "SOURCE_DEFINED_PEER" ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          Source-Defined Peer
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-atlas-surface-subtle text-atlas-text-muted border border-atlas-border-subtle">
                          Comparable Candidate
                        </span>
                      )}
                    </td>

                    {/* Classification */}
                    <td className="py-2.5 px-3 font-sans text-atlas-text-secondary">
                      <div className="truncate max-w-[160px]">
                        {candidate.classification.industry || candidate.classification.sector}
                      </div>
                      <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                        {candidate.classification.taxonomy} {candidate.classification.code || ""}
                      </div>
                    </td>

                    {/* Country */}
                    <td className="py-2.5 px-3 text-atlas-text-muted font-sans">
                      {candidate.headquarters_country}
                    </td>

                    {/* Market Cap */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-primary font-medium">
                      {candidate.formatted_market_cap || "N/A"}
                    </td>

                    {/* Revenue */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                      {candidate.formatted_revenue || "N/A"}
                    </td>

                    {/* Relevance Score */}
                    <td className="py-2.5 px-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <span className="font-semibold text-atlas-text-primary">
                          {Math.round(candidate.relevance_score * 100)}%
                        </span>
                        <div className="w-12 h-1.5 bg-atlas-surface-subtle rounded-full overflow-hidden border border-atlas-border-subtle">
                          <div
                            className={`h-full ${
                              candidate.relevance_score >= 0.85
                                ? "bg-emerald-400"
                                : candidate.relevance_score >= 0.7
                                ? "bg-blue-400"
                                : "bg-atlas-accent"
                            }`}
                            style={{ width: `${Math.round(candidate.relevance_score * 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Selection Reasons */}
                    <td className="py-2.5 px-3 font-sans">
                      <div className="flex flex-wrap gap-1 max-w-[280px]">
                        {candidate.selection_reasons.map((reason, idx) => (
                          <span
                            key={idx}
                            className="text-[10px] bg-atlas-surface-subtle text-atlas-text-muted px-1.5 py-0.5 rounded border border-atlas-border-subtle truncate max-w-full"
                            title={reason}
                          >
                            {reason}
                          </span>
                        ))}
                      </div>
                    </td>

                    {/* Add / Remove Action */}
                    <td className="py-2.5 px-3 text-center">
                      {isSelected ? (
                        <button
                          onClick={() => onRemovePeer(candidate.candidate_company_id)}
                          className="px-2.5 py-1 text-[11px] rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/30 transition-colors inline-flex items-center gap-1 font-sans"
                          title="Click to remove from peer group"
                        >
                          <Check className="w-3 h-3" />
                          <span>Active Peer</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => onAddPeer(candidate.candidate_company_id)}
                          className="px-2.5 py-1 text-[11px] rounded bg-atlas-surface hover:bg-atlas-accent/10 text-atlas-text-secondary hover:text-atlas-accent border border-atlas-border-subtle transition-colors inline-flex items-center gap-1 font-sans"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Add to Peers</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer Info */}
      <div className="p-2.5 border-t border-atlas-border-subtle bg-atlas-surface-subtle text-[11px] text-atlas-text-muted flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <HelpCircle className="w-3.5 h-3.5 text-atlas-accent" />
          <span>
            Candidate peers are generated deterministically based on primary industry classification, operating revenue scale, and corporate filings. Direct commercial competition requires verified market evidence.
          </span>
        </div>
      </div>
    </div>
  );
}
