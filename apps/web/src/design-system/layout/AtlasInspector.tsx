"use client";

import * as React from "react";
import { PanelImperativeHandle } from "react-resizable-panels";
import { AtlasPanel, AtlasPanelProps } from "./AtlasPanel";
import { PanelHeader } from "../components/Panel";
import { IconButton } from "../components/IconButton";
import { PanelRightClose, PanelRightOpen, Maximize2 } from "lucide-react";
import { getPanelCollapsedState, setPanelCollapsedState } from "./AtlasLayoutStorage";

export interface AtlasInspectorProps extends Omit<AtlasPanelProps, 'id'> {
  id: string;
  title?: string;
  defaultCollapsed?: boolean;
  onCollapseChange?: (collapsed: boolean) => void;
  actions?: React.ReactNode;
}

export function AtlasInspector({
  id,
  title,
  defaultCollapsed = false,
  onCollapseChange,
  actions,
  children,
  className,
  ...props
}: AtlasInspectorProps) {
  const panelRef = React.useRef<PanelImperativeHandle>(null);
  const [isClient, setIsClient] = React.useState(false);
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);

  React.useEffect(() => {
    setIsClient(true);
    const saved = getPanelCollapsedState(id, defaultCollapsed);
    setIsCollapsed(saved);
    if (saved && panelRef.current) {
      panelRef.current.collapse();
    }
  }, [id, defaultCollapsed]);

  const toggleCollapse = () => {
    if (!panelRef.current) return;
    
    const willCollapse = !isCollapsed;
    setIsCollapsed(willCollapse);
    setPanelCollapsedState(id, willCollapse);
    
    if (willCollapse) {
      panelRef.current.collapse();
    } else {
      panelRef.current.expand();
    }
    
    if (onCollapseChange) onCollapseChange(willCollapse);
  };

  // Safe defaults
  const minSize = props.minSize ?? 15; // Usually ~ 200px on 1440 screen
  const maxSize = props.maxSize ?? 40; // Max 40%

  return (
    <AtlasPanel
      ref={panelRef}
      id={id}
      collapsible
      collapsedSize={0}
      minSize={minSize}
      maxSize={maxSize}
      onResize={() => {
        if (panelRef.current) {
          setIsCollapsed(panelRef.current.isCollapsed());
        }
      }}
      className={className}
      {...props}
    >
      <div className="flex h-full flex-col bg-atlas-surface-1 border-l border-atlas-border-default">
        {title && (
          <PanelHeader 
            title={title}
            actions={
              <>
                {actions}
                <IconButton 
                  variant="ghost" 
                  size="xs" 
                  onClick={toggleCollapse} 
                  title="Collapse Inspector"
                  aria-label="Collapse Inspector"
                >
                  <PanelRightClose className="w-4 h-4" />
                </IconButton>
              </>
            }
          />
        )}
        <div className="flex-1 overflow-auto custom-scrollbar">
          {children}
        </div>
      </div>
    </AtlasPanel>
  );
}
