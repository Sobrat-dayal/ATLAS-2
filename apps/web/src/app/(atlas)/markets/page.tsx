import { ATLAS_MODULES } from "@/config/atlas-modules";
import { MarketsOverviewPage } from "@/components/markets";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.markets.label} | ATLAS`
  };
}

export default function MarketsPage() {
  return <MarketsOverviewPage />;
}

