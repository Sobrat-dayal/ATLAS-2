"""NOAA / NWS Weather Alerts and METAR Observations Adapter (Stage 134).

Parses Common Alerting Protocol (CAP v1.2) active severe weather alerts,
including polygon boundaries and severity levels, as well as surface observations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import (
    AtlasGeoObservation,
    FreshnessState,
    LiveObservationCategory,
    ObservationDataClass,
    WeatherAlert,
    WeatherAlertSeverity,
    WeatherObservation,
)


class NWSWeatherAdapter:
    """Adapter for National Weather Service CAP alerts and surface observations."""

    def __init__(self) -> None:
        self.provider_id = "noaa_nws"
        self.product_id = "cap_alerts_v1"

    def parse_cap_feature(self, feature: Dict[str, Any]) -> Tuple[WeatherAlert, AtlasGeoObservation]:
        """Parse NWS GeoJSON CAP alert feature into WeatherAlert and AtlasGeoObservation."""
        props = feature.get("properties", {})
        geom = feature.get("geometry")

        alert_id = str(feature.get("id", props.get("id", "nws-alert-001")))
        event_name = props.get("event", "Special Weather Statement")
        headline = props.get("headline", props.get("description", event_name))
        urgency = props.get("urgency", "Expected")
        certainty = props.get("certainty", "Likely")
        area_desc = props.get("areaDesc", "Regional Warning Area")

        # Map severity
        raw_sev = str(props.get("severity", "Moderate")).upper()
        try:
            severity = WeatherAlertSeverity(raw_sev)
        except ValueError:
            severity = WeatherAlertSeverity.MODERATE

        # Timestamps
        eff_str = props.get("effective")
        exp_str = props.get("expires")
        eff_utc = (
            datetime.fromisoformat(eff_str.replace("Z", "+00:00"))
            if eff_str
            else datetime.now(timezone.utc)
        )
        exp_utc = (
            datetime.fromisoformat(exp_str.replace("Z", "+00:00"))
            if exp_str
            else datetime.now(timezone.utc)
        )

        alert = WeatherAlert(
            alert_id=alert_id,
            event=event_name,
            headline=headline,
            severity=severity,
            urgency=urgency,
            certainty=certainty,
            effective_utc=eff_utc,
            expires_utc=exp_utc,
            area_desc=area_desc,
            polygon_geojson=geom,
        )

        # Centroid calculation for point representation
        centroid_lon = 0.0
        centroid_lat = 0.0
        if geom and geom.get("coordinates") and geom.get("type") == "Polygon":
            poly_ring = geom["coordinates"][0]
            if poly_ring:
                centroid_lon = sum(pt[0] for pt in poly_ring) / len(poly_ring)
                centroid_lat = sum(pt[1] for pt in poly_ring) / len(poly_ring)

        observation = AtlasGeoObservation(
            observation_id=alert_id,
            category=LiveObservationCategory.WEATHER_ALERT,
            data_class=ObservationDataClass.OBSERVED,
            entity_id=alert_id,
            entity_name=f"{severity.value}: {event_name}",
            provider_id=self.provider_id,
            product_id=self.product_id,
            source_revision=1,
            longitude=round(centroid_lon, 5),
            latitude=round(centroid_lat, 5),
            geometry=geom or {"type": "Point", "coordinates": [centroid_lon, centroid_lat]},
            observed_at=eff_utc,
            source_published_at=eff_utc,
            received_at=datetime.now(timezone.utc),
            ingested_at=datetime.now(timezone.utc),
            freshness_state=FreshnessState.CURRENT,
            properties={
                "event": event_name,
                "headline": headline,
                "severity": severity.value,
                "urgency": urgency,
                "certainty": certainty,
                "area_desc": area_desc,
                "effective_utc": eff_utc.isoformat(),
                "expires_utc": exp_utc.isoformat(),
            },
            source_attribution="NOAA / National Weather Service",
            provenance_note="NWS Common Alerting Protocol (CAP)",
        )

        return alert, observation

    def parse_metar_observation(self, station_data: Dict[str, Any]) -> Tuple[WeatherObservation, AtlasGeoObservation]:
        """Parse METAR weather station surface report."""
        st_id = str(station_data.get("station_id", "KJFK"))
        st_name = str(station_data.get("station_name", "JFK International Airport"))
        lon = float(station_data["longitude"])
        lat = float(station_data["latitude"])
        obs_time = station_data.get("observation_time_utc", datetime.now(timezone.utc))
        if isinstance(obs_time, str):
            obs_time = datetime.fromisoformat(obs_time.replace("Z", "+00:00"))

        temp_c = station_data.get("temperature_c")
        dew_c = station_data.get("dew_point_c")
        press_hpa = station_data.get("pressure_hpa")
        w_speed = station_data.get("wind_speed_mps")
        w_dir = station_data.get("wind_direction_deg")
        w_gust = station_data.get("wind_gust_mps")
        vis_m = station_data.get("visibility_m")
        cond = station_data.get("condition_text", "Fair")

        weather_obs = WeatherObservation(
            station_id=st_id,
            station_name=st_name,
            observation_time_utc=obs_time,
            temperature_c=temp_c,
            dew_point_c=dew_c,
            pressure_hpa=press_hpa,
            wind_speed_mps=w_speed,
            wind_direction_deg=w_dir,
            wind_gust_mps=w_gust,
            visibility_m=vis_m,
            condition_text=cond,
            longitude=lon,
            latitude=lat,
        )

        obs = AtlasGeoObservation(
            observation_id=f"metar-{st_id}-{obs_time.strftime('%Y%m%d%H%M')}",
            category=LiveObservationCategory.WEATHER_OBSERVATION,
            data_class=ObservationDataClass.OBSERVED,
            entity_id=st_id,
            entity_name=f"{st_id} ({st_name})",
            provider_id=self.provider_id,
            product_id="metar_surface_v1",
            source_revision=1,
            longitude=lon,
            latitude=lat,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            observed_at=obs_time,
            source_published_at=obs_time,
            received_at=datetime.now(timezone.utc),
            ingested_at=datetime.now(timezone.utc),
            freshness_state=FreshnessState.CURRENT,
            properties={
                "temperature_c": temp_c,
                "dew_point_c": dew_c,
                "pressure_hpa": press_hpa,
                "wind_speed_mps": w_speed,
                "wind_direction_deg": w_dir,
                "wind_gust_mps": w_gust,
                "visibility_m": vis_m,
                "condition_text": cond,
            },
            source_attribution="NOAA / National Weather Service / Aviation Weather Center",
            provenance_note="METAR Surface Weather Observation",
        )

        return weather_obs, obs

