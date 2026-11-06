import { SystemReadinessCockpit } from "@/components/system/SystemReadinessCockpit";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: "System Launch Readiness Cockpit | ATLAS Production Hardening",
    description:
      "Stage 150 of 150: Full platform integration audit, 10 readiness gates, security policy evaluation, and production launch monitoring.",
  };
}

export default function SystemStatusPage() {
  return <SystemReadinessCockpit />;
}
