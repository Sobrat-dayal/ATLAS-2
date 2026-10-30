/**
 * Universal Saved System - Typed API Client (Stage 119).
 */

import {
  CreateSavedCollectionRequest,
  CreateSavedConfigurationRequest,
  CreateSavedItemRequest,
  CreateSavedTagRequest,
  ResolvedTarget,
  SavedBulkActionRequest,
  SavedBulkActionResponse,
  SavedCollection,
  SavedCollectionTree,
  SavedItem,
  SavedItemListResponse,
  SavedLibrarySummary,
  SavedSortOption,
  SavedTag,
  SavedTargetDefinition,
  SavedTargetType,
  SavedViewConfiguration,
  UpdateSavedCollectionRequest,
  UpdateSavedItemRequest,
  ValidateConfigurationRequest,
  ValidateConfigurationResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = response.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// ----------------------------------------------------------------------------
// Target Metadata & Resolvers
// ----------------------------------------------------------------------------

export async function getSavedTargetTypes(): Promise<SavedTargetDefinition[]> {
  return request<SavedTargetDefinition[]>("/saved/types");
}

export async function resolveTarget(
  target_type: SavedTargetType,
  target_id: string,
  requested_revision_id?: string
): Promise<ResolvedTarget> {
  return request<ResolvedTarget>("/saved/resolve", {
    method: "POST",
    body: JSON.stringify({
      target_type,
      target_id,
      requested_revision_id,
    }),
  });
}

export async function getLibrarySummary(): Promise<SavedLibrarySummary> {
  return request<SavedLibrarySummary>("/saved/summary");
}

// ----------------------------------------------------------------------------
// Saved Items CRUD
// ----------------------------------------------------------------------------

export interface ListSavedItemsParams {
  search?: string;
  target_type?: SavedTargetType;
  target_module?: string;
  collection_id?: string;
  tag?: string;
  favorite?: boolean;
  pinned?: boolean;
  sort_by?: SavedSortOption;
  page?: number;
  page_size?: number;
}

export async function listSavedItems(params: ListSavedItemsParams = {}): Promise<SavedItemListResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set("search", params.search);
  if (params.target_type) query.set("target_type", params.target_type);
  if (params.target_module) query.set("target_module", params.target_module);
  if (params.collection_id) query.set("collection_id", params.collection_id);
  if (params.tag) query.set("tag", params.tag);
  if (params.favorite !== undefined) query.set("favorite", String(params.favorite));
  if (params.pinned !== undefined) query.set("pinned", String(params.pinned));
  if (params.sort_by) query.set("sort_by", params.sort_by);
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));

  const qs = query.toString();
  return request<SavedItemListResponse>(`/saved${qs ? `?${qs}` : ""}`);
}

export async function saveItem(req: CreateSavedItemRequest): Promise<SavedItem> {
  return request<SavedItem>("/saved", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function getSavedItem(saved_item_id: string): Promise<SavedItem> {
  return request<SavedItem>(`/saved/${encodeURIComponent(saved_item_id)}`);
}

export async function updateSavedItem(
  saved_item_id: string,
  req: UpdateSavedItemRequest
): Promise<SavedItem> {
  return request<SavedItem>(`/saved/${encodeURIComponent(saved_item_id)}`, {
    method: "PATCH",
    body: JSON.stringify(req),
  });
}

export async function deleteSavedItem(saved_item_id: string): Promise<void> {
  return request<void>(`/saved/${encodeURIComponent(saved_item_id)}`, {
    method: "DELETE",
  });
}

export async function restoreSavedItem(saved_item_id: string): Promise<SavedItem> {
  return request<SavedItem>(`/saved/${encodeURIComponent(saved_item_id)}/restore`, {
    method: "POST",
  });
}

export async function toggleFavorite(saved_item_id: string, favorite: boolean): Promise<SavedItem> {
  const method = favorite ? "PUT" : "DELETE";
  return request<SavedItem>(`/saved/${encodeURIComponent(saved_item_id)}/favorite`, {
    method,
  });
}

export async function togglePin(saved_item_id: string, pinned: boolean): Promise<SavedItem> {
  const method = pinned ? "PUT" : "DELETE";
  return request<SavedItem>(`/saved/${encodeURIComponent(saved_item_id)}/pin`, {
    method,
  });
}

// ----------------------------------------------------------------------------
// Collections
// ----------------------------------------------------------------------------

export async function listCollections(): Promise<SavedCollection[]> {
  return request<SavedCollection[]>("/saved/collections");
}

export async function getCollectionTree(): Promise<SavedCollectionTree[]> {
  return request<SavedCollectionTree[]>("/saved/collections/tree");
}

export async function createCollection(req: CreateSavedCollectionRequest): Promise<SavedCollection> {
  return request<SavedCollection>("/saved/collections", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function updateCollection(
  collection_id: string,
  req: UpdateSavedCollectionRequest
): Promise<SavedCollection> {
  return request<SavedCollection>(`/saved/collections/${encodeURIComponent(collection_id)}`, {
    method: "PATCH",
    body: JSON.stringify(req),
  });
}

export async function deleteCollection(collection_id: string): Promise<void> {
  return request<void>(`/saved/collections/${encodeURIComponent(collection_id)}`, {
    method: "DELETE",
  });
}

export async function addItemsToCollection(
  collection_id: string,
  saved_item_ids: string[]
): Promise<{ status: string; added_count: number }> {
  return request<{ status: string; added_count: number }>(
    `/saved/collections/${encodeURIComponent(collection_id)}/items`,
    {
      method: "POST",
      body: JSON.stringify({ saved_item_ids }),
    }
  );
}

export async function removeItemFromCollection(
  collection_id: string,
  saved_item_id: string
): Promise<void> {
  return request<void>(
    `/saved/collections/${encodeURIComponent(collection_id)}/items/${encodeURIComponent(saved_item_id)}`,
    {
      method: "DELETE",
    }
  );
}

// ----------------------------------------------------------------------------
// Tags
// ----------------------------------------------------------------------------

export async function listTags(): Promise<SavedTag[]> {
  return request<SavedTag[]>("/saved/tags");
}

export async function createTag(req: CreateSavedTagRequest): Promise<SavedTag> {
  return request<SavedTag>("/saved/tags", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function assignTagToItem(saved_item_id: string, name: string): Promise<SavedTag> {
  return request<SavedTag>(`/saved/${encodeURIComponent(saved_item_id)}/tags`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function removeTagFromItem(saved_item_id: string, tag_id: string): Promise<void> {
  return request<void>(
    `/saved/${encodeURIComponent(saved_item_id)}/tags/${encodeURIComponent(tag_id)}`,
    {
      method: "DELETE",
    }
  );
}

// ----------------------------------------------------------------------------
// View Configurations
// ----------------------------------------------------------------------------

export async function createConfiguration(
  req: CreateSavedConfigurationRequest
): Promise<SavedViewConfiguration> {
  return request<SavedViewConfiguration>("/saved/configurations", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function getConfiguration(configuration_id: string): Promise<SavedViewConfiguration> {
  return request<SavedViewConfiguration>(`/saved/configurations/${encodeURIComponent(configuration_id)}`);
}

export async function validateConfiguration(
  req: ValidateConfigurationRequest
): Promise<ValidateConfigurationResponse> {
  return request<ValidateConfigurationResponse>("/saved/configurations/validate", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

// ----------------------------------------------------------------------------
// Bulk Operations
// ----------------------------------------------------------------------------

export async function executeBulkAction(req: SavedBulkActionRequest): Promise<SavedBulkActionResponse> {
  return request<SavedBulkActionResponse>("/saved/bulk", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

