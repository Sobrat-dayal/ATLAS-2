import { Metadata } from "next";
import { EcosystemCockpit } from "@/components/ecosystem/EcosystemCockpit";

export function generateMetadata(): Metadata {
  return {
    title: "Developer Platform & Custom Tools | ATLAS Ecosystem",
    description: "Build custom tools, run execution test fixtures, issue scoped API keys, and connect Git repos.",
  };
}

export default function DevelopersPage() {
  return <EcosystemCockpit defaultTab="developers" />;
}
