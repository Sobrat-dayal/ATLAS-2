import { Metadata } from "next";
import { MarketMoversPage } from "@/components/markets/movers";

export function generateMetadata(): Metadata {
  return {
    title: "Market Movers | ATLAS",
    description:
      "Global market movement intelligence, top gainers and losers, most active securities, asset-class-aware rankings and professional real-time market movers terminal.",
  };
}

export default function MarketMoversRoute() {
  return <MarketMoversPage />;
}
