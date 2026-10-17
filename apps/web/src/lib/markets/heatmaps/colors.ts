/**
 * Performance color mapping for ATLAS Market Heatmaps V1 (Stage 64).
 *
 * Implements an institutional diverging color scale:
 * - Positive returns (> 0%): Green family (subtle emerald to rich forest green)
 * - Zero return (0.00%): Neutral zinc/slate tone
 * - Negative returns (< 0%): Red family (subtle ruby to rich crimson)
 * - Missing return (null/undefined): Distinct unavailable pattern (NEVER treated as zero)
 * - Extreme returns: Saturated at domain boundaries (±5.0%) without altering numeric value
 */

export interface HeatmapColorStyle {
  backgroundColor: string;
  borderColor: string;
  textColor: string;
  badgeBg: string;
  badgeText: string;
  isMissing: boolean;
}

const DEFAULT_DOMAIN_MIN = -5.0;
const DEFAULT_DOMAIN_MAX = 5.0;

/**
 * Maps a numeric percent change into institutional financial heatmap styling.
 */
export function getHeatmapTileColor(
  percentChange: number | string | null | undefined,
  domainMin: number = DEFAULT_DOMAIN_MIN,
  domainMax: number = DEFAULT_DOMAIN_MAX
): HeatmapColorStyle {
  if (percentChange === null || percentChange === undefined || percentChange === "") {
    return {
      backgroundColor: "rgba(24, 24, 27, 0.7)", // zinc-900 / muted
      borderColor: "rgba(63, 63, 70, 0.4)",      // zinc-700
      textColor: "rgb(161, 161, 170)",          // zinc-400
      badgeBg: "rgba(39, 39, 42, 0.6)",
      badgeText: "rgb(161, 161, 170)",
      isMissing: true,
    };
  }

  const numVal = typeof percentChange === "string" ? parseFloat(percentChange) : percentChange;
  if (isNaN(numVal)) {
    return {
      backgroundColor: "rgba(24, 24, 27, 0.7)",
      borderColor: "rgba(63, 63, 70, 0.4)",
      textColor: "rgb(161, 161, 170)",
      badgeBg: "rgba(39, 39, 42, 0.6)",
      badgeText: "rgb(161, 161, 170)",
      isMissing: true,
    };
  }

  // Exactly or near zero return (neutral slate/zinc)
  if (Math.abs(numVal) < 0.0001) {
    return {
      backgroundColor: "rgba(39, 39, 42, 0.85)", // zinc-800
      borderColor: "rgba(82, 82, 91, 0.5)",       // zinc-600
      textColor: "rgb(228, 228, 231)",           // zinc-200
      badgeBg: "rgba(63, 63, 70, 0.5)",
      badgeText: "rgb(212, 212, 216)",
      isMissing: false,
    };
  }

  if (numVal > 0) {
    // Clamp magnitude between 0 and domainMax (e.g. 5.0)
    const ratio = Math.min(numVal / domainMax, 1.0);

    if (ratio < 0.2) {
      // +0.01% to +1.0%
      return {
        backgroundColor: "rgba(6, 78, 59, 0.45)",  // emerald-900
        borderColor: "rgba(5, 150, 105, 0.4)",      // emerald-600
        textColor: "rgb(167, 243, 208)",            // emerald-200
        badgeBg: "rgba(6, 78, 59, 0.6)",
        badgeText: "rgb(167, 243, 208)",
        isMissing: false,
      };
    } else if (ratio < 0.5) {
      // +1.0% to +2.5%
      return {
        backgroundColor: "rgba(4, 120, 87, 0.65)",  // emerald-700
        borderColor: "rgba(16, 185, 129, 0.5)",     // emerald-500
        textColor: "rgb(209, 250, 229)",            // emerald-100
        badgeBg: "rgba(4, 120, 87, 0.75)",
        badgeText: "rgb(209, 250, 229)",
        isMissing: false,
      };
    } else if (ratio < 0.8) {
      // +2.5% to +4.0%
      return {
        backgroundColor: "rgba(5, 150, 105, 0.85)", // emerald-600
        borderColor: "rgba(52, 211, 153, 0.6)",     // emerald-400
        textColor: "rgb(255, 255, 255)",
        badgeBg: "rgba(5, 150, 105, 0.9)",
        badgeText: "rgb(255, 255, 255)",
        isMissing: false,
      };
    } else {
      // +4.0% to +5.0%+ (Saturated boundary)
      return {
        backgroundColor: "rgba(16, 185, 129, 0.95)", // emerald-500
        borderColor: "rgba(110, 231, 183, 0.8)",     // emerald-300
        textColor: "rgb(255, 255, 255)",
        badgeBg: "rgba(16, 185, 129, 1.0)",
        badgeText: "rgb(255, 255, 255)",
        isMissing: false,
      };
    }
  } else {
    // Negative return
    const ratio = Math.min(Math.abs(numVal) / Math.abs(domainMin), 1.0);

    if (ratio < 0.2) {
      // -0.01% to -1.0%
      return {
        backgroundColor: "rgba(127, 29, 29, 0.45)", // red-950
        borderColor: "rgba(220, 38, 38, 0.4)",      // red-600
        textColor: "rgb(254, 202, 202)",            // red-200
        badgeBg: "rgba(127, 29, 29, 0.6)",
        badgeText: "rgb(254, 202, 202)",
        isMissing: false,
      };
    } else if (ratio < 0.5) {
      // -1.0% to -2.5%
      return {
        backgroundColor: "rgba(153, 27, 27, 0.65)", // red-800
        borderColor: "rgba(239, 68, 68, 0.5)",      // red-500
        textColor: "rgb(254, 226, 226)",            // red-100
        badgeBg: "rgba(153, 27, 27, 0.75)",
        badgeText: "rgb(254, 226, 226)",
        isMissing: false,
      };
    } else if (ratio < 0.8) {
      // -2.5% to -4.0%
      return {
        backgroundColor: "rgba(185, 28, 28, 0.85)", // red-700
        borderColor: "rgba(248, 113, 113, 0.6)",    // red-400
        textColor: "rgb(255, 255, 255)",
        badgeBg: "rgba(185, 28, 28, 0.9)",
        badgeText: "rgb(255, 255, 255)",
        isMissing: false,
      };
    } else {
      // -4.0% to -5.0%+ (Saturated boundary)
      return {
        backgroundColor: "rgba(220, 38, 38, 0.95)", // red-600
        borderColor: "rgba(252, 165, 165, 0.8)",    // red-300
        textColor: "rgb(255, 255, 255)",
        badgeBg: "rgba(220, 38, 38, 1.0)",
        badgeText: "rgb(255, 255, 255)",
        isMissing: false,
      };
    }
  }
}
