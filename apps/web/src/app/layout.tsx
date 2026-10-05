import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/hooks/auth";
import { AuthorizationProvider } from "@/hooks/authorization";
import { AppearanceProvider } from "@/hooks/appearance";
import { BackgroundProvider } from "@/hooks/background";
import { PreferenceSyncProvider } from "@/hooks/preferences/PreferenceSyncProvider";
import { GlobalApplicationContextProvider } from "@/hooks/application-context";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ATLAS | Terminal",
  description: "AI-native financial operating system",
};

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
        <AuthProvider>
          <AuthorizationProvider>
            <PreferenceSyncProvider>
              <AppearanceProvider>
                <BackgroundProvider>
                  <GlobalApplicationContextProvider>
                    {children}
                  </GlobalApplicationContextProvider>
                </BackgroundProvider>
              </AppearanceProvider>
            </PreferenceSyncProvider>
          </AuthorizationProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
