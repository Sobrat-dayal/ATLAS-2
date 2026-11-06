"use client";

import React, { useState } from "react";
import type { MarketplaceItem } from "@/lib/ecosystem/types";

interface MarketplaceCatalogProps {
  initialItems?: MarketplaceItem[];
}

export const MarketplaceCatalog: React.FC<MarketplaceCatalogProps> = ({
  initialItems = [],
}) => {
  const [items] = useState<MarketplaceItem[]>(initialItems);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedItem, setSelectedItem] = useState<MarketplaceItem | null>(null);
  const [installNotice, setInstallNotice] = useState<string | null>(null);

  const filtered = items.filter((item) => {
    const matchesQuery =
      searchQuery === "" ||
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesKind = selectedCategory === "ALL" || item.kind === selectedCategory;
    return matchesQuery && matchesKind;
  });

  const handleInstallClick = (item: MarketplaceItem) => {
    setInstallNotice(
      `Installation review initiated for '${item.name}'. Please grant requested permissions: [${item.required_permissions.join(", ")}].`
    );
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="space-y-3 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-100">
            Institutional Marketplace Catalog
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Discover verified AI agents, teams, workflows, and plugins. Authentic records only with zero fabricated ratings or adoption metrics.
          </p>
        </div>

        <div className="flex flex-col md:flex-row items-center gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search catalog by name, capability, or keyword..."
            className="w-full md:w-80 rounded border border-zinc-800 bg-black px-3 py-1.5 text-xs text-zinc-200 font-mono"
          />

          <div className="flex rounded border border-zinc-800 bg-[#111] p-0.5 text-xs overflow-x-auto w-full md:w-auto">
            {["ALL", "AGENT", "TEAM", "WORKFLOW", "MCP", "PLUGIN"].map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`rounded px-2.5 py-1 font-medium transition whitespace-nowrap ${
                  selectedCategory === cat
                    ? "bg-zinc-800 text-zinc-100 shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {cat === "ALL" ? "All" : cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {installNotice && (
        <div className="rounded border border-blue-900 bg-blue-950/40 p-2.5 text-xs text-blue-300">
          {installNotice}
        </div>
      )}

      {/* Grid of Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((item) => (
          <div
            key={item.item_id}
            className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 flex flex-col justify-between space-y-3"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="rounded bg-zinc-800 border border-zinc-700 px-1.5 py-0.5 text-[10px] text-zinc-300 font-semibold font-mono">
                  {item.kind}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                    item.verification_status === "OFFICIAL_ATLAS"
                      ? "bg-blue-950 border border-blue-800 text-blue-300"
                      : item.verification_status === "VERIFIED_PARTNER"
                      ? "bg-purple-950 border border-purple-800 text-purple-300"
                      : "bg-zinc-800 text-zinc-400"
                  }`}
                >
                  {item.verification_status}
                </span>
              </div>
              <h3 className="text-xs font-bold text-zinc-100">{item.name}</h3>
              <p className="text-[11px] text-zinc-400 line-clamp-2">{item.description}</p>
            </div>

            <div className="space-y-2 pt-2 border-t border-zinc-800/60 text-[10px] font-mono">
              <div className="flex items-center justify-between text-zinc-400">
                <span>By: {item.publisher_name}</span>
                <span>v{item.version}</span>
              </div>
              <div className="text-zinc-500 truncate">
                Permissions: {item.required_permissions.join(", ") || "None"}
              </div>
              <div className="flex space-x-2 pt-1">
                <button
                  onClick={() => setSelectedItem(item)}
                  className="flex-1 rounded border border-zinc-700 bg-zinc-800 px-2 py-1 text-xs text-zinc-300 hover:bg-zinc-700"
                >
                  Details
                </button>
                <button
                  onClick={() => handleInstallClick(item)}
                  className="flex-1 rounded bg-emerald-950 border border-emerald-800 px-2 py-1 text-xs font-semibold text-emerald-300 hover:bg-emerald-900"
                >
                  Install
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Item Detail Sheet */}
      {selectedItem && (
        <div className="rounded border border-zinc-700 bg-[#0d0d0d] p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
            <h3 className="text-xs font-bold text-zinc-100">
              Extension Details: {selectedItem.name} (v{selectedItem.version})
            </h3>
            <button
              onClick={() => setSelectedItem(null)}
              className="text-xs text-zinc-400 hover:text-zinc-200"
            >
              Close
            </button>
          </div>
          <p className="text-xs text-zinc-300">{selectedItem.description}</p>
          <div className="rounded bg-black p-3 font-mono text-[11px] text-zinc-400 space-y-1.5 border border-zinc-800">
            <div>Kind: {selectedItem.kind}</div>
            <div>Publisher: {selectedItem.publisher_name} ({selectedItem.publisher_id})</div>
            <div>Verification: {selectedItem.verification_status}</div>
            <div>License: {selectedItem.license}</div>
            <div>Required Permissions: {selectedItem.required_permissions.join(", ") || "None"}</div>
            <div>Dependencies: {selectedItem.required_dependencies.join(", ") || "None"}</div>
          </div>
        </div>
      )}
    </div>
  );
};

