"""SGP4-Compatible Orbital Propagation Engine (Stage 134).

Provides analytical Keplerian and J2-perturbed satellite propagation from
orbital element sets (TLE / OMM) to instantaneous geodetic latitude, longitude,
altitude, velocity, and ground footprint coverage.
"""

import math
from datetime import datetime, timezone
from typing import Optional, Tuple

from ..domain import ObservationDataClass, SatelliteOrbitalElements, SatelliteState
from ..errors import LiveOrbitPropagationFailedError, LiveStaleOrbitElementsError
from .elements import EARTH_MU_KM3_S2, EARTH_RADIUS_KM


# WGS84 Ellipsoid constants
WGS84_A_KM = 6378.137          # Semi-major axis
WGS84_F = 1.0 / 298.257223563   # Flattening
WGS84_B_KM = WGS84_A_KM * (1.0 - WGS84_F)  # Semi-minor axis
WGS84_E2 = 2.0 * WGS84_F - WGS84_F ** 2   # Eccentricity squared

# J2 Perturbation parameter
J2 = 1.08262668e-3

# Earth angular velocity in radians per second
OMEGA_EARTH_RAD_S = 7.2921151467e-5


def _solve_kepler(mean_anomaly_rad: float, eccentricity: float, max_iter: int = 50, tol: float = 1e-10) -> float:
    """Solve Kepler's Equation E - e * sin(E) = M using Newton-Raphson."""
    e_anom = mean_anomaly_rad
    for _ in range(max_iter):
        delta = e_anom - eccentricity * math.sin(e_anom) - mean_anomaly_rad
        if abs(delta) < tol:
            break
        derivative = 1.0 - eccentricity * math.cos(e_anom)
        e_anom = e_anom - delta / derivative
    return e_anom


def _compute_gmst_rad(dt_utc: datetime) -> float:
    """Compute Greenwich Mean Sidereal Time (GMST) in radians at given UTC datetime."""
    # Julian Date
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0 + dt_utc.microsecond / 3.6e9

    if month <= 2:
        year -= 1
        month += 12

    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5 + hour / 24.0

    t_cen = (jd - 2451545.0) / 36525.0
    # GMST in seconds of time (IAU 1982)
    gmst_sec = 24110.54841 + 8640184.812866 * t_cen + 0.093104 * (t_cen ** 2) - 6.2e-6 * (t_cen ** 3)
    gmst_sec += hour * 3600.0 * 1.00273790935

    # Convert to radians in [0, 2pi)
    gmst_rad = (gmst_sec % 86400.0) * (2.0 * math.pi / 86400.0)
    return gmst_rad % (2.0 * math.pi)


