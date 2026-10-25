"use client";

import { useState } from "react";
import { Badge, Button } from "@/design-system";
import { CompanyOverviewResponse } from "@/lib/companies/types";
import { useSelectedEntity } from "@/hooks/entity";
import { Building2, Check, Copy, ExternalLink, Globe, MapPin, Tag } from "lucide-react";

export interface CompanyHeaderProps {
  overview: CompanyOverviewResponse;
}

export function CompanyHeader({ overview }: CompanyHeaderProps) {
  const { identity, classification, geography } = overview;
  const { selectedEntityId, selectEntity } = useSelectedEntity();
  const [copied, setCopied] = useState(false);

  const isGloballySelected = selectedEntityId === identity.company_entity_id;

  const handleCopyId = () => {
    navigator.clipboard.writeText(identity.company_entity_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleSelectEntity = () => {
    selectEntity(identity.company_entity_id);
  };

  return (
    <div className="bg-atlas-surface-1 border-b border-atlas-border-default px-6 py-4">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Left: Identity & Badges */}
        <div className="space-y-1.5">
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-atlas-text-muted" aria-hidden="true" />
              <h1 className="text-xl font-bold tracking-tight text-atlas-text-primary">
                {identity.display_name}
              </h1>
            </div>

            {identity.status && (
              <Badge
                variant={identity.status === "active" ? "positive" : "default"}
                className="uppercase tracking-wider font-mono text-[10px]"
              >
                {identity.status}
              </Badge>
            )}

            {identity.organization_type && (
              <Badge variant="outline" className="font-mono text-[10px]">
                {identity.organization_type.replace(/_/g, " ")}
              </Badge>
            )}

            {isGloballySelected ? (
              <Badge variant="primary" className="font-mono text-[10px]">
                Selected Entity
              </Badge>
            ) : null}
          </div>

          {/* Legal Name & Aliases */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-atlas-text-muted">
            {identity.legal_name && identity.legal_name !== identity.display_name && (
              <span>
                Legal: <span className="text-atlas-text-secondary font-medium">{identity.legal_name}</span>
              </span>
            )}

            {identity.short_name && identity.short_name !== identity.display_name && (
              <span>
                Short: <span className="text-atlas-text-secondary">{identity.short_name}</span>
              </span>
            )}

            {identity.aliases && identity.aliases.length > 0 && (
              <span className="hidden sm:inline">
                Aliases: <span className="text-atlas-text-secondary">{identity.aliases.slice(0, 3).join(", ")}</span>
              </span>
            )}

            <button
              type="button"
              onClick={handleCopyId}
              title={`UUID: ${identity.company_entity_id}`}
              className="inline-flex items-center gap-1 font-mono text-[11px] text-atlas-text-muted hover:text-atlas-text-primary transition-colors focus:outline-none"
            >
              <span>{identity.company_entity_id.substring(0, 8)}...</span>
              {copied ? <Check className="w-3 h-3 text-atlas-positive" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>

          {/* Classification & Country Quick Tags */}
          <div className="flex flex-wrap items-center gap-3 pt-1 text-xs text-atlas-text-secondary">
            {classification.sector_name && (
              <span className="inline-flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-atlas-text-muted" aria-hidden="true" />
                <span>{classification.sector_name}</span>
                {classification.industry_name && (
                  <span className="text-atlas-text-muted">· {classification.industry_name}</span>
                )}
              </span>
            )}

            {geography.headquarters_country && (
              <span className="inline-flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-atlas-text-muted" aria-hidden="true" />
                <span>
                  {geography.headquarters_city ? `${geography.headquarters_city}, ` : ""}
                  {geography.headquarters_country}
                </span>
                {geography.country_code && (
                  <span className="font-mono text-[10px] text-atlas-text-muted">({geography.country_code})</span>
                )}
              </span>
            )}
          </div>
        </div>

        {/* Right: Actions & Links */}
        <div className="flex flex-wrap items-center gap-2.5">
          {identity.website_url && (
            <a
              href={identity.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-atlas-border-default rounded-sm text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors"
            >
              <Globe className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Official Website</span>
              <ExternalLink className="w-3 h-3 text-atlas-text-muted" aria-hidden="true" />
            </a>
          )}

          <Button
            size="sm"
            variant={isGloballySelected ? "secondary" : "primary"}
            onClick={handleToggleSelectEntity}
            className="text-xs"
          >
            {isGloballySelected ? "Selected in Terminal" : "Set Selected Entity"}
          </Button>
        </div>
      </div>
    </div>
  );
}
