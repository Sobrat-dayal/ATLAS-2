/**
 * WGS84 Geodetic and Cartesian ECEF Coordinate Engine (Stage 130).
 *
 * Implements rigorous forward and inverse WGS84 ellipsoid transformations,
 * Bowring's closed-form algorithm for sub-millimeter precision, and angle conversions.
 */

// WGS84 Ellipsoid Standard Parameters
export const WGS84_A = 6378137.0; // Semi-major axis in meters
export const WGS84_F = 1.0 / 298.257223563; // Flattening
export const WGS84_B = WGS84_A * (1.0 - WGS84_F); // Semi-minor axis (approx 6356752.314245)
export const WGS84_E2 = 2.0 * WGS84_F - WGS84_F * WGS84_F; // First eccentricity squared
export const WGS84_E_PRIME2 = (WGS84_A * WGS84_A - WGS84_B * WGS84_B) / (WGS84_B * WGS84_B); // Second eccentricity squared

export function degreesToRadians(degrees: number): number {
  if (!Number.isFinite(degrees)) {
    throw new Error("Angle in degrees must be a finite number");
  }
  return (degrees * Math.PI) / 180.0;
}

export function radiansToDegrees(radians: number): number {
  if (!Number.isFinite(radians)) {
    throw new Error("Angle in radians must be a finite number");
  }
  return (radians * 180.0) / Math.PI;
}

export function normalizeLongitude(longitude: number): number {
  let lon = ((((longitude + 180.0) % 360.0) + 360.0) % 360.0) - 180.0;
  if (lon === -180.0 && longitude > 0) {
    lon = 180.0;
  }
  return lon;
}

export function validateGlobeCoordinates(
  longitude: number,
  latitude: number,
  heightMeters: number = 0.0
): void {
  if (!Number.isFinite(longitude) || longitude < -180.0 || longitude > 180.0) {
    throw new Error(`Longitude must be finite and within [-180, 180], got ${longitude}`);
  }
  if (!Number.isFinite(latitude) || latitude < -90.0 || latitude > 90.0) {
    throw new Error(`Latitude must be finite and within [-90, 90], got ${latitude}`);
  }
  if (!Number.isFinite(heightMeters)) {
    throw new Error(`Height must be a finite number of meters, got ${heightMeters}`);
  }
}

/**
 * Convert WGS84 geodetic coordinates (longitude, latitude, height) to Earth-Centered Earth-Fixed (ECEF) Cartesian (X, Y, Z).
 *
 * @returns [x, y, z] in meters.
 */
export function geodeticToCartesian(
  longitudeDeg: number,
  latitudeDeg: number,
  heightMeters: number = 0.0
): [number, number, number] {
  validateGlobeCoordinates(longitudeDeg, latitudeDeg, heightMeters);

  const lam = degreesToRadians(longitudeDeg);
  const phi = degreesToRadians(latitudeDeg);

  const sinPhi = Math.sin(phi);
  const cosPhi = Math.cos(phi);
  const sinLam = Math.sin(lam);
  const cosLam = Math.cos(lam);

  // Radius of curvature in the prime vertical N(phi)
  const n = WGS84_A / Math.sqrt(1.0 - WGS84_E2 * sinPhi * sinPhi);

  const x = (n + heightMeters) * cosPhi * cosLam;
  const y = (n + heightMeters) * cosPhi * sinLam;
  const z = (n * (1.0 - WGS84_E2) + heightMeters) * sinPhi;

  return [x, y, z];
}

/**
 * Convert Earth-Centered Earth-Fixed (ECEF) Cartesian (X, Y, Z) in meters to WGS84 geodetic coordinates.
 *
 * Uses Bowring's formulation for sub-millimeter precision.
 * @returns [longitudeDeg, latitudeDeg, heightMeters]
 */
export function cartesianToGeodetic(
  x: number,
  y: number,
  z: number
): [number, number, number] {
  if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(z)) {
    throw new Error("Cartesian coordinates must be finite numbers");
  }

  const p = Math.hypot(x, y);

  // Polar singularities
  if (p < 1e-7) {
    const lonDeg = 0.0;
    const latDeg = z >= 0 ? 90.0 : -90.0;
    const heightM = Math.abs(z) - WGS84_B;
    return [lonDeg, latDeg, heightM];
  }

  const theta = Math.atan2(z * WGS84_A, p * WGS84_B);
  const sinTheta = Math.sin(theta);
  const cosTheta = Math.cos(theta);

  const phi = Math.atan2(
    z + WGS84_E_PRIME2 * WGS84_B * (sinTheta * sinTheta * sinTheta),
    p - WGS84_E2 * WGS84_A * (cosTheta * cosTheta * cosTheta)
  );
  const lam = Math.atan2(y, x);

  const sinPhi = Math.sin(phi);
  const cosPhi = Math.cos(phi);
  const n = WGS84_A / Math.sqrt(1.0 - WGS84_E2 * sinPhi * sinPhi);

  let heightM: number;
  if (Math.abs(cosPhi) > 1e-4) {
    heightM = p / cosPhi - n;
  } else {
    heightM = Math.abs(z) / Math.abs(sinPhi) - n * (1.0 - WGS84_E2);
  }

  const lonDeg = radiansToDegrees(lam);
  const latDeg = radiansToDegrees(phi);

  return [lonDeg, latDeg, heightM];
}
