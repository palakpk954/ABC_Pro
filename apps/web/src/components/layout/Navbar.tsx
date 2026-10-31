"use client";

import React, { useState, useEffect } from "react";
import { loginAsPersona } from "@/lib/api";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  CalendarDays, 
  GitFork, 
  Users, 
  Briefcase, 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  ChevronDown,
  UserCheck,
  Sun,
  Moon
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/components/theme/ThemeProvider";

const PERSONAS = [
  { name: "Maya Lin", role: "Resource Manager", email: "maya@acmeconsulting.com", badge: "RM" },
  { name: "Daniel Vance", role: "Delivery Head", email: "daniel@acmeconsulting.com", badge: "DH" },
  { name: "Priya Sharma", role: "Team Lead", email: "priya@acmeconsulting.com", badge: "TL" },
  { name: "Alex Mercer", role: "Admin", email: "alex@acmeconsulting.com", badge: "AD" },
];

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: BarChart3 },
  { name: "Staffing Plans", href: "/plans", icon: CalendarDays },
  { name: "What-If Scenarios", href: "/scenarios", icon: GitFork },
  { name: "Employees", href: "/employees", icon: Users },
  { name: "Projects & Roles", href: "/projects", icon: Briefcase },
  { name: "Skills Matrix", href: "/skills", icon: Sparkles },
];

export function Navbar() {
  const pathname = usePathname();
  const [currentPersona, setCurrentPersona] = useState(PERSONAS[0]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    loginAsPersona(currentPersona.email);
  }, []);

  const handleSelectPersona = (p: (typeof PERSONAS)[0]) => {
    setCurrentPersona(p);
    setDropdownOpen(false);
    loginAsPersona(p.email);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/80 bg-background/80 backdrop-blur-xl transition-colors duration-200">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/25 transition-transform duration-300 group-hover:scale-105">
              <Cpu className="h-5 w-5 text-white animate-pulse-subtle" />
              <div className="absolute inset-0 rounded-xl ring-1 ring-inset ring-white/20" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white font-sans">
                  Allocate
                </span>
                <span className="rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 px-2 py-0.5 text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 ring-1 ring-inset ring-indigo-500/20 dark:ring-indigo-500/30">
                  CP-SAT
                </span>
              </div>
              <p className="text-[11px] font-medium text-muted-foreground">
                AI Resource Optimization
              </p>
            </div>
          </Link>

          {/* Nav links */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  id={`nav-link-${item.name.toLowerCase().replace(/\s+/g, "-")}`}
                  className={cn(
                    "flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-all duration-200",
                    isActive
                      ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-600/15 dark:text-indigo-300 shadow-sm ring-1 ring-indigo-500/20 dark:ring-indigo-500/30 font-semibold"
                      : "text-muted-foreground hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-foreground"
                  )}
                >
                  <Icon className={cn("h-4 w-4", isActive ? "text-indigo-600 dark:text-indigo-400" : "text-muted-foreground")} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right side controls */}
        <div className="flex items-center gap-3">
          {/* Solver Status indicator */}
          <div className="hidden lg:flex items-center gap-2 rounded-full bg-slate-100 dark:bg-slate-900/90 px-3 py-1 border border-slate-200 dark:border-white/10 text-[11px] text-slate-600 dark:text-muted-foreground">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </span>
            <span className="font-medium text-slate-700 dark:text-slate-300">Engine Ready</span>
            <span className="text-slate-400 dark:text-slate-600">|</span>
            <span className="font-mono text-slate-500 dark:text-slate-400">Acme Org</span>
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            id="theme-toggle-btn"
            aria-label="Toggle theme"
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/80 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors shadow-sm"
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4 text-amber-400 transition-transform hover:rotate-45" />
            ) : (
              <Moon className="h-4 w-4 text-indigo-600 transition-transform hover:-rotate-12" />
            )}
          </button>

          {/* Persona Switcher */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              id="persona-switcher-btn"
              className="flex items-center gap-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/80 px-3 py-1.5 text-xs text-foreground transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/80 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 shadow-sm"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 dark:bg-indigo-500/20 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 ring-1 ring-indigo-500/20 dark:ring-indigo-500/30">
                {currentPersona.badge}
              </div>
              <div className="text-left hidden sm:block">
                <p className="text-xs font-semibold leading-tight text-slate-800 dark:text-slate-200">{currentPersona.name}</p>
                <p className="text-[10px] text-muted-foreground">{currentPersona.role}</p>
              </div>
              <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-64 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/95 p-1.5 shadow-2xl backdrop-blur-2xl z-50">
                <div className="px-2.5 py-1.5 text-[10px] font-semibold tracking-wider text-muted-foreground uppercase">
                  Active Persona & Role
                </div>
                {PERSONAS.map((p) => (
                  <button
                    key={p.email}
                    onClick={() => {
                      setCurrentPersona(p);
                      setDropdownOpen(false);
                    }}
                    className={cn(
                      "flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-xs transition-colors",
                      currentPersona.email === p.email
                        ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-600/20 dark:text-indigo-200 font-medium"
                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/70"
                    )}
                  >
                    <div className="flex h-6 w-6 items-center justify-center rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-semibold text-slate-700 dark:text-slate-300">
                      {p.badge}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span>{p.name}</span>
                        {currentPersona.email === p.email && (
                          <UserCheck className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                        )}
                      </div>
                      <span className="text-[10px] text-muted-foreground">{p.role}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
