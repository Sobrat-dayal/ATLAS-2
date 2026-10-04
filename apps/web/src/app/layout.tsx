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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <ShellProvider>
          <AppShell>
            {children}
          </AppShell>
        </ShellProvider>
      </body>
    </html>
  );
}
