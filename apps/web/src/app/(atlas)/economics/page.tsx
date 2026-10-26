import { Metadata } from "next";
import { Suspense } from "react";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import { EconomicsWorkspace } from "@/components/economics";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.economics.label} | ATLAS`,
    description:
      "Global Macroeconomic Intelligence, Canonical Economic Indicators, GDP, Inflation, Labor Market, and Sovereign Time Series.",
  };
}

export default function EconomicsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center p-8 text-atlas-text-muted text-xs">
          Loading ATLAS Global Economics...
        </div>
      }
    >
      <EconomicsWorkspace />
    </Suspense>
  );
}
