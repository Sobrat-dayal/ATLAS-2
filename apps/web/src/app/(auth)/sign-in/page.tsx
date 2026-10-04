"use client";

import { useState, type FormEvent } from "react";
import { useAuth } from "@/hooks/auth";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

export default function SignInPage() {
  const { signIn } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Show callback error if redirected from failed auth
  const callbackError = searchParams.get("error");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const { error: signInError } = await signIn(email, password);

    if (signInError) {
      setError(signInError);
      setLoading(false);
      return;
    }

    // Redirect to original destination or home
    const redirectTo = searchParams.get("redirectTo") || "/home";
    router.push(redirectTo);
  }

  return (
    <div className="auth-card">
      {/* Logo / Branding */}
      <div className="auth-card__header">
        <div className="auth-card__logo">
          <span className="auth-card__logo-icon">◆</span>
          <span className="auth-card__logo-text">ATLAS</span>
        </div>
        <p className="auth-card__subtitle">Financial Intelligence Platform</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="auth-card__form">
        <h1 className="auth-card__title">Sign In</h1>

        {(error || callbackError) && (
          <div className="auth-card__error">
            {error || "Authentication failed. Please try again."}
          </div>
        )}

        <div className="auth-card__field">
          <label htmlFor="email" className="auth-card__label">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
            className="auth-card__input"
          />
        </div>

        <div className="auth-card__field">
          <label htmlFor="password" className="auth-card__label">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            autoComplete="current-password"
            className="auth-card__input"
          />
        </div>

        <div className="auth-card__actions-row">
          <Link href="/forgot-password" className="auth-card__link">
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="auth-card__button"
        >
          {loading ? (
            <span className="auth-card__spinner" />
          ) : (
            "Sign In"
          )}
        </button>
      </form>

      {/* Footer */}
      <div className="auth-card__footer">
        <span className="auth-card__footer-text">
          Don&apos;t have an account?{" "}
          <Link href="/sign-up" className="auth-card__link">
            Create account
          </Link>
        </span>
      </div>
    </div>
  );
}
