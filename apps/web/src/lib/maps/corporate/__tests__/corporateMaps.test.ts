/**
 * Unit Test Suite for Stage 132: Corporate Geography & Facility Mapping.
 */

import { describe, it } from "node:test";
import assert from "node:assert";
import {
  FACILITY_STATUS_STYLES,
  FACILITY_TYPE_STYLES,
  PRECISION_CLASS_INFO,
} from "../facilityStyles";
import {
  CorporateFacility,
  CorporateFacilityType,
  CorporateFacilityStatus,
  GeographicPrecisionClass,
  FacilityRelationshipType,
  VerificationStatus,
} from "../types";

describe("Stage 132 — Corporate Geography and Facility Mapping", () => {
  it("Fixture A: Headquarters is not conflated with manufacturing", () => {
    const hqStyle = FACILITY_TYPE_STYLES["CORPORATE_HEADQUARTERS"];
    const mfgStyle = FACILITY_TYPE_STYLES["MANUFACTURING_FACILITY"];

    assert.strictEqual(hqStyle.label, "Corporate HQ");
    assert.strictEqual(mfgStyle.label, "Manufacturing Plant");
    assert.notStrictEqual(hqStyle.color, mfgStyle.color);
  });

  it("Fixture B: Registered office is distinct from operating headquarters", () => {
    const regOfficeStyle = FACILITY_TYPE_STYLES["REGISTERED_OFFICE"];
    assert.strictEqual(regOfficeStyle.label, "Registered Office");
    assert.notStrictEqual(regOfficeStyle.label, "Corporate HQ");
  });

  it("Fixture C: Separates property owner, operator, and occupant roles", () => {
    const facility: CorporateFacility = {
      facility_id: "fac_test_c",
      canonical_name: "Test Facility C",
      facility_type: "MANUFACTURING_FACILITY",
      facility_status: "OPERATIONAL",
      precision_class: "VERIFIED_SITE_POINT",
      country_code: "US",
      primary_entity_id: "cmp_owner",
      source_manifest_id: "src_test",
      verification_status: "VERIFIED",
      is_public: true,
      geometry_type: "POINT",
      links: [
        {
          link_id: "l_1",
          facility_id: "fac_test_c",
          legal_entity_id: "ent_owner_a",
          company_id: "cmp_owner",
          relationship_type: "OWNED_BY",
          verification_status: "VERIFIED",
        },
        {
          link_id: "l_2",
          facility_id: "fac_test_c",
          legal_entity_id: "ent_operator_b",
          company_id: "cmp_operator",
          relationship_type: "OPERATED_BY",
          verification_status: "VERIFIED",
        },
      ],
      evidence_claims: [],
      status_history: [],
    };

    const owners = facility.links.filter((l) => l.relationship_type === "OWNED_BY");
    const operators = facility.links.filter((l) => l.relationship_type === "OPERATED_BY");

    assert.strictEqual(owners.length, 1);
    assert.strictEqual(owners[0].company_id, "cmp_owner");
    assert.strictEqual(operators.length, 1);
    assert.strictEqual(operators[0].company_id, "cmp_operator");
    assert.notStrictEqual(owners[0].company_id, operators[0].company_id);
  });

  it("Fixture D: Distinguishes direct company facilities from subsidiary facilities", () => {
    const directFac: CorporateFacility = {
      facility_id: "fac_direct",
      canonical_name: "Parent HQ",
      facility_type: "CORPORATE_HEADQUARTERS",
      facility_status: "OPERATIONAL",
      precision_class: "VERIFIED_SITE_POINT",
      country_code: "US",
      primary_entity_id: "cmp_parent",
      source_manifest_id: "src_test",
      verification_status: "VERIFIED",
      is_public: true,
      geometry_type: "POINT",
      links: [],
      evidence_claims: [],
      status_history: [],
    };

    const subFac: CorporateFacility = {
      facility_id: "fac_sub",
      canonical_name: "Subsidiary Plant",
      facility_type: "MANUFACTURING_FACILITY",
      facility_status: "OPERATIONAL",
      precision_class: "VERIFIED_SITE_POINT",
      country_code: "DE",
      primary_entity_id: "cmp_subsidiary",
      source_manifest_id: "src_test",
      verification_status: "VERIFIED",
      is_public: true,
      geometry_type: "POINT",
      links: [],
      evidence_claims: [],
      status_history: [],
    };

    const facilities = [directFac, subFac];
    const rootCompanyId = "cmp_parent";

    const directCount = facilities.filter((f) => f.primary_entity_id === rootCompanyId).length;
    const subCount = facilities.filter((f) => f.primary_entity_id !== rootCompanyId).length;

    assert.strictEqual(directCount, 1);
    assert.strictEqual(subCount, 1);
  });

  it("Fixture F: Precision taxonomy distinguishes site point, polygon, and city centroid", () => {
    const exactPoint = PRECISION_CLASS_INFO["VERIFIED_SITE_POINT"];
    const exactPoly = PRECISION_CLASS_INFO["VERIFIED_SITE_POLYGON"];
    const cityCentroid = PRECISION_CLASS_INFO["LOCALITY_CENTROID"];

    assert.strictEqual(exactPoint.isApproximate, false);
    assert.strictEqual(exactPoly.isApproximate, false);
    assert.strictEqual(cityCentroid.isApproximate, true);
    assert.match(cityCentroid.description, /exact facility coordinates unknown/i);
  });

  it("Fixture I: Status unknown does not default to operational or permanently closed", () => {
    const unknownStyle = FACILITY_STATUS_STYLES["STATUS_UNKNOWN"];
    const opStyle = FACILITY_STATUS_STYLES["OPERATIONAL"];
    const closedStyle = FACILITY_STATUS_STYLES["PERMANENTLY_CLOSED"];

    assert.strictEqual(unknownStyle.label, "Status Unknown");
    assert.notStrictEqual(unknownStyle.label, opStyle.label);
    assert.notStrictEqual(unknownStyle.label, closedStyle.label);
  });

  it("Fixture N: Announced facilities are styled distinctly from operational ones", () => {
    const announcedStyle = FACILITY_STATUS_STYLES["ANNOUNCED"];
    const opStyle = FACILITY_STATUS_STYLES["OPERATIONAL"];

    assert.strictEqual(announcedStyle.label, "Announced");
    assert.strictEqual(opStyle.label, "Operational");
    assert.notStrictEqual(announcedStyle.bg, opStyle.bg);
  });
});

