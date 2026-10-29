import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { ThemeProvider } from "@/components/theme/ThemeProvider";

export const metadata: Metadata = {
  title: "Allocate — AI-Assisted Resource Allocation Platform",
  description:
    "Deterministic, explainable, and growth-aware resource allocation for IT services and consulting organizations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans min-h-screen bg-background text-foreground flex flex-col transition-colors duration-200">
        <ThemeProvider>
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="border-t border-border/60 py-6 text-center text-xs text-muted-foreground bg-slate-50/50 dark:bg-transparent">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
              <p>Allocate MVP &copy; 2026. Deterministic CP-SAT Constraint Optimization.</p>
              <div className="flex items-center gap-4 text-[11px]">
                <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-medium">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Human-in-the-Loop Approved
                </span>
                <span>12-Week Rolling Horizon</span>
              </div>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
