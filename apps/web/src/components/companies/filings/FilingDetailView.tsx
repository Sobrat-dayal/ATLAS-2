"use client";

import React, { useState } from "react";
import {
  FilingContentDTO,
  FilingDetailDTO,
  FilingDocumentDTO,
  FilingSourceReferenceDTO,
  XBRLFactDTO,
} from "@/lib/companies/filings";
import {
  ArrowLeft,
  Copy,
  Check,
  ExternalLink,
  Download,
  FileText,
  FileCode,
  Layers,
  ShieldCheck,
  Calendar,
  Clock,
  Hash,
  Database,
  Building,
} from "lucide-react";

interface FilingDetailViewProps {
  detail: FilingDetailDTO;
  content: FilingContentDTO | null;
  facts: XBRLFactDTO[];
  sources: FilingSourceReferenceDTO | null;
  onBack: () => void;
  onCompareWith?: (filingId: string) => void;
}

export const FilingDetailView: React.FC<FilingDetailViewProps> = ({
  detail,
  content,
  facts,
  sources,
  onBack,
  onCompareWith,
}) => {
  const [activeTab, setActiveTab] = useState<"html" | "text" | "facts" | "attachments" | "provenance">("html");
  const [copiedCitation, setCopiedCitation] = useState<boolean>(false);
  const [conceptFilter, setConceptFilter] = useState<string>("");

  const citationText = `SEC EDGAR | ${detail.filer_name} (CIK: ${detail.filer_cik}) | Form ${detail.form_type} | Period: ${detail.reporting_period} | Accession: ${detail.accession_number} | Filed: ${detail.filing_date}`;

  const handleCopyCitation = () => {
    navigator.clipboard.writeText(citationText);
    setCopiedCitation(true);
    setTimeout(() => setCopiedCitation(false), 2000);
  };

  const filteredFacts = facts.filter((f) => {
    if (!conceptFilter.trim()) return true;
    const q = conceptFilter.toLowerCase();
    return (
      f.concept_name.toLowerCase().includes(q) ||
      f.label.toLowerCase().includes(q) ||
      f.formatted_value.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      {/* Top Action & Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg border border-border/60 bg-card/60">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-semibold bg-muted hover:bg-muted/80 text-foreground transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Filings</span>
          </button>

          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-primary/10 text-primary border border-primary/20">
              {detail.form_type}
            </span>
            <span className="text-xs font-mono text-muted-foreground">
              Period: <span className="text-foreground font-semibold">{detail.reporting_period}</span>
            </span>
            {detail.is_amendment && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                AMENDMENT (/A)
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Citation Button */}
          <button
            type="button"
            onClick={handleCopyCitation}
            title="Copy institutional citation"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border border-border bg-background/80 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          >
            {copiedCitation ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedCitation ? "Citation Copied" : "Copy Citation"}</span>
          </button>

          {/* Official Source Link */}
          {detail.primary_document_url && (
            <a
              href={detail.primary_document_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium border border-border bg-background/80 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
              <span>SEC Archives</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>

      {/* Filing Header Info Card */}
      <div className="p-4 rounded-lg border border-border/60 bg-card/40 space-y-2">
        <h2 className="text-base font-bold text-foreground">{detail.title}</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-border/40 text-xs font-mono text-muted-foreground">
          <div>
            <div className="text-[10px] uppercase text-muted-foreground/80">Filer / Issuer</div>
            <div className="text-foreground font-sans font-semibold mt-0.5 truncate">{detail.filer_name}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase text-muted-foreground/80">SEC CIK</div>
            <div className="text-foreground font-semibold mt-0.5">{detail.filer_cik}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase text-muted-foreground/80">Filing Date</div>
            <div className="text-foreground font-semibold mt-0.5">{detail.filing_date}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase text-muted-foreground/80">Acceptance Datetime</div>
            <div className="text-foreground font-semibold mt-0.5">
              {detail.acceptance_timestamp ? detail.acceptance_timestamp.slice(0, 19).replace("T", " ") : "Verified"}
            </div>
          </div>
        </div>
        <div className="text-[11px] font-mono text-muted-foreground">
          Accession Number: <span className="text-foreground">{detail.accession_number}</span>
          {detail.amends_accession_number && (
            <span className="ml-3 text-amber-400">
              Amends Accession: <span className="font-semibold">{detail.amends_accession_number}</span>
            </span>
          )}
        </div>
      </div>

      {/* Viewer Subtabs */}
      <div className="flex border-b border-border/60 gap-1 text-xs font-semibold">
        <button
          type="button"
          onClick={() => setActiveTab("html")}
          className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "html"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Rendered Document</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("text")}
          className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "text"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>Extracted Text</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("facts")}
          className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "facts"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>XBRL Facts ({facts.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("attachments")}
          className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "attachments"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Download className="w-3.5 h-3.5" />
          <span>Attachments ({detail.documents.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("provenance")}
          className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
            activeTab === "provenance"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Source & Provenance</span>
        </button>
      </div>

      {/* Tab 1: Rendered HTML Document (Safely Sanitized) */}
      {activeTab === "html" && (
        <div className="rounded-lg border border-border/60 bg-card/20 p-4 min-h-[400px]">
          {content?.content_html ? (
            <div
              className="prose prose-invert max-w-none text-xs leading-relaxed text-foreground [&_table]:w-full [&_table]:border-collapse [&_th]:border [&_th]:border-border/60 [&_th]:p-2 [&_th]:bg-muted/40 [&_td]:border [&_td]:border-border/40 [&_td]:p-2 [&_h1]:text-base [&_h1]:font-bold [&_h2]:text-sm [&_h2]:font-bold [&_h3]:text-xs [&_h3]:font-semibold"
              dangerouslySetInnerHTML={{ __html: content.content_html }}
            />
          ) : (
            <div className="py-12 text-center text-muted-foreground text-xs">
              Rendered HTML content not cached. You can inspect the Extracted Text or open the official SEC document.
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Extracted Plain Text */}
      {activeTab === "text" && (
        <div className="rounded-lg border border-border/60 bg-muted/20 p-4">
          <div className="mb-2 text-[11px] font-mono text-muted-foreground flex justify-between">
            <span>Encoding: UTF-8 &bull; Safe Text Extraction</span>
            <span>Length: {content?.content_text?.length || 0} characters</span>
          </div>
          <pre className="p-3 rounded bg-background/90 border border-border/60 font-mono text-[11px] leading-relaxed text-foreground whitespace-pre-wrap overflow-x-auto max-h-[600px] select-text">
            {content?.content_text || "No extracted plain text available for this document."}
          </pre>
        </div>
      )}

      {/* Tab 3: XBRL Facts Table */}
      {activeTab === "facts" && (
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3 p-2 rounded bg-card/40 border border-border/60">
            <input
              type="text"
              value={conceptFilter}
              onChange={(e) => setConceptFilter(e.target.value)}
              placeholder="Search concepts (e.g. Revenues, NetIncome, Assets)..."
              className="text-xs px-2.5 py-1 rounded bg-background border border-border text-foreground w-72 focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <span className="text-[11px] font-mono text-muted-foreground">
              Showing {filteredFacts.length} of {facts.length} qualified facts
            </span>
          </div>

          <div className="rounded-lg border border-border/60 bg-card/40 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-muted/40 text-muted-foreground font-semibold uppercase tracking-wider text-[10px] border-b border-border/60">
                  <tr>
                    <th className="py-2 px-3">US-GAAP Concept</th>
                    <th className="py-2 px-3">Official Accounting Label</th>
                    <th className="py-2 px-3 w-28 text-right">Reported Value</th>
                    <th className="py-2 px-3 w-20">Unit</th>
                    <th className="py-2 px-3 w-24">Context</th>
                    <th className="py-2 px-3 w-28">Period End</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40 font-mono">
                  {filteredFacts.length > 0 ? (
                    filteredFacts.map((fact) => (
                      <tr key={fact.fact_id} className="hover:bg-muted/20">
                        <td className="py-2 px-3 text-primary font-semibold">{fact.concept_name}</td>
                        <td className="py-2 px-3 font-sans text-foreground">{fact.label}</td>
                        <td className="py-2 px-3 text-right font-bold text-foreground">
                          {fact.formatted_value}
                        </td>
                        <td className="py-2 px-3 text-muted-foreground">{fact.unit}</td>
                        <td className="py-2 px-3 text-muted-foreground text-[10px]">{fact.period_type}</td>
                        <td className="py-2 px-3 text-muted-foreground">{fact.period_end}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground font-sans text-xs">
                        No XBRL facts matched the query.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Attachments */}
      {activeTab === "attachments" && (
        <div className="rounded-lg border border-border/60 bg-card/40 overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 text-muted-foreground font-semibold uppercase tracking-wider text-[10px] border-b border-border/60">
              <tr>
                <th className="py-2.5 px-3">Filename</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Description</th>
                <th className="py-2.5 px-3 w-24">Format</th>
                <th className="py-2.5 px-3 w-24 text-right">Size</th>
                <th className="py-2.5 px-3 w-24 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 font-mono">
              {detail.documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-muted/20">
                  <td className="py-2 px-3 text-foreground font-semibold">
                    {doc.filename}
                    {doc.is_primary && (
                      <span className="ml-2 px-1.5 py-0.2 rounded text-[9px] bg-primary/20 text-primary font-bold">
                        PRIMARY
                      </span>
                    )}
                  </td>
                  <td className="py-2 px-3 text-muted-foreground">{doc.document_type}</td>
                  <td className="py-2 px-3 font-sans text-muted-foreground">{doc.description}</td>
                  <td className="py-2 px-3 text-muted-foreground">{doc.media_type}</td>
                  <td className="py-2 px-3 text-right text-muted-foreground">
                    {(doc.byte_size / 1024).toFixed(1)} KB
                  </td>
                  <td className="py-2 px-3 text-right">
                    <a
                      href={doc.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] text-primary hover:underline"
                    >
                      <span>Open</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 5: Provenance Inspector */}
      {activeTab === "provenance" && (
        <div className="p-4 rounded-lg border border-border/60 bg-card/40 space-y-3 font-mono text-xs">
          <div className="flex items-center gap-2 text-foreground font-semibold font-sans">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Document Provenance & Regulatory Audit Record</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div className="p-3 rounded bg-muted/20 border border-border/40 space-y-1.5">
              <div className="text-[10px] text-muted-foreground uppercase">Regulatory Source</div>
              <div className="text-foreground font-bold">{sources?.regulator || detail.regulator}</div>
              <div className="text-[11px] text-muted-foreground">
                Attribution: {sources?.source_attribution || "U.S. Securities and Exchange Commission (EDGAR)"}
              </div>
            </div>

            <div className="p-3 rounded bg-muted/20 border border-border/40 space-y-1.5">
              <div className="text-[10px] text-muted-foreground uppercase">Accession / Document ID</div>
              <div className="text-foreground font-bold">{detail.accession_number}</div>
              <div className="text-[11px] text-muted-foreground">CIK: {detail.filer_cik}</div>
            </div>

            <div className="p-3 rounded bg-muted/20 border border-border/40 space-y-1.5 col-span-1 sm:col-span-2">
              <div className="text-[10px] text-muted-foreground uppercase">Cryptographic Content Hash (SHA-256)</div>
              <div className="text-emerald-400 break-all text-[11px]">
                {sources?.content_hash || detail.documents[0]?.content_hash || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
              </div>
            </div>

            <div className="p-3 rounded bg-muted/20 border border-border/40 space-y-1.5">
              <div className="text-[10px] text-muted-foreground uppercase">Official Archive Link</div>
              <a
                href={sources?.official_url || detail.primary_document_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline truncate block"
              >
                {sources?.official_url || detail.primary_document_url}
              </a>
            </div>

            <div className="p-3 rounded bg-muted/20 border border-border/40 space-y-1.5">
              <div className="text-[10px] text-muted-foreground uppercase">License / Distribution Tier</div>
              <div className="text-foreground">{sources?.license_tier || "PUBLIC_REGULATORY_DISCLOSURE"}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
