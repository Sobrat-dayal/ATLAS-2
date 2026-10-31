import { ATLAS_MODULES } from "@/config/atlas-modules";
import { OptionsTerminal } from "@/components/options/OptionsTerminal";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.options.label} | ATLAS Options Analytics Terminal`,
    description: "Institutional-grade options research, chains, volatility analytics, and multi-leg strategy modeling.",
  };
}

export default function OptionsPage() {
  return <OptionsTerminal />;
}
