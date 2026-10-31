/**
 * Predicate labels, badge colors, and verification metadata (Stage 136).
 */

import { PredicateType, RelationshipVerificationStatus } from './types';

export const PROHIBITED_PREDICATES = [
  'AFFECTS',
  'AFFECTED_BY',
  'CAUSED_LOSS',
  'DAMAGED',
  'EXPOSED_TO',
  'RISK_OF',
  'IMPACTED',
  'DESTROYED',
  'BANKRUPTED',
] as const;

export interface PredicateMetadata {
  code: PredicateType;
  label: string;
  category: 'direct' | 'regulatory' | 'geographic' | 'corporate' | 'event_event' | 'structural';
  badgeColor: string;
  description: string;
}

export const PREDICATE_REGISTRY: Record<PredicateType, PredicateMetadata> = {
  DIRECT_SUBJECT: {
    code: 'DIRECT_SUBJECT',
    label: 'Direct Subject',
    category: 'direct',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    description: 'The entity is the primary direct actor or explicit focal point of the event.',
  },
  EXPLICITLY_MENTIONS: {
    code: 'EXPLICITLY_MENTIONS',
    label: 'Explicitly Mentions',
    category: 'direct',
    badgeColor: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
    description: 'Entity is cited explicitly within the body or disclosure text.',
  },
  ANNOUNCED_BY: {
    code: 'ANNOUNCED_BY',
    label: 'Announced By',
    category: 'corporate',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    description: 'The reporting company, issuer, or agency that officially announced the event.',
  },
  ISSUED_BY: {
    code: 'ISSUED_BY',
    label: 'Issued By',
    category: 'regulatory',
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    description: 'Government, sanctions, or regulatory body that officially promulgated the decree.',
  },
  REGULATED_BY: {
    code: 'REGULATED_BY',
    label: 'Regulated By',
    category: 'regulatory',
    badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    description: 'Regulatory authority conducting review or enforcement.',
  },
  OFFICIALLY_DESIGNATES: {
    code: 'OFFICIALLY_DESIGNATES',
    label: 'Officially Designates',
    category: 'regulatory',
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    description: 'Strict legal designation (e.g. OFAC SDN list). Requires exact entity match.',
  },
  OFFICIAL_ACTION_TARGET: {
    code: 'OFFICIAL_ACTION_TARGET',
    label: 'Action Target',
    category: 'regulatory',
    badgeColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    description: 'Entity subjected to civil, antitrust, or regulatory investigation.',
  },
  CORPORATE_ACTION_PARTICIPANT: {
    code: 'CORPORATE_ACTION_PARTICIPANT',
    label: 'Action Participant',
    category: 'corporate',
    badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
    description: 'Participant in corporate transaction (e.g., Acquirer in M&A).',
  },
  CORPORATE_ACTION_TARGET: {
    code: 'CORPORATE_ACTION_TARGET',
    label: 'Action Target',
    category: 'corporate',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    description: 'Target company of tender offer, acquisition, or buyout.',
  },
  CONCERNS_INSTRUMENT: {
    code: 'CONCERNS_INSTRUMENT',
    label: 'Concerns Instrument',
    category: 'direct',
    badgeColor: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    description: 'Explicit security, share class, or bond mentioned in the filing.',
  },
  RELEASES_INDICATOR: {
    code: 'RELEASES_INDICATOR',
    label: 'Releases Indicator',
    category: 'direct',
    badgeColor: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
    description: 'Macroeconomic time series released by statistical authority.',
  },
  DECIDED_BY: {
    code: 'DECIDED_BY',
    label: 'Decided By',
    category: 'regulatory',
    badgeColor: 'bg-violet-500/10 text-violet-400 border-violet-500/30',
    description: 'Monetary policy committee or central bank governor.',
  },
  HAS_ISSUING_JURISDICTION: {
    code: 'HAS_ISSUING_JURISDICTION',
    label: 'Issuing Jurisdiction',
    category: 'geographic',
    badgeColor: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
    description: 'Sovereign nation or jurisdiction responsible for the official act.',
  },
  OCCURRED_IN: {
    code: 'OCCURRED_IN',
    label: 'Occurred In',
    category: 'geographic',
    badgeColor: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    description: 'Geographic nation or administrative region where the event took place.',
  },
  REPORTED_AT: {
    code: 'REPORTED_AT',
    label: 'Reported At',
    category: 'geographic',
    badgeColor: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
    description: 'Location from which news report or dispatch originated.',
  },
  REFERENCES_COMMODITY: {
    code: 'REFERENCES_COMMODITY',
    label: 'References Commodity',
    category: 'direct',
    badgeColor: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    description: 'Physical commodity or standardized contract benchmark.',
  },
  REFERENCES_SECTOR: {
    code: 'REFERENCES_SECTOR',
    label: 'References Sector',
    category: 'direct',
    badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    description: 'GICS or ICB economic sector explicitly referenced.',
  },
  REFERENCES_INDUSTRY: {
    code: 'REFERENCES_INDUSTRY',
    label: 'References Industry',
    category: 'direct',
    badgeColor: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
    description: 'Granular industry classification cited in event text.',
  },
  REFERENCES_FACILITY: {
    code: 'REFERENCES_FACILITY',
    label: 'References Facility',
    category: 'direct',
    badgeColor: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
    description: 'Corporate factory, distribution hub, or office site.',
  },
  REFERENCES_INFRASTRUCTURE_ASSET: {
    code: 'REFERENCES_INFRASTRUCTURE_ASSET',
    label: 'References Infrastructure',
    category: 'direct',
    badgeColor: 'bg-orange-500/10 text-orange-300 border-orange-500/30',
    description: 'Power plant, port, airport, pipeline, or grid segment.',
  },
  GEOGRAPHICALLY_NEAR: {
    code: 'GEOGRAPHICALLY_NEAR',
    label: 'Geographically Near',
    category: 'geographic',
    badgeColor: 'bg-amber-500/15 text-amber-400 border-amber-500/40 font-semibold',
    description: 'Spatial distance within verified radius; strictly asserts spatial coordinates, NO damage claims.',
  },
  SOURCE_REPORTED_ASSOCIATION: {
    code: 'SOURCE_REPORTED_ASSOCIATION',
    label: 'Reported Association',
    category: 'direct',
    badgeColor: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
    description: 'Journalistic report or rumor connecting entity to event. Candidate until confirmed.',
  },
  // Event-to-Event
  REVISES: {
    code: 'REVISES',
    label: 'Revises',
    category: 'event_event',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    description: 'Formally modifies numerical value or dates of prior event.',
  },
  SUPERSEDES: {
    code: 'SUPERSEDES',
    label: 'Supersedes',
    category: 'event_event',
    badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    description: 'Completely replaces a preliminary or prior announcement.',
  },
  CORRECTS: {
    code: 'CORRECTS',
    label: 'Corrects',
    category: 'event_event',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    description: 'Corrects an erratum in a published event record.',
  },
  RETRACTS: {
    code: 'RETRACTS',
    label: 'Retracts',
    category: 'event_event',
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    description: 'Officially retracts or invalidates a previously released event.',
  },
  FORMAL_FOLLOW_UP_TO: {
    code: 'FORMAL_FOLLOW_UP_TO',
    label: 'Formal Follow-Up To',
    category: 'event_event',
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    description: 'Sequential continuation in a structured administrative process.',
  },
  IMPLEMENTS: {
    code: 'IMPLEMENTS',
    label: 'Implements',
    category: 'event_event',
    badgeColor: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
    description: 'Executes or carries into effect a prior policy or agreement.',
  },
  OFFICIALLY_RESPONDS_TO: {
    code: 'OFFICIALLY_RESPONDS_TO',
    label: 'Officially Responds To',
    category: 'event_event',
    badgeColor: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    description: 'Formal statement or counter-filing addressing prior action.',
  },
  // Structural
  SUBSIDIARY_OF: {
    code: 'SUBSIDIARY_OF',
    label: 'Subsidiary Of',
    category: 'structural',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    description: 'Entity is owned or controlled by parent corporate entity.',
  },
  PARENT_OF: {
    code: 'PARENT_OF',
    label: 'Parent Of',
    category: 'structural',
    badgeColor: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    description: 'Entity holds controlling equity in subsidiary entity.',
  },
  ISSUED_BY_COMPANY: {
    code: 'ISSUED_BY_COMPANY',
    label: 'Issued By Company',
    category: 'structural',
    badgeColor: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    description: 'Financial instrument was issued by this corporate entity.',
  },
  OPERATED_BY: {
    code: 'OPERATED_BY',
    label: 'Operated By',
    category: 'structural',
    badgeColor: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
    description: 'Physical asset or facility is managed by operating entity.',
  },
  LOCATED_IN: {
    code: 'LOCATED_IN',
    label: 'Located In',
    category: 'structural',
    badgeColor: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    description: 'Physical site is situated within sovereign boundary.',
  },
  PRIMARY_EXCHANGE_IN: {
    code: 'PRIMARY_EXCHANGE_IN',
    label: 'Primary Exchange In',
    category: 'structural',
    badgeColor: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
    description: 'Primary exchange listing country for security.',
  },
  COMPRISING_SECTOR: {
    code: 'COMPRISING_SECTOR',
    label: 'Comprising Sector',
    category: 'structural',
    badgeColor: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
    description: 'Sector classification encompassing the business line.',
  },
};

export const VERIFICATION_STATUS_META: Record<RelationshipVerificationStatus, { label: string; badgeColor: string }> = {
  VERIFIED_DIRECT: {
    label: 'Verified Direct',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  },
  SOURCE_SUPPORTED: {
    label: 'Source Supported',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  },
  CORROBORATED: {
    label: 'Corroborated',
    badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  },
  CANDIDATE: {
    label: 'Candidate (Unverified)',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  },
  CONFLICTED: {
    label: 'Conflicted Sources',
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  },
  REJECTED: {
    label: 'Rejected',
    badgeColor: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
  },
  REVOKED: {
    label: 'Revoked',
    badgeColor: 'bg-red-500/10 text-red-400 border-red-500/30',
  },
};

