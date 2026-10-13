import { HomePage } from "@/components/home";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Home | ATLAS",
  description: "ATLAS Operational Command Center",
};

export default function HomeRoute() {
  return <HomePage />;
}
