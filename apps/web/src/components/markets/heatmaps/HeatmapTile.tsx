"use client";

import React, { useState } from "react";
import {
  HeatmapLeafNode,
  TreemapRect,
  formatMarketCap,
  formatPrice,
  formatSignedPercent,
  getHeatmapTileColor,
} from "@/lib/markets/heatmaps";

interface HeatmapTileProps {
  rect: TreemapRect<HeatmapLeafNode>;
  isSelected: boolean;
  onSelect: (node: HeatmapLeafNode) => void;
  weightUnit?: string | null;
}

export function HeatmapTile({
  rect,
  isSelected,
  onSelect,
  weightUnit = "USD",
}: HeatmapTileProps) {
  const [isHovered, setIsHovered] = useState(false);
  const node = rect.data;
  const colorStyle = getHeatmapTileColor(node.percent_change);

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`${node.symbol}: ${formatSignedPercent(node.percent_change)}, ${node.display_name}`}
      onClick={() => onSelect(node)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(node);
        }
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: "absolute",
        left: `${rect.x}px`,
        top: `${rect.y}px`,
        width: `${rect.width}px`,
        height: `${rect.height}px`,
        backgroundColor: colorStyle.backgroundColor,
        borderColor: isSelected
          ? "rgb(255, 255, 255)"
          : isHovered
          ? "rgba(255, 255, 255, 0.7)"
          : colorStyle.borderColor,
      }}
      className={`group relative overflow-hidden rounded-[3px] border transition-all duration-150 cursor-pointer select-none flex flex-col justify-center items-center p-1 text-center ${
        isSelected ? "ring-2 ring-white z-20 shadow-lg scale-[1.01]" : isHovered ? "z-10 shadow-md" : "z-0"
      }`}
    >
      {/* Tile Core Content */}
      {!rect.isTiny ? (
        <>
          <span
            className="font-bold tracking-tight leading-none text-xs sm:text-sm font-mono truncate max-w-full"
            style={{ color: colorStyle.textColor }}
          >
            {node.symbol}
          </span>

          <span
            className="font-semibold text-[11px] sm:text-xs font-mono mt-0.5"
            style={{ color: colorStyle.textColor }}
          >
            {formatSignedPercent(node.percent_change)}
          </span>

          {rect.canShowName && (
            <span
              className="text-[9px] font-sans truncate max-w-full opacity-80 mt-0.5"
              style={{ color: colorStyle.textColor }}
            >
              {node.display_name}
            </span>
          )}
        </>
      ) : (
        /* Tiny Tile View: minimal ticker label */
        <span
          className="font-bold text-[9px] font-mono leading-none truncate max-w-full"
          style={{ color: colorStyle.textColor }}
        >
          {rect.width >= 35 ? node.symbol : ""}
        </span>
      )}

      {/* Hover Detail Tooltip */}
      {isHovered && (
        <div
          className="pointer-events-none absolute bottom-full mb-1 left-1/2 -translate-x-1/2 z-50 w-64 p-2.5 rounded-md bg-zinc-950/95 text-zinc-100 border border-zinc-700 shadow-2xl text-left backdrop-blur-md"
        >
          <div className="flex items-center justify-between gap-2 border-b border-zinc-800 pb-1.5 mb-1.5">
            <div>
              <span className="font-bold text-sm font-mono text-white">{node.symbol}</span>
              <span className="text-[10px] text-zinc-400 block truncate max-w-[150px]">
                {node.display_name}
              </span>
            </div>
            <span
              className={`px-1.5 py-0.5 rounded text-xs font-mono font-bold ${
                (Number(node.percent_change) || 0) >= 0 ? "text-emerald-400 bg-emerald-950" : "text-red-400 bg-red-950"
              }`}
            >
              {formatSignedPercent(node.percent_change)}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-[11px]">
            <div>
              <span className="text-zinc-400 block text-[9px] uppercase tracking-wider">Price</span>
              <span className="font-mono text-zinc-200">
                {formatPrice(node.current_price, node.currency)}
              </span>
            </div>
            <div>
              <span className="text-zinc-400 block text-[9px] uppercase tracking-wider">Prev Reference</span>
              <span className="font-mono text-zinc-300">
                {formatPrice(node.reference_price, node.currency)}
              </span>
            </div>

            {node.weight_value && (
              <div className="col-span-2 pt-1 border-t border-zinc-800/60">
                <span className="text-zinc-400 text-[9px] uppercase tracking-wider">Market Cap: </span>
                <span className="font-mono font-semibold text-zinc-200">
                  {formatMarketCap(node.weight_value, weightUnit || "USD")}
                </span>
                {node.normalized_weight && (
                  <span className="text-zinc-400 text-[10px] ml-1">
                    ({(Number(node.normalized_weight) * 100).toFixed(1)}% of universe)
                  </span>
                )}
              </div>
            )}

            {node.sector && (
              <div className="col-span-2">
                <span className="text-zinc-400 text-[9px] uppercase tracking-wider">Sector: </span>
                <span className="text-zinc-300 font-medium">{node.sector}</span>
              </div>
            )}

            <div className="col-span-2 pt-1 border-t border-zinc-800/60 flex items-center justify-between text-[10px] text-zinc-500">
              <span>{node.exchange_or_venue} • {node.provider}</span>
              <span>{node.delay_status}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
