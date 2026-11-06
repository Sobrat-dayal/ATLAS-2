import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Model Context Protocol (MCP) Registry | ATLAS Ecosystem",
    description: "Manage, connect, and inspect Model Context Protocol servers with SSRF security firewalls.",
  };
}

export default function MCPPage() {
  return <EcosystemCockpit defaultTab="mcp" />;
}
