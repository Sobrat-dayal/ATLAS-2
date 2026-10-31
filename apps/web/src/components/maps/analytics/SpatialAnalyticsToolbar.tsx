/**
 * Spatial Analytics Toolbar Toggle Button (Stage 131).
 */

import React from 'react';
import { Sliders } from 'lucide-react';

interface SpatialAnalyticsToolbarProps {
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export function SpatialAnalyticsToolbar({
  isOpen,
  onToggle,
  className = '',
}: SpatialAnalyticsToolbarProps) {
  return (
    <button
      onClick={onToggle}
      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono border transition-all ${
        isOpen
          ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300 shadow-sm'
          : 'bg-zinc-900/90 border-zinc-800 text-zinc-300 hover:text-zinc-100 hover:bg-zinc-800'
      } ${className}`}
      title="Toggle Spatial Analytics Engine (deck.gl + H3)"
      aria-label="Toggle Spatial Analytics"
    >
      <Sliders className="w-3.5 h-3.5 text-emerald-400" />
      <span>Analytics</span>
    </button>
  );
}

