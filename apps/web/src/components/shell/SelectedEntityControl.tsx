"use client";

import { useSelectedEntity } from "@/hooks/entity";
import { Building2, X, AlertCircle, Loader2, FileText, Globe, Box } from "lucide-react";
import { IconButton } from "@/design-system/components/IconButton";
import { Badge } from "@/design-system/components/Badge";

export function SelectedEntityControl() {
  const { selectedEntityId, selectedEntity, status, clearSelectedEntity, refreshSelectedEntity } = useSelectedEntity();

  if (!selectedEntityId) {
    return null; // As per instruction 238: do not show a large "No Entity Selected" control
  }

  // Generic Entity Type Icon mapping
  const getIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case "company":
      case "equity":
        return <Building2 className="h-3.5 w-3.5" />;
      case "research_document":
        return <FileText className="h-3.5 w-3.5" />;
      case "country":
      case "geographic_entity":
        return <Globe className="h-3.5 w-3.5" />;
      default:
        return <Box className="h-3.5 w-3.5" />;
    }
  };

  const humanizeType = (type?: string) => {
    if (!type) return "Unknown Entity";
    return type
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  if (status === "loading") {
    return (
      <div className="flex items-center space-x-2 px-3 py-1 bg-atlas-surface-2 border border-atlas-border-default rounded-sm">
        <Loader2 className="h-3.5 w-3.5 animate-spin text-atlas-text-secondary" />
        <span className="text-xs text-atlas-text-secondary">Loading context...</span>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex items-center space-x-2 px-3 py-1 bg-red-950/30 border border-red-500/30 rounded-sm group relative">
        <AlertCircle className="h-3.5 w-3.5 text-red-400" />
        <span className="text-xs text-red-400 max-w-[120px] truncate" title="Error loading entity context">
          Failed to load context
        </span>
        <button 
          onClick={() => refreshSelectedEntity()}
          className="text-xs text-red-300 hover:text-red-100 underline decoration-red-500/50"
        >
          Retry
        </button>
        <button
          onClick={clearSelectedEntity}
          className="ml-2 text-atlas-text-secondary hover:text-atlas-text-primary"
          title="Clear selected entity"
          aria-label="Clear selected entity"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  if (status === "ready" && selectedEntity) {
    const displayName = selectedEntity.display_name || selectedEntity.canonical_name;
    const typeLabel = humanizeType(selectedEntity.entity_type);
    
    return (
      <div className="flex items-center bg-atlas-surface-2 border border-atlas-border-default rounded-sm h-7 overflow-hidden">
        {/* Type Icon & Label */}
        <div className="flex items-center bg-atlas-surface-3 px-2 h-full text-atlas-text-secondary border-r border-atlas-border-default">
          {getIcon(selectedEntity.entity_type)}
          <span className="text-[10px] font-medium tracking-wider uppercase ml-1.5 hidden md:inline-block">
            {typeLabel}
          </span>
        </div>
        
        {/* Display Name */}
        <div 
          className="px-2.5 flex items-center text-xs font-medium text-atlas-text-primary max-w-[150px] lg:max-w-[250px] truncate"
          title={`${displayName}\nID: ${selectedEntity.entity_id}`}
        >
          {displayName}
        </div>
        
        {/* Clear Action */}
        <button
          onClick={clearSelectedEntity}
          className="flex items-center justify-center h-full px-1.5 text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors border-l border-atlas-border-default"
          title="Clear selected entity"
          aria-label="Clear selected entity"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  return null;
}
