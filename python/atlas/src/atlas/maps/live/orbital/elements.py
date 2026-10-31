"""Orbital Elements and TLE/OMM Parser (Stage 134).

Parses Two-Line Element (TLE) sets and Orbit Mean-Elements Messages (OMM)
into institutional Keplerian orbital representations.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from ..domain import SatelliteOrbitalElements


EARTH_RADIUS_KM = 6378.137
EARTH_MU_KM3_S2 = 398600.4418  # Standard gravitational parameter (GM)


def parse_tle_pair(line1: str, line2: str, name: str = "UNKNOWN") -> SatelliteOrbitalElements:
    """Parse a standard NORAD Two-Line Element (TLE) set into SatelliteOrbitalElements.

    Line 1 columns:
      03-07: NORAD Catalog Number
      10-17: International Designator
      19-32: Epoch (YYDDD.DDDDDDDD)
      54-61: B* drag term
    Line 2 columns:
      03-07: NORAD Catalog Number
      09-16: Inclination (degrees)
      18-25: RAAN (degrees)
      27-33: Eccentricity (decimal point assumed)
      35-42: Argument of Perigee (degrees)
      44-51: Mean Anomaly (degrees)
      53-63: Mean Motion (revs per day)
    """
    line1 = line1.strip()
    line2 = line2.strip()

    norad_id = int(line1[2:7].strip())
    intl_desig = line1[9:17].strip()

    # Parse TLE Epoch (YYDDD.DDDDDDDD)
    epoch_str = line1[18:32].strip()
    epoch_yy = int(epoch_str[0:2])
    epoch_ddd = float(epoch_str[2:])
    year = 2000 + epoch_yy if epoch_yy < 57 else 1900 + epoch_yy

    # Days to datetime
    import datetime as dt
    epoch_start = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    epoch_utc = epoch_start + dt.timedelta(days=(epoch_ddd - 1.0))

    # Parse B* drag term: format e.g. " 12345-4" -> 0.12345e-4
    bstar_str = line1[53:61].strip()
    try:
        if "-" in bstar_str[1:]:
            parts = bstar_str.split("-")
            bstar = float(parts[0]) * (10 ** -float(parts[1])) * 1e-5
        elif "+" in bstar_str[1:]:
            parts = bstar_str.split("+")
            bstar = float(parts[0]) * (10 ** float(parts[1])) * 1e-5
        else:
            bstar = float(bstar_str) * 1e-5
    except Exception:
        bstar = 0.0

    inclination_deg = float(line2[8:16].strip())
    raan_deg = float(line2[17:25].strip())
    ecc_str = "0." + line2[26:33].strip()
    eccentricity = float(ecc_str)
    arg_perigee_deg = float(line2[34:42].strip())
    mean_anomaly_deg = float(line2[43:51].strip())
    mean_motion_rev_day = float(line2[52:63].strip())

    # Derived Keplerian parameters
    n_rad_s = mean_motion_rev_day * (2.0 * math.pi) / 86400.0
    semi_major_axis_km = (EARTH_MU_KM3_S2 / (n_rad_s ** 2)) ** (1.0 / 3.0)
    period_minutes = (2.0 * math.pi / n_rad_s) / 60.0

    r_perigee = semi_major_axis_km * (1.0 - eccentricity)
    r_apogee = semi_major_axis_km * (1.0 + eccentricity)
    perigee_km = max(0.0, r_perigee - EARTH_RADIUS_KM)
    apogee_km = max(0.0, r_apogee - EARTH_RADIUS_KM)

    return SatelliteOrbitalElements(
        norad_cat_id=norad_id,
        name=name,
        intl_designator=intl_desig,
        epoch_utc=epoch_utc,
        inclination_deg=inclination_deg,
        raan_deg=raan_deg,
        eccentricity=eccentricity,
        arg_perigee_deg=arg_perigee_deg,
        mean_anomaly_deg=mean_anomaly_deg,
        mean_motion_rev_day=mean_motion_rev_day,
        bstar=bstar,
        period_minutes=period_minutes,
        apogee_km=apogee_km,
        perigee_km=perigee_km,
    )
