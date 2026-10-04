import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ShellProvider } from "@/hooks/shell/useShellState";
import { AppShell } from "@/components/shell";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ATLAS | Terminal",
  description: "AI-native financial operating system",
};

import { AppearanceProvider } from "@/hooks/appearance";
import { BackgroundProvider } from "@/hooks/background";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Inline script to prevent flash of wrong theme before hydration
  const themeInitScript = `
    try {
      var saved = localStorage.getItem('atlas.appearance.v1');
      var theme = 'dark';
      var density = 'compact';
      var accent = 'blue';
      
      if (saved) {
        var parsed = JSON.parse(saved);
        theme = parsed.theme || 'dark';
        density = parsed.density || 'compact';
        accent = parsed.accent || 'blue';
      }
      
      if (theme === 'system') {
        theme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
      }
      
      document.documentElement.setAttribute('data-theme', theme);
      document.documentElement.setAttribute('data-density', density);
      document.documentElement.setAttribute('data-accent', accent);
    } catch (e) {}
  `;

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className={`${inter.className} antialiased`}>
        <AppearanceProvider>
          <BackgroundProvider>
            <ShellProvider>
              <AppShell>
                {children}
              </AppShell>
            </ShellProvider>
          </BackgroundProvider>
        </AppearanceProvider>
      </body>
    </html>
  );
}
