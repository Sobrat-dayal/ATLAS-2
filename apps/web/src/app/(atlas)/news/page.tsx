import { Metadata } from "next";
import { NewsWorkspace } from "@/components/news";
import { ATLAS_MODULES } from "@/config/atlas-modules";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.news.label} | ATLAS`,
    description: "Source-verified institutional financial news, publisher provenance, and entity-linked market feeds.",
  };
}

export default function NewsPage() {
  return <NewsWorkspace />;
}
