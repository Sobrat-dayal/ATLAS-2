"use client";

import React from "react";
import { FileText, ExternalLink, ShieldCheck, Hash } from "lucide-react";
import { OfficialPublicationDTO } from "@/lib/economics/central-banks";

interface PublicationsPanelProps {
  publications: OfficialPublicationDTO[];
  selectedPublicationId: string | null;
  onSelectPublication: (documentId: string) => void;
}

export function PublicationsPanel({
  publications,
  selectedPublicationId,
  onSelectPublication,
}: PublicationsPanelProps) {
  const selectedPub =
    publications.find((p) => p.document_id === selectedPublicationId) || publications[0];

  return (
    <div className="space-y-5">
      {/* Publications Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Official Central Bank Publications & Statements
            </h3>
          </div>
          <span className="text-xs font-mono text-atlas-text-muted">
            {publications.length} Verified Documents
          </span>
        </div>

        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 font-mono text-[11px] text-atlas-text-muted uppercase">
                <th className="py-2.5 px-3">Title</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Published At (UTC)</th>
                <th className="py-2.5 px-3">Format</th>
                <th className="py-2.5 px-3">Source Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle/50 font-mono">
              {publications.map((pub) => {
                const isSelected = pub.document_id === selectedPub?.document_id;
                return (
                  <tr
                    key={pub.document_id}
                    onClick={() => onSelectPublication(pub.document_id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-atlas-accent/10 border-l-2 border-atlas-accent"
                        : "hover:bg-atlas-surface-elevated/40"
                    }`}
                  >
                    <td className="py-3 px-3 font-semibold text-atlas-text-primary font-sans max-w-sm truncate">
                      {pub.title}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-atlas-background text-atlas-text-primary border border-atlas-border-subtle">
                        {pub.publication_kind}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-atlas-text-muted">
                      {new Date(pub.published_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-[11px] text-atlas-text-muted">
                      {pub.media_type}
                    </td>
                    <td className="py-3 px-3">
                      <a
                        href={pub.source_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-atlas-accent hover:underline flex items-center gap-1 font-mono text-[11px]"
                      >
                        Source <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Document Excerpt Inspector */}
      {selectedPub && (
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h4 className="text-sm font-semibold text-atlas-text-primary font-sans">
                {selectedPub.title}
              </h4>
            </div>
            <div className="flex items-center gap-3 text-[10px] font-mono text-atlas-text-muted">
              <span className="flex items-center gap-1">
                <Hash className="w-3 h-3" />
                {selectedPub.content_hash}
              </span>
              <span>•</span>
              <span>Revision: {selectedPub.source_revision}</span>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
              Sanitized Official Statement Excerpt
            </span>
            <div className="bg-atlas-background rounded p-4 border border-atlas-border-subtle text-xs text-atlas-text-primary font-serif leading-relaxed italic">
              "{selectedPub.sanitized_excerpt}"
            </div>
            <div className="flex items-center justify-between pt-2 text-xs">
              <span className="text-[10px] font-mono text-atlas-text-muted">
                Official document authenticated directly from monetary authority.
              </span>
              <a
                href={selectedPub.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-atlas-accent hover:underline flex items-center gap-1 font-mono text-xs"
              >
                Access Full Official Statement <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
