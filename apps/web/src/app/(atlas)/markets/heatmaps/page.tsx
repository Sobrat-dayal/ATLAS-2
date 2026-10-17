import { Metadata } from "next";
import { MarketHeatmapsPage } from "@/components/markets/heatmaps";

export function generateMetadata(): Metadata {
  return {
    title: "Market Heatmaps | ATLAS",
    description:
      "Institutional market visualization, sector & industry treemaps, price-movement heatmaps, market-capitalization weighting, interactive drilldowns and real-time market intelligence.",
  };
}

export default function MarketHeatmapsRoute() {
  return <MarketHeatmapsPage />;
}
