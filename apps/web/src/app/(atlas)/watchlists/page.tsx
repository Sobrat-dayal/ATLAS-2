import { Metadata } from "next";
import { WatchlistsWorkspace } from "@/components/watchlists/WatchlistsWorkspace";

export function generateMetadata(): Metadata {
  return {
    title: "Watchlists | ATLAS Financial Terminal",
    description:
      "Persistent multi-asset financial instrument watchlists, canonical tracking, drag-and-drop reordering, and authorized market quote snapshots.",
  };
}

export default function WatchlistsPage() {
  return <WatchlistsWorkspace />;
}
