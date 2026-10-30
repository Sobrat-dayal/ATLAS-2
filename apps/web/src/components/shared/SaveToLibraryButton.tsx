"use client";

import { useState } from "react";
import { Bookmark, Check } from "lucide-react";
import { Button } from "@/design-system";
import { saveItem } from "@/lib/saved/api";
import { SavedTargetType } from "@/lib/saved/types";
import { SaveToLibraryDialog } from "./SaveToLibraryDialog";

interface SaveToLibraryButtonProps {
  targetType: SavedTargetType;
  targetId: string;
  defaultTitle?: string;
  targetRevisionId?: string;
  viewConfigurationId?: string;
  variant?: "primary" | "secondary" | "ghost";
  size?: "xs" | "sm" | "md";
  className?: string;
  onSaved?: () => void;
}

export function SaveToLibraryButton({
  targetType,
  targetId,
  defaultTitle,
  targetRevisionId,
  viewConfigurationId,
  variant = "secondary",
  size = "xs",
  className = "",
  onSaved,
}: SaveToLibraryButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Quick 1-click save
  const handleQuickSave = async (e: React.MouseEvent) => {
    // If shift or alt is pressed, or if already saved, open advanced dialog
    if (e.shiftKey || e.altKey) {
      setIsDialogOpen(true);
      return;
    }

    if (isSaved) {
      setIsDialogOpen(true);
      return;
    }

    setIsSaving(true);
    try {
      await saveItem({
        target_type: targetType,
        target_id: targetId,
        target_revision_id: targetRevisionId,
        display_title_override: defaultTitle,
        view_configuration_id: viewConfigurationId,
      });
      setIsSaved(true);
      onSaved?.();
    } catch (err: unknown) {
      // If error or already exists, fallback to open dialog
      setIsDialogOpen(true);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        onClick={handleQuickSave}
        disabled={isSaving}
        className={`flex items-center gap-1.5 text-xs ${className} ${
          isSaved ? "text-blue-400 border-blue-500/30 bg-blue-500/10" : ""
        }`}
        title={isSaved ? "Saved to Library (Click to edit)" : "Save to Library (Shift+Click for options)"}
      >
        {isSaved ? (
          <Check className="w-3.5 h-3.5 text-blue-400" />
        ) : (
          <Bookmark className={`w-3.5 h-3.5 ${isSaving ? "animate-pulse" : ""}`} />
        )}
        <span>{isSaved ? "Saved" : isSaving ? "Saving..." : "Save"}</span>
      </Button>

      <SaveToLibraryDialog
        isOpen={isDialogOpen}
        targetType={targetType}
        targetId={targetId}
        defaultTitle={defaultTitle}
        targetRevisionId={targetRevisionId}
        viewConfigurationId={viewConfigurationId}
        onClose={() => setIsDialogOpen(false)}
        onSuccess={() => {
          setIsSaved(true);
          onSaved?.();
        }}
      />
    </>
  );
}
