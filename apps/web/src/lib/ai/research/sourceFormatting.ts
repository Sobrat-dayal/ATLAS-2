/**
 * Formatting utilities for research sources, citations, and reliability tiers.
 */

import { LicensingClass, ResearchSourceType } from "./types";

export function formatReliabilityTier(tier: string): { label: string; badgeClass: string } {
  switch (tier.toUpperCase()) {
    case "PRIMARY_REGULATORY":
      return {
        label: "Regulatory (SEC/EDGAR)",
        badgeClass: "bg-emerald-950/60 border-emerald-500/40 text-emerald-300",
      };
    case "PRIMARY_OFFICIAL":
      return {
        label: "Official IR / Press",
        badgeClass: "bg-cyan-950/60 border-cyan-500/40 text-cyan-300",
      };
    case "BROKER_CONSENSUS":
      return {
        label: "Institutional Research",
        badgeClass: "bg-indigo-950/60 border-indigo-500/40 text-indigo-300",
      };
    case "FINANCIAL_WIRE":
      return {
        label: "Financial Wire",
        badgeClass: "bg-amber-950/60 border-amber-500/40 text-amber-300",
      };
    case "USER_INTERNAL":
    case "USER_PRIVATE":
      return {
        label: "User Vault (Private)",
        badgeClass: "bg-purple-950/60 border-purple-500/40 text-purple-300",
      };
    default:
      return {
        label: tier,
        badgeClass: "bg-zinc-800 border-zinc-700 text-zinc-300",
      };
  }
}

export function formatLicensingClass(cls: LicensingClass): { label: string; icon: string } {
  switch (cls) {
    case "PUBLIC_DOMAIN":
      return { label: "Public Domain", icon: "Globe" };
    case "PROPRIETARY_LICENSED":
      return { label: "Proprietary Licensed", icon: "Lock" };
    case "INTERNAL_CONFIDENTIAL":
      return { label: "Internal Confidential", icon: "Shield" };
    case "USER_PRIVATE":
      return { label: "User Private", icon: "Key" };
  }
}

export function formatPublicationDate(isoDate: string): string {
  try {
    const d = new Date(isoDate);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return isoDate;
  }
}

