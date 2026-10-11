export interface GlobalSearchEntityResult {
  result_type: "entity";
  entity_id: string;
  entity_type: string;
  canonical_name: string;
  display_name: string;
  match_kind: string;
  matched_text: string;
  identifier_scheme_key?: string | null;
  alias_type_key?: string | null;
  scope_entity_id?: string | null;
  scope_display_name?: string | null;
}

export interface GlobalSearchResponse {
  results: GlobalSearchEntityResult[];
}

export interface SearchEntitiesOptions {
  query: string;
  entityTypes?: string[];
  limit?: number;
  signal?: AbortSignal;
}

export async function searchEntities(options: SearchEntitiesOptions): Promise<GlobalSearchResponse> {
  const { query, entityTypes, limit = 20, signal } = options;
  const trimmed = query.trim();
  if (!trimmed) {
    return { results: [] };
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const params = new URLSearchParams();
  params.set("q", trimmed);
  if (limit) {
    params.set("limit", limit.toString());
  }
  if (entityTypes && entityTypes.length > 0) {
    for (const t of entityTypes) {
      params.append("entity_types", t);
    }
  }

  const res = await fetch(`${apiUrl}/api/v1/search/entities?${params.toString()}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    signal,
  });

  if (!res.ok) {
    throw new Error(`Search request failed with status ${res.status}`);
  }

  return (await res.json()) as GlobalSearchResponse;
}
