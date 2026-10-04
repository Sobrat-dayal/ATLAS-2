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
import type { User, Session } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/browser";

/* ──────────────────────────────────────────────
   Types
   ────────────────────────────────────────────── */

interface AuthState {
  /** The current Supabase user, or null if signed out. */
  user: User | null;
  /** The current session (contains access_token). */
  session: Session | null;
  /** True while the initial session is loading. */
  loading: boolean;
  /** Convenience: true when user is authenticated. */
  isAuthenticated: boolean;
}

interface AuthActions {
  /** Sign in with email + password. */
  signIn: (
    email: string,
    password: string
  ) => Promise<{ error: string | null }>;

  /** Create a new account with email + password. */
  signUp: (
    email: string,
    password: string
  ) => Promise<{ error: string | null; needsVerification: boolean }>;

  /** Sign out the current user. */
  signOut: () => Promise<void>;

  /** Send a password-reset email. */
  forgotPassword: (email: string) => Promise<{ error: string | null }>;

  /** Reset password (called from the recovery link page). */
  resetPassword: (
    newPassword: string
  ) => Promise<{ error: string | null }>;

  /** Refresh the session manually. */
  refreshSession: () => Promise<void>;
}

type AuthContextValue = AuthState & AuthActions;

/* ──────────────────────────────────────────────
   Context
   ────────────────────────────────────────────── */

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/* ──────────────────────────────────────────────
   Sanitize error messages
   ────────────────────────────────────────────── */

function sanitizeError(error: { message: string } | null): string | null {
  if (!error) return null;
  const msg = error.message.toLowerCase();

  if (msg.includes("invalid login credentials") || msg.includes("invalid_credentials")) {
    return "Invalid email or password.";
  }
  if (msg.includes("email not confirmed")) {
    return "Please verify your email before signing in.";
  }
  if (msg.includes("user already registered") || msg.includes("already been registered")) {
    return "An account with this email already exists.";
  }
  if (msg.includes("password") && msg.includes("short")) {
    return "Password must be at least 6 characters.";
  }
  if (msg.includes("rate limit") || msg.includes("too many")) {
    return "Too many attempts. Please try again later.";
  }
  // Generic fallback — never leak raw Supabase errors
  return "Something went wrong. Please try again.";
}

/* ──────────────────────────────────────────────
   Provider
   ────────────────────────────────────────────── */

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  const supabase = useMemo(() => createClient(), []);

  // Bootstrap: get initial session and subscribe to auth changes
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session: s } }) => {
      setSession(s);
      setUser(s?.user ?? null);
      setLoading(false);
    });

    // Subscribe to auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s);
      setUser(s?.user ?? null);
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase]);

  /* ── Actions ── */

  const signIn = useCallback(
    async (email: string, password: string) => {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      return { error: sanitizeError(error) };
    },
    [supabase]
  );

  const signUp = useCallback(
    async (email: string, password: string) => {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) {
        return { error: sanitizeError(error), needsVerification: false };
      }

      // If identities is empty or user is unconfirmed, verification is needed
      const needsVerification =
        data.user?.identities?.length === 0 ||
        data.user?.confirmed_at == null;

      return { error: null, needsVerification };
    },
    [supabase]
  );

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    // Middleware will handle the redirect on next navigation
    window.location.href = "/sign-in";
  }, [supabase]);

  const forgotPassword = useCallback(
    async (email: string) => {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      return { error: sanitizeError(error) };
    },
    [supabase]
  );

  const resetPassword = useCallback(
    async (newPassword: string) => {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });
      return { error: sanitizeError(error) };
    },
    [supabase]
  );

  const refreshSession = useCallback(async () => {
    const { data } = await supabase.auth.refreshSession();
    setSession(data.session);
    setUser(data.session?.user ?? null);
  }, [supabase]);

  /* ── Value ── */

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      session,
      loading,
      isAuthenticated: !!user,
      signIn,
      signUp,
      signOut,
      forgotPassword,
      resetPassword,
      refreshSession,
    }),
    [user, session, loading, signIn, signUp, signOut, forgotPassword, resetPassword, refreshSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/* ──────────────────────────────────────────────
   Hook
   ────────────────────────────────────────────── */

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return ctx;
}
