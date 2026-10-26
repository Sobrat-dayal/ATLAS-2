/**
 * Authenticated REST API Client for Global Economic Calendar (Stage 92).
 */

import {
  AlertDeliveryIntentDTO,
  CalendarViewPreset,
  CreateEventAlertRequestDTO,
  EconomicCalendarCoverageDTO,
  EconomicCalendarEventDetailDTO,
  EconomicCalendarEventDTO,
  EconomicCalendarResponseDTO,
  EconomicEventObservationDTO,
  ConsensusSnapshotDTO,
  ScheduleRevisionDTO,
  UpdateEventAlertRequestDTO,
  UserEventAlertDTO,
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

export class EconomicCalendarApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "ECONOMIC_CALENDAR_API_ERROR") {
    super(message);
    this.name = "EconomicCalendarApiError";
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
      // Ignore JSON parse errors for non-JSON responses
    }
    throw new EconomicCalendarApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export interface GetCalendarEventsParams {
  start_date?: string;
  end_date?: string;
  display_timezone?: string;
  view_preset?: CalendarViewPreset;
  geography_id?: string;
  category?: string;
  importance?: string;
  status?: string;
  search?: string;
  user_id?: string;
}

/**
 * Fetch scheduled and released economic calendar events with filters.
 */
export async function getCalendarEvents(
  params: GetCalendarEventsParams = {}
): Promise<EconomicCalendarResponseDTO> {
  const query = new URLSearchParams();
  if (params.start_date) query.set("start_date", params.start_date);
  if (params.end_date) query.set("end_date", params.end_date);
  if (params.display_timezone) query.set("display_timezone", params.display_timezone);
  if (params.view_preset) query.set("view_preset", params.view_preset);
  if (params.geography_id) query.set("geography_id", params.geography_id);
  if (params.category) query.set("category", params.category);
  if (params.importance) query.set("importance", params.importance);
  if (params.status) query.set("status", params.status);
  if (params.search) query.set("search", params.search);
  if (params.user_id) query.set("user_id", params.user_id);

  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/events?${query.toString()}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<EconomicCalendarResponseDTO>(res);
}

/**
 * Fetch detailed event view including all observations, consensus snapshots, and schedule revisions.
 */
export async function getCalendarEventDetail(
  eventId: string,
  displayTimezone?: string
): Promise<EconomicCalendarEventDetailDTO> {
  const query = new URLSearchParams();
  if (displayTimezone) query.set("display_timezone", displayTimezone);

  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/events/${eventId}?${query.toString()}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicCalendarEventDetailDTO>(res);
}

/**
 * Fetch released observations for a calendar event.
 */
export async function getCalendarEventObservations(
  eventId: string
): Promise<EconomicEventObservationDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/events/${eventId}/observations`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicEventObservationDTO[]>(res);
}

/**
 * Fetch pre-release consensus forecasts for a calendar event.
 */
export async function getCalendarEventForecasts(
  eventId: string
): Promise<ConsensusSnapshotDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/events/${eventId}/forecasts`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<ConsensusSnapshotDTO[]>(res);
}

/**
 * Fetch schedule revisions / postponement history for an event.
 */
export async function getCalendarEventHistory(
  eventId: string
): Promise<ScheduleRevisionDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/events/${eventId}/history`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<ScheduleRevisionDTO[]>(res);
}

/**
 * Fetch event categories.
 */
export async function getCalendarCategories(): Promise<string[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/categories`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<string[]>(res);
}

/**
 * Fetch supported geographic jurisdictions.
 */
export async function getCalendarGeographies(): Promise<string[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/geographies`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<string[]>(res);
}

/**
 * Fetch coverage statistics across calendar sources and forecast availability.
 */
export async function getCalendarCoverage(): Promise<EconomicCalendarCoverageDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/coverage`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicCalendarCoverageDTO>(res);
}

/**
 * Fetch user-owned event alert rules.
 */
export async function getUserAlerts(userId: string = "usr-default"): Promise<UserEventAlertDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/alerts?user_id=${userId}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<UserEventAlertDTO[]>(res);
}

/**
 * Create a new user alert for an economic release event.
 */
export async function createEventAlert(
  payload: CreateEventAlertRequestDTO,
  userId: string = "usr-default"
): Promise<UserEventAlertDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/alerts?user_id=${userId}`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse<UserEventAlertDTO>(res);
}

/**
 * Update an existing event alert.
 */
export async function updateEventAlert(
  alertId: string,
  payload: UpdateEventAlertRequestDTO,
  userId: string = "usr-default"
): Promise<UserEventAlertDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/alerts/${alertId}?user_id=${userId}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse<UserEventAlertDTO>(res);
}

/**
 * Delete / cancel a user event alert.
 */
export async function deleteEventAlert(
  alertId: string,
  userId: string = "usr-default"
): Promise<boolean> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/alerts/${alertId}?user_id=${userId}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<boolean>(res);
}

/**
 * Fetch alert delivery intent history for notifications.
 */
export async function getAlertDeliveryHistory(
  userId: string = "usr-default"
): Promise<AlertDeliveryIntentDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/alerts/history?user_id=${userId}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<AlertDeliveryIntentDTO[]>(res);
}

/**
 * Trigger server-side background alert evaluation.
 */
export async function evaluateCalendarAlerts(
  asOfTime?: string
): Promise<{ evaluated_at: string; total_intents_dispatched: number }> {
  const query = new URLSearchParams();
  if (asOfTime) query.set("as_of_time", asOfTime);

  const url = `${getBaseApiUrl()}/api/v1/economics/calendar/alerts/evaluate?${query.toString()}`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
  });
  return handleResponse<{ evaluated_at: string; total_intents_dispatched: number }>(res);
}
