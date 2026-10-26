/**
 * Authenticated REST API Client for Central Bank Intelligence (Stage 91).
 */

import {
  CentralBankBalanceSheetSummaryDTO,
  CentralBankCoverageResponseDTO,
  CentralBankInstitutionDTO,
  CentralBankOverviewDTO,
  CentralBankPolicyProgramDTO,
  CommitteeVotingRecordDTO,
  MonetaryPolicyDecisionDTO,
  MonetaryPolicyFrameworkDTO,
  MonetaryPolicyMeetingDTO,
  OfficialForwardGuidanceDTO,
  OfficialPublicationDTO,
  OfficialSpeechDTO,
  PolicyInstrumentDTO,
  PolicyTimelineEventDTO,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function getHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...extra,
  };
}

export class CentralBankApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "CENTRAL_BANK_API_ERROR") {
    super(message);
    this.name = "CentralBankApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    let errorCode = "UNKNOWN_ERROR";
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail =
          typeof errorJson.detail === "string"
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Body not JSON
    }
    throw new CentralBankApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function getCentralBanks(): Promise<CentralBankInstitutionDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CentralBankInstitutionDTO[]>(res);
}

export async function getCentralBankOverview(bankId: string): Promise<CentralBankOverviewDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/overview`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CentralBankOverviewDTO>(res);
}

export async function getCentralBankProfile(bankId: string): Promise<CentralBankInstitutionDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/profile`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CentralBankInstitutionDTO>(res);
}

export async function getMonetaryPolicyFramework(bankId: string): Promise<MonetaryPolicyFrameworkDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/framework`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<MonetaryPolicyFrameworkDTO>(res);
}

export async function getPolicyInstruments(bankId: string): Promise<PolicyInstrumentDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/instruments`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<PolicyInstrumentDTO[]>(res);
}

export async function getPolicyDecisions(
  bankId: string,
  asOf?: string
): Promise<MonetaryPolicyDecisionDTO[]> {
  const params = new URLSearchParams();
  if (asOf) params.append("as_of", asOf);
  const q = params.toString() ? `?${params.toString()}` : "";
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/decisions${q}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<MonetaryPolicyDecisionDTO[]>(res);
}

export async function getPolicyDecision(
  bankId: string,
  decisionId: string
): Promise<MonetaryPolicyDecisionDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/decisions/${encodeURIComponent(decisionId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<MonetaryPolicyDecisionDTO>(res);
}

export async function getPolicyMeetings(bankId: string): Promise<MonetaryPolicyMeetingDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/meetings`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<MonetaryPolicyMeetingDTO[]>(res);
}

export async function getMeetingVotingRecord(
  bankId: string,
  meetingId: string
): Promise<CommitteeVotingRecordDTO | null> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/meetings/${encodeURIComponent(meetingId)}/voting`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CommitteeVotingRecordDTO | null>(res);
}

export async function getPublications(bankId: string): Promise<OfficialPublicationDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/publications`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<OfficialPublicationDTO[]>(res);
}

export async function getSpeeches(bankId: string): Promise<OfficialSpeechDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/speeches`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<OfficialSpeechDTO[]>(res);
}

export async function getForwardGuidance(bankId: string): Promise<OfficialForwardGuidanceDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/guidance`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<OfficialForwardGuidanceDTO[]>(res);
}

export async function getBalanceSheet(
  bankId: string
): Promise<CentralBankBalanceSheetSummaryDTO | null> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/balance-sheet`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CentralBankBalanceSheetSummaryDTO | null>(res);
}

export async function getPolicyPrograms(bankId: string): Promise<CentralBankPolicyProgramDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/programs`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CentralBankPolicyProgramDTO[]>(res);
}

export async function getPolicyTimeline(bankId: string): Promise<PolicyTimelineEventDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/timeline`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<PolicyTimelineEventDTO[]>(res);
}

export async function getCentralBankCoverage(
  bankId: string
): Promise<CentralBankCoverageResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/central-banks/${encodeURIComponent(bankId)}/coverage`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<CentralBankCoverageResponseDTO>(res);
}
