"use client";

import React from "react";
import { BeneficialOwnerDTO } from "@/lib/companies/ownership";
import {
  ShieldCheck,
  Building2,
  ExternalLink,
  Info,
  Layers,
  Vote,
  Sliders,
} from "lucide-react";

interface BeneficialOwnersTableProps {
  items: BeneficialOwnerDTO[];
  reportingPeriod: string;
}

export const BeneficialOwnersTable: React.FC<BeneficialOwnersTableProps> = ({
  items,
  reportingPeriod,
}) => {
  return (
    <div className="space-y-3">
      {/* Overview explanation banner */}
      <div className="flex items-start gap-2 p-3 rounded-lg border border-border/50 bg-card/60 text-xs">
        <ShieldCheck className="h-4 w-4 text-primary shrink-0 mt-0.5" />
        <div className="text-muted-foreground">
          <span className="font-semibold text-foreground">Beneficial Ownership Disclosures (Schedules 13D & 13G): </span>
          SEC Section 13(d) and 13(g) require any person or group acquiring beneficial ownership of more than 5% of a voting class of registered equity securities to report their holdings, voting discretion, and dispositive power.
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 border-b border-border/60 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <tr>
              <th className="py-2.5 px-3">Beneficial Owner / Group</th>
              <th className="py-2.5 px-3 text-right">Beneficial Shares</th>
              <th className="py-2.5 px-3 text-right">Disclosed %</th>
              <th className="py-2.5 px-3 text-right">Sole Voting</th>
              <th className="py-2.5 px-3 text-right">Shared Voting</th>
              <th className="py-2.5 px-3 text-right">Sole Dispositive</th>
              <th className="py-2.5 px-3 text-right">Shared Dispositive</th>
              <th className="py-2.5 px-3 text-right">Filed</th>
              <th className="py-2.5 px-3 text-center">Filing Schedule</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {items.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-muted-foreground">
                  No Schedule 13D or 13G beneficial ownership disclosures available.
                </td>
              </tr>
            ) : (
              items.map((item) => {
                const pos = item.position;

                return (
                  <tr key={pos.position_id} className="hover:bg-muted/20 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-foreground flex items-center gap-1.5">
                        <Building2 className="h-3 w-3 text-primary shrink-0" />
                        <span className="truncate max-w-[240px]" title={pos.holder.name}>
                          {pos.holder.name}
                        </span>
                      </div>
                      <div className="text-[10px] text-muted-foreground font-mono mt-0.5 flex items-center gap-2">
                        <span>{item.is_group_filing ? `Group: ${item.group_name || "Disclosed Group"}` : "Single Filer"}</span>
                        <span>•</span>
                        <span>{pos.ownership_form.replace(/_/g, " ")}</span>
                      </div>
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-medium text-foreground">
                      {pos.formatted_shares}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-bold text-primary">
                      {pos.formatted_percentage || `${pos.source_reported_percentage?.toFixed(2)}%`}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                      {item.sole_voting_power !== null && item.sole_voting_power !== undefined
                        ? (item.sole_voting_power / 1e6).toFixed(2) + "M"
                        : "—"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                      {item.shared_voting_power !== null && item.shared_voting_power !== undefined
                        ? (item.shared_voting_power / 1e6).toFixed(2) + "M"
                        : "—"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                      {item.sole_dispositive_power !== null && item.sole_dispositive_power !== undefined
                        ? (item.sole_dispositive_power / 1e6).toFixed(2) + "M"
                        : "—"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                      {item.shared_dispositive_power !== null && item.shared_dispositive_power !== undefined
                        ? (item.shared_dispositive_power / 1e6).toFixed(2) + "M"
                        : "—"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-[11px] text-muted-foreground">
                      <div>{pos.filing_date}</div>
                      <div className="text-[9px] text-emerald-500/80">Active Vintage</div>
                    </td>

                    <td className="py-2.5 px-3 text-center">
                      <span
                        className="inline-flex items-center gap-1 font-mono text-[10px] text-primary/80 hover:text-primary cursor-pointer"
                        title={`Source Document ID: ${pos.source_document_id || "SEC-13G"}`}
                      >
                        {pos.disclosure_type}
                        <ExternalLink className="h-2.5 w-2.5" />
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* SEC Rule 13d-3 voting vs dispositive distinction */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-muted-foreground">
        <div className="p-3 rounded-lg border border-border/40 bg-muted/20">
          <div className="flex items-center gap-1.5 font-semibold text-foreground mb-1">
            <Vote className="h-3.5 w-3.5 text-primary" />
            <span>Voting Power vs Dispositive Power</span>
          </div>
          <p className="text-[11px]">
            SEC Rule 13d-3 defines beneficial ownership through either the power to vote (voting power) or the power to direct disposition (dispositive power). An asset manager may have full dispositive power over client shares while delegating voting power, or share voting with fund trustees.
          </p>
        </div>

        <div className="p-3 rounded-lg border border-border/40 bg-muted/20">
          <div className="flex items-center gap-1.5 font-semibold text-foreground mb-1">
            <Sliders className="h-3.5 w-3.5 text-sky-400" />
            <span>Schedule 13G Passive vs 13D Activist</span>
          </div>
          <p className="text-[11px]">
            Schedule 13G is filed by eligible passive institutional investors, exempt investors, and passive &lt;20% holders. Schedule 13D is filed by parties who acquire &gt;5% with potential intent to influence or control company management or governance.
          </p>
        </div>
      </div>
    </div>
  );
};
