import { DepartmentRegistry } from "@/components/agents/departments/DepartmentRegistry";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: "AI Departments | ATLAS Agents V3",
    description: "Specialized enterprise AI department registry and domain governance.",
  };
}

export default function DepartmentsPage() {
  return (
    <div className="p-4 bg-[#070707] min-h-[calc(100vh-4rem)]">
      <DepartmentRegistry />
    </div>
  );
}
