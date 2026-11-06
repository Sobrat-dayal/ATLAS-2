import { TaskRegistry } from "@/components/agents/tasks/TaskRegistry";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: "Tasks & Workflows | ATLAS Agents V3",
    description: "Durable multi-agent task registry, DAG planning, and review workflows.",
  };
}

export default function TasksPage() {
  return (
    <div className="p-4 bg-[#070707] min-h-[calc(100vh-4rem)]">
      <TaskRegistry />
    </div>
  );
}

