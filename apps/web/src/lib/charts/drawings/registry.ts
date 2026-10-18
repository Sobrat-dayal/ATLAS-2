/**
 * Typed Drawing Tool Registry for ATLAS Charts (Stage 71).
 *
 * Provides central registration and validation for all 9 canonical drawing tools.
 */

import { DrawingAnchor, DrawingToolDefinition, DrawingType } from "./types";

export const DRAWING_TOOLS: Record<DrawingType, DrawingToolDefinition> = {
  trendline: {
    type: "trendline",
    displayName: "Trendline",
    description: "Draw a directional line segment between two financial price and time anchors.",
    requiredAnchors: 2,
    iconName: "TrendingUp",
    category: "line",
  },
  horizontal_line: {
    type: "horizontal_line",
    displayName: "Horizontal Line",
    description: "Draw an infinite horizontal price level spanning the entire chart width.",
    requiredAnchors: 1,
    iconName: "Minus",
    category: "line",
  },
  horizontal_ray: {
    type: "horizontal_ray",
    displayName: "Horizontal Ray",
    description: "Draw a horizontal price ray originating at an anchor and extending rightward.",
    requiredAnchors: 1,
    iconName: "MoveRight",
    category: "line",
  },
  vertical_line: {
    type: "vertical_line",
    displayName: "Vertical Line",
    description: "Draw an infinite vertical time marker through a specific trading date or timestamp.",
    requiredAnchors: 1,
    iconName: "Split",
    category: "line",
  },
  rectangle: {
    type: "rectangle",
    displayName: "Rectangle Zone",
    description: "Highlight a time and price zone with custom boundary styling and fill opacity.",
    requiredAnchors: 2,
    iconName: "Square",
    category: "zone",
  },
  price_range: {
    type: "price_range",
    displayName: "Price Range",
    description: "Measure absolute and percentage price change between two vertical levels.",
    requiredAnchors: 2,
    iconName: "ArrowUpDown",
    category: "measurement",
  },
  time_range: {
    type: "time_range",
    displayName: "Time Range",
    description: "Measure elapsed calendar duration and qualified trading bar count.",
    requiredAnchors: 2,
    iconName: "ArrowLeftRight",
    category: "measurement",
  },
  price_time_measure: {
    type: "price_time_measure",
    displayName: "Price & Time Measurement",
    description: "Measure simultaneous price difference, percentage change, elapsed time, and bar count.",
    requiredAnchors: 2,
    iconName: "Maximize2",
    category: "measurement",
  },
  fibonacci_retracement: {
    type: "fibonacci_retracement",
    displayName: "Fibonacci Retracement",
    description: "Render standard institutional Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%, 78.6%).",
    requiredAnchors: 2,
    iconName: "GitCommit",
    category: "fibonacci",
  },
};

export class DrawingToolRegistry {
  private static tools: Map<DrawingType, DrawingToolDefinition> = new Map(
    Object.entries(DRAWING_TOOLS) as [DrawingType, DrawingToolDefinition][]
  );

  public static get(type: DrawingType): DrawingToolDefinition | undefined {
    return this.tools.get(type);
  }

  public static getAll(): DrawingToolDefinition[] {
    return Array.from(this.tools.values());
  }

  public static validateAnchors(type: DrawingType, anchors: DrawingAnchor[]): boolean {
    const tool = this.tools.get(type);
    if (!tool) return false;
    if (anchors.length < tool.requiredAnchors) return false;

    // Validate that each anchor has finite, valid numeric values
    for (const a of anchors) {
      if (typeof a.time !== "number" || isNaN(a.time) || !isFinite(a.time)) {
        return false;
      }
      if (typeof a.price !== "number" || isNaN(a.price) || !isFinite(a.price)) {
        return false;
      }
    }

    return true;
  }
}
