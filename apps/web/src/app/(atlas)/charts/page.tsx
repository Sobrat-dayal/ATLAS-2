import { Metadata } from "next";
import { ChartsPage } from "@/components/charts";

export function generateMetadata(): Metadata {
  return {
    title: "Charts | ATLAS Financial Intelligence",
    description: "Institutional financial charting workspace, historical candlestick engine and market exploration.",
  };
}

export default function Page() {
  return <ChartsPage />;
}
