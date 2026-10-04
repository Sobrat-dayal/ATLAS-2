import * as React from "react"
import { cn } from "../utils/cn"

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const Panel = React.forwardRef<HTMLDivElement, PanelProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-md border border-atlas-border-default bg-atlas-surface-1 overflow-hidden",
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
Panel.displayName = "Panel"

export interface PanelHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

const PanelHeader = React.forwardRef<HTMLDivElement, PanelHeaderProps>(
  ({ className, title, subtitle, actions, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center justify-between px-4 py-3 border-b border-atlas-border-default",
          className
        )}
        {...props}
      >
        <div>
          <h3 className="text-sm font-medium text-atlas-text-primary">{title}</h3>
          {subtitle && (
            <p className="text-xs text-atlas-text-muted mt-0.5">{subtitle}</p>
          )}
        </div>
        {actions && <div className="flex items-center space-x-2">{actions}</div>}
      </div>
    )
  }
)
PanelHeader.displayName = "PanelHeader"

export interface PanelContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  noPadding?: boolean;
}

const PanelContent = React.forwardRef<HTMLDivElement, PanelContentProps>(
  ({ className, children, noPadding = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(!noPadding && "p-4", className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)
PanelContent.displayName = "PanelContent"

export { Panel, PanelHeader, PanelContent }
