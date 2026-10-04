"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";
import { useAuth } from "../auth";
import { getActiveAtlasModule, ATLAS_MODULES } from "@/config/atlas-modules";
import { usePathname } from "next/navigation";

export interface AuthorizationState {
  roles: string[];
  permissions: string[];
  isLoading: boolean;
  error: Error | null;
}

export interface AuthorizationActions {
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  canViewModule: (moduleId: string) => boolean;
  refreshAuthorization: () => Promise<void>;
}

export type AuthorizationContextValue = AuthorizationState & AuthorizationActions;

const AuthorizationContext = createContext<AuthorizationContextValue | undefined>(undefined);

export function AuthorizationProvider({ children }: { children: ReactNode }) {
  const { session, isAuthenticated } = useAuth();
  const [roles, setRoles] = useState<string[]>([]);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAuthz = useCallback(async () => {
    if (!session?.access_token) {
      setRoles([]);
      setPermissions([]);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const res = await fetch("/api/v1/authz/me", {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!res.ok) {
        throw new Error(`Authorization failed: ${res.status}`);
      }

      const data = await res.json();
      setRoles(data.roles || []);
      setPermissions(data.permissions || []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch authorization"));
      setRoles([]);
      setPermissions([]);
    } finally {
      setIsLoading(false);
    }
  }, [session?.access_token]);

  useEffect(() => {
    fetchAuthz();
  }, [fetchAuthz]);

  const hasPermission = useCallback(
    (permission: string) => permissions.includes(permission),
    [permissions]
  );

  const hasAnyPermission = useCallback(
    (perms: string[]) => perms.some((p) => permissions.includes(p)),
    [permissions]
  );

  const hasAllPermissions = useCallback(
    (perms: string[]) => perms.every((p) => permissions.includes(p)),
    [permissions]
  );

  const canViewModule = useCallback(
    (moduleId: string) => {
      const module = Object.values(ATLAS_MODULES).find((m) => m.id === moduleId);
      if (!module) return false;
      return hasPermission(module.requiredPermission);
    },
    [hasPermission]
  );

  const value = useMemo<AuthorizationContextValue>(
    () => ({
      roles,
      permissions,
      isLoading,
      error,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      canViewModule,
      refreshAuthorization: fetchAuthz,
    }),
    [roles, permissions, isLoading, error, hasPermission, hasAnyPermission, hasAllPermissions, canViewModule, fetchAuthz]
  );

  // If not authenticated, we can still provide empty context
  if (!isAuthenticated && !session) {
    return <AuthorizationContext.Provider value={value}>{children}</AuthorizationContext.Provider>;
  }

  return <AuthorizationContext.Provider value={value}>{children}</AuthorizationContext.Provider>;
}

export function useAuthorization(): AuthorizationContextValue {
  const ctx = useContext(AuthorizationContext);
  if (ctx === undefined) {
    throw new Error("useAuthorization must be used within an <AuthorizationProvider>");
  }
  return ctx;
}
