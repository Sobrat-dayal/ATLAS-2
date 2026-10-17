import { Metadata } from "next";
import { CrossAssetMarketsPage } from "@/components/markets/cross-asset";

export function generateMetadata(): Metadata {
  return {
    title: "Cross-Asset Markets | ATLAS",
    description:
      "Global multi-asset market intelligence, equities–bonds–FX–crypto–futures comparison, synchronized performance analysis, macro market context, and institutional cross-market terminal.",
  };
}

export default function CrossAssetMarketsRoute() {
  return <CrossAssetMarketsPage />;
}
