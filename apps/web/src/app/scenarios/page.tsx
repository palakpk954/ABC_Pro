"use client";

import React, { useState } from "react";
import { MOCK_SCENARIOS, MOCK_PLAN } from "@/lib/mockData";
import { Scenario } from "@/lib/api";
import { formatCurrency, cn } from "@/lib/utils";
import { 
  GitFork, 
  Plus, 
  TrendingDown, 
  TrendingUp, 
  Briefcase, 
  CheckCircle2, 
  Layers, 
  Sparkles
} from "lucide-react";

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>(MOCK_SCENARIOS);
  const [activeScenario, setActiveScenario] = useState<Scenario>(MOCK_SCENARIOS[0]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newScenarioName, setNewScenarioName] = useState("");
  const [newScenarioDesc, setNewScenarioDesc] = useState("");
  const [selectedType, setSelectedType] = useState<"leave" | "project" | "weights">("leave");
  const [notification, setNotification] = useState<string | null>(null);

  const handleCreateScenario = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newScenarioName) return;

    const newScen: Scenario = {
      id: `scen-${Date.now()}`,
      base_plan_id: MOCK_PLAN.id,
      name: newScenarioName,
      description: newScenarioDesc || "Simulated what-if perturbation analyzed against base plan.",
      modifications: { type: selectedType },
      diff_summary: {
        profit_delta: selectedType === "project" ? 42000 : -18500,
        growth_delta: selectedType === "project" ? 12000 : 22000,
        revenue_delta: selectedType === "project" ? 150000 : 0,
        cost_delta: selectedType === "project" ? 108000 : 18500,
        moved_assignments_count: 6,
        unassigned_roles_count: 0,
        affected_employees: ["Alex Rivera", "Sophia Chen", "Elena Rostova"],
        affected_projects: ["Global FinTech Core Banking Migration", "AI Copilot Search"],
      },
      created_at: new Date().toISOString(),
    };

    setScenarios([newScen, ...scenarios]);
    setActiveScenario(newScen);
    setShowCreateModal(false);
    setNewScenarioName("");
    setNewScenarioDesc("");
    setNotification(`Scenario "${newScen.name}" created and solved! Diff calculated against base plan.`);
    setTimeout(() => setNotification(null), 5000);
  };

  const diff = activeScenario.diff_summary;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded-md bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              What-If Counterfactual Analysis
            </span>
            <span className="text-xs text-muted-foreground">FR-15 / FR-26</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Scenario Comparison & Diff
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Evaluate counterfactual conditions (key person leaves, won deals, capacity shocks) against the active baseline plan.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          id="create-scenario-btn"
          className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-all"
        >
          <Plus className="h-4 w-4" />
          Create What-If Scenario
        </button>
      </div>

      {notification && (
        <div className="rounded-xl border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-950/40 p-3.5 text-xs text-indigo-800 dark:text-indigo-200 flex items-center gap-2.5 animate-accordion-down">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-indigo-600 dark:text-indigo-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Scenarios List Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {scenarios.map((s) => (
          <button
            key={s.id}
            onClick={() => setActiveScenario(s)}
            className={cn(
              "flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-semibold whitespace-nowrap transition-all border",
              activeScenario.id === s.id
                ? "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-600/20 dark:text-indigo-200 dark:border-indigo-500/40 shadow-sm"
                : "bg-white dark:bg-slate-900/60 text-slate-600 dark:text-muted-foreground border-slate-200 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white"
            )}
          >
            <GitFork className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>{s.name}</span>
          </button>
        ))}
      </div>

      {/* Side-by-Side Diff Dashboard */}
      {diff && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Diff Impact KPI Cards (Top Banner) */}
          <div className="lg:col-span-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Profit Delta */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Portfolio Profit Delta</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span
                  className={cn(
                    "text-2xl font-bold font-mono",
                    (diff.profit_delta ?? diff.profit_diff ?? 0) >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
                  )}
                >
                  {(diff.profit_delta ?? diff.profit_diff ?? 0) >= 0 ? "+" : ""}
                  {formatCurrency(diff.profit_delta ?? diff.profit_diff ?? 0)}
                </span>
                {(diff.profit_delta ?? diff.profit_diff ?? 0) < 0 ? (
                  <span className="flex items-center text-xs font-semibold text-rose-600 dark:text-rose-400">
                    <TrendingDown className="h-3 w-3" /> Margin Drop
                  </span>
                ) : (
                  <span className="flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                    <TrendingUp className="h-3 w-3" /> Margin Gain
                  </span>
                )}
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Base: {formatCurrency(MOCK_PLAN.profit_score || 412500)} &rarr; Scenario:{" "}
                {formatCurrency((MOCK_PLAN.profit_score || 412500) + (diff.profit_delta ?? diff.profit_diff ?? 0))}
              </p>
            </div>

            {/* Growth Delta */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Growth Score Delta</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span
                  className={cn(
                    "text-2xl font-bold font-mono",
                    (diff.growth_delta ?? diff.growth_diff ?? 0) >= 0 ? "text-purple-600 dark:text-purple-400" : "text-rose-600 dark:text-rose-400"
                  )}
                >
                  {(diff.growth_delta ?? diff.growth_diff ?? 0) >= 0 ? "+" : ""}
                  {(((diff.growth_delta ?? diff.growth_diff ?? 0)) / 1000).toFixed(1)}k pts
                </span>
                <span className="text-xs font-semibold text-purple-600 dark:text-purple-400 flex items-center">
                  <Sparkles className="h-3 w-3" /> Skill Value
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Stretch reallocations and mentorship pairings adjusted
              </p>
            </div>

            {/* Assignments Moved */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Staffing Perturbations</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-mono text-indigo-700 dark:text-indigo-300">
                  {diff.moved_assignments_count}
                </span>
                <span className="text-xs text-muted-foreground">Assignments Shifted</span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                Across {diff.affected_employees?.length || 0} impacted engineers
              </p>
            </div>

            {/* Feasibility Check */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/70 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
              <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">Hard Constraints Feasibility</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
                  100%
                </span>
                <span className="rounded bg-emerald-50 dark:bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300">
                  Feasible
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                0 Unstaffed mandatory project roles
              </p>
            </div>
          </div>

          {/* Side-by-Side Detailed Breakdown */}
          <div className="lg:col-span-6 rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
            <div className="flex items-center gap-2 mb-4">
              <Layers className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Impacted Engineers & Staffing Changes</h3>
            </div>
            <div className="space-y-3">
              {(diff.affected_employees || []).map((empName: any, i: number) => (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-800/40 p-3 border border-slate-200 dark:border-white/5 text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 font-bold">
                      {empName[0]}
                    </div>
                    <div>
                      <span className="font-semibold text-slate-900 dark:text-slate-200">{empName}</span>
                      <p className="text-[10px] text-muted-foreground">
                        Reallocated to cover coverage gap in FinTech Core Migration
                      </p>
                    </div>
                  </div>
                  <span className="rounded-md bg-amber-50 dark:bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-500/30">
                    +4h Shifted
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Scenario Details & Narrative */}
          <div className="lg:col-span-6 rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900/60 p-5 backdrop-blur-xl shadow-sm dark:shadow-xl">
            <div className="flex items-center gap-2 mb-4">
              <Briefcase className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Scenario Narrative & Impacted Engagements</h3>
            </div>
            <div className="rounded-xl bg-slate-50 dark:bg-slate-800/40 p-4 border border-slate-200 dark:border-white/5 space-y-3 text-xs">
              <div>
                <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Description
                </span>
                <p className="mt-1 text-slate-700 dark:text-slate-300 leading-relaxed">
                  {activeScenario.description}
                </p>
              </div>

              <div className="border-t border-slate-200 dark:border-white/5 pt-3">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Impacted Project Engagements
                </span>
                <div className="mt-2 space-y-2">
                  {(diff.affected_projects || []).map((proj: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-800 dark:text-slate-200 font-medium">
                      <div className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                      <span>{proj}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Create Scenario */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">Create What-If Scenario</h3>
            <p className="text-xs text-muted-foreground mb-4">
              Simulate operational conditions without modifying the approved base plan.
            </p>

            <form onSubmit={handleCreateScenario} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Scenario Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Lead Architect 4-Week Absence"
                  value={newScenarioName}
                  onChange={(e) => setNewScenarioName(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/80 px-3.5 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Scenario Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: "leave", label: "Employee Leave" },
                    { id: "project", label: "Add New Deal" },
                    { id: "weights", label: "Weight Shift" },
                  ].map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setSelectedType(t.id as any)}
                      className={cn(
                        "rounded-lg p-2 text-center border font-semibold transition-all",
                        selectedType === t.id
                          ? "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-600/20 dark:text-indigo-300 dark:border-indigo-500/40"
                          : "bg-slate-50 dark:bg-slate-800/50 text-muted-foreground border-slate-200 dark:border-white/5 hover:bg-slate-100 dark:hover:bg-slate-800"
                      )}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1">Notes / Description</label>
                <textarea
                  rows={3}
                  placeholder="Describe the operational perturbation to evaluate..."
                  value={newScenarioDesc}
                  onChange={(e) => setNewScenarioDesc(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800/80 px-3.5 py-2 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-200 dark:border-white/10">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="rounded-xl px-4 py-2 text-muted-foreground hover:text-slate-900 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 font-semibold text-white hover:bg-indigo-500 shadow-lg shadow-indigo-600/20"
                >
                  Solve & Compare Diff
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
