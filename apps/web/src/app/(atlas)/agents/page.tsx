import { ATLAS_MODULES } from "@/config/atlas-modules";
import { AgentsHub } from "@/components/agents/AgentsHub";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.agents.label} | ATLAS Agents V3 Enterprise Orchestration`,
    description:
      "Autonomous multi-agent teams, specialized AI departments, collaborative intelligence and enterprise orchestration.",
  };
}

export default function AgentsPage() {
  return <AgentsHub />;
}
