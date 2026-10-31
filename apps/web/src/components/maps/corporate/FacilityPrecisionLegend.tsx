"use client";

import React, { useState } from "react";
import { Compass, ChevronDown, ChevronUp } from "lucide-react";
import { PRECISION_CLASS_INFO } from "@/lib/maps/corporate/facilityStyles";
import { GeographicPrecisionClass } from "@/lib/maps/corporate/types";

export function FacilityPrecisionLegend({ className = "" }: { className?: string }) {
  const [isOpen, setIsOpen] = useState(false);

  const displayClasses: GeographicPrecisionClass[] = [
    "VERIFIED_SITE_POINT",
    "VERIFIED_SITE_POLYGON",
    "VERIFIED_STREET_ADDRESS",
    "GEOCODED_ADDRESS_APPROXIMATE",
    "LOCALITY_CENTROID",
  ];

  return (
    <div className={`bg-zinc-950/90 backdrop-blur-xs border border-zinc-800 rounded shadow-lg text-xs ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 flex items-center justify-between text-zinc-300 hover:text-zinc-100 transition-colors"
      >
        <div className="flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-wider">
          <Compass className="w-3.5 h-3.5 text-sky-400" />
          <span>Coordinate Precision Legend</span>
        </div>
        {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="p-3 border-t border-zinc-800/80 space-y-2">
          {displayClasses.map((cls) => {
            const info = PRECISION_CLASS_INFO[cls];
            return (
              <div key={cls} className="flex items-start gap-2">
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium border shrink-0 ${info.badge}`}>
                  {info.label}
                </span>
                <span className="text-[10px] text-zinc-400 leading-tight mt-0.5">
                  {info.description}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

