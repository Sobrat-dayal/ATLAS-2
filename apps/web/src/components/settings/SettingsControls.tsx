"use client";

import React, { ReactNode } from "react";
import { SettingsCategory } from "@/config/settings-registry";
import { cn } from "@/design-system/utils/cn";

interface SettingsPageProps {
  category: SettingsCategory;
  children: ReactNode;
}

export function SettingsPage({ category, children }: SettingsPageProps) {
  return (
    <div className="w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-atlas-text-primary tracking-tight mb-2">
          {category.label}
        </h1>
        <p className="text-atlas-text-muted text-sm max-w-2xl">
          {category.description}
        </p>
      </div>
      <div className="space-y-8">
        {children}
      </div>
    </div>
  );
}

interface SettingsGroupProps {
  title?: string;
  description?: string;
  children: ReactNode;
  danger?: boolean;
}

export function SettingsGroup({ title, description, children, danger }: SettingsGroupProps) {
  return (
    <div className={`space-y-4 ${danger ? 'p-4 border border-red-500/20 bg-red-500/5 rounded-md' : ''}`}>
      {(title || description) && (
        <div className="border-b border-atlas-border-default pb-2">
          {title && <h3 className={`text-base font-medium ${danger ? 'text-red-500' : 'text-atlas-text-primary'}`}>{title}</h3>}
          {description && <p className="text-sm text-atlas-text-muted mt-1">{description}</p>}
        </div>
      )}
      <div className="space-y-0 border border-atlas-border-default rounded-md overflow-hidden bg-atlas-bg-1">
        {React.Children.map(children, (child, i) => (
          <div key={i} className={i > 0 ? "border-t border-atlas-border-default" : ""}>
            {child}
          </div>
        ))}
      </div>
    </div>
  );
}

interface SettingsRowProps {
  label: string;
  description?: string;
  children?: ReactNode;
  badge?: ReactNode;
  vertical?: boolean;
  className?: string;
}

export function SettingsRow({ label, description, children, badge, vertical, className }: SettingsRowProps) {
  if (vertical) {
    return (
      <div className="p-4 flex flex-col space-y-3">
        <div className="flex flex-col space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-atlas-text-primary">{label}</span>
            {badge && <div>{badge}</div>}
          </div>
          {description && <span className="text-xs text-atlas-text-muted">{description}</span>}
        </div>
        <div className="w-full">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className={cn("p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4", className)}>
      <div className="flex flex-col space-y-1 flex-1 pr-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-atlas-text-primary">{label}</span>
          {badge && <div>{badge}</div>}
        </div>
        {description && <span className="text-xs text-atlas-text-muted max-w-[85%]">{description}</span>}
      </div>
      <div className="flex-shrink-0 min-w-[200px] flex justify-end">
        {children}
      </div>
    </div>
  );
}

export function SettingsFoundationState({ message = "Not configured" }: { message?: string }) {
  return (
    <span className="text-sm text-atlas-text-muted px-3 py-1 bg-atlas-surface-2 rounded-md border border-atlas-border-default whitespace-nowrap">
      {message}
    </span>
  );
}
