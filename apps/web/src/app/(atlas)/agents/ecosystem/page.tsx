import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Ecosystem & Platform Extensibility | ATLAS Stage 149",
    description:
      "Model Context Protocol (MCP) registry, plugin sandboxes, .atlas-agent packaging, developer tools, and marketplace.",
  };
}

export default function EcosystemPage() {
  return <EcosystemCockpit defaultTab="overview" />;
}
