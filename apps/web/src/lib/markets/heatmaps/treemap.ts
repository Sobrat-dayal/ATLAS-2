/**
 * Squarified Treemap Layout Engine for ATLAS Market Heatmaps V1 (Stage 64).
 *
 * Implements the canonical squarified treemap algorithm (Bruls, Huizing, van Wijk).
 * Guarantees:
 * - Deterministic tile geometry for identical snapshot data and viewport bounds.
 * - Area strictly proportional to normalized weight.
 * - Non-overlapping rectangles fitted within bounded width and height.
 * - Hierarchical grouping: sector container bounds with nested constituent tiles.
 * - Graceful tiny tile classification (suppresses label clutter, preserves accessibility).
 */

import { HeatmapGroupNode, HeatmapLeafNode } from "./types";

export interface TreemapRect<T = HeatmapLeafNode> {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  data: T;
  isTiny: boolean;
  canShowName: boolean;
}

export interface GroupTreemapRect {
  group: HeatmapGroupNode;
  x: number;
  y: number;
  width: number;
  height: number;
  headerHeight: number;
  children: TreemapRect<HeatmapLeafNode>[];
}

interface LayoutItem<T> {
  id: string;
  weight: number;
  data: T;
}

/**
 * Calculates worst aspect ratio for a row of items along length w.
 */
function worstAspectRatio(row: number[], w: number): number {
  if (row.length === 0) return Infinity;
  const s = row.reduce((a, b) => a + b, 0);
  if (s <= 0 || w <= 0) return Infinity;
  let maxArea = row[0];
  let minArea = row[0];
  for (let i = 1; i < row.length; i++) {
    if (row[i] > maxArea) maxArea = row[i];
    if (row[i] < minArea) minArea = row[i];
  }
  const w2 = w * w;
  const s2 = s * s;
  return Math.max((w2 * maxArea) / s2, s2 / (w2 * minArea));
}

/**
 * Squarifies a list of layout items within a target bounding box.
 */
export function computeSquarifiedLayout<T>(
  items: LayoutItem<T>[],
  x: number,
  y: number,
  width: number,
  height: number,
  padding: number = 2
): TreemapRect<T>[] {
  if (items.length === 0 || width <= 0 || height <= 0) {
    return [];
  }

  // Ensure positive weights
  const validItems = items.filter((item) => item.weight > 0);
  if (validItems.length === 0) {
    // If all weights are 0, assign equal weights
    const fallbackWeight = 1 / items.length;
    return computeSquarifiedLayout(
      items.map((i) => ({ ...i, weight: fallbackWeight })),
      x,
      y,
      width,
      height,
      padding
    );
  }

  const totalWeight = validItems.reduce((acc, curr) => acc + curr.weight, 0);
  const totalArea = width * height;

  // Scale weights to area units
  const areas = validItems.map((item) => ({
    ...item,
    area: (item.weight / totalWeight) * totalArea,
  }));

  // Sort descending by area for squarified packing
  areas.sort((a, b) => b.area - a.area);

  const rects: TreemapRect<T>[] = [];

  let curX = x;
  let curY = y;
  let curW = width;
  let curH = height;

  let row: typeof areas = [];

  function layoutRow(rowToLayout: typeof areas, w: number, isVertical: boolean) {
    const rowArea = rowToLayout.reduce((acc, curr) => acc + curr.area, 0);
    const rowThickness = w > 0 ? rowArea / w : 0;

    let offset = isVertical ? curY : curX;

    for (const item of rowToLayout) {
      const itemLen = rowThickness > 0 ? item.area / rowThickness : 0;

      const rx = isVertical ? curX : offset;
      const ry = isVertical ? offset : curY;
      const rw = isVertical ? rowThickness : itemLen;
      const rh = isVertical ? itemLen : rowThickness;

      const paddedX = rx + padding / 2;
      const paddedY = ry + padding / 2;
      const paddedW = Math.max(0, rw - padding);
      const paddedH = Math.max(0, rh - padding);

      rects.push({
        id: item.id,
        x: paddedX,
        y: paddedY,
        width: paddedW,
        height: paddedH,
        data: item.data,
        isTiny: paddedW < 52 || paddedH < 36,
        canShowName: paddedW >= 95 && paddedH >= 65,
      });

      offset += itemLen;
    }

    if (isVertical) {
      curX += rowThickness;
      curW = Math.max(0, curW - rowThickness);
    } else {
      curY += rowThickness;
      curH = Math.max(0, curH - rowThickness);
    }
  }

  for (let i = 0; i < areas.length; i++) {
    const item = areas[i];
    const isVertical = curW < curH; // Pack along shorter dimension
    const length = isVertical ? curH : curW;

    const rowAreas = row.map((r) => r.area);
    const currentWorst = worstAspectRatio(rowAreas, length);
    const candidateWorst = worstAspectRatio([...rowAreas, item.area], length);

    if (row.length === 0 || candidateWorst <= currentWorst) {
      row.push(item);
    } else {
      layoutRow(row, length, isVertical);
      row = [item];
    }
  }

  if (row.length > 0) {
    const isVertical = curW < curH;
    const length = isVertical ? curH : curW;
    layoutRow(row, length, isVertical);
  }

  return rects;
}

