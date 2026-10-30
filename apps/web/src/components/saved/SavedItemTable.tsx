"use client";

import Link from "next/link";
import {
  ExternalLink,
  Info,
  Pin,
  Star,
  Trash2,
} from "lucide-react";
import { Badge } from "@/design-system";
import {
  formatTargetTypeLabel,
  getAvailabilityBadgeVariant,
  getTargetTypeBadgeVariant,
} from "@/lib/saved/deepLinks";
import { SavedItem } from "@/lib/saved/types";

interface SavedItemTableProps {
  items: SavedItem[];
  selectedItemIds: string[];
  inspectedItemId?: string;
  onSelectItem: (id: string) => void;
  onSelectAll: () => void;
  onInspectItem: (item: SavedItem) => void;
  onToggleFavorite: (item: SavedItem) => void;
  onTogglePin: (item: SavedItem) => void;
  onDeleteItem: (item: SavedItem) => void;
}

export function SavedItemTable({
  items,
  selectedItemIds,
  inspectedItemId,
  onSelectItem,
  onSelectAll,
  onInspectItem,
  onToggleFavorite,
  onTogglePin,
  onDeleteItem,
}: SavedItemTableProps) {
  const allSelected = items.length > 0 && selectedItemIds.length === items.length;

  if (items.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-atlas-text-muted">
        <div className="w-10 h-10 rounded-full bg-atlas-surface-1 border border-atlas-border-default flex items-center justify-center mb-2">
          <Info className="w-5 h-5 text-atlas-text-muted" />
        </div>
        <p className="text-sm font-medium text-atlas-text-primary">No saved items found</p>
        <p className="text-xs text-atlas-text-muted mt-1 max-w-sm">
          Bookmark financial instruments, reports, charts, screeners, or portfolio views using the Save action across ATLAS.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto">
      <table className="w-full text-left border-collapse text-xs">
        <thead className="bg-atlas-surface-1 border-b border-atlas-border-default sticky top-0 z-10 text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider">
          <tr>
            <th className="w-8 px-3 py-2 text-center">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={onSelectAll}
                className="rounded border-atlas-border-default cursor-pointer"
              />
            </th>
            <th className="w-7 px-1 py-2 text-center">Fav</th>
            <th className="px-3 py-2">Resource</th>
            <th className="px-3 py-2">Type</th>
            <th className="px-3 py-2">Module</th>
            <th className="px-3 py-2 hidden md:table-cell">Tags</th>
            <th className="px-3 py-2">Status</th>
            <th className="px-3 py-2 hidden lg:table-cell">Saved At</th>
            <th className="w-20 px-3 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-atlas-border-default/60">
          {items.map((item) => {
            const isSelected = selectedItemIds.includes(item.saved_item_id);
            const isInspected = inspectedItemId === item.saved_item_id;

            return (
              <tr
                key={item.saved_item_id}
                onClick={() => onInspectItem(item)}
                className={`group cursor-pointer transition-colors ${
                  isInspected
                    ? "bg-atlas-surface-2"
                    : isSelected
                    ? "bg-atlas-surface-1"
                    : "hover:bg-atlas-surface-1/60"
                }`}
              >
                {/* Checkbox */}
                <td
                  className="px-3 py-2 text-center"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectItem(item.saved_item_id);
                  }}
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onSelectItem(item.saved_item_id)}
                    className="rounded border-atlas-border-default cursor-pointer"
                  />
                </td>

                {/* Favorite Toggle */}
                <td
                  className="px-1 py-2 text-center"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleFavorite(item);
                  }}
                >
                  <button
                    type="button"
                    className="p-1 text-atlas-text-muted hover:text-amber-400"
                    title={item.favorite ? "Unfavorite" : "Favorite"}
                  >
                    <Star
                      className={`w-3.5 h-3.5 ${
                        item.favorite ? "text-amber-400 fill-amber-400" : "text-atlas-text-muted"
                      }`}
                    />
                  </button>
                </td>

                {/* Resource Title & Deep Link */}
                <td className="px-3 py-2 max-w-[280px]">
                  <div className="flex items-center gap-1.5 truncate">
                    {item.pinned && (
                      <span title="Pinned item">
                        <Pin className="w-3 h-3 text-purple-400 shrink-0 fill-purple-400/20" />
                      </span>
                    )}
                    <span className="font-medium text-atlas-text-primary truncate">
                      {item.display_title}
                    </span>
                  </div>
                  <div className="text-[10px] text-atlas-text-muted truncate font-mono">
                    ID: {item.target_id}
                    {item.target_revision_id && ` · rev:${item.target_revision_id}`}
                  </div>
                </td>

                {/* Type Badge */}
                <td className="px-3 py-2 whitespace-nowrap">
                  <Badge variant={getTargetTypeBadgeVariant(item.target_type)} className="text-[10px]">
                    {formatTargetTypeLabel(item.target_type)}
                  </Badge>
                </td>

                {/* Module */}
                <td className="px-3 py-2 whitespace-nowrap text-atlas-text-muted font-mono text-[11px] capitalize">
                  {item.target_module}
                </td>

                {/* Tags */}
                <td className="px-3 py-2 hidden md:table-cell max-w-[160px]">
                  <div className="flex flex-wrap gap-1 truncate">
                    {item.tags.length === 0 ? (
                      <span className="text-[10px] text-atlas-text-muted/50">—</span>
                    ) : (
                      item.tags.slice(0, 2).map((t) => (
                        <span
                          key={t}
                          className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-atlas-surface-2 text-atlas-text-muted border border-atlas-border-default truncate"
                        >
                          {t}
                        </span>
                      ))
                    )}
                    {item.tags.length > 2 && (
                      <span className="text-[9px] text-atlas-text-muted font-mono">+{item.tags.length - 2}</span>
                    )}
                  </div>
                </td>

                {/* Runtime Availability Status */}
                <td className="px-3 py-2 whitespace-nowrap">
                  <Badge variant={getAvailabilityBadgeVariant(item.availability_status)} className="text-[10px]">
                    {item.availability_status.replace(/_/g, " ")}
                  </Badge>
                </td>

                {/* Saved At */}
                <td className="px-3 py-2 hidden lg:table-cell whitespace-nowrap text-[11px] text-atlas-text-muted font-mono">
                  {new Date(item.saved_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </td>

                {/* Actions */}
                <td
                  className="px-3 py-2 text-right whitespace-nowrap"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center justify-end gap-1">
                    <Link
                      href={item.safe_deep_link}
                      className="p-1 text-atlas-text-muted hover:text-blue-400 rounded"
                      title="Open Original Resource"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                    <button
                      type="button"
                      onClick={() => onTogglePin(item)}
                      className={`p-1 rounded ${
                        item.pinned
                          ? "text-purple-400"
                          : "text-atlas-text-muted hover:text-atlas-text-primary"
                      }`}
                      title={item.pinned ? "Unpin" : "Pin"}
                    >
                      <Pin className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => onDeleteItem(item)}
                      className="p-1 text-atlas-text-muted hover:text-rose-400 rounded"
                      title="Remove from Saved"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
