/**
 * Analytical Color Scale Interpolator and Palettes (Stage 131).
 *
 * Supplies RGBA color arrays [R, G, B, A] for deck.gl layers and CSS gradients for legends.
 * Includes color-blind safe palettes (Viridis, Cividis) and distinct suppressed data styling.
 */

import { ColorPalette } from './types';

export const PALETTES: Record<ColorPalette, [number, number, number][]> = {
  viridis: [
    [68, 1, 84],
    [72, 35, 116],
    [64, 67, 135],
    [52, 94, 141],
    [41, 120, 142],
    [32, 144, 140],
    [34, 167, 132],
    [68, 190, 112],
    [121, 209, 81],
    [189, 222, 38],
    [253, 231, 36],
  ],
  magma: [
    [0, 0, 4],
    [28, 16, 68],
    [79, 18, 123],
    [129, 37, 129],
    [181, 54, 122],
    [229, 80, 100],
    [251, 135, 97],
    [254, 194, 135],
    [252, 253, 191],
  ],
  blues: [
    [247, 251, 255],
    [222, 235, 247],
    [198, 219, 239],
    [158, 202, 225],
    [107, 174, 214],
    [66, 146, 198],
    [33, 113, 181],
    [8, 81, 156],
    [8, 48, 107],
  ],
  turbo: [
    [48, 18, 59],
    [70, 134, 251],
    [27, 229, 181],
    [164, 252, 60],
    [251, 185, 56],
    [227, 68, 10],
    [122, 4, 3],
  ],
  cividis: [
    [0, 32, 76],
    [0, 53, 103],
    [38, 71, 116],
    [71, 89, 124],
    [103, 107, 132],
    [136, 126, 137],
    [171, 147, 138],
    [208, 171, 133],
    [244, 200, 117],
    [255, 234, 70],
  ],
  spectral: [
    [158, 1, 66],
    [213, 62, 79],
    [244, 109, 67],
    [253, 174, 97],
    [254, 224, 139],
    [230, 245, 152],
    [171, 221, 164],
    [102, 194, 165],
    [50, 136, 189],
    [94, 79, 162],
  ],
};

// Neutral muted color for privacy-suppressed cells
export const SUPPRESSED_COLOR: [number, number, number, number] = [80, 80, 85, 140];

/**
 * Maps a numeric value to an RGBA color array [r, g, b, a].
 */
export function getColorForValue(
  value: number | null,
  min: number,
  max: number,
  palette: ColorPalette = 'viridis',
  isSuppressed: boolean = false,
  alpha: number = 200
): [number, number, number, number] {
  if (isSuppressed || value === null || isNaN(value)) {
    return SUPPRESSED_COLOR;
  }

  const colors = PALETTES[palette] || PALETTES.viridis;
  const range = max - min;
  const normalized = range > 0 ? Math.max(0, Math.min(1, (value - min) / range)) : 0.5;

  const scaled = normalized * (colors.length - 1);
  const idx = Math.floor(scaled);
  const frac = scaled - idx;

  if (idx >= colors.length - 1) {
    const last = colors[colors.length - 1];
    return [last[0], last[1], last[2], alpha];
  }

  const c1 = colors[idx];
  const c2 = colors[idx + 1];

  const r = Math.round(c1[0] + frac * (c2[0] - c1[0]));
  const g = Math.round(c1[1] + frac * (c2[1] - c1[1]));
  const b = Math.round(c1[2] + frac * (c2[2] - c1[2]));

  return [r, g, b, alpha];
}

/**
 * Generates CSS linear-gradient string for legend rendering.
 */
export function getCssGradient(palette: ColorPalette = 'viridis'): string {
  const colors = PALETTES[palette] || PALETTES.viridis;
  const stops = colors.map((c, i) => {
    const pct = Math.round((i / (colors.length - 1)) * 100);
    return `rgb(${c[0]}, ${c[1]}, ${c[2]}) ${pct}%`;
  });
  return `linear-gradient(to right, ${stops.join(', ')})`;
}

