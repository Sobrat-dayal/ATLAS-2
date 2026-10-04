import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ATLAS | Authentication",
  description: "Sign in to the ATLAS financial intelligence platform",
};

/**
 * Auth layout — renders outside the AppShell.
 * Auth pages get their own minimal chrome: centered card on dark background.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="auth-layout">
      <div className="auth-layout__backdrop" />
      <div className="auth-layout__content">
        {children}
      </div>
    </div>
  );
}
