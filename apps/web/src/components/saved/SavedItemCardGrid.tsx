"use client";

import Link from "next/link";
import {
  ExternalLink,
  Folder,
  Pin,
  Star,
  Tag as TagIcon,
  Trash2,
} from "lucide-react";
import { Badge } from "@/design-system";
import {
  formatTargetTypeLabel,
  getAvailabilityBadgeVariant,
  getTargetTypeBadgeVariant,
} from "@/lib/saved/deepLinks";
import { SavedItem } from "@/lib/saved/types";

interface SavedItemCardGridProps {
  items: SavedItem[];
  selectedItemIds: string[];
  inspectedItemId?: string;
  onSelectItem: (id: string) => void;
  onInspectItem: (item: SavedItem) => void;
  onToggleFavorite: (item: SavedItem) => void;
  onTogglePin: (item: SavedItem) => void;
  onDeleteItem: (item: SavedItem) => void;
}

export function SavedItemCardGrid({
  items,
  selectedItemIds,
  inspectedItemId,
  onSelectItem,
  onInspectItem,
  onToggleFavorite,
  onTogglePin,
  onDeleteItem,
}: SavedItemCardGridProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className="flex-1 overflow-auto p-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
      {items.map((item) => {
        const isSelected = selectedItemIds.includes(item.saved_item_id);
        const isInspected = inspectedItemId === item.saved_item_id;

        return (
          <div
            key={item.saved_item_id}
            onClick={() => onInspectItem(item)}
            className={`flex flex-col justify-between p-3 rounded-sm border cursor-pointer transition-all ${
              isInspected
                ? "bg-atlas-surface-2 border-atlas-border-focus shadow-md"
                : isSelected
                ? "bg-atlas-surface-1 border-atlas-border-focus"
                : "bg-atlas-surface-1 border-atlas-border-default hover:border-atlas-border-default/80"
            }`}
          >
            {/* Card Header */}
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5 truncate">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onClick={(e) => e.stopPropagation()}
                    onChange={() => onSelectItem(item.saved_item_id)}
                    className="rounded border-atlas-border-default cursor-pointer"
                  />
                  <Badge variant={getTargetTypeBadgeVariant(item.target_type)} className="text-[10px]">
                    {formatTargetTypeLabel(item.target_type)}
                  </Badge>
                  {item.pinned && (
                    <span title="Pinned">
                      <Pin className="w-3 h-3 text-purple-400 shrink-0 fill-purple-400/20" />
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleFavorite(item);
                    }}
                    className="p-1 text-atlas-text-muted hover:text-amber-400"
                  >
                    <Star
                      className={`w-3.5 h-3.5 ${
                        item.favorite ? "text-amber-400 fill-amber-400" : "text-atlas-text-muted"
                      }`}
                    />
                  </button>
                  <Link
                    href={item.safe_deep_link}
                    onClick={(e) => e.stopPropagation()}
                    className="p-1 text-atlas-text-muted hover:text-blue-400"
                    title="Open Resource"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Title & Target ID */}
              <h3 className="text-xs font-semibold text-atlas-text-primary line-clamp-1 mb-0.5">
                {item.display_title}
              </h3>
              <p className="text-[10px] text-atlas-text-muted font-mono truncate mb-2">
                ID: {item.target_id}
              </p>

              {/* Note Excerpt if present */}
              {item.user_note && (
                <div className="bg-atlas-surface-0/60 p-1.5 rounded-sm border border-atlas-border-default/60 text-[11px] text-atlas-text-muted line-clamp-2 italic mb-2">
                  &ldquo;{item.user_note}&rdquo;
                </div>
              )}
            </div>

            {/* Card Footer: Tags & Status */}
            <div className="mt-2 pt-2 border-t border-atlas-border-default/60 flex flex-col gap-1.5">
              <div className="flex items-center justify-between text-[10px]">
                <Badge variant={getAvailabilityBadgeVariant(item.availability_status)} className="text-[9px]">
                  {item.availability_status.replace(/_/g, " ")}
                </Badge>
                <span className="font-mono text-atlas-text-muted capitalize">
                  {item.target_module}
                </span>
              </div>

              {/* Tag Pills */}
              {item.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {item.tags.slice(0, 3).map((t) => (
                    <span
                      key={t}
                      className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-atlas-surface-2 text-atlas-text-muted border border-atlas-border-default truncate"
                    >
                      #{t}
                    </span>
                  ))}
                  {item.tags.length > 3 && (
                    <span className="text-[9px] text-atlas-text-muted font-mono">+{item.tags.length - 3}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
