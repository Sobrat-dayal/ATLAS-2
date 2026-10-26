"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  ExternalLink,
  ShieldCheck,
  Truck,
  Building2,
  DollarSign,
} from "lucide-react";
import { SupplyChainRelationshipDTO } from "@/lib/companies/supply-chain";

interface CustomersTableProps {
  customers: SupplyChainRelationshipDTO[];
  onInspect: (relationshipId: string) => void;
  selectedRelationshipId?: string | null;
}

export function CustomersTable({
  customers,
  onInspect,
  selectedRelationshipId,
}: CustomersTableProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = customers.filter((c) => {
    return (
      c.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.supplied_item_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.supplied_item_description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md overflow-hidden">
      {/* Table Toolbar */}
      <div className="p-3 border-b border-atlas-border-subtle flex flex-wrap items-center justify-between gap-2 bg-atlas-surface-subtle/50">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-atlas-text-muted" />
            <input
              type="text"
              placeholder="Search customers, channels, distributors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1 bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-atlas-accent w-64"
            />
          </div>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            Orientation: SUBJECT COMPANY → CUSTOMER
          </span>
        </div>

        <div className="text-[11px] text-atlas-text-muted font-mono">
          Showing {filtered.length} of {customers.length} Verified Customers & Channels
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-surface-subtle text-atlas-text-muted font-medium text-[11px]">
              <th className="py-2.5 px-3">Customer / Channel Partner</th>
              <th className="py-2.5 px-3">Relationship Category</th>
              <th className="py-2.5 px-3">Distributed Products / Scope</th>
              <th className="py-2.5 px-3">Revenue Exposure</th>
              <th className="py-2.5 px-3">Verification</th>
              <th className="py-2.5 px-3">Disclosed Evidence</th>
              <th className="py-2.5 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle text-atlas-text-secondary">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-atlas-text-muted">
                  No verified customers or commercial channels match your filter criteria.
                </td>
              </tr>
            ) : (
              filtered.map((rel) => {
                const isSelected = selectedRelationshipId === rel.relationship_id;
                return (
                  <tr
                    key={rel.relationship_id}
                    className={`hover:bg-atlas-surface-subtle/70 transition-colors ${
                      isSelected ? "bg-emerald-500/10 border-l-2 border-l-emerald-500" : ""
                    }`}
                  >
                    {/* Customer Name */}
                    <td className="py-2.5 px-3">
                      <div className="font-medium text-atlas-text-primary flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
                        <span>{rel.customer_name}</span>
                      </div>
                      <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                        {rel.notes || "Commercial customer channel"}
                      </div>
                    </td>

                    {/* Relationship Category */}
                    <td className="py-2.5 px-3">
                      <span className="font-mono text-[10px] bg-atlas-surface-subtle px-1.5 py-0.5 rounded text-atlas-text-primary border border-atlas-border-subtle">
                        {rel.relationship_type.replace(/_/g, " ")}
                      </span>
                    </td>

                    {/* Products / Scope */}
                    <td className="py-2.5 px-3 max-w-xs">
                      <div className="font-medium text-atlas-text-primary text-[11px] truncate">
                        {rel.supplied_item_type}
                      </div>
                      <div className="text-[10px] text-atlas-text-muted truncate mt-0.5">
                        {rel.supplied_item_description}
                      </div>
                    </td>

                    {/* Revenue Exposure */}
                    <td className="py-2.5 px-3">
                      {rel.reported_revenue_percentage != null ? (
                        <span className="font-mono text-[11px] font-semibold text-emerald-400">
                          {rel.reported_revenue_percentage.toFixed(1)}% of Revenue
                        </span>
                      ) : (
                        <span className="text-[11px] text-atlas-text-muted">
                          Non-reportable (&lt;10% threshold)
                        </span>
                      )}
                    </td>

                    {/* Verification Status */}
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded ${
                          rel.verification_status === "VERIFIED"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                        }`}
                      >
                        <ShieldCheck className="w-2.5 h-2.5" />
                        {rel.verification_status}
                      </span>
                    </td>

                    {/* Disclosed Evidence */}
                    <td className="py-2.5 px-3">
                      {rel.primary_evidence ? (
                        <button
                          onClick={() => onInspect(rel.relationship_id)}
                          className="text-[11px] text-blue-400 hover:text-blue-300 font-mono flex items-center gap-1 text-left group"
                          title="Click to view regulatory filing excerpt and review details"
                        >
                          <FileText className="w-3 h-3 text-atlas-text-muted group-hover:text-blue-400" />
                          <span className="underline decoration-blue-500/30 underline-offset-2">
                            {rel.primary_evidence.source_title}
                          </span>
                        </button>
                      ) : (
                        <span className="text-[10px] text-atlas-text-muted">
                          {rel.evidence_count} source records
                        </span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => onInspect(rel.relationship_id)}
                        className="px-2 py-1 text-[11px] bg-atlas-surface-subtle hover:bg-atlas-accent hover:text-white text-atlas-text-primary rounded border border-atlas-border-subtle transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
