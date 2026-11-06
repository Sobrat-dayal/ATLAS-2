import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Marketplace & Extensions Catalog | ATLAS Ecosystem",
    description: "Browse verified plugins, tools, and agent packages with publisher transparency and zero fabricated metrics.",
  };
}

export default function MarketplacePage() {
  return <EcosystemCockpit defaultTab="marketplace" />;
}
