"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchAccessGrantResponse,
  ResearchRole,
  ResearchResourceType,
  CreateAccessGrantRequest,
} from "@/lib/research/types";
import {
  getResearchRoleDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchParticipantsModalProps {
  isOpen: boolean;
  onClose: () => void;
  resourceType: ResearchResourceType;
  resourceId: string;
  participants: ResearchAccessGrantResponse[];
  isLoading?: boolean;
  onGrantParticipant: (data: CreateAccessGrantRequest) => Promise<unknown>;
  onUpdateParticipant: (grantId: string, role: ResearchRole) => Promise<unknown>;
  onRevokeParticipant: (grantId: string) => Promise<unknown>;
}

export function ResearchParticipantsModal({
  isOpen,
  onClose,
  resourceType,
  resourceId,
  participants,
  isLoading = false,
  onGrantParticipant,
  onUpdateParticipant,
  onRevokeParticipant,
}: ResearchParticipantsModalProps) {
  const [newPrincipalId, setNewPrincipalId] = useState<string>("");
  const [newRole, setNewRole] = useState<ResearchRole>("REVIEWER");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGrant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPrincipalId.trim()) return;

    setErrorMsg(null);
    setIsSubmitting(true);
    try {
      await onGrantParticipant({
        principal_id: newPrincipalId.trim(),
        role: newRole,
      });
      setNewPrincipalId("");
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to grant participant access.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRoleChange = async (grantId: string, role: ResearchRole) => {
    try {
      await onUpdateParticipant(grantId, role);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to update role.");
    }
  };

  const handleRevoke = async (grantId: string) => {
    if (!confirm("Revoke this collaborator's access?")) return;
    try {
      await onRevokeParticipant(grantId);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to revoke participant access.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-xl rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-2xl flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-atlas-border-default p-4">
          <div>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              Participant Governance & Research Access
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Configure collaborators and access grants for {resourceType} <strong>{resourceId}</strong>
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

        {/* Grant New Participant Form */}
        <form onSubmit={handleGrant} className="border-b border-atlas-border-default bg-atlas-surface-1 p-4 space-y-3">
          <div className="text-xs font-semibold text-atlas-text-primary">
            Grant Research Collaboration Access
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newPrincipalId}
              onChange={(e) => setNewPrincipalId(e.target.value)}
              placeholder="User ID or Email (e.g. analyst-colleague)"
              className="flex-1 rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-3 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
            />
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value as ResearchRole)}
              className="rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-2 py-1.5 text-xs text-atlas-text-primary"
            >
              <option value="VIEWER">Viewer (Read-only)</option>
              <option value="COMMENTER">Commenter (Notes & Threads)</option>
              <option value="REVIEWER">Reviewer (Audit & Approve)</option>
              <option value="EDITOR">Editor (Edit & Model)</option>
              <option value="OWNER">Owner (Full Admin)</option>
            </select>
            <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
              {isSubmitting ? "Granting..." : "Grant"}
            </Button>
          </div>
        </form>

        {/* Participants Table */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-xs font-semibold text-atlas-text-secondary mb-2">
            Active Collaborators ({participants.length})
          </div>

          {isLoading ? (
            <div className="py-6 text-center text-xs text-atlas-text-muted">
              Loading participants...
            </div>
          ) : participants.length === 0 ? (
            <div className="py-6 text-center text-xs text-atlas-text-muted">
              No individual access grants recorded. The resource owner has exclusive access.
            </div>
          ) : (
            <div className="divide-y divide-atlas-border-default border border-atlas-border-default rounded-xs bg-atlas-surface-1">
              {participants.map((g) => {
                const roleMeta = getResearchRoleDisplay(g.role);
                const isRevoked = !!g.revoked_at;

                return (
                  <div key={g.grant_id} className="flex items-center justify-between p-3 gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-atlas-text-primary">
                          {g.principal_id}
                        </span>
                        <Badge variant={roleMeta.variant} className="text-[10px]">
                          {roleMeta.label}
                        </Badge>
                        {isRevoked && (
                          <Badge variant="negative" className="text-[10px]">
                            Revoked
                          </Badge>
                        )}
                      </div>
                      <p className="mt-0.5 text-[11px] text-atlas-text-muted">
                        Granted by {g.granted_by} on {formatResearchDate(g.created_at)}
                      </p>
                    </div>

                    {!isRevoked && (
                      <div className="flex items-center gap-2">
                        <select
                          value={g.role}
                          onChange={(e) => handleRoleChange(g.grant_id, e.target.value as ResearchRole)}
                          className="rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-1.5 py-1 text-[11px] text-atlas-text-primary"
                        >
                          <option value="VIEWER">Viewer</option>
                          <option value="COMMENTER">Commenter</option>
                          <option value="REVIEWER">Reviewer</option>
                          <option value="EDITOR">Editor</option>
                          <option value="OWNER">Owner</option>
                        </select>
                        <Button
                          variant="ghost"
                          size="xs"
                          className="text-rose-400 hover:text-rose-300"
                          onClick={() => handleRevoke(g.grant_id)}
                        >
                          Revoke
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="border-t border-atlas-border-default p-3 flex justify-end">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
