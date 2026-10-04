"use client";

import { useState, type FormEvent } from "react";
import { useAuth } from "@/hooks/auth";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();

  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const { error: resetError } = await forgotPassword(email);

    if (resetError) {
      setError(resetError);
      setLoading(false);
      return;
    }

    setSent(true);
    setLoading(false);
  }

  if (sent) {
    return (
      <div className="auth-card">
        <div className="auth-card__header">
          <div className="auth-card__logo">
            <span className="auth-card__logo-icon">◆</span>
            <span className="auth-card__logo-text">ATLAS</span>
          </div>
        </div>
        <div className="auth-card__form">
          <h1 className="auth-card__title">Check Your Email</h1>
          <p className="auth-card__description">
            If an account with <strong>{email}</strong> exists, we&apos;ve sent
            password reset instructions to that address.
          </p>
          <Link href="/sign-in" className="auth-card__button" style={{ textAlign: "center", display: "block", textDecoration: "none" }}>
            Back to Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-card">
      {/* Logo */}
      <div className="auth-card__header">
        <div className="auth-card__logo">
          <span className="auth-card__logo-icon">◆</span>
          <span className="auth-card__logo-text">ATLAS</span>
        </div>
        <p className="auth-card__subtitle">Financial Intelligence Platform</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="auth-card__form">
        <h1 className="auth-card__title">Reset Password</h1>
        <p className="auth-card__description">
          Enter your email address and we&apos;ll send you a link to reset your
          password.
        </p>

        {error && <div className="auth-card__error">{error}</div>}

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

        <button
          type="submit"
          disabled={loading}
          className="auth-card__button"
        >
          {loading ? <span className="auth-card__spinner" /> : "Send Reset Link"}
        </button>
      </form>

      <div className="auth-card__footer">
        <span className="auth-card__footer-text">
          Remember your password?{" "}
          <Link href="/sign-in" className="auth-card__link">
            Sign in
          </Link>
        </span>
      </div>
    </div>
  );
}
