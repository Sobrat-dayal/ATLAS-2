import { ShellProvider } from "@/hooks/shell/useShellState";
import { AppShell } from "@/components/shell";

/**
 * Atlas route group layout — wraps all authenticated app pages in the AppShell.
 * Auth pages use a separate (auth) group with their own layout.
 */
export default function AtlasGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ShellProvider>
      <AppShell>{children}</AppShell>
    </ShellProvider>
  );
}
