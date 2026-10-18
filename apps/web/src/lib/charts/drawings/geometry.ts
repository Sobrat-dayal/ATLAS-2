/**
 * Screen-Space Geometry and Hit-Testing Utilities for Drawing Tools (Stage 71).
 */

import { LineStrokeStyle, ScreenPoint } from "./types";

/**
 * Returns the Euclidean distance between two screen points.
 */
export function pointDistance(p1: ScreenPoint, p2: ScreenPoint): number {
  const dx = p1.x - p2.x;
  const dy = p1.y - p2.y;
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Returns the shortest distance from point P to line segment AB.
 */
export function distanceToSegment(p: ScreenPoint, a: ScreenPoint, b: ScreenPoint): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const lenSq = dx * dx + dy * dy;

  if (lenSq === 0) {
    return pointDistance(p, a);
  }

  // Projection scalar t on segment [0, 1]
  const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / lenSq));
  const projX = a.x + t * dx;
  const projY = a.y + t * dy;

  return pointDistance(p, { x: projX, y: projY });
}

/**
 * Returns the shortest distance from point P to an infinite horizontal line at y.
 */
export function distanceToHorizontalLine(p: ScreenPoint, y: number): number {
  return Math.abs(p.y - y);
}

/**
 * Returns the shortest distance from point P to a horizontal ray starting at A and extending rightward.
 */
export function distanceToHorizontalRay(p: ScreenPoint, a: ScreenPoint): number {
  if (p.x >= a.x) {
    return Math.abs(p.y - a.y);
  }
  // If left of ray start, distance to anchor A
  return pointDistance(p, a);
}

/**
 * Returns the shortest distance from point P to an infinite vertical line at x.
 */
export function distanceToVerticalLine(p: ScreenPoint, x: number): number {
  return Math.abs(p.x - x);
}

/**
 * Checks if point P is inside a rectangle defined by two opposing corners A and B.
 */
export function isPointInRectangle(p: ScreenPoint, a: ScreenPoint, b: ScreenPoint): boolean {
  const minX = Math.min(a.x, b.x);
  const maxX = Math.max(a.x, b.x);
  const minY = Math.min(a.y, b.y);
  const maxY = Math.max(a.y, b.y);

  return p.x >= minX && p.x <= maxX && p.y >= minY && p.y <= maxY;
}

/**
 * Returns the shortest distance from point P to the four perimeter edges of a rectangle.
 */
export function distanceToRectangleBorder(p: ScreenPoint, a: ScreenPoint, b: ScreenPoint): number {
  const minX = Math.min(a.x, b.x);
  const maxX = Math.max(a.x, b.x);
  const minY = Math.min(a.y, b.y);
  const maxY = Math.max(a.y, b.y);

  const top = distanceToSegment(p, { x: minX, y: minY }, { x: maxX, y: minY });
  const bottom = distanceToSegment(p, { x: minX, y: maxY }, { x: maxX, y: maxY });
  const left = distanceToSegment(p, { x: minX, y: minY }, { x: minX, y: maxY });
  const right = distanceToSegment(p, { x: maxX, y: minY }, { x: maxX, y: maxY });

  return Math.min(top, bottom, left, right);
}

/**
 * Converts a line style to SVG stroke-dasharray attribute string.
 */
export function strokeStyleToDashArray(style: LineStrokeStyle, lineWidth: number = 1): string | undefined {
  switch (style) {
    case "dashed":
      return `${Math.max(4, lineWidth * 3)} ${Math.max(3, lineWidth * 2)}`;
    case "dotted":
      return `${Math.max(2, lineWidth)} ${Math.max(2, lineWidth * 2)}`;
    case "solid":
    default:
      return undefined;
  }
}