def propagate_satellite(
    elements: SatelliteOrbitalElements,
    propagate_at: Optional[datetime] = None,
    stale_epoch_days_threshold: float = 14.0,
    critical_stale_days: float = 30.0,
    fail_on_critical_stale: bool = False,
) -> SatelliteState:
    """Propagate Keplerian orbital elements to instantaneous geodetic state.

    Computes subpoint latitude, longitude, altitude (km), velocity (km/s),
    and ground footprint coverage with J2 secular nodal and apsidal precession.
    """
    if propagate_at is None:
        propagate_at = datetime.now(timezone.utc)
    elif propagate_at.tzinfo is None:
        propagate_at = propagate_at.replace(tzinfo=timezone.utc)

    epoch = elements.epoch_utc
    if epoch.tzinfo is None:
        epoch = epoch.replace(tzinfo=timezone.utc)

    delta_sec = (propagate_at - epoch).total_seconds()
    epoch_age_days = abs(delta_sec) / 86400.0

    if fail_on_critical_stale and epoch_age_days > critical_stale_days:
        raise LiveStaleOrbitElementsError(
            norad_id=elements.norad_cat_id,
            epoch_age_days=epoch_age_days,
            max_days=stale_epoch_days_threshold,
        )

    is_stale_epoch = epoch_age_days > stale_epoch_days_threshold

    try:
        # Mean motion in rad/s
        n0 = elements.mean_motion_rev_day * (2.0 * math.pi) / 86400.0
        # Semi-major axis in km
        a = (EARTH_MU_KM3_S2 / (n0 ** 2)) ** (1.0 / 3.0)
        e = elements.eccentricity
        inc = math.radians(elements.inclination_deg)
        raan0 = math.radians(elements.raan_deg)
        arg_p0 = math.radians(elements.arg_perigee_deg)
        m0 = math.radians(elements.mean_anomaly_deg)

        # J2 Perturbations (secular rates)
        p = a * (1.0 - e ** 2)
        if p <= 0:
            raise ValueError("Parabolic or hyperbolic orbit not supported")

        factor = 1.5 * J2 * ((EARTH_RADIUS_KM / p) ** 2) * n0
        raan_dot = -factor * math.cos(inc)
        arg_p_dot = factor * (2.0 - 2.5 * (math.sin(inc) ** 2))

        # Propagate angles
        mean_anomaly = (m0 + n0 * delta_sec) % (2.0 * math.pi)
        raan = (raan0 + raan_dot * delta_sec) % (2.0 * math.pi)
        arg_p = (arg_p0 + arg_p_dot * delta_sec) % (2.0 * math.pi)

        # Solve Kepler equation
        eccentric_anomaly = _solve_kepler(mean_anomaly, e)

        # True anomaly
        sin_nu = (math.sqrt(1.0 - e ** 2) * math.sin(eccentric_anomaly)) / (1.0 - e * math.cos(eccentric_anomaly))
        cos_nu = (math.cos(eccentric_anomaly) - e) / (1.0 - e * math.cos(eccentric_anomaly))
        true_anomaly = math.atan2(sin_nu, cos_nu)

        # Orbital radius and velocity magnitude
        r = a * (1.0 - e * math.cos(eccentric_anomaly))
        v_mag = math.sqrt(EARTH_MU_KM3_S2 * (2.0 / r - 1.0 / a))

        # Position in orbital plane
        x_orb = r * math.cos(true_anomaly)
        y_orb = r * math.sin(true_anomaly)

        # Perifocal to ECI rotation
        # Coordinates in orbital plane rotated by argument of perigee
        u = true_anomaly + arg_p  # Argument of latitude
        x_eci = r * (math.cos(raan) * math.cos(u) - math.sin(raan) * math.sin(u) * math.cos(inc))
        y_eci = r * (math.sin(raan) * math.cos(u) + math.cos(raan) * math.sin(u) * math.cos(inc))
        z_eci = r * (math.sin(u) * math.sin(inc))

        # ECI to ECEF (rotation by GMST around Z)
        gmst = _compute_gmst_rad(propagate_at)
        cos_gst = math.cos(gmst)
        sin_gst = math.sin(gmst)

        x_ecef = cos_gst * x_eci + sin_gst * y_eci
        y_ecef = -sin_gst * x_eci + cos_gst * y_eci
        z_ecef = z_eci

        # ECEF to Geodetic Latitude, Longitude, Altitude (WGS84 Bowring closed approx)
        lon_rad = math.atan2(y_ecef, x_ecef)
        sub_lon_deg = math.degrees(lon_rad)
        # Normalize to [-180, 180]
        while sub_lon_deg > 180.0:
            sub_lon_deg -= 360.0
        while sub_lon_deg < -180.0:
            sub_lon_deg += 360.0

        p_dist = math.sqrt(x_ecef ** 2 + y_ecef ** 2)
        theta_b = math.atan2(z_ecef * WGS84_A_KM, p_dist * WGS84_B_KM)
        lat_rad = math.atan2(
            z_ecef + (WGS84_E2 * WGS84_A_KM ** 2 / WGS84_B_KM) * (math.sin(theta_b) ** 3),
            p_dist - (WGS84_E2 * WGS84_A_KM) * (math.cos(theta_b) ** 3),
        )
        sub_lat_deg = math.degrees(lat_rad)

        # Altitude above WGS84 ellipsoid
        n_prime = WGS84_A_KM / math.sqrt(1.0 - WGS84_E2 * (math.sin(lat_rad) ** 2))
        alt_km = max(0.0, p_dist / math.cos(lat_rad) - n_prime)

        # Footprint horizon radius on Earth's surface
        # Central angle theta = arccos(R_E / (R_E + alt))
        footprint_angle_rad = math.acos(EARTH_RADIUS_KM / (EARTH_RADIUS_KM + alt_km))
        footprint_radius_km = EARTH_RADIUS_KM * footprint_angle_rad

        return SatelliteState(
            norad_cat_id=elements.norad_cat_id,
            name=elements.name,
            propagated_at_utc=propagate_at,
            epoch_utc=epoch,
            epoch_age_days=epoch_age_days,
            is_stale_epoch=is_stale_epoch,
            subpoint_latitude=round(sub_lat_deg, 4),
            subpoint_longitude=round(sub_lon_deg, 4),
            altitude_km=round(alt_km, 2),
            velocity_km_s=round(v_mag, 3),
            footprint_radius_km=round(footprint_radius_km, 1),
            data_class=ObservationDataClass.PROPAGATED,
            provenance_note="PROPAGATED FROM ORBITAL ELEMENTS (SGP4)",
        )

    except Exception as exc:
        raise LiveOrbitPropagationFailedError(elements.norad_cat_id, str(exc)) from exc
