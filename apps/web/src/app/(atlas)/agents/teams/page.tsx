import { TeamRegistry } from "@/components/agents/teams/TeamRegistry";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: "AI Teams | ATLAS Agents V3",
    description: "Multi-agent team registry, coordinator roles, and squad composition.",
  };
}

export default function TeamsPage() {
  return (
    <div className="p-4 bg-[#070707] min-h-[calc(100vh-4rem)]">
      <TeamRegistry />
    </div>
  );
}
