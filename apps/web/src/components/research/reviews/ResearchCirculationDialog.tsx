"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchInternalCirculationResponse,
  CreateCirculationRequest,
} from "@/lib/research/types";
import {
  getCirculationStatusDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchCirculationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  reportId: string;
  revisionNumber: number;
  isApproved: boolean;
  circulations: ResearchInternalCirculationResponse[];
  isLoading?: boolean;
  onCirculate: (data: CreateCirculationRequest) => Promise<unknown>;
  onRevokeCirculation: (circulationId: string) => Promise<unknown>;
}

export function ResearchCirculationDialog({
  isOpen,
  onClose,
  reportId,
  revisionNumber,
  isApproved,
  circulations,
  isLoading = false,
  onCirculate,
  onRevokeCirculation,
}: ResearchCirculationDialogProps) {
  const [recipientsInput, setRecipientsInput] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCirculate = async (e: React.FormEvent) => {
    e.preventDefault();
    const recipientList = recipientsInput
      .split(/[,;\n]/)
      .map((s) => s.trim())
      .filter(Boolean);

    if (recipientList.length === 0) {
      setErrorMsg("Please enter at least one recipient user ID or email.");
      return;
    }

    setErrorMsg(null);
    setIsSubmitting(true);
    try {
      await onCirculate({
        revision_number: revisionNumber,
        recipient_user_ids: recipientList,
        notes: notes.trim() || undefined,
      });
      setRecipientsInput("");
      setNotes("");
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMsg(e.message || "Failed to circulate report.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRevoke = async (circulationId: string) => {
    if (!confirm("Revoke this internal circulation grant?")) return;
    try {
      await onRevokeCirculation(circulationId);
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMsg(e.message || "Failed to revoke circulation.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-2xl flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-atlas-border-default p-4">
          <div>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              Controlled Internal Research Circulation
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Report <strong>{reportId}</strong> (Revision v{revisionNumber})
            </p>
          </div>
          <Button variant="ghost" size="xs" onClick={onClose}>
            ✕
          </Button>
        </div>

        {errorMsg && (
          <div className="mx-4 mt-3 rounded-xs border border-rose-500/30 bg-rose-500/10 p-2 text-xs text-rose-400">
            {errorMsg}
          </div>
        )}

        {/* Approval Check Warning */}
        {!isApproved && (
          <div className="m-4 rounded-xs border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-400">
            <strong>Approval Required:</strong> This revision has not yet received formal reviewer approval. Institutional policy prohibits unapproved draft circulation.
          </div>
        )}

        {/* Circulate Form */}
        {isApproved && (
          <form onSubmit={handleCirculate} className="border-b border-atlas-border-default bg-atlas-surface-1 p-4 space-y-3">
            <div>
              <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
                Authorized Internal Recipients (comma or line separated):
              </label>
              <textarea
                value={recipientsInput}
                onChange={(e) => setRecipientsInput(e.target.value)}
                placeholder="pm-equities-01, risk-officer-02, portfolio-manager@firm.com"
                className="w-full h-18 rounded-xs border border-atlas-border-default bg-atlas-surface-2 p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
                Circulation Notes / Scope:
              </label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. For Q4 Equity Investment Committee evaluation"
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
              />
            </div>

            <div className="flex justify-end">
              <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                {isSubmitting ? "Circulating..." : "Authorize Internal Circulation"}
              </Button>
            </div>
          </form>
        )}

        {/* Existing Circulations List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <div className="text-xs font-semibold text-atlas-text-secondary">
            Circulation History ({circulations.length})
          </div>

          {isLoading ? (
            <div className="py-4 text-center text-xs text-atlas-text-muted">
              Loading circulation records...
            </div>
          ) : circulations.length === 0 ? (
            <div className="py-4 text-center text-xs text-atlas-text-muted">
              No internal circulations active for this report.
            </div>
          ) : (
            <div className="divide-y divide-atlas-border-default border border-atlas-border-default rounded-xs bg-atlas-surface-1">
              {circulations.map((c) => {
                const statusMeta = getCirculationStatusDisplay(c.status);
                const isActive = c.status === "ACTIVE";

                return (
                  <div key={c.circulation_id} className="p-3 text-xs flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant={statusMeta.variant} className="text-[10px]">
                          {statusMeta.label}
                        </Badge>
                        <span className="font-mono text-[11px] text-atlas-text-muted">
                          v{c.revision_number} • {formatResearchDate(c.created_at)}
                        </span>
                      </div>
                      <div className="mt-1 text-atlas-text-primary">
                        <strong>{c.recipient_user_ids.length} Recipients:</strong>{" "}
                        <span className="text-atlas-text-secondary font-mono text-[11px]">
                          {c.recipient_user_ids.join(", ")}
                        </span>
                      </div>
                      {c.notes && (
                        <p className="mt-0.5 text-[11px] italic text-atlas-text-muted">
                          &ldquo;{c.notes}&rdquo;
                        </p>
                      )}
                    </div>

                    {isActive && (
                      <Button
                        variant="ghost"
                        size="xs"
                        className="text-rose-400 hover:text-rose-300"
                        onClick={() => handleRevoke(c.circulation_id)}
                      >
                        Revoke
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-atlas-border-default p-3 flex justify-end">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
