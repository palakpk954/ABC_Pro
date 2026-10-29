"use client";

import React from "react";
import { Project, Plan } from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import { CheckCircle2, XCircle, AlertCircle, Building2, Calendar, Star } from "lucide-react";

interface ProjectPortfolioPanelProps {
  projects: Project[];
  plan: Plan;
}

export function ProjectPortfolioPanel({ projects, plan }: ProjectPortfolioPanelProps) {
  const droppedReasons = plan.dropped_project_reasons || {};

  const selectedProjects = projects.filter((p) => p.status !== "dropped");
  const droppedProjects = projects.filter((p) => p.status === "dropped");

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Selected Projects */}
      <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">Accepted Portfolio Engagements</h3>
          </div>
          <span className="rounded-full bg-emerald-50 dark:bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20">
            {selectedProjects.length} Selected
          </span>
        </div>

        <div className="space-y-3">
          {selectedProjects.map((p) => (
            <div
              key={p.id}
              className="rounded-xl border border-slate-200/80 dark:border-white/5 bg-slate-50/60 dark:bg-slate-800/40 p-4 transition-all hover:bg-slate-100/80 dark:hover:bg-slate-800/70 hover:border-emerald-500/30"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white">{p.name}</h4>
                    {p.mandatory && (
                      <span className="rounded bg-rose-50 dark:bg-rose-500/20 px-1.5 py-0.5 text-[10px] font-bold text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-500/30">
                        Mandatory
                      </span>
                    )}
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Building2 className="h-3 w-3 text-slate-400" /> {p.client}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 text-slate-400" /> 12 Weeks
                    </span>
                    <span className="flex items-center gap-1 text-amber-600 dark:text-amber-300 font-medium">
                      <Star className="h-3 w-3 fill-amber-500 text-amber-500 dark:fill-amber-300 dark:text-amber-300" /> Priority {p.priority}/5
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-sm font-bold font-mono text-emerald-600 dark:text-emerald-400">
                    {formatCurrency(p.revenue)}
                  </span>
                  <p className="text-[10px] text-muted-foreground mt-0.5">
                    {p.roles.length} Roles Staffed
                  </p>
                </div>
              </div>

              {/* Roles summary */}
              {p.roles.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5 border-t border-slate-200 dark:border-white/5 pt-2.5">
                  {p.roles.map((r) => (
                    <span
                      key={r.id}
                      className={cn(
                        "rounded-md px-2 py-0.5 text-[11px] font-medium border",
                        r.is_stretch_allowed
                          ? "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-500/10 dark:text-purple-300 dark:border-purple-500/20"
                          : "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-700/50 dark:text-slate-300 dark:border-slate-600/50"
                      )}
                    >
                      {r.role_title} ({r.hours_per_week}h/w)
                      {r.is_stretch_allowed && " ✨"}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Dropped / Counterfactual Projects */}
      <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl transition-all">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-rose-600 dark:text-rose-400" />
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">Dropped Projects & Explainability</h3>
          </div>
          <span className="rounded-full bg-rose-50 dark:bg-rose-500/10 px-2.5 py-0.5 text-xs font-semibold text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20">
            {droppedProjects.length} Dropped
          </span>
        </div>

        {droppedProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
            <CheckCircle2 className="h-8 w-8 text-emerald-500 dark:text-emerald-400/50 mb-2" />
            <p className="text-sm">No candidate projects were dropped in this plan.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {droppedProjects.map((p) => {
              const reason =
                droppedReasons[p.id] ||
                "Opportunity displaced: lower contribution margin than alternative portfolio projects given constrained senior staff capacity.";

              return (
                <div
                  key={p.id}
                  className="rounded-xl border border-rose-200 dark:border-rose-500/20 bg-rose-50/40 dark:bg-rose-950/10 p-4 transition-all"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-200">{p.name}</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Client: {p.client} &bull; Potential Revenue: {formatCurrency(p.revenue)}
                      </p>
                    </div>
                    <span className="rounded bg-rose-100 dark:bg-rose-500/20 px-2 py-0.5 text-[10px] font-semibold text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-500/30">
                      Excluded
                    </span>
                  </div>

                  <div className="mt-3 rounded-lg border border-rose-200 dark:border-rose-500/20 bg-white dark:bg-slate-900/90 p-3 shadow-sm">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 text-amber-500 dark:text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-amber-700 dark:text-amber-400">
                          Solver Explanation (FR-20 Counterfactual)
                        </span>
                        <p className="text-xs text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">
                          {reason}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
