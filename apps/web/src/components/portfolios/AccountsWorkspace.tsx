"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { formatDate } from "@/lib/portfolios/formatting";
import { AccountDTO, PortfolioDTO } from "@/lib/portfolios/types";
import { Info, Layers, Plus } from "lucide-react";

interface AccountsWorkspaceProps {
  portfolio: PortfolioDTO;
  accounts: AccountDTO[];
  onOpenCreateAccount: () => void;
}

export function AccountsWorkspace({
  portfolio,
  accounts,
  onOpenCreateAccount,
}: AccountsWorkspaceProps) {
  return (
    <div className="space-y-4 p-4">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-atlas-accent" />
            <h2 className="text-base font-bold text-atlas-text-primary">
              Investment Accounts in {portfolio.name}
            </h2>
            <Badge variant="outline">{accounts.length} Account(s)</Badge>
          </div>
          <p className="mt-1 text-xs text-atlas-text-muted">
            Investment accounts hold segregated cash and security holdings under a common reporting portfolio.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={onOpenCreateAccount}
          className="h-8 gap-1.5 text-xs"
        >
          <Plus className="h-3.5 w-3.5" />
          Add Investment Account
        </Button>
      </div>

      {/* Institutional Policy Notice */}
      <div className="flex items-center gap-2 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs text-atlas-text-muted">
        <Info className="h-4 w-4 shrink-0 text-atlas-accent" />
        <span>
          <strong>Accounting Sandbox Standard:</strong> Brokerage records and investment accounts represent internal ledger source-of-truth. No external brokerage login or live trading order execution is permitted under Stage 110.
        </span>
      </div>

      {/* Accounts Table */}
      <div className="overflow-x-auto rounded-sm border border-atlas-border-default bg-atlas-surface-0">
        {accounts.length === 0 ? (
          <div className="py-12 text-center text-xs text-atlas-text-muted">
            No accounts in this portfolio.
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default bg-atlas-surface-1/70 text-[11px] font-semibold text-atlas-text-muted">
                <th className="py-2.5 px-3">Account Name</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Primary Currency</th>
                <th className="py-2.5 px-3">Custodian</th>
                <th className="py-2.5 px-3">Account Identifier</th>
                <th className="py-2.5 px-3 text-center">Status</th>
                <th className="py-2.5 pr-3 text-right">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40">
              {accounts.map((acc) => (
                <tr key={acc.id} className="hover:bg-atlas-surface-1 transition-colors">
                  <td className="py-2.5 px-3 font-medium text-atlas-text-primary">
                    {acc.account_name}
                  </td>
                  <td className="py-2.5 px-3">
                    <Badge variant="outline" className="text-[10px]">
                      {acc.account_type}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-3 font-mono font-bold text-atlas-text-primary">
                    {acc.primary_currency}
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-secondary">
                    {acc.custodian_name || "Self-Directed"}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-atlas-text-muted">
                    {acc.account_number_mask || "—"}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <Badge variant={acc.status === "ACTIVE" ? "positive" : "default"}>
                      {acc.status}
                    </Badge>
                  </td>
                  <td className="py-2.5 pr-3 text-right text-atlas-text-muted text-[11px]">
                    {formatDate(acc.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
