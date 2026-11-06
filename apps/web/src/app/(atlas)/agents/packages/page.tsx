import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Agent Packages (.atlas-agent) | ATLAS Ecosystem",
    description: "Import, validate, and export standalone .atlas-agent packages with Zip-Slip defense and secret scrubbing.",
  };
}

export default function PackagesPage() {
  return <EcosystemCockpit defaultTab="packages" />;
}
