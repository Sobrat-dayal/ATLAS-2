"use client";

import { useState, type FormEvent } from "react";
import { useAuth } from "@/hooks/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ResetPasswordPage() {
  const { resetPassword } = useAuth();
  const router = useRouter();

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

    const { error: resetError } = await resetPassword(password);

    if (resetError) {
      setError(resetError);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setLoading(false);

    // Redirect to home after short delay
    setTimeout(() => {
      router.push("/home");
    }, 2000);
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
          <h1 className="auth-card__title">Password Updated</h1>
          <p className="auth-card__description">
            Your password has been successfully reset. Redirecting you to
            ATLAS...
          </p>
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
        <h1 className="auth-card__title">Set New Password</h1>

        {error && <div className="auth-card__error">{error}</div>}

        <div className="auth-card__field">
          <label htmlFor="password" className="auth-card__label">
            New Password
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
            Confirm New Password
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
          {loading ? <span className="auth-card__spinner" /> : "Reset Password"}
        </button>
      </form>

      <div className="auth-card__footer">
        <span className="auth-card__footer-text">
          <Link href="/sign-in" className="auth-card__link">
            Back to Sign In
          </Link>
        </span>
      </div>
    </div>
  );
}
