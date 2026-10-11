"use client";

import React from "react";
import Link from "next/link";
import { Info } from "lucide-react";

export interface ReservedPanelStateProps {
  title: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
  details?: string;
  actionLink?: {
    label: string;
    href: string;
  };
  notice?: string;
}

/**
 * Professional reserved-state placeholder for bottom workspace panels.
 * Honest and factual: clearly indicates that underlying execution systems
 * are reserved for future roadmap stages. Never renders fake data or loaders.
 */
export function ReservedPanelState({
  title,
  description,
  icon: Icon,
  details,
  actionLink,
  notice,
}: ReservedPanelStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[140px] text-center p-6 text-atlas-text-muted select-none">
      {Icon && (
        <div className="flex h-10 w-10 items-center justify-center rounded border border-atlas-border-default bg-atlas-surface-2 mb-3 text-atlas-text-secondary">
          <Icon className="h-5 w-5" />
        </div>
      )}

      <h4 className="text-sm font-semibold tracking-wide text-atlas-text-primary uppercase mb-1">
        {title}
      </h4>

      <p className="max-w-md text-xs text-atlas-text-secondary mb-3 leading-relaxed">
        {description}
      </p>

      {details && (
        <p className="max-w-lg text-[11px] text-atlas-text-muted mb-3 font-mono leading-normal bg-atlas-surface-2/60 border border-atlas-border-subtle rounded px-3 py-1.5">
          {details}
        </p>
      )}

      {notice && (
        <div className="flex items-center gap-1.5 text-[11px] text-atlas-text-muted/80 mb-3 max-w-md">
          <Info className="h-3 w-3 shrink-0 text-atlas-accent/70" />
          <span>{notice}</span>
        </div>
      )}

      {actionLink && (
        <Link
          href={actionLink.href}
          className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium text-atlas-accent bg-atlas-surface-hover hover:bg-atlas-surface-selected border border-atlas-border-default rounded transition-colors"
        >
          {actionLink.label} &rarr;
        </Link>
      )}
    </div>
  );
}
