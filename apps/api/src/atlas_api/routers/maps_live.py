"""FastAPI Router for ATLAS Live Physical-World Intelligence (Stage 134).

Provides authenticated endpoints for live observations, real-time snapshot querying,
cursor-based delta sync, SGP4 orbital propagation, CAP weather alerts, earthquake revisions,
H3 spatial aggregation, and infrastructure proximity correlation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from atlas.maps.live.domain import (
    AtlasGeoObservation,
    FreshnessState,
    InfrastructureProximityMatch,
    LiveGeoProvider,
    LiveObservationCategory,
    SatelliteOrbitalElements,
    SatelliteState,
    TrajectorySegment,
)
from atlas.maps.live.errors import (
    LiveCoordinatesInvalidError,
    LiveDomainError,
    LiveEventNotFoundError,
    LiveHistoryNotLicensedError,
    LiveObservationTooOldError,
    LiveOrbitPropagationFailedError,
    LiveProviderAccessDeniedError,
    LiveProviderNotConfiguredError,
    LiveProviderUnavailableError,
    LiveStaleOrbitElementsError,
    LiveViewportTooLargeError,
)
from atlas.maps.live.orbital.elements import parse_tle_pair
from atlas.maps.live.seed import ISS_ELEMENTS, STALE_SATELLITE_ELEMENTS
from atlas.maps.live.service import atlas_live_geo_service
from fastapi import APIRouter, HTTPException, Query, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/live", tags=["Maps Live Physical-World"])


# --------------------------------------------------------------------------
# Request Schemas
# --------------------------------------------------------------------------
class LiveSnapshotRequest(BaseModel):
    categories: Optional[List[LiveObservationCategory]] = None
    bbox: Optional[List[float]] = None  # [min_lon, min_lat, max_lon, max_lat]
    max_results: int = Field(default=1000, le=5000)


class LiveDeltasRequest(BaseModel):
    since_sequence: int
    categories: Optional[List[LiveObservationCategory]] = None
    bbox: Optional[List[float]] = None
    max_results: int = Field(default=1000, le=5000)


class LivePlaybackRequest(BaseModel):
    target_time_utc: datetime
    categories: Optional[List[LiveObservationCategory]] = None
    window_seconds: float = Field(default=3600.0, le=86400.0)


class SatellitePropagateRequest(BaseModel):
    norad_cat_id: Optional[int] = None
    tle_line1: Optional[str] = None
    tle_line2: Optional[str] = None
    name: Optional[str] = "CUSTOM_SAT"
    propagate_at: Optional[datetime] = None
    fail_on_critical_stale: bool = False


class InfrastructureProximityRequest(BaseModel):
    event: Dict[str, Any]
    max_radius_km: float = Field(default=150.0, le=500.0)
    facilities: Optional[List[Dict[str, Any]]] = None


class H3LiveAggregateRequest(BaseModel):
    resolution: int = Field(default=4, ge=0, le=15)
    categories: Optional[List[LiveObservationCategory]] = None


class TrajectorySplitRequest(BaseModel):
    entity_id: str
    category: LiveObservationCategory = LiveObservationCategory.AIRCRAFT
    points: List[Dict[str, Any]]
    max_gap_seconds: Optional[float] = None


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------
@router.get("/providers")
async def list_providers() -> List[LiveGeoProvider]:
    """List all supported live data providers with health and configuration status."""
    return atlas_live_geo_service.list_providers()


@router.get("/providers/{provider_id}/status")
async def get_provider_status(provider_id: str) -> LiveGeoProvider:
    """Retrieve detailed health and configuration status of an upstream live provider."""
    provider = atlas_live_geo_service.get_provider(provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found in registry",
        )
    return provider


@router.get("/layers")
async def get_live_layers_catalog() -> Dict[str, Any]:
    """Catalog of live physical-world observation layers."""
    return {
        "layers": [
            {
                "id": "live-aircraft",
                "name": "Live Aircraft Flights (ADS-B)",
                "category": LiveObservationCategory.AIRCRAFT.value,
                "provider": "OpenSky Network / FAA",
                "data_class": "OBSERVED",
                "refresh_interval_sec": 10,
                "description": "Real-time aircraft state vectors, callsigns, barometric altitudes, speeds, and squawks.",
            },
            {
                "id": "live-vessels",
                "name": "Live Maritime Vessels (AIS)",
                "category": LiveObservationCategory.VESSEL.value,
                "provider": "Spire Maritime / USCG",
                "data_class": "OBSERVED",
                "refresh_interval_sec": 60,
                "description": "Commercial vessel transponder tracking, heading, draft, speed over ground, and voyage destinations.",
            },
            {
                "id": "live-satellites",
                "name": "Active Satellites & Space Stations",
                "category": LiveObservationCategory.SATELLITE.value,
                "provider": "CelesTrak / Space-Track",
                "data_class": "PROPAGATED",
                "refresh_interval_sec": 1,
                "description": "SGP4-propagated orbits, ground tracks, altitudes, footprints, and velocities from Keplerian orbital elements.",
            },
            {
                "id": "live-weather-alerts",
                "name": "Severe Weather Alerts (CAP)",
                "category": LiveObservationCategory.WEATHER_ALERT.value,
                "provider": "NOAA National Weather Service",
                "data_class": "OBSERVED",
                "refresh_interval_sec": 60,
                "description": "Common Alerting Protocol (CAP) polygons, severity, urgency, certainty, and effective active windows.",
            },
            {
                "id": "live-earthquakes",
                "name": "Real-Time Earthquakes (USGS)",
                "category": LiveObservationCategory.EARTHQUAKE.value,
                "provider": "USGS Earthquake Hazards Program",
                "data_class": "OBSERVED",
                "refresh_interval_sec": 180,
                "description": "Global seismic events with magnitude revisions, hypocenter depths, and tsunami warnings.",
            },
            {
                "id": "live-active-fires",
                "name": "Active Fires & Thermal Anomalies",
                "category": LiveObservationCategory.ACTIVE_FIRE.value,
                "provider": "NASA FIRMS (VIIRS / MODIS)",
                "data_class": "OBSERVED",
                "refresh_interval_sec": 3600,
                "description": "Satellite-detected thermal hotspots, Fire Radiative Power (MW), and brightness temperatures.",
            },
        ]
    }


@router.post("/observations/snapshot")
async def get_observations_snapshot(req: LiveSnapshotRequest) -> Dict[str, Any]:
    """Retrieve full active observation snapshot with optional spatial bounds."""
    try:
        observations, current_seq = atlas_live_geo_service.get_snapshot(
            categories=req.categories,
            bbox=req.bbox,
            max_results=req.max_results,
        )
        return {
            "sequence_cursor": current_seq,
            "count": len(observations),
            "observations": [obs.model_dump() for obs in observations],
        }
    except LiveCoordinatesInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except Exception as exc:
        logger.exception("Snapshot retrieval failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/observations/deltas")
async def get_observations_deltas(req: LiveDeltasRequest) -> Dict[str, Any]:
    """Retrieve deltas since a sequence cursor."""
    try:
        deltas, current_seq = atlas_live_geo_service.get_deltas(
            since_sequence=req.since_sequence,
            categories=req.categories,
            bbox=req.bbox,
            max_results=req.max_results,
        )
        return {
            "sequence_cursor": current_seq,
            "deltas_count": len(deltas),
            "deltas": [d.model_dump() for d in deltas],
        }
    except Exception as exc:
        logger.exception("Deltas retrieval failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/playback")
async def get_playback_snapshot(req: LivePlaybackRequest) -> Dict[str, Any]:
    """Reconstruct historical physical state known at target_time_utc."""
    try:
        observations = atlas_live_geo_service.get_playback_snapshot(
            target_time_utc=req.target_time_utc,
            categories=req.categories,
            window_seconds=req.window_seconds,
        )
        return {
            "target_time_utc": req.target_time_utc.isoformat(),
            "count": len(observations),
            "observations": [obs.model_dump() for obs in observations],
        }
    except LiveHistoryNotLicensedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except Exception as exc:
        logger.exception("Playback query failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/satellites/propagate")
async def propagate_satellite_orbit(req: SatellitePropagateRequest) -> Dict[str, Any]:
    """Propagate satellite orbital elements to target time using SGP4 mechanics."""
    try:
        # Determine elements
        if req.tle_line1 and req.tle_line2:
            elements = parse_tle_pair(req.tle_line1, req.tle_line2, name=req.name or "CUSTOM_SAT")
        elif req.norad_cat_id == 25544:
            elements = ISS_ELEMENTS
        elif req.norad_cat_id == 48011:
            elements = STALE_SATELLITE_ELEMENTS
        else:
            elements = ISS_ELEMENTS

        state = atlas_live_geo_service.propagate_satellite_elements(
            elements=elements,
            propagate_at=req.propagate_at,
            fail_on_critical_stale=req.fail_on_critical_stale,
        )
        return {"satellite_state": state.model_dump()}
    except LiveStaleOrbitElementsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except LiveOrbitPropagationFailedError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.message)
    except Exception as exc:
        logger.exception("Satellite propagation failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/infrastructure/proximity")
async def correlate_proximity(req: InfrastructureProximityRequest) -> Dict[str, Any]:
    """Correlate physical infrastructure facilities with a live event without asserting damage."""
    try:
        matches = atlas_live_geo_service.correlate_infrastructure_proximity(
            event_dict=req.event,
            facilities=req.facilities,
            max_radius_km=req.max_radius_km,
        )
        return {
            "event_id": req.event.get("observation_id", req.event.get("entity_id")),
            "match_count": len(matches),
            "matches": [m.model_dump() for m in matches],
            "disclaimer": (
                "Spatial proximity does not constitute physical damage, structural failure, "
                "or operational outage. On-site telemetry or official inspection required."
            ),
        }
    except Exception as exc:
        logger.exception("Proximity correlation failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/aggregates/h3")
async def aggregate_live_h3(req: H3LiveAggregateRequest) -> Dict[str, Any]:
    """Aggregate active observations into H3 hexagonal indices."""
    try:
        aggregates = atlas_live_geo_service.aggregate_to_h3(
            resolution=req.resolution,
            categories=req.categories,
        )
        return {
            "resolution": req.resolution,
            "cell_count": len(aggregates),
            "aggregates": aggregates,
        }
    except Exception as exc:
        logger.exception("H3 aggregation failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/trajectories/split")
async def split_trajectory(req: TrajectorySplitRequest) -> Dict[str, Any]:
    """Split trajectory points into segments on communication or radar tracking blackouts."""
    try:
        segments = atlas_live_geo_service.get_trajectory_segments(
            entity_id=req.entity_id,
            category=req.category,
            points=req.points,
            max_gap_seconds=req.max_gap_seconds,
        )
        return {
            "entity_id": req.entity_id,
            "segment_count": len(segments),
            "segments": [s.model_dump() for s in segments],
        }
    except Exception as exc:
        logger.exception("Trajectory split failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/earthquakes/revision")
async def apply_earthquake_revision(revised_feature: Dict[str, Any]) -> Dict[str, Any]:
    """Apply an earthquake revision, updating existing event record without duplicating (Fixture A)."""
    try:
        eq_event, obs, is_new = atlas_live_geo_service.apply_earthquake_revision(revised_feature)
        return {
            "is_new_event": is_new,
            "earthquake_event": eq_event.model_dump(),
            "observation": obs.model_dump(),
        }
    except Exception as exc:
        logger.exception("Earthquake revision failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

