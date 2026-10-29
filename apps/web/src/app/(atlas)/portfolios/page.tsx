import { ATLAS_MODULES } from "@/config/atlas-modules";
import { PortfolioWorkspace } from "@/components/portfolios/PortfolioWorkspace";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.portfolios.label} | ATLAS`,
    description:
      "Institutional-grade portfolio management, investment accounts, transaction ledgers, FIFO tax lots, and marked valuation.",
  };
}

export default function PortfoliosPage() {
  return <PortfolioWorkspace />;
}
