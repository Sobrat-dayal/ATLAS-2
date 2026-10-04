"use client";

import { useState, type FormEvent } from "react";
import { useAuth } from "@/hooks/auth";
import Link from "next/link";

export default function SignUpPage() {
  const { signUp } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    const { error: signUpError, needsVerification } = await signUp(
      email,
      password
    );

    if (signUpError) {
      setError(signUpError);
      setLoading(false);
      return;
    }

    if (needsVerification) {
      setSuccess(true);
      setLoading(false);
      return;
    }

    // Auto-signed-in (e.g. email confirmation disabled)
    window.location.href = "/home";
  }

  if (success) {
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
            We&apos;ve sent a verification link to{" "}
            <strong>{email}</strong>. Click the link in the email to activate
            your account.
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
        <h1 className="auth-card__title">Create Account</h1>

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

        <div className="auth-card__field">
          <label htmlFor="password" className="auth-card__label">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Min. 6 characters"
            required
            autoComplete="new-password"
            className="auth-card__input"
          />
        </div>

        <div className="auth-card__field">
          <label htmlFor="confirm-password" className="auth-card__label">
            Confirm Password
          </label>
          <input
            id="confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-enter password"
            required
            autoComplete="new-password"
            className="auth-card__input"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="auth-card__button"
        >
          {loading ? <span className="auth-card__spinner" /> : "Create Account"}
        </button>
      </form>

      {/* Footer */}
      <div className="auth-card__footer">
        <span className="auth-card__footer-text">
          Already have an account?{" "}
          <Link href="/sign-in" className="auth-card__link">
            Sign in
          </Link>
        </span>
      </div>
    </div>
  );
}
