import { Metadata } from "next";
import { EquitiesPage } from "@/components/markets/equities";

export function generateMetadata(): Metadata {
  return {
    title: "Equities Markets | ATLAS",
    description:
      "Exchange-aware equity discovery, canonical instrument exploration and terminal interface.",
  };
}

export default function EquitiesRoute() {
  return <EquitiesPage />;
}
