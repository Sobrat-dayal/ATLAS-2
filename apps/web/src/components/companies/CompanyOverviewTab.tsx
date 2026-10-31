"use client";

import { CompanyOverviewResponse } from "@/lib/companies/types";
import { Badge } from "@/design-system";
import {
  Building,
  CheckCircle2,
  FileBadge,
  HelpCircle,
  Layers,
  MapPin,
  Tag,
} from "lucide-react";

export interface CompanyOverviewTabProps {
  overview: CompanyOverviewResponse;
}

export function CompanyOverviewTab({ overview }: CompanyOverviewTabProps) {
  const { description, identifiers, geography, classification, market_summary } = overview;

  return (
    <div className="space-y-6">
      {/* 1. Corporate Description */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4">
        <div className="flex items-center gap-2 mb-2.5 pb-2 border-b border-atlas-border-subtle">
          <Building className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
            Corporate Description & Profile
          </h2>
        </div>
        {description ? (
          <p className="text-sm text-atlas-text-secondary leading-relaxed font-sans max-w-4xl">
            {description}
          </p>
        ) : (
          <div className="flex items-center gap-2 text-xs text-atlas-text-muted py-2 italic">
            <HelpCircle className="w-4 h-4" />
            <span>Description unavailable in canonical records.</span>
          </div>
        )}
      </div>

      {/* 2. Three Column Details Strip: Identifiers, Classification, Geography */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Identifiers Card */}
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <FileBadge className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
                Corporate Identifiers
              </h3>
            </div>
            <span className="text-[11px] text-atlas-text-muted">Stage 21 Registry</span>
          </div>

          {identifiers && identifiers.length > 0 ? (
            <div className="divide-y divide-atlas-border-subtle text-xs">
              {identifiers.map((ident) => (
                <div key={ident.scheme_key + ident.value} className="py-2 flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-atlas-text-primary">{ident.scheme_name}</div>
                    <div className="font-mono text-[11px] text-atlas-text-muted">{ident.scheme_key}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-medium text-atlas-text-secondary">{ident.value}</div>
                    <div className="inline-flex items-center gap-1 text-[10px] text-atlas-positive">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      <span>{ident.verification_status}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-atlas-text-muted py-4 italic text-center">
              No verified corporate identifiers registered.
            </div>
          )}
        </div>

        {/* Classification Card */}
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
                Industry Classification
              </h3>
            </div>
            <Badge variant="outline" className="font-mono text-[10px]">
              {classification.taxonomy}
            </Badge>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <div className="text-atlas-text-muted">Sector</div>
              <div className="font-medium text-atlas-text-primary text-sm mt-0.5">
                {classification.sector_name || "Unclassified"}
              </div>
            </div>

            <div>
              <div className="text-atlas-text-muted">Industry</div>
              <div className="font-medium text-atlas-text-secondary mt-0.5">
                {classification.industry_name || "Unclassified"}
              </div>
            </div>

            <div className="pt-2 border-t border-atlas-border-subtle grid grid-cols-2 gap-2 text-[11px] text-atlas-text-muted font-mono">
              <div>
                <span>Taxonomy Version:</span>{" "}
                <span className="text-atlas-text-secondary">{classification.taxonomy_version || "2023"}</span>
              </div>
              <div className="text-right">
                <span>Source:</span> <span className="text-atlas-text-secondary">{classification.source}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Geography Card */}
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
                Corporate Geography
              </h3>
            </div>
            <span className="text-[11px] text-atlas-text-muted">Stage 19 Geographic</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <div className="text-atlas-text-muted">Headquarters</div>
              <div className="font-medium text-atlas-text-primary text-sm mt-0.5">
                {geography.headquarters_city ? `${geography.headquarters_city}, ` : ""}
                {geography.headquarters_country || "Unavailable"}
              </div>
            </div>

            {geography.address_text && (
              <div>
                <div className="text-atlas-text-muted">Physical Facility</div>
                <div className="text-atlas-text-secondary font-mono text-[11px] mt-0.5">
                  {geography.address_text}
                </div>
              </div>
            )}

            <div className="pt-2 border-t border-atlas-border-subtle grid grid-cols-2 gap-2 text-[11px] text-atlas-text-muted">
              <div>
                <span>Incorporation:</span>{" "}
                <span className="text-atlas-text-secondary">
                  {geography.incorporation_jurisdiction || "Unavailable"}
                </span>
              </div>
              <div className="text-right">
                <span>Country Code:</span>{" "}
                <span className="font-mono text-atlas-text-secondary">{geography.country_code || "N/A"}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-atlas-border-subtle">
              <a
                href={`/maps?company=${encodeURIComponent(overview.company_entity_id)}`}
                className="w-full flex items-center justify-center gap-1.5 py-1.5 px-2 bg-sky-950/40 hover:bg-sky-900/40 border border-sky-800/40 rounded text-[11px] text-sky-400 font-semibold transition-colors"
              >
                <MapPin className="w-3 h-3" />
                <span>View Geographic Footprint</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Market Summary Strip */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
              Market Issuance & Capitalization Context
            </h3>
          </div>
          <span className="text-[11px] text-atlas-text-muted">Non-Synthetic Data</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <div className="text-atlas-text-muted">Market Capitalization</div>
            <div className="text-base font-bold text-atlas-text-primary font-mono mt-0.5">
              {market_summary.market_cap || "Unavailable"}
            </div>
            {market_summary.market_cap_methodology && (
              <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                Method: {market_summary.market_cap_methodology}
              </div>
            )}
          </div>

          <div>
            <div className="text-atlas-text-muted">Primary Reference Security</div>
            <div className="text-base font-bold text-atlas-text-primary font-mono mt-0.5">
              {market_summary.reference_symbol || "None"}
            </div>
            {market_summary.reference_venue && (
              <div className="text-[10px] text-atlas-text-muted mt-0.5">
                Venue: {market_summary.reference_venue}
              </div>
            )}
          </div>

          <div>
            <div className="text-atlas-text-muted">Listed Equity Securities</div>
            <div className="text-base font-bold text-atlas-text-primary font-mono mt-0.5">
              {market_summary.listed_equity_count}
            </div>
            <div className="text-[10px] text-atlas-text-muted mt-0.5">Common / Preferred / ADRs</div>
          </div>

          <div>
            <div className="text-atlas-text-muted">Corporate Bonds</div>
            <div className="text-base font-bold text-atlas-text-primary font-mono mt-0.5">
              {market_summary.bond_count}
            </div>
            <div className="text-[10px] text-atlas-text-muted mt-0.5">Verified Debt Issuance</div>
          </div>
        </div>
      </div>
    </div>
  );
}
