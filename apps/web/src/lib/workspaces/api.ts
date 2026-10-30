/**
 * Typed API Client for ATLAS Workspaces Architecture (Stage 120).
 */

import {
  AddPanelRequest,
  CreateWorkspaceRequest,
  PanelTypeDefinition,
  UpdateLayoutRequest,
  UpdateWorkspaceMetadataRequest,
  Workspace,
  WorkspaceLayout,
  WorkspaceLinkGroup,
  WorkspacePanelInstance,
  WorkspaceSortOption,
  WorkspaceTemplate,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errBody: any;
    try {
      errBody = await res.json();
    } catch {
      errBody = { message: res.statusText };
    }
    const errorMsg = errBody?.detail?.message || errBody?.message || `Request failed with status ${res.status}`;
    const err = new Error(errorMsg);
    (err as any).status = res.status;
    (err as any).code = errBody?.detail?.code || errBody?.code;
    throw err;
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json() as Promise<T>;
}

export async function listWorkspaces(
  sortBy: WorkspaceSortOption = "RECENTLY_OPENED",
  includeArchived: boolean = false
): Promise<Workspace[]> {
  const query = new URLSearchParams({
    sort_by: sortBy,
    include_archived: String(includeArchived),
  });
  return fetchJSON<Workspace[]>(`/workspaces?${query.toString()}`);
}

export async function createWorkspace(data: CreateWorkspaceRequest): Promise<Workspace> {
  return fetchJSON<Workspace>("/workspaces", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getWorkspace(workspaceId: string): Promise<Workspace> {
  return fetchJSON<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}`);
}

export async function updateWorkspace(
  workspaceId: string,
  data: UpdateWorkspaceMetadataRequest
): Promise<Workspace> {
  return fetchJSON<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteWorkspace(workspaceId: string, permanent: boolean = false): Promise<void> {
  await fetchJSON<void>(`/workspaces/${encodeURIComponent(workspaceId)}?permanent=${permanent}`, {
    method: "DELETE",
  });
}

export async function duplicateWorkspace(workspaceId: string, newName?: string): Promise<Workspace> {
  return fetchJSON<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}/duplicate`, {
    method: "POST",
    body: JSON.stringify({ new_name: newName }),
  });
}

export async function restoreWorkspace(workspaceId: string): Promise<Workspace> {
  return fetchJSON<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}/restore`, {
    method: "POST",
  });
}

export async function setDefaultWorkspace(workspaceId: string): Promise<Workspace> {
  return fetchJSON<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}/set-default`, {
    method: "POST",
  });
}

// ---------------- Layout Operations ----------------

export async function getLayout(workspaceId: string): Promise<WorkspaceLayout> {
  return fetchJSON<WorkspaceLayout>(`/workspaces/${encodeURIComponent(workspaceId)}/layout`);
}

export async function updateLayout(
  workspaceId: string,
  data: UpdateLayoutRequest
): Promise<WorkspaceLayout> {
  return fetchJSON<WorkspaceLayout>(`/workspaces/${encodeURIComponent(workspaceId)}/layout`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function recoverLayout(workspaceId: string): Promise<WorkspaceLayout> {
  return fetchJSON<WorkspaceLayout>(`/workspaces/${encodeURIComponent(workspaceId)}/recover`, {
    method: "POST",
  });
}

// ---------------- Panel Operations ----------------

export async function addPanel(
  workspaceId: string,
  data: AddPanelRequest
): Promise<WorkspacePanelInstance> {
  return fetchJSON<WorkspacePanelInstance>(`/workspaces/${encodeURIComponent(workspaceId)}/panels`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePanel(
  workspaceId: string,
  panelId: string,
  data: Partial<WorkspacePanelInstance>
): Promise<WorkspacePanelInstance> {
  return fetchJSON<WorkspacePanelInstance>(
    `/workspaces/${encodeURIComponent(workspaceId)}/panels/${encodeURIComponent(panelId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    }
  );
}

export async function removePanel(workspaceId: string, panelId: string): Promise<void> {
  await fetchJSON<void>(
    `/workspaces/${encodeURIComponent(workspaceId)}/panels/${encodeURIComponent(panelId)}`,
    {
      method: "DELETE",
    }
  );
}

// ---------------- Link Groups ----------------

export async function listLinkGroups(workspaceId: string): Promise<WorkspaceLinkGroup[]> {
  return fetchJSON<WorkspaceLinkGroup[]>(`/workspaces/${encodeURIComponent(workspaceId)}/link-groups`);
}

export async function createLinkGroup(
  workspaceId: string,
  name: string,
  color: string,
  initialContext?: Record<string, unknown>
): Promise<WorkspaceLinkGroup> {
  return fetchJSON<WorkspaceLinkGroup>(`/workspaces/${encodeURIComponent(workspaceId)}/link-groups`, {
    method: "POST",
    body: JSON.stringify({ name, color, initial_context: initialContext }),
  });
}

export async function updateLinkGroupContext(
  workspaceId: string,
  linkGroupId: string,
  context: Record<string, unknown>
): Promise<WorkspaceLinkGroup> {
  return fetchJSON<WorkspaceLinkGroup>(
    `/workspaces/${encodeURIComponent(workspaceId)}/link-groups/${encodeURIComponent(linkGroupId)}`,
    {
      method: "PATCH",
      body: JSON.stringify({ context }),
    }
  );
}

export async function deleteLinkGroup(workspaceId: string, linkGroupId: string): Promise<void> {
  await fetchJSON<void>(
    `/workspaces/${encodeURIComponent(workspaceId)}/link-groups/${encodeURIComponent(linkGroupId)}`,
    {
      method: "DELETE",
    }
  );
}

// ---------------- Templates & Types ----------------

export async function listTemplates(): Promise<WorkspaceTemplate[]> {
  return fetchJSON<WorkspaceTemplate[]>("/workspaces/templates");
}

export async function getTemplate(templateId: string): Promise<WorkspaceTemplate> {
  return fetchJSON<WorkspaceTemplate>(`/workspaces/templates/${encodeURIComponent(templateId)}`);
}

export async function listPanelTypes(): Promise<PanelTypeDefinition[]> {
  return fetchJSON<PanelTypeDefinition[]>("/workspaces/panel-types");
}

