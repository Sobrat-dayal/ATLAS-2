import * as React from "react"
import { cn } from "../utils/cn"

export interface PageHeaderProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
}

export function PageHeader({ className, title, description, actions, ...props }: PageHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between pb-4 mb-4 border-b border-atlas-border-subtle", className)} {...props}>
      <div>
        <h1 className="text-xl font-semibold text-atlas-text-primary tracking-tight">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-atlas-text-muted">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex items-center space-x-2">
          {actions}
        </div>
      )}
    </div>
  )
}
