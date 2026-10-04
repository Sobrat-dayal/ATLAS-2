"use client";

import * as React from "react"
import { cn } from "../utils/cn"
import { Settings } from "lucide-react";
import { IconButton } from "../components/IconButton";
import { useSectionSettingsDrawer } from "@/hooks/settings/useSectionSettings";
import { AtlasModuleId } from "@/config/atlas-modules";
import { SECTION_SETTINGS_REGISTRY } from "@/config/section-settings";

export interface PageHeaderProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
  moduleId?: AtlasModuleId;
}

export function PageHeader({ className, title, description, actions, moduleId, ...props }: PageHeaderProps) {
  const { openDrawer } = useSectionSettingsDrawer();

  return (
    <div className={cn("flex items-center justify-between pb-4 mb-4 border-b border-atlas-border-subtle", className)} {...props}>
      <div>
        <h1 className="text-xl font-semibold text-atlas-text-primary tracking-tight">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-atlas-text-muted">{description}</p>
        )}
      </div>
      {(actions || moduleId) && (
        <div className="flex items-center space-x-2">
          {actions}
          
          {moduleId && SECTION_SETTINGS_REGISTRY[moduleId] && (
            <IconButton 
              title={`${SECTION_SETTINGS_REGISTRY[moduleId].title}`}
              onClick={() => openDrawer(moduleId)}
              variant="ghost"
              size="sm"
            >
              <Settings className="h-4 w-4" />
            </IconButton>
          )}
        </div>
      )}
    </div>
  )
}
