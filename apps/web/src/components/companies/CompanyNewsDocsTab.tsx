"use client";

import { Badge } from "@/design-system";
import { CompanyDocumentReference, CompanyNewsReference } from "@/lib/companies/types";
import { ExternalLink, FileText, Newspaper } from "lucide-react";

export interface CompanyNewsDocsTabProps {
  news: CompanyNewsReference[];
  documents: CompanyDocumentReference[];
}

export function CompanyNewsDocsTab({ news, documents }: CompanyNewsDocsTabProps) {
  return (
    <div className="space-y-6">
      {/* 1. Verified Corporate News References */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Newspaper className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
              Verified Corporate News References
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              {news.length} {news.length === 1 ? "Article" : "Articles"}
            </Badge>
          </div>
          <span className="text-[11px] text-atlas-text-muted">Stage 36 Canonical News</span>
        </div>

        {news && news.length > 0 ? (
          <div className="divide-y divide-atlas-border-subtle">
            {news.map((item, idx) => {
              const formattedDate = new Date(item.published_at).toLocaleString(undefined, {
                dateStyle: "medium",
                timeStyle: "short",
              });

              return (
                <div key={idx} className="p-4 hover:bg-atlas-surface-2/60 transition-colors space-y-1.5">
                  <div className="flex items-start justify-between gap-4">
                    <h4 className="text-sm font-semibold text-atlas-text-primary hover:text-atlas-accent transition-colors">
                      {item.url ? (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5"
                        >
                          <span>{item.title}</span>
                          <ExternalLink className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
                        </a>
                      ) : (
                        item.title
                      )}
                    </h4>
                    <span className="text-[11px] font-mono text-atlas-text-muted shrink-0">
                      {formattedDate}
                    </span>
                  </div>

                  {item.summary && (
                    <p className="text-xs text-atlas-text-secondary leading-relaxed line-clamp-2">
                      {item.summary}
                    </p>
                  )}

                  <div className="flex items-center gap-3 text-[11px] text-atlas-text-muted pt-1">
                    <span>
                      Publisher: <strong className="text-atlas-text-secondary font-medium">{item.publisher}</strong>
                    </span>
                    {item.authors && item.authors.length > 0 && (
                      <span>By: {item.authors.join(", ")}</span>
                    )}
                    <span className="font-mono text-[10px]">Source: {item.source}</span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-atlas-text-muted italic">
            No canonical verified news articles linked to this corporate entity.
          </div>
        )}
      </div>

      {/* 2. Verified Corporate Research & Document References */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
              Corporate Research & Regulatory Filings
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              {documents.length} {documents.length === 1 ? "Document" : "Documents"}
            </Badge>
          </div>
          <span className="text-[11px] text-atlas-text-muted">Stage 20 Documents</span>
        </div>

        {documents && documents.length > 0 ? (
          <div className="divide-y divide-atlas-border-subtle">
            {documents.map((doc, idx) => (
              <div key={idx} className="p-4 hover:bg-atlas-surface-2/60 transition-colors flex items-center justify-between gap-4">
                <div className="space-y-1">
                  <h4 className="text-sm font-semibold text-atlas-text-primary">
                    {doc.url ? (
                      <a
                        href={doc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 hover:text-atlas-accent transition-colors"
                      >
                        <span>{doc.title}</span>
                        <ExternalLink className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
                      </a>
                    ) : (
                      doc.title
                    )}
                  </h4>
                  <div className="flex items-center gap-3 text-[11px] text-atlas-text-muted">
                    {doc.document_kind && (
                      <Badge variant="outline" className="capitalize text-[10px] font-mono">
                        {doc.document_kind.replace(/_/g, " ")}
                      </Badge>
                    )}
                    {doc.publication_date && <span>Filed: {doc.publication_date}</span>}
                    {doc.language_code && <span className="uppercase">{doc.language_code}</span>}
                  </div>
                </div>

                {doc.url && (
                  <a
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 text-xs font-medium border border-atlas-border-default rounded-xs text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-3 transition-colors inline-flex items-center gap-1.5 shrink-0"
                  >
                    <span>View Filing</span>
                    <ExternalLink className="w-3 h-3 text-atlas-text-muted" />
                  </a>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-atlas-text-muted italic">
            No canonical corporate filings or research documents cataloged for this entity.
          </div>
        )}
      </div>
    </div>
  );
}
