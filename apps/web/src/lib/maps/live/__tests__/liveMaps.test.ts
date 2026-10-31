import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  formatFreshnessAge,
  getFreshnessBadge,
  getDataClassBadge,
  getCategoryLabel,
  getProviderStatusBadge,
} from "../freshness";
import {
  AtlasGeoObservation,
  FreshnessState,
  InfrastructureProximityMatch,
  LiveObservationCategory,
  ObservationDataClass,
} from "../types";

describe("Stage 134 — Live Physical-World Intelligence Web Tests", () => {
  it("Fixture B: formats freshness age thresholds accurately", () => {
    assert.equal(formatFreshnessAge(15), "15s ago");
    assert.equal(formatFreshnessAge(120), "2m ago");
    assert.equal(formatFreshnessAge(3700), "1h 1m ago");
    assert.equal(formatFreshnessAge(90000), "1d ago");
  });

  it("Fixture B: assigns institutional freshness badge styling", () => {
    const currBadge = getFreshnessBadge("CURRENT");
    assert.equal(currBadge.label, "CURRENT");
    assert.match(currBadge.text, /text-emerald/);

    const delayedBadge = getFreshnessBadge("DELAYED");
    assert.equal(delayedBadge.label, "DELAYED");
    assert.match(delayedBadge.text, /text-amber/);

    const staleBadge = getFreshnessBadge("STALE");
    assert.equal(staleBadge.label, "STALE");
    assert.match(staleBadge.text, /text-orange/);

    const expBadge = getFreshnessBadge("EXPIRED");
    assert.equal(expBadge.label, "EXPIRED");

    const histBadge = getFreshnessBadge("HISTORICAL");
    assert.equal(histBadge.label, "HISTORICAL");
    assert.match(histBadge.text, /text-blue/);
  });

  it("Fixture E & G: distinguishes OBSERVED vs PROPAGATED data classes", () => {
    const obsBadge = getDataClassBadge("OBSERVED");
    assert.equal(obsBadge.tag, "OBSERVED");
    assert.match(obsBadge.label, /PHYSICAL MEASUREMENT/);

    const propBadge = getDataClassBadge("PROPAGATED");
    assert.equal(propBadge.tag, "PROPAGATED");
    assert.match(propBadge.label, /ORBITAL PROPAGATION/);

    const fcastBadge = getDataClassBadge("FORECAST");
    assert.equal(fcastBadge.tag, "FORECAST");
  });

  it("Fixture I & K: formats provider health badges without mock claims", () => {
    const online = getProviderStatusBadge("ONLINE");
    assert.equal(online.label, "ONLINE");

    const unconf = getProviderStatusBadge("UNCONFIGURED");
    assert.equal(unconf.label, "UNCONFIGURED");

    const restricted = getProviderStatusBadge("ACCESS_RESTRICTED");
    assert.equal(restricted.label, "RESTRICTED");
  });

  it("Fixture M: verifies infrastructure proximity disclaimer invariant", () => {
    const match: InfrastructureProximityMatch = {
      facility_id: "FAC-001",
      facility_name: "Bay Area Refinery",
      facility_sector: "ENERGY",
      facility_coordinates: [-122.38, 37.93],
      observation_id: "eq-test",
      observation_category: "EARTHQUAKE",
      event_entity_id: "eq-1",
      distance_km: 12.5,
      inside_alert_perimeter: false,
      damage_assessment: "UNVERIFIED_PROXIMITY_ONLY",
      damage_confirmed: false,
      disclaimer:
        "Spatial proximity does not constitute physical damage, structural failure, or operational outage. On-site telemetry or official inspection required.",
    };

    assert.equal(match.damage_assessment, "UNVERIFIED_PROXIMITY_ONLY");
    assert.equal(match.damage_confirmed, false);
    assert.match(match.disclaimer, /does not constitute physical damage/);
  });

  it("resolves canonical human-readable category labels", () => {
    assert.equal(getCategoryLabel("AIRCRAFT"), "Flights (ADS-B)");
    assert.equal(getCategoryLabel("VESSEL"), "Vessels (AIS)");
    assert.equal(getCategoryLabel("SATELLITE"), "Satellites (SGP4)");
    assert.equal(getCategoryLabel("WEATHER_ALERT"), "Weather Alerts (CAP)");
    assert.equal(getCategoryLabel("EARTHQUAKE"), "Earthquakes (USGS)");
    assert.equal(getCategoryLabel("ACTIVE_FIRE"), "Thermal Hotspots (FIRMS)");
  });
});
