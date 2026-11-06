import { AgentWorkforceDashboard } from "@/components/agents/operations/AgentWorkforceDashboard";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: "Workforce Operations | ATLAS Agents V3",
    description: "Enterprise multi-agent workforce health, cost telemetry, and approval inbox.",
  };
}

export default function OperationsPage() {
  return (
    <div className="p-4 bg-[#070707] min-h-[calc(100vh-4rem)]">
      <AgentWorkforceDashboard />
    </div>
  );
}

