"use client";

import React, { useState } from "react";
import {
  Users,
  Plus,
  Trash2,
  Edit2,
  Lock,
  Check,
  X,
  AlertCircle,
  FolderPlus,
} from "lucide-react";
import { UserPeerGroupDTO, CompanyPeerCandidateDTO } from "@/lib/companies/peers";

interface PeerGroupManagerProps {
  peerGroups: UserPeerGroupDTO[];
  selectedGroupId: string | null;
  onSelectGroup: (groupId: string) => void;
  candidates: CompanyPeerCandidateDTO[];
  onCreateGroup: (name: string, description?: string, peerIds?: string[]) => Promise<UserPeerGroupDTO>;
  onUpdateGroup: (groupId: string, name?: string, peerIds?: string[], expectedRevision?: number) => Promise<UserPeerGroupDTO>;
  onDeleteGroup: (groupId: string) => Promise<void>;
  isMutating: boolean;
}

export function PeerGroupManager({
  peerGroups,
  selectedGroupId,
  onSelectGroup,
  candidates,
  onCreateGroup,
  onUpdateGroup,
  onDeleteGroup,
  isMutating,
}: PeerGroupManagerProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupDesc, setNewGroupDesc] = useState("");
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([]);

  const [editingGroupId, setEditingGroupId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleStartCreate = () => {
    setIsCreating(true);
    setNewGroupName("");
    setNewGroupDesc("");
    // Default with top 3 candidates
    setSelectedCandidates(candidates.slice(0, 3).map((c) => c.candidate_company_id));
    setErrorMessage(null);
  };

  const handleSaveCreate = async () => {
    if (!newGroupName.trim()) {
      setErrorMessage("Peer group name is required.");
      return;
    }
    if (selectedCandidates.length === 0) {
      setErrorMessage("At least one peer company must be included.");
      return;
    }
    try {
      await onCreateGroup(newGroupName.trim(), newGroupDesc.trim() || undefined, selectedCandidates);
      setIsCreating(false);
      setErrorMessage(null);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to create peer group");
    }
  };

  const handleStartEdit = (group: UserPeerGroupDTO) => {
    setEditingGroupId(group.id);
    setEditName(group.name);
    setErrorMessage(null);
  };

  const handleSaveEdit = async (group: UserPeerGroupDTO) => {
    if (!editName.trim()) {
      setErrorMessage("Group name cannot be blank.");
      return;
    }
    try {
      await onUpdateGroup(group.id, editName.trim(), undefined, group.revision);
      setEditingGroupId(null);
      setErrorMessage(null);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to update peer group");
    }
  };

  const handleDelete = async (groupId: string) => {
    if (confirm("Are you sure you want to delete this custom peer group?")) {
      try {
        await onDeleteGroup(groupId);
      } catch (err: any) {
        setErrorMessage(err.message || "Failed to delete peer group");
      }
    }
  };

  const toggleCandidateSelection = (candidateId: string) => {
    if (selectedCandidates.includes(candidateId)) {
      setSelectedCandidates(selectedCandidates.filter((id) => id !== candidateId));
    } else {
      if (selectedCandidates.length >= 25) {
        alert("Maximum 25 peer companies permitted.");
        return;
      }
      setSelectedCandidates([...selectedCandidates, candidateId]);
    }
  };

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle mb-4">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary flex items-center gap-2">
            <Users className="w-4 h-4 text-atlas-accent" />
            Institutional Peer Groups
          </h3>
          <p className="text-xs text-atlas-text-muted mt-0.5">
            Manage custom analyst peer groups. Changes are persisted per authenticated user.
          </p>
        </div>

        <button
          onClick={handleStartCreate}
          disabled={isCreating || isMutating}
          className="px-3 py-1.5 text-xs rounded bg-atlas-accent text-white hover:bg-atlas-accent/90 transition-colors flex items-center gap-1.5 disabled:opacity-50"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Peer Group</span>
        </button>
      </div>

      {errorMessage && (
        <div className="p-2.5 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Creation Modal / Inline Drawer */}
      {isCreating && (
        <div className="p-4 mb-4 bg-atlas-surface-subtle border border-atlas-border-subtle rounded">
          <div className="text-xs font-semibold text-atlas-text-primary mb-3 flex items-center gap-1.5">
            <FolderPlus className="w-4 h-4 text-atlas-accent" />
            Create Custom Peer Group
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[11px] text-atlas-text-muted mb-1 font-medium">Group Name *</label>
              <input
                type="text"
                placeholder="e.g. Mega-Cap Tech Hardware Peers"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-atlas-accent"
              />
            </div>
            <div>
              <label className="block text-[11px] text-atlas-text-muted mb-1 font-medium">Description</label>
              <input
                type="text"
                placeholder="Methodology rationale or scope..."
                value={newGroupDesc}
                onChange={(e) => setNewGroupDesc(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-atlas-accent"
              />
            </div>
          </div>

          <div className="mb-3">
            <label className="block text-[11px] text-atlas-text-muted mb-1 font-medium">
              Select Initial Peer Companies ({selectedCandidates.length}/25)
            </label>
            <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-2 bg-atlas-surface border border-atlas-border-subtle rounded">
              {candidates.map((cand) => {
                const isChecked = selectedCandidates.includes(cand.candidate_company_id);
                return (
                  <button
                    key={cand.candidate_company_id}
                    onClick={() => toggleCandidateSelection(cand.candidate_company_id)}
                    type="button"
                    className={`px-2 py-1 text-[11px] rounded border transition-colors flex items-center gap-1 ${
                      isChecked
                        ? "bg-atlas-accent/15 border-atlas-accent text-atlas-accent font-medium"
                        : "bg-atlas-surface-subtle border-atlas-border-subtle text-atlas-text-muted hover:text-atlas-text-secondary"
                    }`}
                  >
                    <span>{cand.ticker}</span>
                    <span className="text-[10px] opacity-75">({cand.display_name.split(" ")[0]})</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => setIsCreating(false)}
              className="px-3 py-1 text-xs text-atlas-text-muted hover:text-atlas-text-primary transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveCreate}
              disabled={isMutating}
              className="px-3 py-1 text-xs rounded bg-atlas-accent text-white hover:bg-atlas-accent/90 transition-colors disabled:opacity-50"
            >
              {isMutating ? "Saving..." : "Save Peer Group"}
            </button>
          </div>
        </div>
      )}

      {/* Peer Groups List */}
      <div className="space-y-2">
        {peerGroups.map((group) => {
          const isSelected = selectedGroupId === group.id;
          const isSystem = group.owner_user_id === "system_default";
          const isEditing = editingGroupId === group.id;

          return (
            <div
              key={group.id}
              className={`p-3 rounded border transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                isSelected
                  ? "bg-atlas-accent/5 border-atlas-accent/40"
                  : "bg-atlas-surface border-atlas-border-subtle hover:border-atlas-border"
              }`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  {isEditing ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="px-2 py-0.5 text-xs bg-atlas-surface border border-atlas-accent rounded text-atlas-text-primary"
                      />
                      <button
                        onClick={() => handleSaveEdit(group)}
                        className="p-1 hover:text-emerald-400 text-atlas-text-muted"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setEditingGroupId(null)}
                        className="p-1 hover:text-red-400 text-atlas-text-muted"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <span className="text-xs font-semibold text-atlas-text-primary">
                      {group.name}
                    </span>
                  )}

                  {isSystem ? (
                    <span className="px-1.5 py-0.2 rounded text-[10px] bg-atlas-surface-subtle border border-atlas-border-subtle text-atlas-text-muted flex items-center gap-1 font-mono">
                      <Lock className="w-3 h-3 text-atlas-text-muted" />
                      System Default
                    </span>
                  ) : (
                    <span className="px-1.5 py-0.2 rounded text-[10px] bg-blue-500/10 text-blue-400 font-mono">
                      User Private (rev {group.revision})
                    </span>
                  )}
                </div>

                {group.description && (
                  <p className="text-[11px] text-atlas-text-muted mt-0.5">
                    {group.description}
                  </p>
                )}

                <div className="mt-1.5 flex items-center gap-3 text-[10px] text-atlas-text-muted font-mono">
                  <span>{group.peer_company_ids.length} Peers Included</span>
                  <span>•</span>
                  <span>Updated {new Date(group.updated_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 self-end sm:self-center">
                {isSelected ? (
                  <span className="px-2.5 py-1 text-[11px] rounded bg-atlas-accent/15 text-atlas-accent font-medium border border-atlas-accent/30 flex items-center gap-1">
                    <Check className="w-3 h-3" />
                    Active Group
                  </span>
                ) : (
                  <button
                    onClick={() => onSelectGroup(group.id)}
                    className="px-2.5 py-1 text-[11px] rounded bg-atlas-surface-subtle hover:bg-atlas-accent/10 text-atlas-text-secondary hover:text-atlas-accent border border-atlas-border-subtle transition-colors"
                  >
                    Select Group
                  </button>
                )}

                {!isSystem && !isEditing && (
                  <>
                    <button
                      onClick={() => handleStartEdit(group)}
                      className="p-1.5 text-atlas-text-muted hover:text-atlas-text-primary transition-colors"
                      title="Rename Group"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(group.id)}
                      className="p-1.5 text-atlas-text-muted hover:text-red-400 transition-colors"
                      title="Delete Group"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
