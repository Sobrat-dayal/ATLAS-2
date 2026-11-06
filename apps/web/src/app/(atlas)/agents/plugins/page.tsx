import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Plugin Registry & Sandboxes | ATLAS Ecosystem",
    description: "Install, configure, and govern scoped AI plugins in isolated multi-tenant sandboxes.",
  };
}

export default function PluginsPage() {
  return <EcosystemCockpit defaultTab="plugins" />;
}

