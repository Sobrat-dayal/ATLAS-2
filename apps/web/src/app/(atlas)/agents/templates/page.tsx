import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Starter Templates | ATLAS Ecosystem",
    description: "Launch pre-configured agent, team, and workflow starter templates into draft state.",
  };
}

export default function TemplatesPage() {
  return <EcosystemCockpit defaultTab="templates" />;
}

