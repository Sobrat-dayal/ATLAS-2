"use client";

import React, { useId } from "react";
import { cn } from "@/design-system/utils/cn";

export interface HomeWidgetSurfaceProps {
  id?: string;
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  contentClassName?: string;
  noPadding?: boolean;
}

export function HomeWidgetSurface({
  id,
  title,
  subtitle,
  badge,
  actions,
  children,
  className,
  contentClassName,
  noPadding = false,
}: HomeWidgetSurfaceProps) {
  const generatedId = useId();
  const headingId = id ? `widget-heading-${id}` : `widget-heading-${generatedId}`;

  return (
    <section
      aria-labelledby={headingId}
      className={cn(
        "rounded-md border border-atlas-border-default bg-atlas-surface-1 flex flex-col overflow-hidden",
        className
      )}
    >
      {/* Widget Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2/60">
        <div className="min-w-0 pr-2">
          <div className="flex items-center gap-2">
            <h2
              id={headingId}
              className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary truncate"
            >
              {title}
            </h2>
            {badge}
          </div>
          {subtitle && (
            <p className="text-[11px] text-atlas-text-muted mt-0.5 truncate">
              {subtitle}
            </p>
          )}
        </div>

        {actions && (
          <div className="flex items-center gap-2 flex-shrink-0">
            {actions}
          </div>
        )}
      </div>

      {/* Widget Content */}
      <div className={cn("flex-1 min-w-0", !noPadding && "p-3.5", contentClassName)}>
        {children}
      </div>
    </section>
  );
}