/**
 * Computes hierarchical layout: sector groups with nested constituent leaf tiles.
 */
export function computeHierarchicalTreemap(
  groups: HeatmapGroupNode[],
  width: number,
  height: number,
  groupPadding: number = 6,
  tilePadding: number = 2
): GroupTreemapRect[] {
  if (groups.length === 0 || width <= 0 || height <= 0) {
    return [];
  }

  // 1. Convert groups to layout items
  const groupItems: LayoutItem<HeatmapGroupNode>[] = groups.map((g) => {
    const numWeight =
      typeof g.normalized_weight === "string"
        ? parseFloat(g.normalized_weight)
        : typeof g.normalized_weight === "number"
        ? g.normalized_weight
        : typeof g.total_weight === "string"
        ? parseFloat(g.total_weight)
        : typeof g.total_weight === "number"
        ? g.total_weight
        : g.constituent_count;

    return {
      id: g.group_id,
      weight: Math.max(numWeight, 0.0001),
      data: g,
    };
  });

  // 2. Compute group bounding boxes
  const groupBoxes = computeSquarifiedLayout(
    groupItems,
    0,
    0,
    width,
    height,
    groupPadding
  );

  const result: GroupTreemapRect[] = [];

  // 3. For each group box, layout child leaf nodes inside
  for (const box of groupBoxes) {
    const group = box.data;
    const headerH = box.height >= 70 ? 26 : 0; // Header only if box has reasonable height

    const contentX = box.x;
    const contentY = box.y + headerH;
    const contentW = box.width;
    const contentH = Math.max(0, box.height - headerH);

    const childItems: LayoutItem<HeatmapLeafNode>[] = group.children.map((child) => {
      const leafWeight =
        typeof child.normalized_weight === "string"
          ? parseFloat(child.normalized_weight)
          : typeof child.normalized_weight === "number"
          ? child.normalized_weight
          : typeof child.weight_value === "string"
          ? parseFloat(child.weight_value)
          : typeof child.weight_value === "number"
          ? child.weight_value
          : 1;

      return {
        id: child.node_id,
        weight: Math.max(leafWeight, 0.0001),
        data: child,
      };
    });

    const childRects = computeSquarifiedLayout(
      childItems,
      contentX,
      contentY,
      contentW,
      contentH,
      tilePadding
    );

    result.push({
      group,
      x: box.x,
      y: box.y,
      width: box.width,
      height: box.height,
      headerHeight: headerH,
      children: childRects,
    });
  }

  return result;
}
